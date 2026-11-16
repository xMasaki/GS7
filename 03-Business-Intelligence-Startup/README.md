# 03 — Business Intelligence & Startup Development · Pitch de Negócio + MVP CitizenTech

**Produto:** AcessaCidade · **Professor:** Henio Luiz Scheidt · **Papel no MVP:** negócio e pitch — o modelo de
negócio, os indicadores e o pitch que defende o MVP diante da banca.
**Entrega:** PDF único (Lean Canvas + modelo de negócio + links clicáveis para vídeo, MVP e repositório) no portal
da disciplina até **19/11/2026, 23h55** — um envio por equipe. Ficha Técnica do MVP:
[`docs/FICHA_TECNICA_MVP.md`](../docs/FICHA_TECNICA_MVP.md) (na raiz do repositório).

> Tudo o que é **hipótese** está marcado como hipótese; validações, resultados de testes com usuários, nomes e links
> ficam como `[PREENCHER]` até a equipe ter o dado real. Nenhuma parceria, contrato ou resultado foi inventado.
> Ações manuais: [`PENDENCIAS_E_ACOES_MANUAIS.txt`](PENDENCIAS_E_ACOES_MANUAIS.txt).

## 1. Entregáveis oficiais × onde estão

| Entregável (PDF oficial, pág. 32) | Arquivo(s) | Situação |
|---|---|---|
| Vídeo-pitch (até 5 min) com demo do MVP — link público, todos participam | `pitch/ROTEIRO_PITCH.md`, `pitch/STORYBOARD.md`, `pitch/LISTA_DE_CENAS.md`, `pitch/ROTEIRO_DE_GRAVACAO.md` | Roteiro pronto; **gravação pendente** |
| Lean Canvas consolidado: 9 blocos com o que foi validado | `business-model/LEAN_CANVAS.md` / `.html` / `.xlsx` (fonte única: `lean_canvas.json`) | Blocos completos; **status de validação a preencher com fatos do CP1/entrevistas** |
| Modelo de negócio: proposta de valor, receita e preço, canais e métricas | `business-model/MODELO_DE_NEGOCIO.md`, `ESTRATEGIA_DE_PRECO.md`, `METRICAS_E_IMPACTO.md`, `MODELO_FINANCEIRO_HIPOTETICO.xlsx` | Pronto, com premissas declaradas (valores hipotéticos) |
| MVP em URL pública + repositório + Ficha Técnica do MVP | `../docs/FICHA_TECNICA_MVP.md`; dashboard `#/painel` (`dashboard/README.md`) | Ficha pronta; **URL e repositório a preencher** |
| PDF único com links clicáveis | `docs/DOCUMENTO_DE_ENTREGA_BI.md` + `scripts/gerar_pdf_entrega.py` + `docs/links_entrega.yaml` | Gerador testado; **links a preencher** |

Rubrica (14 pts): Pitch 7 — Lean Canvas 2,0 · Modelo de Negócio 2,5 · Narrativa 2,5; MVP 7 — Demonstração ponta a
ponta 3,5 · Valor entregue evidenciado 3,5. O valor entregue depende de **evidência real**: teste com usuários
(`pitch/ROTEIRO_TESTE_USABILIDADE.md`, `pitch/TERMO_CONSENTIMENTO_MODELO.md`,
`pitch/registro_testes_usuarios_TEMPLATE.xlsx`) e métrica antes/depois (`pitch/LISTA_DE_EVIDENCIAS.md`).

## 2. Estrutura da pasta

```text
03-Business-Intelligence-Startup/
├── README.md                          # este arquivo
├── PENDENCIAS_E_ACOES_MANUAIS.txt     # o que a equipe precisa fazer, passo a passo
├── business-model/
│   ├── lean_canvas.json               # FONTE ÚNICA do Lean Canvas (editar aqui)
│   ├── LEAN_CANVAS.md / .html / .xlsx # gerados por scripts/gerar_lean_canvas.py
│   ├── MODELO_DE_NEGOCIO.md           # proposta de valor, quem paga, canais, receita, custos, ponto de equilíbrio, escala, riscos
│   ├── ESTRATEGIA_DE_PRECO.md         # planos e preços HIPOTÉTICOS com premissas
│   ├── METRICAS_E_IMPACTO.md          # métricas de produto, negócio e impacto; antes/depois; ODS
│   └── MODELO_FINANCEIRO_HIPOTETICO.xlsx  # premissas + ponto de equilíbrio + 36 meses (fórmulas do Excel)
├── pitch/
│   ├── ROTEIRO_PITCH.md               # 6 blocos, 5:00, falas por integrante
│   ├── STORYBOARD.md · LISTA_DE_CENAS.md · ROTEIRO_DE_GRAVACAO.md
│   ├── LISTA_DE_EVIDENCIAS.md         # o que comprova "valor entregue"
│   ├── ROTEIRO_TESTE_USABILIDADE.md · TERMO_CONSENTIMENTO_MODELO.md
│   ├── registro_testes_usuarios_TEMPLATE.xlsx  # modelo VAZIO para resultados reais
│   └── evidencias/README.md           # onde guardar prints e registros (sem dados pessoais)
├── dashboard/
│   ├── README.md                      # KPIs do #/painel: fórmula, fonte, camada; ligação com a Gold
│   ├── exportar_gold_para_excel.py    # Gold (CSV) -> AcessaCidade_indicadores.xlsx com gráficos nativos
│   └── AcessaCidade_indicadores.xlsx  # gerado a partir de data/processed/gold (dados incluem SIMULADOS)
├── docs/
│   ├── DOCUMENTO_DE_ENTREGA_BI.md     # fonte do PDF único
│   ├── links_entrega.yaml             # URLs do vídeo, MVP e repositório
│   ├── PROBLEMA_E_CIDADAO.md          # personas HIPOTÉTICAS, jornada atual, custos do problema
│   ├── ANALISE_CONCORRENCIA.md        # alternativas (156/ouvidorias, apps de zeladoria, redes sociais)
│   └── PROXIMOS_PASSOS.md
├── scripts/
│   ├── gerar_lean_canvas.py           # JSON -> MD + HTML (A4 paisagem) + XLSX
│   ├── gerar_planilhas.py             # modelo financeiro + modelo de registro de testes
│   └── gerar_pdf_entrega.py           # PDF único com links clicáveis (Edge via Playwright)
└── tests/
    └── test_bi_artefatos.py           # 7 testes: canvas (9 blocos, tudo HIPÓTESE), geradores, links
```

Testes: `.\.venv\Scripts\python.exe -m pytest 03-Business-Intelligence-Startup\tests` (também rodam no `pytest` da raiz).

## 3. Como gerar tudo (PowerShell, na raiz do repositório)

```powershell
# Lean Canvas (MD, HTML A4 paisagem, XLSX) a partir de business-model/lean_canvas.json
.\.venv\Scripts\python.exe 03-Business-Intelligence-Startup\scripts\gerar_lean_canvas.py

# Modelo financeiro hipotético + modelo vazio de registro de testes com usuários
.\.venv\Scripts\python.exe 03-Business-Intelligence-Startup\scripts\gerar_planilhas.py

# Indicadores da camada Gold em Excel (rode antes o pipeline da disciplina 02)
.\.venv\Scripts\python.exe 03-Business-Intelligence-Startup\dashboard\exportar_gold_para_excel.py

# PDF único da entrega (preencha docs/links_entrega.yaml antes; --estrito falha se restar [PREENCHER])
.\.venv\Scripts\python.exe 03-Business-Intelligence-Startup\scripts\gerar_pdf_entrega.py --estrito
```

Requisitos: venv da raiz (`requirements-dev.txt`: openpyxl, markdown, pyyaml, pypdf, playwright) e Microsoft Edge
instalado (o PDF usa `channel="msedge"`; não é preciso `playwright install`).

## 4. Verificação realizada (resultados reais, 2026-11-15)

| Comando | Resultado |
|---|---|
| `gerar_lean_canvas.py` | Gerou `LEAN_CANVAS.md`, `.html` e `.xlsx` (código de saída 0) |
| `gerar_planilhas.py` | Gerou as planilhas; cenário hipotético: ponto de equilíbrio com 24 clientes, mês 17, caixa acumulado positivo no mês 33 (valores **hipotéticos**, decorrentes das premissas) |
| `exportar_gold_para_excel.py` (contra `data/processed/gold/` real do pipeline) | `AcessaCidade_indicadores.xlsx`: Bairros 9 linhas, Categorias 8, Período 19, Status 5, Triagem da foto 4; aviso de que os dados incluem registros **SIMULADOS** |
| Lean Canvas HTML → PDF (Edge headless) | 1 página A4 paisagem (841,9 × 595,0 pt) — arquivo de verificação fora do repositório |
| `gerar_pdf_entrega.py` (sem links preenchidos) | PDF de 15 páginas gerado; 0 links clicáveis; lista de pendências: 3 links vazios e marcadores `[PREENCHER]` no documento, no canvas e no modelo de negócio |

## 5. Conexão com o MVP e com as outras disciplinas

- O **dashboard do MVP** é a rota `#/painel`: indicadores operacionais (`GET /api/indicadores`) e analíticos da
  camada Gold do pipeline (`GET /api/indicadores/analiticos`). Definições em `dashboard/README.md`.
- O pitch demonstra o fluxo central na URL pública: registrar denúncia com foto → triagem com etapas (disciplina 04)
  → consultar protocolo → perguntar ao helper (disciplina 01) → painel atualizado (disciplinas 02/03).
- Publicação e URL pública: disciplina 06. Robô de cadastro: disciplina 05. Placa com QR Code: disciplina 07.

## 6. Links da entrega

- Vídeo-pitch: [PREENCHER: URL_VIDEO]
- MVP: [PREENCHER: URL_MVP]
- Repositório: [PREENCHER: URL_REPOSITORIO]
- Integrantes: [PREENCHER: nomes, RMs e papéis]
