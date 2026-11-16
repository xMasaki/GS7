"""Compara a predição da triagem com o rótulo manual e gera a matriz de confusão.

Entradas:
    --dados    CSV gerado por analisar_pasta.py (padrão: results/dados_extraidos.csv)
    --rotulos  CSV de rótulos manuais (padrão: samples/rotulos_manuais_sinteticas.csv)
Saídas:
    results/comparacao_manual.csv
    results/RELATORIO_COMPARACAO.md

Uso (na raiz do repositório):
    .venv\\Scripts\\python.exe 04-Applied-Computer-Vision\\scripts\\avaliar_comparacao.py
Para fotos reais (depois da coleta e da rotulagem manual):
    .venv\\Scripts\\python.exe 04-Applied-Computer-Vision\\scripts\\avaliar_comparacao.py ^
        --dados 04-Applied-Computer-Vision\\results_reais\\dados_extraidos.csv ^
        --rotulos 04-Applied-Computer-Vision\\samples\\real\\rotulos_manuais_reais.csv ^
        --saida 04-Applied-Computer-Vision\\results_reais --base REAL
"""

from __future__ import annotations

import argparse
import csv
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

COMPONENT = Path(__file__).resolve().parents[1]
CLASSES = ["POSSIBLE_POTHOLE", "NOT_IDENTIFIED", "INCONCLUSIVE"]
CURTO = {"POSSIBLE_POTHOLE": "POSSÍVEL BURACO", "NOT_IDENTIFIED": "NÃO IDENTIFICADO", "INCONCLUSIVE": "INCONCLUSIVO"}

AVISO_SINTETICA = (
    "> **AVISO IMPORTANTE — BASE SINTÉTICA.** Todas as imagens avaliadas aqui foram **geradas por computador** "
    "(`scripts/gerar_imagens_sinteticas.py`) e o \"rótulo manual\" é o **rótulo esperado por construção** da cena. "
    "O gerador e a regra de classificação foram escritos pela mesma equipe, a partir das mesmas hipóteses físicas "
    "(buraco = região escura, rugosa e de borda abrupta), e os limiares foram ajustados observando estas mesmas "
    "imagens — então a concordância tende a ser **otimista**. "
    "Estes números **NÃO medem o desempenho no mundo real** e **não podem ser apresentados como acurácia** do "
    "AcessaCidade. Servem para verificar o funcionamento do fluxo e para discutir os tipos de erro."
)

AVISO_REAL = (
    "> **Base REAL.** Rótulos atribuídos manualmente por pessoas da equipe. Amostra pequena e de conveniência: "
    "os números descrevem apenas estas fotos e não devem ser generalizados sem uma coleta maior e diversificada."
)

DISCUSSAO_ERRO = {
    ("sombra", "POSSIBLE_POTHOLE"): "Falso positivo em sombra: a sombra forma região escura e compacta; se a borda for nítida, a regra a confunde com buraco.",
    ("sombra", "INCONCLUSIVE"): "Sombra marcada como inconclusiva: região escura compacta com textura/borda ambíguas. Erro conservador (vai para revisão humana).",
    ("mancha", "POSSIBLE_POTHOLE"): "Falso positivo em mancha: mancha escura e compacta atende aos critérios geométricos.",
    ("mancha", "INCONCLUSIVE"): "Mancha marcada como inconclusiva: escura e compacta, mas sem a rugosidade de um buraco. Erro conservador.",
    ("poca", "POSSIBLE_POTHOLE"): "Falso positivo em poça: a água escura e a borda nítida imitam um buraco (e poças muitas vezes ESTÃO em buracos).",
    ("poca", "INCONCLUSIVE"): "Poça marcada como inconclusiva: escura e com borda nítida, porém fundo liso. Erro conservador; na prática uma poça pode esconder um buraco.",
    ("tampa_bueiro", "POSSIBLE_POTHOLE"): "Falso positivo em tampa de bueiro: disco escuro, com relevo (textura alta) e aro de borda abrupta — a regra não distingue objetos fabricados.",
    ("tampa_bueiro", "INCONCLUSIVE"): "Tampa de bueiro marcada como inconclusiva.",
    ("rachadura", "POSSIBLE_POTHOLE"): "Falso positivo em rachadura: trecho largo da rachadura formou região compacta.",
    ("buraco_dificil", "NOT_IDENTIFIED"): "Falso negativo em buraco difícil (raso ou cheio de água): pouco contraste ou fundo liso demais.",
    ("buraco_dificil", "INCONCLUSIVE"): "Buraco difícil marcado como inconclusivo: indícios parciais; vai para revisão humana.",
    ("buraco", "NOT_IDENTIFIED"): "Falso negativo: o buraco não se destacou o suficiente do piso.",
    ("buraco", "INCONCLUSIVE"): "Buraco marcado como inconclusivo: indícios parciais.",
}


def ler_csv(path: Path) -> list[dict]:
    with open(path, newline="", encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def fmt(v: float, casas: int = 1) -> str:
    return f"{v:.{casas}f}".replace(".", ",")


def comparar(dados: list[dict], rotulos: list[dict]) -> tuple[list[dict], list[str]]:
    pred = {r["arquivo"]: r for r in dados}
    linhas, faltando = [], []
    for r in rotulos:
        nome = r["arquivo"].strip()
        manual = r.get("rotulo_manual", "").strip().upper()
        if not nome or manual not in CLASSES:
            continue
        p = pred.get(nome)
        if p is None or p.get("classificacao") not in CLASSES:
            faltando.append(nome)
            continue
        linhas.append({
            "arquivo": nome,
            "cenario": r.get("cenario", ""),
            "rotulo_manual": manual,
            "predicao": p["classificacao"],
            "acerto": "sim" if manual == p["classificacao"] else "nao",
            "pontuacao": p.get("pontuacao", ""),
            "decisao": p.get("decisao", ""),
        })
    return linhas, faltando


def matriz(linhas: list[dict]) -> dict:
    m = {a: {b: 0 for b in CLASSES} for a in CLASSES}
    for ln in linhas:
        m[ln["rotulo_manual"]][ln["predicao"]] += 1
    return m


def relatorio(linhas, faltando, base: str, dados_path: Path, rotulos_path: Path) -> str:
    m = matriz(linhas)
    n = len(linhas)
    acertos = sum(1 for ln in linhas if ln["acerto"] == "sim")
    out = ["# Relatório de comparação: triagem automática × rótulo manual", ""]
    out.append(AVISO_SINTETICA if base == "SINTETICA" else AVISO_REAL)
    out += [
        "",
        f"- Gerado em: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')} por `scripts/avaliar_comparacao.py`",
        f"- Base: **{base}**",
        f"- Predições: `{dados_path.name}` · Rótulos: `{rotulos_path.name}`",
        f"- Imagens comparadas: **{n}**" + (f" (sem predição: {', '.join(faltando)})" if faltando else ""),
        f"- Concordância total: **{acertos}/{n}** ({fmt(100 * acertos / n if n else 0)}%) — "
        + ("concordância com o rótulo esperado por construção, **não** acurácia no mundo real." if base == "SINTETICA" else "apenas nesta amostra."),
        "",
        "## Matriz de confusão",
        "",
        "Linhas = rótulo manual; colunas = predição da triagem.",
        "",
        "| Manual \\ Predição | " + " | ".join(CURTO[c] for c in CLASSES) + " | Total |",
        "|---|" + "---:|" * (len(CLASSES) + 1),
    ]
    for a in CLASSES:
        tot = sum(m[a].values())
        out.append(f"| **{CURTO[a]}** | " + " | ".join(str(m[a][b]) for b in CLASSES) + f" | {tot} |")
    out += ["", "## Acertos por classe", "", "| Classe | Imagens | Acertos | Taxa de acerto (revocação) | Precisão |", "|---|---:|---:|---:|---:|"]
    for c in CLASSES:
        tot = sum(m[c].values())
        hit = m[c][c]
        pred_tot = sum(m[a][c] for a in CLASSES)
        rec = fmt(100 * hit / tot) + "%" if tot else "—"
        prec = fmt(100 * hit / pred_tot) + "%" if pred_tot else "—"
        out.append(f"| {CURTO[c]} | {tot} | {hit} | {rec} | {prec} |")

    fp = m["NOT_IDENTIFIED"]["POSSIBLE_POTHOLE"] + m["INCONCLUSIVE"]["POSSIBLE_POTHOLE"]
    fn = m["POSSIBLE_POTHOLE"]["NOT_IDENTIFIED"]
    out += [
        "",
        "## Leitura dos erros",
        "",
        f"- **Falsos positivos** (marcado como possível buraco sem haver buraco): {fp}.",
        f"- **Falsos negativos** (buraco marcado como \"nenhum indício\"): {fn}.",
        f"- **Erros conservadores** (algo marcado como inconclusivo, indo para revisão humana): "
        f"{sum(m[a]['INCONCLUSIVE'] for a in CLASSES if a != 'INCONCLUSIVE')}.",
        "",
    ]
    erros = [ln for ln in linhas if ln["acerto"] == "nao"]
    if erros:
        out += ["| Imagem | Cenário | Manual | Predição | Pontuação | Discussão |", "|---|---|---|---|---:|---|"]
        for ln in erros:
            disc = DISCUSSAO_ERRO.get((ln["cenario"], ln["predicao"]), "Erro a investigar com a revisão humana das imagens intermediárias.")
            pasta = Path(ln["arquivo"]).stem
            out.append(
                f"| [{ln['arquivo']}]({pasta}/painel_etapas.jpg) | {ln['cenario']} | {CURTO[ln['rotulo_manual']]} | "
                f"{CURTO[ln['predicao']]} | {ln['pontuacao']} | {disc} |"
            )
    else:
        out.append("Nenhum erro nesta base. Em base sintética isso indica apenas coerência entre gerador e regra.")
    out += [
        "",
        "## Limitações e próximos passos",
        "",
        "- A pontuação é **heurística** (soma ponderada de critérios), não uma probabilidade calibrada.",
        "- Sombras, manchas, poças, tampas de bueiro e rachaduras largas podem gerar falsos positivos; "
        "buracos rasos, cheios de água ou da mesma cor do piso podem gerar falsos negativos.",
        "- Toda triagem passa por **revisão humana** (status \"Aguardando revisão\").",
        "- Próximo passo obrigatório: repetir esta comparação com **fotos reais** rotuladas manualmente "
        "(`samples/real/`, ver `PENDENCIAS_E_ACOES_MANUAIS.txt`). [PREENCHER: resultados da base real, quando existirem]",
        "",
        "Cada imagem tem o painel com todas as etapas em `results/<nome>/painel_etapas.jpg`.",
        "",
    ]
    return "\n".join(out)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Compara predição × rótulo manual (matriz de confusão).")
    ap.add_argument("--dados", type=Path, default=COMPONENT / "results" / "dados_extraidos.csv")
    ap.add_argument("--rotulos", type=Path, default=COMPONENT / "samples" / "rotulos_manuais_sinteticas.csv")
    ap.add_argument("--saida", type=Path, default=COMPONENT / "results")
    ap.add_argument("--base", choices=["SINTETICA", "REAL"], default="SINTETICA")
    args = ap.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")

    for p in (args.dados, args.rotulos):
        if not p.exists():
            print(f"Arquivo não encontrado: {p}")
            return 2
    linhas, faltando = comparar(ler_csv(args.dados), ler_csv(args.rotulos))
    if not linhas:
        print("Nenhuma imagem em comum entre predições e rótulos.")
        return 1
    args.saida.mkdir(parents=True, exist_ok=True)
    with open(args.saida / "comparacao_manual.csv", "w", newline="", encoding="utf-8") as fh:
        wr = csv.DictWriter(fh, fieldnames=list(linhas[0].keys()))
        wr.writeheader()
        wr.writerows(linhas)
    texto = relatorio(linhas, faltando, args.base, args.dados, args.rotulos)
    (args.saida / "RELATORIO_COMPARACAO.md").write_text(texto, encoding="utf-8")

    m = matriz(linhas)
    acertos = sum(1 for ln in linhas if ln["acerto"] == "sim")
    print(f"Base {args.base}: {acertos}/{len(linhas)} concordâncias")
    print("Manual \\ Predição".ljust(20) + "".join(c[:12].rjust(14) for c in CLASSES))
    for a in CLASSES:
        print(a[:18].ljust(20) + "".join(str(m[a][b]).rjust(14) for b in CLASSES))
    print(f"Contagem por cenário com erro: {dict(Counter(ln['cenario'] for ln in linhas if ln['acerto'] == 'nao'))}")
    print(f"Saídas: {args.saida / 'comparacao_manual.csv'} e {args.saida / 'RELATORIO_COMPARACAO.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
