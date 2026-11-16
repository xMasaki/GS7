# 02 — Big Data Architecture & Data Integration · Pipeline de Dados do MVP CitizenTech

Componente **Dados** do AcessaCidade (FIAP Global Solution 2026.2 — CitizenTech, ODS 11): pipeline **ELT** orquestrado
que coleta denúncias de problemas de acessibilidade em calçadas, trata-as em camadas **raw → bronze → silver → gold**
num warehouse **DuckDB** e publica indicadores para o app (`GET /api/indicadores/analiticos`) e para o BI.

> Dados de demonstração **simulados** (cidade fictícia "Cidade Exemplo", `origem_dado=SIMULADO`). Nenhum dado real de pessoa.

## Início rápido (Windows, sem Airflow)

```powershell
cd C:\caminho\para\GS7-4ESPR
$env:PYTHONPATH = "02-Big-Data-Architecture/src"
.\.venv\Scripts\python.exe -m acessacidade_pipeline --sem-api      # pipeline completo, só fonte simulada
.\.venv\Scripts\python.exe -m pytest 02-Big-Data-Architecture/tests # testes
```

Airflow 2.10.5 (Docker): ver [`airflow/README.md`](airflow/README.md). Tudo em [`docs/INSTRUCOES_EXECUCAO.md`](docs/INSTRUCOES_EXECUCAO.md).

## Estrutura

| Caminho | Conteúdo |
|---|---|
| `src/acessacidade_pipeline/` | pacote: `config`, `simulate`, `parsing`, `regras`, `dominio`, `warehouse`, `extract`, `raw`, `bronze`, `silver`, `gold`, `quality`, `publish`, `run_pipeline` / `__main__` |
| `dags/acessacidade_elt_pipeline.py` | DAG TaskFlow: `extract_and_load_raw → transform_bronze → curate_silver → build_gold → quality_report → publish_gold` (`@daily`, `catchup=False`, `retries=1`) |
| `airflow/` | `docker-compose.airflow.yml` (Airflow 2.10.5 standalone, Python 3.11) e README |
| `notebooks/` | notebook didático executado (adaptação da Aula 06) e `executar_notebook.py` |
| `tests/` | `test_pipeline_*.py` — parsing, regras, camadas, Gold/contrato 4.8, idempotência, DAG (stub), API (MockTransport) |
| `docs/` | arquitetura, dicionário de dados, regras, instruções, evidências, relatório de entrega (+ `gerar_pdf_relatorio.py`) |
| `docs/evidencias/` | `execucao_local_runner.log` (execução real) e prints a produzir |
| `requirements-pipeline.txt` | dependências do pipeline |
| `PENDENCIAS_E_ACOES_MANUAIS.txt` | o que falta e o passo a passo das ações manuais |

Dados (fora desta pasta): `data/samples/denuncias_simuladas.csv` (+ `LEIAME_denuncias_simuladas.md`),
`data/exports/` (cópias das exportações da API, não versionadas), `data/processed/` (Gold CSV/JSON, relatório de
qualidade; o warehouse `.duckdb` não é versionado).

## Integração com os demais componentes

| Com | Como | Contrato |
|---|---|---|
| Backend (app) | `GET /api/export/denuncias?formato=csv` + `X-Pipeline-Token` (extração) | 4.7 |
| Backend (app) | `POST /api/pipeline/gold` + `X-Pipeline-Token` (publicação do snapshot) | 4.8 |
| BI (disciplina 03) | `data/processed/gold/*.csv` e `gold_snapshot.json` | 4.8 / 8 |
| Visão computacional (04) | consome `visao_classificacao` vinda da API (chaves 3.4) | 3.4 |

## Entregáveis do PDF (disciplina 02) e onde estão

| Entregável | Situação |
|---|---|
| Repositório com o pipeline (scripts, notebooks ou DAGs) e instruções de execução | pronto (esta pasta) |
| Diagrama de arquitetura e dicionário de dados das tabelas entregues | pronto: `docs/ARQUITETURA_PIPELINE.md`, `docs/DICIONARIO_DE_DADOS.md`; PDF único gerado por `docs/gerar_pdf_relatorio.py` a partir de `docs/RELATORIO_ENTREGA_BIGDATA.md` (preencher equipe/links) |
| Prints ou vídeo do pipeline rodando (DAG no Airflow, logs, dados carregados) | **pendente** — depende de Docker/WSL2 (ver `PENDENCIAS_E_ACOES_MANUAIS.txt`) |
| Link do repositório + PDF único, no portal até 19/11 23h55, um envio por equipe | **pendente** (ação da equipe) |

Critérios: 14 pontos — pipeline funcional 8 · arquitetura e documentação 6. O PDF remete aos critérios detalhados
"no README da disciplina" publicado pela professora: [PREENCHER: conferir e colar aqui os critérios oficiais].

## Crédito

O notebook e o desenho Raw/Bronze reaproveitam as ideias do notebook **Aula 06 — "De ETL para ELT: Camadas Raw e
Bronze"** da disciplina (FIAP), adaptadas do domínio de vendas para denúncias de acessibilidade.
