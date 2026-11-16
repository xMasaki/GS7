"""Exporta a camada Gold do pipeline AcessaCidade para uma pasta de trabalho Excel com gráficos nativos.

Lê os CSVs Gold gerados pelo pipeline da disciplina 02 (contrato, seção 4.8) e monta
`AcessaCidade_indicadores.xlsx` com uma aba por indicador e gráficos do próprio Excel
(openpyxl.chart), para análise em Excel ou importação no Power BI (opcional).

Arquivos procurados em --gold-dir (padrão: data/processed/gold/), aceitando os prefixos
"", "gold_" ou "gold." no nome:
  denuncias_por_bairro.csv     colunas: bairro, total, possiveis_buracos
  denuncias_por_categoria.csv  colunas: categoria, rotulo, total
  denuncias_por_periodo.csv    colunas: periodo, total
  denuncias_por_status.csv     colunas: status, rotulo, total
  resultado_visao.csv          colunas: classificacao, rotulo, total
Metadados (opcional): gold_snapshot.json (em --gold-dir ou na pasta pai) — usado para a aba
"Qualidade" e, se algum CSV faltar, como fonte alternativa das mesmas tabelas.

Uso (na raiz do repositório):
    .\\.venv\\Scripts\\python.exe 03-Business-Intelligence-Startup\\dashboard\\exportar_gold_para_excel.py
    .\\.venv\\Scripts\\python.exe 03-Business-Intelligence-Startup\\dashboard\\exportar_gold_para_excel.py --gold-dir <pasta> --saida <arquivo.xlsx>

Códigos de saída: 0 = ok · 2 = nenhum dado Gold encontrado · 3 = arquivo com colunas inválidas.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from openpyxl import Workbook
from openpyxl.chart import BarChart, LineChart, Reference
from openpyxl.chart.label import DataLabelList
from openpyxl.chart.series import SeriesLabel
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

RAIZ_REPO = Path(__file__).resolve().parents[2]
GOLD_PADRAO = RAIZ_REPO / "data" / "processed" / "gold"
SAIDA_PADRAO = Path(__file__).resolve().parent / "AcessaCidade_indicadores.xlsx"

# Cores (série única por gráfico; segunda série só no gráfico de bairros)
COR_1 = "2A78D6"
COR_2 = "EB6834"
AZUL_CAB = "1F5FAE"


class ErroDados(Exception):
    """Arquivo Gold encontrado, mas com estrutura diferente da do contrato."""


# chave -> (aba, colunas obrigatórias, colunas numéricas, título)
CONJUNTOS: dict[str, tuple[str, list[str], list[str], str]] = {
    "denuncias_por_bairro": ("Bairros", ["bairro", "total", "possiveis_buracos"], ["total", "possiveis_buracos"],
                             "Denúncias por bairro"),
    "denuncias_por_categoria": ("Categorias", ["categoria", "rotulo", "total"], ["total"],
                                "Denúncias por tipo de obstáculo"),
    "denuncias_por_periodo": ("Periodo", ["periodo", "total"], ["total"], "Denúncias por período"),
    "denuncias_por_status": ("Status", ["status", "rotulo", "total"], ["total"], "Denúncias por status"),
    "resultado_visao": ("Triagem_da_foto", ["classificacao", "rotulo", "total"], ["total"],
                        "Resultado da triagem automática da foto"),
}

MENSAGEM_SEM_DADOS = """Nenhum dado da camada Gold foi encontrado em:
  {pasta}

Como gerar os dados:
  1. Rode o pipeline de dados da disciplina 02 (runner local ou DAG do Airflow), conforme
     02-Big-Data-Architecture/README.md. Ele grava os CSVs Gold em data/processed/gold/.
  2. Rode este script novamente.
Ou aponte para outra pasta com:  --gold-dir <pasta_com_os_csv>
"""


def _localizar(pasta: Path, chave: str) -> Path | None:
    for prefixo in ("", "gold_", "gold."):
        candidato = pasta / f"{prefixo}{chave}.csv"
        if candidato.is_file():
            return candidato
    return None


def _converter(valor, coluna: str, origem: str):
    if valor is None or str(valor).strip() == "":
        return 0
    try:
        numero = float(str(valor).strip().replace(",", "."))
    except ValueError as exc:
        raise ErroDados(f"{origem}: valor não numérico '{valor}' na coluna '{coluna}'.") from exc
    return int(numero) if numero.is_integer() else numero


def _normalizar(linhas: list[dict], obrigatorias: list[str], numericas: list[str], origem: str) -> list[dict]:
    if linhas:
        faltando = [c for c in obrigatorias if c not in linhas[0]]
        if faltando:
            raise ErroDados(f"{origem}: faltam as colunas {faltando}. Esperado: {obrigatorias}.")
    saida = []
    for linha in linhas:
        nova = {c: linha.get(c) for c in obrigatorias}
        for c in numericas:
            nova[c] = _converter(nova[c], c, origem)
        saida.append(nova)
    return saida


def ler_csv(caminho: Path, obrigatorias: list[str], numericas: list[str]) -> list[dict]:
    with caminho.open(encoding="utf-8-sig", newline="") as f:
        leitor = csv.DictReader(f)
        cabecalho = [c.strip() for c in (leitor.fieldnames or [])]
        faltando = [c for c in obrigatorias if c not in cabecalho]
        if faltando:
            raise ErroDados(f"{caminho.name}: faltam as colunas {faltando}. Encontrado: {cabecalho}. "
                            f"Esperado (contrato 4.8): {obrigatorias}.")
        linhas = [{(k or "").strip(): v for k, v in linha.items()} for linha in leitor]
    return _normalizar(linhas, obrigatorias, numericas, caminho.name)


def ler_snapshot(pasta: Path) -> tuple[dict | None, Path | None]:
    for candidato in (pasta / "gold_snapshot.json", pasta.parent / "gold_snapshot.json"):
        if candidato.is_file():
            try:
                dados = json.loads(candidato.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                raise ErroDados(f"{candidato.name}: JSON inválido ({exc}).") from exc
            if isinstance(dados, dict):
                return dados, candidato
    return None, None


def carregar(pasta: Path) -> tuple[dict[str, list[dict]], dict[str, str], dict | None]:
    """Retorna (tabelas, origem de cada tabela, snapshot)."""
    tabelas: dict[str, list[dict]] = {}
    origens: dict[str, str] = {}
    snapshot, caminho_snap = ler_snapshot(pasta) if pasta.is_dir() else (None, None)
    for chave, (_, obrig, nums, _) in CONJUNTOS.items():
        arquivo = _localizar(pasta, chave) if pasta.is_dir() else None
        if arquivo:
            tabelas[chave] = ler_csv(arquivo, obrig, nums)
            origens[chave] = arquivo.name
        elif snapshot and isinstance(snapshot.get(chave), list):
            tabelas[chave] = _normalizar(snapshot[chave], obrig, nums, f"{caminho_snap.name}:{chave}")
            origens[chave] = f"{caminho_snap.name} (campo {chave})"
    return tabelas, origens, snapshot


def _cabecalho(ws, colunas: list[str], larguras: list[int]) -> None:
    for i, (nome, larg) in enumerate(zip(colunas, larguras), start=1):
        c = ws.cell(row=1, column=i, value=nome)
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor=AZUL_CAB)
        ws.column_dimensions[get_column_letter(i)].width = larg
    ws.freeze_panes = "A2"


def _estilo_barra(grafico: BarChart, titulo: str, horizontal: bool) -> None:
    grafico.type = "bar" if horizontal else "col"
    grafico.title = titulo
    grafico.title.overlay = False
    grafico.style = 10
    grafico.gapWidth = 60
    grafico.height = 9
    grafico.width = 18
    grafico.y_axis.majorGridlines = None
    grafico.y_axis.delete = False
    grafico.x_axis.delete = False
    if horizontal:
        grafico.x_axis.scaling.orientation = "maxMin"  # mantém a ordem da tabela de cima para baixo
        grafico.y_axis.crosses = "max"  # eixo de valores embaixo, mesmo com as categorias invertidas


def _grafico_barras(ws, titulo: str, col_cat: int, cols_val: list[int], n: int, ancora: str,
                    horizontal: bool = False, nomes: list[str] | None = None) -> None:
    g = BarChart()
    _estilo_barra(g, titulo, horizontal)
    for i, col in enumerate(cols_val):
        g.add_data(Reference(ws, min_col=col, min_row=1, max_row=n + 1), titles_from_data=True)
        g.series[i].graphicalProperties.solidFill = COR_1 if i == 0 else COR_2
        g.series[i].graphicalProperties.line.noFill = True
        if nomes:
            g.series[i].tx = SeriesLabel(v=nomes[i])
    g.set_categories(Reference(ws, min_col=col_cat, min_row=2, max_row=n + 1))
    if len(cols_val) == 1:
        g.legend = None
        g.dataLabels = DataLabelList()
        g.dataLabels.showVal = True
        g.dataLabels.showSerName = False
        g.dataLabels.showCatName = False
        g.dataLabels.showLegendKey = False
        g.dataLabels.showPercent = False
    else:
        g.legend.position = "t"
        g.legend.overlay = False
    ws.add_chart(g, ancora)


def montar_planilha(tabelas: dict[str, list[dict]], origens: dict[str, str], snapshot: dict | None,
                    pasta: Path, destino: Path) -> None:
    wb = Workbook()
    ws = wb.active
    ws.title = "Leia-me"
    simulados = snapshot.get("inclui_simulados") if snapshot else None
    linhas_info = [
        ("AcessaCidade — indicadores analíticos (camada Gold)", True),
        (f"Planilha gerada em: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')} (UTC)", False),
        (f"Pasta de origem: {pasta}", False),
        (f"Snapshot Gold gerado em: {snapshot.get('gerado_em', 'não informado')}" if snapshot
         else "Snapshot Gold (gold_snapshot.json): não encontrado — metadados indisponíveis.", False),
        (f"Execução do pipeline: {snapshot.get('execucao_id', 'não informada')}" if snapshot else "", False),
        ("Inclui dados simulados: " + ("SIM — os números NÃO representam denúncias reais" if simulados
                                         else "não" if simulados is False else "não informado pelo pipeline"), bool(simulados)),
        ("", False),
        ("Origem de cada aba:", True),
    ]
    for chave, (aba, *_rest) in CONJUNTOS.items():
        linhas_info.append((f"  {aba}: {origens.get(chave, 'sem dados')}", False))
    if snapshot and isinstance(snapshot.get("fontes"), list):
        linhas_info.append(("", False))
        linhas_info.append(("Fontes declaradas pelo pipeline:", True))
        for fonte in snapshot["fontes"]:
            linhas_info.append((f"  {fonte.get('nome', '?')}: {fonte.get('linhas', '?')} linhas", False))
    linhas_info += [
        ("", False),
        ("Definições dos indicadores: 03-Business-Intelligence-Startup/dashboard/README.md", False),
        ("A triagem da foto é heurística (OpenCV) e exige revisão humana; a pontuação não é probabilidade.", False),
        ("Power BI (opcional): Obter dados > Pasta de Trabalho do Excel > selecione as abas desejadas.", False),
    ]
    r = 1
    for texto, negrito in linhas_info:
        if texto == "" and r > 1 and not negrito:
            r += 1
            continue
        c = ws.cell(row=r, column=1, value=texto)
        c.font = Font(bold=negrito, size=13 if r == 1 else 10, color="7A2E00" if "SIM —" in texto else None)
        r += 1
    ws.column_dimensions["A"].width = 110

    # Resumo
    wr = wb.create_sheet("Resumo", 1)
    _cabecalho(wr, ["Indicador", "Valor", "Fórmula / fonte"], [44, 14, 80])
    resumo = []
    if "denuncias_por_bairro" in tabelas:
        resumo.append(("Total de denúncias (soma por bairro)", "=SUM(Bairros!B2:B10000)", "Σ total — gold.denuncias_por_bairro"))
        resumo.append(("Possíveis buracos identificados pela triagem", "=SUM(Bairros!C2:C10000)",
                       "Σ possiveis_buracos — gold.denuncias_por_bairro"))
        resumo.append(("% de denúncias com possível buraco", '=IFERROR(B3/B2,"")',
                       "possiveis_buracos ÷ total"))
        resumo.append(("Bairros com denúncias", "=COUNTA(Bairros!A2:A10000)", "nº de linhas — gold.denuncias_por_bairro"))
    if "resultado_visao" in tabelas:
        resumo.append(("Denúncias com foto analisada", "=" + "+".join(
            f'SUMIF(Triagem_da_foto!A2:A10000,"{k}",Triagem_da_foto!C2:C10000)'
            for k in ("POSSIBLE_POTHOLE", "NOT_IDENTIFIED", "INCONCLUSIVE")),
                       "Σ total das classificações POSSIBLE_POTHOLE, NOT_IDENTIFIED, INCONCLUSIVE — gold.resultado_visao"))
    if "denuncias_por_periodo" in tabelas:
        resumo.append(("Períodos cobertos", "=COUNTA(Periodo!A2:A10000)", "nº de linhas — gold.denuncias_por_periodo"))
    qualidade = snapshot.get("qualidade") if snapshot else None
    if isinstance(qualidade, dict) and "percentual_registros_validos" in qualidade:
        resumo.append(("% de registros válidos no pipeline", qualidade["percentual_registros_validos"],
                       "qualidade.percentual_registros_validos — gold_snapshot.json"))
    for i, (rot, val, form) in enumerate(resumo, start=2):
        wr.cell(row=i, column=1, value=rot)
        c = wr.cell(row=i, column=2, value=val)
        if rot.startswith("%") and isinstance(val, str):
            c.number_format = "0.0%"
        wr.cell(row=i, column=3, value=form)

    # Abas de dados + gráficos
    for chave, (aba, obrig, _nums, titulo) in CONJUNTOS.items():
        if chave not in tabelas:
            continue
        dados = tabelas[chave]
        wsd = wb.create_sheet(aba)
        _cabecalho(wsd, obrig, [30 if c in ("bairro", "rotulo", "categoria", "classificacao", "status") else 16 for c in obrig])
        if chave in ("denuncias_por_bairro", "denuncias_por_categoria", "denuncias_por_status", "resultado_visao"):
            dados = sorted(dados, key=lambda d: d["total"], reverse=True)
        if chave == "denuncias_por_periodo":
            dados = sorted(dados, key=lambda d: str(d["periodo"]))
        for linha in dados:
            wsd.append([linha[c] for c in obrig])
        n = len(dados)
        if n == 0:
            wsd.cell(row=2, column=1, value="(sem linhas nesta tabela)")
            continue
        ancora = f"{get_column_letter(len(obrig) + 2)}2"
        if chave == "denuncias_por_bairro":
            _grafico_barras(wsd, titulo, 1, [2, 3], n, ancora, horizontal=True,
                            nomes=["Total de denúncias", "Possíveis buracos (triagem da foto)"])
        elif chave == "denuncias_por_periodo":
            g = LineChart()
            g.title = titulo
            g.title.overlay = False
            g.height, g.width = 9, 18
            g.y_axis.majorGridlines = None
            g.y_axis.delete = False
            g.x_axis.delete = False
            g.add_data(Reference(wsd, min_col=2, min_row=1, max_row=n + 1), titles_from_data=True)
            g.set_categories(Reference(wsd, min_col=1, min_row=2, max_row=n + 1))
            g.series[0].graphicalProperties.line.solidFill = COR_1
            g.series[0].graphicalProperties.line.width = 25400
            g.series[0].smooth = False
            g.legend = None
            wsd.add_chart(g, ancora)
        else:
            _grafico_barras(wsd, titulo, 2, [3], n, ancora, horizontal=True)

    if isinstance(qualidade, dict) and qualidade:
        wq = wb.create_sheet("Qualidade")
        _cabecalho(wq, ["Indicador de qualidade do pipeline", "Valor"], [46, 16])
        for k, v in qualidade.items():
            wq.append([k, v])

    wb.properties.title = "AcessaCidade — indicadores analíticos (Gold)"
    wb.properties.creator = "AcessaCidade (exportar_gold_para_excel.py)"
    destino.parent.mkdir(parents=True, exist_ok=True)
    wb.save(destino)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--gold-dir", type=Path, default=GOLD_PADRAO, help="pasta com os CSVs Gold")
    ap.add_argument("--saida", type=Path, default=SAIDA_PADRAO, help="arquivo .xlsx de saída")
    args = ap.parse_args(argv)
    try:
        tabelas, origens, snapshot = carregar(args.gold_dir)
    except ErroDados as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        return 3
    if not tabelas:
        print(MENSAGEM_SEM_DADOS.format(pasta=args.gold_dir), file=sys.stderr)
        return 2
    faltando = [CONJUNTOS[k][0] for k in CONJUNTOS if k not in tabelas]
    montar_planilha(tabelas, origens, snapshot, args.gold_dir, args.saida)
    print(f"Planilha gerada: {args.saida}")
    for chave, origem in origens.items():
        print(f"  {CONJUNTOS[chave][0]}: {len(tabelas[chave])} linhas (de {origem})")
    if faltando:
        print(f"  Aviso: sem dados para {faltando} — essas abas não foram criadas.")
    if snapshot and snapshot.get("inclui_simulados"):
        print("  Aviso: o pipeline informou que os dados incluem registros SIMULADOS.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
