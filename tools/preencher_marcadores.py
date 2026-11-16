"""Preenche os marcadores de preenchimento do repositório a partir de dados_entrega.yaml.

Fluxo (nesta ordem):
  1. lê e VALIDA dados_entrega.yaml (aborta sem tocar em nada se algum valor for inválido);
  2. varre os documentos (.md, lean_canvas.json e os docs/links_entrega.yaml) procurando marcadores que tenham
     correspondência EXATA na tabela ALIASES abaixo;
  3. mostra o PREVIEW (quantas substituições por campo, em quais arquivos e linhas) e o DIFF de cada arquivo;
  4. pede confirmação ([s/N]);
  5. grava (com backup em .preencher_backup/<data-hora>/), regenera o Lean Canvas se o JSON mudou e confere que
     uma segunda passada não acha mais nada para trocar;
  6. grava o relatório final em docs/RELATORIO_PREENCHIMENTO.md (sem nenhum dado pessoal: só campos e contagens).

Garantias:
  - campo vazio no YAML = o script não mexe nos marcadores daquele campo (nada é inventado nem "chutado");
  - marcador sem correspondência exata na tabela fica como está (ex.: o marcador sem texto, "URL pública" genérico,
    "papel" solto, evidências, medições) — o relatório lista tudo que sobrou;
  - o link de vídeo é resolvido POR DISCIPLINA (cada professor pede um vídeo diferente): arquivos das pastas
    01, 02, 04, 05 e 07 usam links.videos."NN"; a raiz e a pasta 03 usam links.video_pitch;
  - composições ("nomes e RMs dos integrantes") só são preenchidas se TODOS os integrantes informados tiverem
    os campos necessários — nunca sai "Fulano ()" nem RM pela metade;
  - não são alterados: PENDENCIAS_E_ACOES_MANUAIS.txt, PASSO_A_PASSO, scripts (.py/.ps1), testes, arquivos
    gerados (LEAN_CANVAS.md/.html — o script atualiza a fonte lean_canvas.json e roda o gerador) nem
    docs/INVENTARIO_PREENCHER.md. Esses arquivos documentam ou geram marcadores, não são lugar de preencher.

Uso (na raiz do repositório, PowerShell):
    .\\.venv\\Scripts\\python.exe tools\\preencher_marcadores.py --dry-run   # só mostra preview e diff
    .\\.venv\\Scripts\\python.exe tools\\preencher_marcadores.py             # preview + diff + confirmação
    .\\.venv\\Scripts\\python.exe tools\\preencher_marcadores.py --sim       # sem a pergunta (automação)

Códigos de saída: 0 = concluído ou nada a fazer; 1 = cancelado na confirmação; 2 = erro (YAML ausente/inválido).
"""
from __future__ import annotations

import argparse
import difflib
import json
import os
import re
import shutil
import subprocess
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

# O texto-base do marcador é montado em pedaços para este arquivo não contar como "ocorrência" no inventário.
_P = "PREENCHER"
MARC = re.compile(r"\[" + _P + r"(?::[^\]\r\n]*)?\]")
EM = "—"  # travessão usado nos marcadores "Integrante N — nome" / "integrante N — RM"


def _m(texto: str) -> str:
    """Monta o marcador completo a partir do texto depois dos dois pontos."""
    return "[" + _P + ": " + texto + "]"


def _exibir(texto: str) -> str:
    """Forma segura para relatórios: não deixa um marcador 'vivo' no texto gerado."""
    return texto.replace("[" + _P, "‹" + _P)


# --------------------------------------------------------------------------------------------------------------
# Tabela de correspondência: texto EXATO do marcador -> identificador do campo do YAML
# --------------------------------------------------------------------------------------------------------------
ALIASES: dict[str, str] = {}


def _alias(chave: str, *textos: str) -> None:
    for t in textos:
        ALIASES[_m(t)] = chave


_alias("equipe.nome", "nome da equipe", "nome da equipe / startup")
_alias("link.mvp", "URL_MVP", "URL pública do MVP", "URL pública do AcessaCidade", "http://<fqdn>:8000")
_alias("link.repositorio", "URL_REPOSITORIO", "URL do repositório", "URL do repositorio",
       "URL do repositório público no GitHub", "URL pública do repositório GitHub", "link do repositório",
       "https://github.com/<owner>/<repo>")
_alias("link.video", "URL_VIDEO", "link do vídeo", "link do video")
_alias("integrantes.nomes_rms", "nomes e RMs dos integrantes", "nomes e RMs de todos os integrantes")
_alias("integrantes.nomes_rms_papeis", "nomes, RMs e papéis")
for _n in range(1, 6):
    _alias(f"integrante.{_n}.nome", f"Integrante {_n}", f"Integrante {_n} {EM} nome")
    _alias(f"integrante.{_n}.nome_rm", f"integrante {_n} {EM} RM")

# Regras de contexto (uma linha): preenchem os campos "soltos" que acompanham um marcador de integrante.
RE_LINHA_TABELA = re.compile(  # | [Integrante N] | [RM] | [papel] |   (tabela do documento de entrega da disciplina 03)
    r"^(\|[ \t]*\[" + _P + r": Integrante (\d)\][ \t]*\|[ \t]*)(\[" + _P + r"\])([ \t]*\|[ \t]*)(\[" + _P
    + r"\])([ \t]*\|)")
RE_LINHA_PITCH = re.compile(  # [Integrante N — nome], [papel em poucas palavras]   (roteiro do pitch, bloco 6)
    r"(\[" + _P + r": Integrante (\d) " + EM + r" nome\],[ \t]*)(\[" + _P + r": papel[^\]\r\n]*\])")

# --------------------------------------------------------------------------------------------------------------
# Escopo da varredura
# --------------------------------------------------------------------------------------------------------------
DIRS_IGNORADOS = {".git", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache", ".preencher_backup",
                  ".terraform", "entregas", "tests", "tests_e2e", "data"}
ARQUIVOS_IGNORADOS = {"INVENTARIO_PREENCHER.md", "RELATORIO_PREENCHIMENTO.md"}
PREFIXOS_IGNORADOS = ("PENDENCIAS_E_ACOES_MANUAIS",)
GERADOS = {"03-Business-Intelligence-Startup/business-model/LEAN_CANVAS.md"}  # vêm de lean_canvas.json
CANVAS_JSON = "03-Business-Intelligence-Startup/business-model/lean_canvas.json"
CANVAS_GERADOR = "03-Business-Intelligence-Startup/scripts/gerar_lean_canvas.py"
RELATORIO_PADRAO = "docs/RELATORIO_PREENCHIMENTO.md"
BACKUP_DIR = ".preencher_backup"


# --------------------------------------------------------------------------------------------------------------
# Dados
# --------------------------------------------------------------------------------------------------------------
@dataclass
class Integrante:
    nome: str = ""
    rm: str = ""
    papel: str = ""

    def vazio(self) -> bool:
        return not (self.nome or self.rm or self.papel)


@dataclass
class Dados:
    equipe: str = ""
    integrantes: list[Integrante] = field(default_factory=list)
    mvp: str = ""
    repositorio: str = ""
    video_pitch: str = ""
    videos: dict[str, str] = field(default_factory=dict)
    avisos: list[str] = field(default_factory=list)

    def integrante(self, n: int) -> Integrante:
        return self.integrantes[n - 1] if 0 < n <= len(self.integrantes) else Integrante()

    def preenchidos(self) -> int:
        valores = [self.equipe, self.mvp, self.repositorio, self.video_pitch, *self.videos.values()]
        for i in self.integrantes:
            valores += [i.nome, i.rm, i.papel]
        return sum(1 for v in valores if v)


class ErroDados(Exception):
    pass


def _texto(valor, caminho: str, erros: list[str]) -> str:
    if valor is None:
        return ""
    if isinstance(valor, (dict, list, bool)):
        erros.append(f"{caminho}: esperado texto, veio {type(valor).__name__}")
        return ""
    s = str(valor).strip()
    if not s:
        return ""
    if re.search(_P, s, re.I):
        erros.append(f"{caminho}: o valor ainda contém a palavra de marcador — informe o dado real")
    if re.search(r"[<>|\r\n]", s):
        erros.append(f"{caminho}: não use <, >, | nem quebra de linha (quebram links e tabelas Markdown)")
    return s


def _url(valor, caminho: str, erros: list[str], avisos: list[str], http_ok: bool = False, repo: bool = False) -> str:
    s = _texto(valor, caminho, erros)
    if not s:
        return ""
    if repo:
        s = re.sub(r"\.git$", "", s.rstrip("/"))
    else:
        s = s.rstrip("/")
    padrao = r"^https?://[^\s\"'\[\]]+$" if http_ok else r"^https://[^\s\"'\[\]]+$"
    if not re.match(padrao, s):
        erros.append(f"{caminho}: URL inválida ({'http:// ou https://' if http_ok else 'precisa começar com https://'}, "
                     "sem espaços)")
    elif s.startswith("http://"):
        avisos.append(f"{caminho}: usa http:// — será gravada nos documentos, mas NÃO nos docs/links_entrega.yaml "
                      "(eles exigem https://).")
    if repo and not re.match(r"^https://(www\.)?github\.com/[^/\s]+/[^/\s]+$", s):
        avisos.append(f"{caminho}: não parece https://github.com/<conta>/<repositório> — confira.")
    return s


def carregar_dados(caminho: Path) -> Dados:
    try:
        import yaml
    except ImportError as exc:  # pragma: no cover
        raise ErroDados("PyYAML não instalado. Use o venv do projeto (requirements-dev.txt).") from exc
    if not caminho.is_file():
        raise ErroDados(f"Arquivo não encontrado: {caminho}")
    try:
        bruto = yaml.safe_load(caminho.read_text(encoding="utf-8-sig"))
    except yaml.YAMLError as exc:
        raise ErroDados(f"YAML inválido em {caminho.name}: {exc}") from exc
    if bruto is None:
        bruto = {}
    if not isinstance(bruto, dict):
        raise ErroDados("O YAML precisa ter 'equipe' e 'links' no nível raiz.")

    erros: list[str] = []
    d = Dados()
    equipe = bruto.get("equipe") or {}
    links = bruto.get("links") or {}
    if not isinstance(equipe, dict) or not isinstance(links, dict):
        raise ErroDados("'equipe' e 'links' devem ser blocos (chave: valor).")

    d.equipe = _texto(equipe.get("nome"), "equipe.nome", erros)
    lista = equipe.get("integrantes") or []
    if not isinstance(lista, list):
        raise ErroDados("equipe.integrantes deve ser uma lista.")
    for idx, item in enumerate(lista, 1):
        item = item or {}
        if not isinstance(item, dict):
            erros.append(f"equipe.integrantes[{idx}]: esperado nome/rm/papel")
            continue
        d.integrantes.append(Integrante(
            nome=_texto(item.get("nome"), f"equipe.integrantes[{idx}].nome", erros),
            rm=_texto(item.get("rm"), f"equipe.integrantes[{idx}].rm", erros),
            papel=_texto(item.get("papel"), f"equipe.integrantes[{idx}].papel", erros)))
    if len(d.integrantes) > 5:
        d.avisos.append("Há mais de 5 integrantes: os marcadores do projeto só existem para os 5 primeiros.")
    for idx, i in enumerate(d.integrantes, 1):
        if (i.rm or i.papel) and not i.nome:
            d.avisos.append(f"equipe.integrantes[{idx}] tem RM/papel sem nome — nada será gravado para ele.")

    d.mvp = _url(links.get("mvp"), "links.mvp", erros, d.avisos, http_ok=True)
    d.repositorio = _url(links.get("repositorio"), "links.repositorio", erros, d.avisos, repo=True)
    d.video_pitch = _url(links.get("video_pitch"), "links.video_pitch", erros, d.avisos)
    videos = links.get("videos") or {}
    if not isinstance(videos, dict):
        raise ErroDados("links.videos deve ser um bloco \"NN\": URL.")
    for k, v in videos.items():
        url = _url(v, f'links.videos."{k}"', erros, d.avisos)
        if url:
            d.videos[str(k).zfill(2)] = url
    if erros:
        raise ErroDados("Valores inválidos em " + caminho.name + ":\n  - " + "\n  - ".join(erros))
    return d


# --------------------------------------------------------------------------------------------------------------
# Resolução de valores
# --------------------------------------------------------------------------------------------------------------
def disciplina_de(rel: str) -> str | None:
    m = re.match(r"^(\d{2})-", rel)
    return m.group(1) if m else None


def _video(d: Dados, disc: str | None) -> tuple[str, str]:
    if disc in (None, "03"):
        return "links.video_pitch", d.video_pitch
    return f'links.videos."{disc}"', d.videos.get(disc, "")


def _composto(d: Dados, com_papel: bool) -> str:
    ativos = [i for i in d.integrantes[:5] if not i.vazio()]
    if not ativos:
        return ""
    partes = []
    for i in ativos:
        if not i.nome or not i.rm or (com_papel and not i.papel):
            return ""
        partes.append(f"{i.nome} ({i.rm}, {i.papel})" if com_papel else f"{i.nome} ({i.rm})")
    return ", ".join(partes)


def resolver(chave: str, d: Dados, rel: str) -> tuple[str, str]:
    """Devolve (campo do YAML que alimenta o marcador, valor — vazio se ainda não informado)."""
    if chave == "equipe.nome":
        return "equipe.nome", d.equipe
    if chave == "link.mvp":
        return "links.mvp", d.mvp
    if chave == "link.repositorio":
        return "links.repositorio", d.repositorio
    if chave == "link.video":
        return _video(d, disciplina_de(rel))
    if chave == "integrantes.nomes_rms":
        return "equipe.integrantes (nome e rm de todos)", _composto(d, False)
    if chave == "integrantes.nomes_rms_papeis":
        return "equipe.integrantes (nome, rm e papel de todos)", _composto(d, True)
    m = re.match(r"^integrante\.(\d)\.(nome|nome_rm|rm|papel)$", chave)
    if m:
        n, campo = int(m.group(1)), m.group(2)
        i = d.integrante(n)
        rotulo = f"equipe.integrantes[{n}]"
        if campo == "nome":
            return f"{rotulo}.nome", i.nome
        if campo == "nome_rm":
            return f"{rotulo}.nome e .rm", f"{i.nome} {EM} {i.rm}" if i.nome and i.rm else ""
        if campo == "rm":
            return f"{rotulo}.rm", i.rm if i.nome else ""
        return f"{rotulo}.papel", i.papel if i.nome else ""
    raise KeyError(chave)


# --------------------------------------------------------------------------------------------------------------
# Processamento de um texto
# --------------------------------------------------------------------------------------------------------------
@dataclass
class Hit:
    linha: int
    campo: str      # campo do YAML que originou o valor
    marcador: str   # texto original do marcador (já em forma segura para exibir)


@dataclass
class Pendente:
    linha: int
    marcador: str
    campo: str | None  # campo do YAML que falta preencher; None = sem correspondência no projeto


def _escapar(valor: str, sufixo: str) -> str:
    return json.dumps(valor, ensure_ascii=False)[1:-1] if sufixo == ".json" else valor


def processar_texto(texto: str, rel: str, d: Dados, sufixo: str = ".md") -> tuple[str, list[Hit], list[Pendente]]:
    hits: list[Hit] = []
    partes = texto.split("\n")
    for idx, linha in enumerate(partes):
        n_linha = idx + 1
        if _P not in linha:
            continue

        def cb_tabela(m: re.Match) -> str:
            n = int(m.group(2))
            _, rm = resolver(f"integrante.{n}.rm", d, rel)
            _, papel = resolver(f"integrante.{n}.papel", d, rel)
            if rm:
                hits.append(Hit(n_linha, f"equipe.integrantes[{n}].rm", _exibir(m.group(3))))
            if papel:
                hits.append(Hit(n_linha, f"equipe.integrantes[{n}].papel", _exibir(m.group(5))))
            return m.group(1) + (rm or m.group(3)) + m.group(4) + (papel or m.group(5)) + m.group(6)

        def cb_pitch(m: re.Match) -> str:
            n = int(m.group(2))
            _, papel = resolver(f"integrante.{n}.papel", d, rel)
            if not papel:
                return m.group(0)
            hits.append(Hit(n_linha, f"equipe.integrantes[{n}].papel", _exibir(m.group(3))))
            return m.group(1) + papel

        def cb_generico(m: re.Match) -> str:
            chave = ALIASES.get(m.group(0))
            if chave is None:
                return m.group(0)
            campo, valor = resolver(chave, d, rel)
            if not valor:
                return m.group(0)
            hits.append(Hit(n_linha, campo, _exibir(m.group(0))))
            return _escapar(valor, sufixo)

        nova = RE_LINHA_TABELA.sub(cb_tabela, linha)
        nova = RE_LINHA_PITCH.sub(cb_pitch, nova)
        nova = MARC.sub(cb_generico, nova)
        partes[idx] = nova
    novo = "\n".join(partes)
    return novo, hits, pendentes_de(novo, rel, d)


def pendentes_de(texto: str, rel: str, d: Dados) -> list[Pendente]:
    saida = []
    for n_linha, linha in enumerate(texto.split("\n"), 1):
        if _P not in linha:
            continue
        for m in MARC.finditer(linha):
            chave = ALIASES.get(m.group(0))
            campo = resolver(chave, d, rel)[0] if chave else None
            saida.append(Pendente(n_linha, _exibir(m.group(0)), campo))
    return saida


# YAML de links por disciplina (docs/links_entrega.yaml): url_video / url_mvp / url_repositorio
def processar_links_yaml(texto: str, rel: str, d: Dados) -> tuple[str, list[Hit], list[Pendente], list[str]]:
    disc = disciplina_de(rel)
    campo_video, video = _video(d, disc)
    alvos = {"url_video": (campo_video, video), "url_mvp": ("links.mvp", d.mvp),
             "url_repositorio": ("links.repositorio", d.repositorio)}
    hits: list[Hit] = []
    pend: list[Pendente] = []
    avisos: list[str] = []
    partes = texto.split("\n")
    for idx, linha in enumerate(partes):
        m = re.match(r'^(url_video|url_mvp|url_repositorio):([ \t]*)(?:""|\'\')([ \t]*(?:#[^\r\n]*)?\r?)$', linha)
        if not m:
            continue
        campo, valor = alvos[m.group(1)]
        if not valor:
            pend.append(Pendente(idx + 1, m.group(1) + ': ""', campo))
        elif not valor.startswith("https://"):
            avisos.append(f"{rel}: {m.group(1)} não gravado (o valor é http://; este arquivo exige https://).")
            pend.append(Pendente(idx + 1, m.group(1) + ': ""', campo))
        else:
            partes[idx] = f"{m.group(1)}:{m.group(2)}{json.dumps(valor, ensure_ascii=False)}{m.group(3)}"
            hits.append(Hit(idx + 1, campo, m.group(1) + ': ""'))
    return "\n".join(partes), hits, pend, avisos


# --------------------------------------------------------------------------------------------------------------
# Varredura de arquivos
# --------------------------------------------------------------------------------------------------------------
@dataclass
class Resultado:
    rel: str
    caminho: Path
    sufixo: str
    original: str
    novo: str
    bom: bool
    hits: list[Hit]
    pendentes: list[Pendente]
    avisos: list[str] = field(default_factory=list)

    @property
    def mudou(self) -> bool:
        return self.novo != self.original


def listar_candidatos(raiz: Path) -> list[Path]:
    achados: list[Path] = []
    for pasta, dirs, arquivos in os.walk(raiz):
        dirs[:] = sorted(x for x in dirs if x not in DIRS_IGNORADOS)
        for nome in sorted(arquivos):
            p = Path(pasta) / nome
            rel = p.relative_to(raiz).as_posix()
            if nome in ARQUIVOS_IGNORADOS or nome.startswith(PREFIXOS_IGNORADOS) or rel in GERADOS:
                continue
            if nome.endswith(".md") or rel == CANVAS_JSON or re.match(r"^\d{2}-[^/]+/docs/links_entrega\.yaml$", rel):
                achados.append(p)
    return achados


def varrer(raiz: Path, d: Dados) -> tuple[list[Resultado], list[str]]:
    resultados: list[Resultado] = []
    avisos: list[str] = []
    for p in listar_candidatos(raiz):
        rel = p.relative_to(raiz).as_posix()
        bruto = p.read_bytes()
        bom = bruto.startswith(b"\xef\xbb\xbf")
        try:
            texto = bruto.decode("utf-8-sig" if bom else "utf-8")
        except UnicodeDecodeError:
            avisos.append(f"{rel}: não é UTF-8 — ignorado.")
            continue
        sufixo = p.suffix.lower()
        if rel.endswith("links_entrega.yaml"):
            novo, hits, pend, av = processar_links_yaml(texto, rel, d)
            avisos += av
            resultados.append(Resultado(rel, p, sufixo, texto, novo, bom, hits, pend))
            continue
        if _P not in texto:
            continue
        novo, hits, pend = processar_texto(texto, rel, d, sufixo)
        resultados.append(Resultado(rel, p, sufixo, texto, novo, bom, hits, pend))
    return resultados, avisos


# --------------------------------------------------------------------------------------------------------------
# Apresentação
# --------------------------------------------------------------------------------------------------------------
def preview(resultados: list[Resultado]) -> str:
    mudados = [r for r in resultados if r.mudou]
    por_campo: dict[str, list[tuple[str, int]]] = defaultdict(list)
    for r in mudados:
        for h in r.hits:
            por_campo[h.campo].append((r.rel, h.linha))
    linhas = ["", "PREVIEW DAS SUBSTITUIÇÕES", "=" * 78]
    if not mudados:
        linhas.append("Nenhuma substituição possível com os valores informados.")
        return "\n".join(linhas)
    linhas.append(f"{'campo do YAML':<48} {'trocas':>7} {'arquivos':>9}")
    for campo in sorted(por_campo):
        trocas = por_campo[campo]
        linhas.append(f"{campo:<48} {len(trocas):>7} {len({a for a, _ in trocas}):>9}")
    total = sum(len(v) for v in por_campo.values())
    linhas.append("-" * 78)
    linhas.append(f"{'TOTAL':<48} {total:>7} {len(mudados):>9}")
    linhas.append("")
    for r in mudados:
        detalhe = ", ".join(str(n) for n in sorted({h.linha for h in r.hits}))
        linhas.append(f"  {r.rel}  (linhas {detalhe})")
    return "\n".join(linhas)


def diff_texto(r: Resultado) -> str:
    return "\n".join(difflib.unified_diff(
        r.original.splitlines(), r.novo.splitlines(), fromfile=f"a/{r.rel}", tofile=f"b/{r.rel}", n=0, lineterm=""))


def aguardando(resultados: list[Resultado]) -> Counter:
    c: Counter = Counter()
    for r in resultados:
        for p in r.pendentes:
            if p.campo:
                c[p.campo] += 1
    return c


def sem_correspondencia(resultados: list[Resultado]) -> Counter:
    c: Counter = Counter()
    for r in resultados:
        for p in r.pendentes:
            if not p.campo:
                c[p.marcador] += 1
    return c


# --------------------------------------------------------------------------------------------------------------
# Gravação, pós-ações e relatório
# --------------------------------------------------------------------------------------------------------------
def gravar(raiz: Path, resultados: list[Resultado], carimbo: str) -> Path:
    destino = raiz / BACKUP_DIR / carimbo
    for r in resultados:
        if not r.mudou:
            continue
        copia = destino / r.rel
        copia.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(r.caminho, copia)
    for r in resultados:
        if r.mudou:
            conteudo = ("﻿" if r.bom else "") + r.novo
            r.caminho.write_bytes(conteudo.encode("utf-8"))
    return destino


def regenerar_canvas(raiz: Path) -> str:
    gerador = raiz / CANVAS_GERADOR
    if not gerador.is_file():
        return f"gerador não encontrado ({CANVAS_GERADOR}); rode-o manualmente."
    proc = subprocess.run([sys.executable, str(gerador)], cwd=raiz, capture_output=True, text=True,
                          encoding="utf-8", errors="replace")
    if proc.returncode == 0:
        return "Lean Canvas regenerado (LEAN_CANVAS.md/.html/.xlsx) a partir de lean_canvas.json."
    return f"o gerador do Lean Canvas falhou (código {proc.returncode}): {proc.stderr.strip()[:300]}"


def escrever_relatorio(raiz: Path, caminho: Path, d: Dados, resultados: list[Resultado], aplicado: bool,
                       carimbo: str, backup: Path | None, pos_acoes: list[str], avisos: list[str],
                       restantes: list[Resultado]) -> None:
    mudados = [r for r in resultados if r.mudou]
    por_campo: Counter = Counter(h.campo for r in mudados for h in r.hits)
    campos_arquivos: dict[str, set] = defaultdict(set)
    for r in mudados:
        for h in r.hits:
            campos_arquivos[h.campo].add(r.rel)
    esperando = aguardando(restantes)
    sem_regra = sem_correspondencia(restantes)
    total = sum(por_campo.values())
    L = [f"# Relatório de preenchimento de marcadores — {carimbo}", "",
         "> Gerado por `tools/preencher_marcadores.py`. Não contém dados pessoais: só campos, contagens e arquivos.",
         "> Os marcadores aparecem como `‹PREENCHER` para este relatório não contar como pendência.", "",
         "## Resumo", "",
         f"- Fonte dos dados: `dados_entrega.yaml` ({d.preenchidos()} campo(s) preenchido(s)).",
         f"- Substituições gravadas: **{total}** em **{len(mudados)}** arquivo(s).",
         f"- Backup dos originais: `{backup.relative_to(raiz).as_posix()}/`" if backup else "- Backup: não aplicável.",
         "- Segunda passada de conferência: nenhuma substituição pendente para os valores informados." if aplicado
         else "- Situação: nada foi gravado.", ""]
    if por_campo:
        L += ["## Substituições por campo", "", "| Campo do YAML | Trocas | Arquivos |", "|---|---:|---:|"]
        for campo in sorted(por_campo):
            L.append(f"| `{campo}` | {por_campo[campo]} | {len(campos_arquivos[campo])} |")
        L += ["", "## Arquivos alterados", ""]
        for r in mudados:
            L.append(f"- `{r.rel}` — linhas {', '.join(str(n) for n in sorted({h.linha for h in r.hits}))}")
        L.append("")
    if pos_acoes:
        L += ["## Ações automáticas após a gravação", ""] + [f"- {a}" for a in pos_acoes] + [""]
    if avisos:
        L += ["## Avisos", ""] + [f"- {a}" for a in avisos] + [""]
    L += ["## O que continua pendente", ""]
    if esperando:
        L += ["### Têm correspondência, mas o campo do YAML ainda está vazio", "",
              "| Campo do YAML a preencher | Marcadores que dependem dele |", "|---|---:|"]
        for campo, n in sorted(esperando.items()):
            L.append(f"| `{campo}` | {n} |")
        L.append("")
    if sem_regra:
        L += ["### Sem correspondência neste script (não foram tocados)", "",
              "Medições, evidências, datas, decisões e dados que só existem depois de uma ação real. "
              "Veja `docs/INVENTARIO_PREENCHER.md` e os `PENDENCIAS_E_ACOES_MANUAIS.txt` de cada pasta.", "",
              "| Marcador | Ocorrências |", "|---|---:|"]
        for marc, n in sem_regra.most_common(25):
            L.append(f"| `{marc}` | {n} |")
        if len(sem_regra) > 25:
            L.append(f"| _… mais {len(sem_regra) - 25} textos distintos_ | |")
        L.append("")
    L += ["## Próximos passos", "",
          "1. Conferir o resultado: `.\\.venv\\Scripts\\python.exe -m pytest`.",
          "2. Se algo saiu errado, restaurar do backup indicado acima (copie os arquivos de volta mantendo as pastas).",
          "3. Marcar nos `PENDENCIAS_E_ACOES_MANUAIS.txt` o que já foi preenchido (esses arquivos não são alterados "
          "pelo script).",
          "4. Gerar os PDFs: `.\\tools\\gerar_todos_pdfs.ps1 -RepoUrl <URL do repositório> -Estrito`.", ""]
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text("\n".join(L), encoding="utf-8", newline="\n")


# --------------------------------------------------------------------------------------------------------------
# Programa principal
# --------------------------------------------------------------------------------------------------------------
def main(argv: list[str] | None = None) -> int:
    for fluxo in (sys.stdout, sys.stderr):
        try:
            fluxo.reconfigure(encoding="utf-8")
        except (AttributeError, OSError):
            pass
    ap = argparse.ArgumentParser(description="Preenche os marcadores do projeto a partir de dados_entrega.yaml.")
    ap.add_argument("--raiz", type=Path, default=RAIZ, help="raiz do repositório (padrão: a deste script)")
    ap.add_argument("--dados", type=Path, default=None, help="YAML de entrada (padrão: <raiz>/dados_entrega.yaml)")
    ap.add_argument("--dry-run", action="store_true", help="mostra preview e diff e NÃO grava nada")
    ap.add_argument("--sim", "-y", action="store_true", help="não pergunta antes de gravar")
    ap.add_argument("--sem-diff", action="store_true", help="omite o diff (mantém o preview)")
    ap.add_argument("--sem-regenerar", action="store_true", help="não roda o gerador do Lean Canvas")
    ap.add_argument("--relatorio", type=Path, default=None, help=f"relatório final (padrão: <raiz>/{RELATORIO_PADRAO})")
    args = ap.parse_args(argv)

    raiz = args.raiz.resolve()
    dados_yaml = args.dados or raiz / "dados_entrega.yaml"
    try:
        d = carregar_dados(dados_yaml)
    except ErroDados as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        return 2

    print(f"Dados lidos de {dados_yaml.name}: {d.preenchidos()} campo(s) preenchido(s).")
    for a in d.avisos:
        print(f"  AVISO: {a}")
    if d.preenchidos() == 0:
        print("Nada a fazer: dados_entrega.yaml está vazio. Preencha só o que você realmente tem e rode de novo.")
        return 0

    resultados, avisos_varredura = varrer(raiz, d)
    avisos = d.avisos + avisos_varredura
    for a in avisos_varredura:
        print(f"  AVISO: {a}")
    print(preview(resultados))
    mudados = [r for r in resultados if r.mudou]
    total = sum(len(r.hits) for r in mudados)

    if mudados and not args.sem_diff:
        print("\nDIFF DAS ALTERAÇÕES\n" + "=" * 78)
        for r in mudados:
            print(diff_texto(r))
            print()

    esperando = aguardando(resultados)
    if esperando:
        print("Campos vazios que ainda seguram marcadores (nada foi trocado por eles):")
        for campo, n in sorted(esperando.items()):
            print(f"  - {campo}: {n} marcador(es)")
    print(f"Marcadores sem correspondência (ficam como estão): {sum(sem_correspondencia(resultados).values())}")

    if not mudados:
        return 0
    if args.dry_run:
        print(f"\n[dry-run] {total} substituição(ões) em {len(mudados)} arquivo(s) — nada foi gravado.")
        return 0

    if not args.sim:
        try:
            resp = input(f"\nAplicar {total} substituição(ões) em {len(mudados)} arquivo(s)? "
                         f"Um backup será criado em {BACKUP_DIR}/. [s/N] ").strip().lower()
        except EOFError:
            resp = ""
        if resp not in {"s", "sim", "y", "yes"}:
            print("Cancelado. Nada foi alterado.")
            return 1

    carimbo = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    backup = gravar(raiz, resultados, carimbo)
    print(f"\n{total} substituição(ões) gravada(s) em {len(mudados)} arquivo(s). Backup: {backup}")

    pos: list[str] = []
    if any(r.rel == CANVAS_JSON for r in mudados) and not args.sem_regenerar:
        pos.append(regenerar_canvas(raiz))
        print("  " + pos[-1])

    conferencia, _ = varrer(raiz, d)
    ainda = sum(len(r.hits) for r in conferencia)
    if ainda:
        avisos.append(f"Conferência: {ainda} marcador(es) ainda poderiam ser trocados — rode o script de novo.")
    print("Conferência: " + ("segunda passada sem nada para trocar." if not ainda else f"{ainda} restante(s)!"))

    rel_final = args.relatorio or raiz / RELATORIO_PADRAO
    escrever_relatorio(raiz, rel_final, d, resultados, aplicado=not ainda, carimbo=carimbo, backup=backup,
                       pos_acoes=pos, avisos=avisos, restantes=conferencia)
    print(f"Relatório final: {rel_final}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
