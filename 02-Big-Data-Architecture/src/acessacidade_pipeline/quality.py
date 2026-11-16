"""Relatório de qualidade + verificações automáticas (quality gate) da execução.

Gera data/processed/relatorio_qualidade.json e .md. Se alguma verificação falhar, o
relatório é salvo mesmo assim e a tarefa levanta `QualityGateError` — na DAG isso impede
a publicação de um snapshot Gold inconsistente (publish_gold não roda).
"""
from __future__ import annotations

import csv
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from .config import PipelineConfig
from .dominio import STATUS, TIPO_OBSTACULO, VISAO_CLASSIFICACAO
from .gold import TABELAS_GOLD, calcular_qualidade
from .raw import TABELA_APP, TABELA_SIMULADA
from .warehouse import contar

log = logging.getLogger("acessacidade_pipeline")

CHAVES_SNAPSHOT = ("disponivel", "gerado_em", "execucao_id", "inclui_simulados", "fontes",
                   "denuncias_por_bairro", "denuncias_por_categoria", "denuncias_por_periodo",
                   "denuncias_por_status", "resultado_visao", "qualidade")
CHAVES_QUALIDADE = ("linhas_raw", "linhas_bronze", "duplicatas_removidas", "datas_invalidas",
                    "coordenadas_invalidas", "campos_obrigatorios_ausentes", "percentual_registros_validos")
MARCADOR_DADO_PESSOAL = "Pessoa Simulada"

FLAGS_BRONZE = ("flag_possui_nome", "flag_data_ausente", "flag_data_invalida", "flag_coordenada_ausente",
                "flag_coordenada_invalida", "flag_pontuacao_invalida", "flag_logradouro_ausente",
                "flag_bairro_ausente", "flag_tipo_ausente", "flag_descricao_ausente", "flag_impacto_ausente",
                "flag_campo_obrigatorio_ausente")
FLAGS_SILVER = ("flag_bairro_nao_padronizado", "flag_tipo_nao_reconhecido", "flag_impacto_nao_reconhecido",
                "flag_status_inferido", "flag_visao_inconsistente", "flag_coordenada_fora_area",
                "flag_data_invalida")


class QualityGateError(RuntimeError):
    """Uma ou mais verificações de qualidade falharam."""


def _linhas_csv(caminho: Path) -> int:
    with open(caminho, encoding="utf-8-sig", newline="") as arq:
        leitor = csv.reader(arq)
        next(leitor, None)
        return sum(1 for linha in leitor if linha)


def _somar_flags(con, tabela: str, flags: tuple[str, ...]) -> dict:
    expr = ", ".join(f"count(*) FILTER (WHERE {f}) AS {f}" for f in flags)
    linha = con.execute(f"SELECT {expr} FROM {tabela}").fetchone()
    return {f: int(v) for f, v in zip(flags, linha)}


def coletar(con, cfg: PipelineConfig) -> dict:
    """Coleta contagens e flags de todas as camadas."""
    qualidade = calcular_qualidade(con)
    motivos = con.execute("""
        SELECT motivo, count(*) AS total FROM (
            SELECT unnest(string_split(motivos_invalidade, '; ')) AS motivo
            FROM silver.denuncias WHERE NOT registro_valido
        ) GROUP BY motivo ORDER BY total DESC, motivo
    """).fetchall()
    bairros_nao_padronizados = [r[0] for r in con.execute(
        "SELECT DISTINCT bairro FROM silver.denuncias WHERE flag_bairro_nao_padronizado ORDER BY 1").fetchall()]
    return {
        "camadas": {
            "raw": {"denuncias_simuladas": contar(con, TABELA_SIMULADA), "denuncias_app": contar(con, TABELA_APP),
                    "linhas_arquivo_simulado": _linhas_csv(cfg.samples_csv) if cfg.samples_csv.exists() else None},
            "bronze": {"denuncias": contar(con, "bronze.denuncias")},
            "silver": {"denuncias": contar(con, "silver.denuncias"),
                       "denuncias_duplicadas": contar(con, "silver.denuncias_duplicadas"),
                       "registros_validos": qualidade["registros_validos"]},
            "gold": {t: contar(con, f"gold.{t}") for t in TABELAS_GOLD},
        },
        "qualidade_contrato": qualidade,
        "flags_bronze": _somar_flags(con, "bronze.denuncias", FLAGS_BRONZE),
        "flags_silver": _somar_flags(con, "silver.denuncias", FLAGS_SILVER),
        "motivos_invalidade": [{"motivo": m, "total": int(t)} for m, t in motivos],
        "bairros_fora_do_dicionario": bairros_nao_padronizados,
    }


def verificar(con, cfg: PipelineConfig, dados: dict) -> list[dict]:
    """Verificações automáticas. Cada item: {verificacao, ok, detalhe}."""
    v: list[dict] = []

    def add(nome: str, ok: bool, detalhe: str) -> None:
        v.append({"verificacao": nome, "ok": bool(ok), "detalhe": detalhe})

    cam = dados["camadas"]
    q = dados["qualidade_contrato"]
    add("RAW não vazia", q["linhas_raw"] > 0, f"{q['linhas_raw']} linhas na RAW")
    if cam["raw"]["linhas_arquivo_simulado"] is not None:
        add("RAW fiel à fonte simulada", cam["raw"]["denuncias_simuladas"] == cam["raw"]["linhas_arquivo_simulado"],
            f"arquivo={cam['raw']['linhas_arquivo_simulado']} raw={cam['raw']['denuncias_simuladas']}")
    add("BRONZE ≤ RAW", q["linhas_bronze"] <= q["linhas_raw"], f"{q['linhas_bronze']} ≤ {q['linhas_raw']}")
    soma = cam["silver"]["denuncias"] + cam["silver"]["denuncias_duplicadas"]
    add("SILVER + duplicadas = BRONZE", soma == q["linhas_bronze"], f"{soma} = {q['linhas_bronze']}")

    colunas_pessoais = con.execute("""
        SELECT table_schema || '.' || table_name || '.' || column_name FROM information_schema.columns
        WHERE table_schema IN ('bronze', 'silver', 'gold') AND lower(column_name) LIKE '%nome%'
          AND NOT starts_with(lower(column_name), 'flag_')  -- flag_possui_nome é só um indicador booleano
    """).fetchall()
    add("Sem coluna de nome fora da RAW", not colunas_pessoais,
        "nenhuma" if not colunas_pessoais else ", ".join(c[0] for c in colunas_pessoais))

    textos = [p for p in Path(cfg.gold_dir).glob("*.csv")] + [cfg.snapshot_path]
    com_nome = [p.name for p in textos if p.exists() and MARCADOR_DADO_PESSOAL in p.read_text(encoding="utf-8")]
    add("Arquivos Gold sem dados pessoais", not com_nome, "nenhum" if not com_nome else ", ".join(com_nome))

    snapshot = json.loads(cfg.snapshot_path.read_text(encoding="utf-8")) if cfg.snapshot_path.exists() else {}
    faltando = [c for c in CHAVES_SNAPSHOT if c not in snapshot]
    faltando += [f"qualidade.{c}" for c in CHAVES_QUALIDADE if c not in snapshot.get("qualidade", {})]
    add("Snapshot no formato do contrato 4.8", not faltando, "ok" if not faltando else f"faltando: {faltando}")

    cats = {r["categoria"] for r in snapshot.get("denuncias_por_categoria", [])}
    sts = {r["status"] for r in snapshot.get("denuncias_por_status", [])}
    vis = {r["classificacao"] for r in snapshot.get("resultado_visao", [])}
    fora = (cats - set(TIPO_OBSTACULO)) | (sts - set(STATUS)) | (vis - set(VISAO_CLASSIFICACAO))
    add("Chaves Gold pertencem ao contrato (seção 3)", not fora, "ok" if not fora else f"fora: {sorted(map(str, fora))}")

    validos = q["registros_validos"]
    somas = {
        "por_bairro": sum(r["total"] for r in snapshot.get("denuncias_por_bairro", [])),
        "por_categoria": sum(r["total"] for r in snapshot.get("denuncias_por_categoria", [])),
        "por_periodo_mensal": sum(r["total"] for r in snapshot.get("denuncias_por_periodo", [])),
        "por_status": sum(r["total"] for r in snapshot.get("denuncias_por_status", [])),
        "resultado_visao": sum(r["total"] for r in snapshot.get("resultado_visao", [])),
    }
    add("Agregados Gold somam os registros válidos", all(s == validos for s in somas.values()),
        f"válidos={validos} somas={somas}")
    pct = q["percentual_registros_validos"]
    add("Percentual de válidos entre 0 e 100", 0 <= pct <= 100, f"{pct}%")
    return v


def _markdown(rel: dict) -> str:
    q = rel["qualidade_contrato"]
    cam = rel["camadas"]
    linhas = [
        "# Relatório de qualidade — pipeline AcessaCidade",
        "",
        f"- Execução: `{rel['execucao_id']}`",
        f"- Gerado em (UTC): {rel['gerado_em']}",
        f"- Situação: **{rel['situacao']}**",
        "- Dados: fonte SIMULADA (Cidade Exemplo, fictícia)"
        + (" + exportação da aplicação" if cam["raw"]["denuncias_app"] else "; exportação da API não carregada nesta execução"),
        "",
        "## Contagens por camada",
        "",
        "| Camada | Tabela | Linhas |",
        "|---|---|---:|",
        f"| raw | raw.denuncias_simuladas | {cam['raw']['denuncias_simuladas']} |",
        f"| raw | raw.denuncias_app | {cam['raw']['denuncias_app']} |",
        f"| bronze | bronze.denuncias | {cam['bronze']['denuncias']} |",
        f"| silver | silver.denuncias | {cam['silver']['denuncias']} |",
        f"| silver | silver.denuncias_duplicadas | {cam['silver']['denuncias_duplicadas']} |",
    ]
    linhas += [f"| gold | gold.{t} | {n} |" for t, n in cam["gold"].items()]
    linhas += ["", "## Indicadores (contrato 4.8, campo `qualidade`)", "", "| Indicador | Valor |", "|---|---:|"]
    linhas += [f"| {k} | {v} |" for k, v in q.items()]
    linhas += ["", "## Flags da Bronze (problemas técnicos sinalizados)", "", "| Flag | Registros |", "|---|---:|"]
    linhas += [f"| {k} | {v} |" for k, v in rel["flags_bronze"].items()]
    linhas += ["", "## Flags da Silver (regras de negócio)", "", "| Flag | Registros |", "|---|---:|"]
    linhas += [f"| {k} | {v} |" for k, v in rel["flags_silver"].items()]
    linhas += ["", "## Motivos de invalidade (RN-12)", "", "| Motivo | Registros |", "|---|---:|"]
    linhas += [f"| {m['motivo']} | {m['total']} |" for m in rel["motivos_invalidade"]] or ["| (nenhum) | 0 |"]
    linhas += ["", "## Bairros fora do dicionário oficial (mantidos com grafia limpa)", ""]
    linhas += [f"- {b}" for b in rel["bairros_fora_do_dicionario"]] or ["- (nenhum)"]
    linhas += ["", "## Verificações automáticas", "", "| Verificação | Resultado | Detalhe |", "|---|---|---|"]
    linhas += [f"| {c['verificacao']} | {'OK' if c['ok'] else 'FALHOU'} | {c['detalhe']} |" for c in rel["verificacoes"]]
    linhas.append("")
    return "\n".join(linhas)


def gerar_relatorio(con, cfg: PipelineConfig, execucao_id: str, gerado_em: datetime | None = None,
                    contexto: dict | None = None) -> dict:
    gerado_em = gerado_em or datetime.now(timezone.utc)
    dados = coletar(con, cfg)
    verificacoes = verificar(con, cfg, dados)
    falhas = [c for c in verificacoes if not c["ok"]]
    rel = {
        "execucao_id": execucao_id,
        "gerado_em": gerado_em.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "situacao": "APROVADO" if not falhas else "REPROVADO",
        **dados,
        "verificacoes": verificacoes,
    }
    if contexto:
        rel["extracao_api"] = contexto.get("extracao_api")
    cfg.processed_dir.mkdir(parents=True, exist_ok=True)
    cfg.relatorio_json_path.write_text(json.dumps(rel, ensure_ascii=False, indent=2, default=str) + "\n",
                                       encoding="utf-8")
    cfg.relatorio_md_path.write_text(_markdown(rel), encoding="utf-8")
    for c in verificacoes:
        (log.info if c["ok"] else log.error)("[qualidade] %s: %s (%s)", c["verificacao"],
                                              "OK" if c["ok"] else "FALHOU", c["detalhe"])
    if falhas:
        raise QualityGateError("Verificações de qualidade falharam: " + "; ".join(c["verificacao"] for c in falhas))
    return rel
