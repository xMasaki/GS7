# Evidências necessárias — disciplina 02 (Big Data Architecture & Data Integration)

O PDF da GS pede: "Prints ou vídeo curto do pipeline rodando (DAG no Airflow, logs, dados carregados)".
Salve tudo em `02-Big-Data-Architecture/docs/evidencias/` com os nomes sugeridos abaixo.

## Já existentes (geradas automaticamente, reais)

| Arquivo | O que prova |
|---|---|
| `docs/evidencias/execucao_local_runner.log` | execução completa real das 6 tarefas pelo runner local (`--sem-api`), com contagens por camada e verificações de qualidade |
| `data/processed/relatorio_qualidade.md` / `.json` | relatório de qualidade da última execução (situação APROVADO) |
| `data/processed/gold/*.csv`, `gold_snapshot.json` | dados Gold carregados |
| `notebooks/AcessaCidade_ELT_Raw_Bronze_Silver_Gold.ipynb` | notebook executado, com as saídas reais de cada camada |

## A produzir pela equipe (dependem de Docker/Airflow ou da API publicada)

| # | Evidência | Nome sugerido | Como obter |
|---|---|---|---|
| 1 | Lista de DAGs com `acessacidade_elt_pipeline` ativa | `01_airflow_lista_dags.png` | UI do Airflow → DAGs |
| 2 | Visão **Graph** com as 6 tarefas verdes | `02_airflow_graph_sucesso.png` | DAG → Graph, após um Trigger |
| 3 | Visão **Grid** com a execução (e, se houver, a execução agendada diária) | `03_airflow_grid.png` | DAG → Grid |
| 4 | Log da tarefa `extract_and_load_raw` (linhas RAW) | `04_log_extract.png` | Grid → tarefa → Logs |
| 5 | Log da tarefa `quality_report` (verificações OK, APROVADO) | `05_log_quality.png` | idem |
| 6 | Log da tarefa `publish_gold` com `Snapshot ... publicado (HTTP 200)` | `06_log_publish.png` | execução com API + `PIPELINE_TOKEN` |
| 7 | XCom de `build_gold` (contagens) | `07_xcom_build_gold.png` | tarefa → XCom |
| 8 | Dados carregados: `gold_snapshot.json` aberto ou `GET /api/indicadores/analiticos` no navegador | `08_indicadores_analiticos.png` | navegador na URL da API |
| 9 | Dados carregados no DuckDB (consulta em uma tabela Gold) | `09_duckdb_gold.png` | notebook seção 6, ou `duckdb` CLI |
| 10 | Painel do app/BI exibindo os indicadores vindos da Gold | `10_painel_indicadores.png` | `#/painel` do app (a exibição da Gold publicada já foi conferida pelo E2E local em 15/11/2026; o print é da equipe) |
| 11 | Vídeo curto (1–3 min): Trigger da DAG → Graph verde → log → indicadores na API | `video_pipeline.mp4` ou link | gravador de tela (Win+Alt+R / Xbox Game Bar, OBS) |
| 12 | Log de execução com API real | `execucao_com_api.log` | **Já gerado** em 15/11/2026 contra a API local (runner; 28 linhas exportadas da API, `Publicação: OK`) — [docs/evidencias/execucao_com_api.log](evidencias/execucao_com_api.log). Opcional: repetir contra a URL pública |
Regras: não editar imagens para "simular" sucesso; se uma etapa falhar, registre a falha real e a correção.
Não mostre o valor de `PIPELINE_TOKEN` nem senhas nos prints (o Airflow mascara variáveis sensíveis, mas confira).

Links a incluir no relatório: repositório [PREENCHER: URL do repositório], vídeo [PREENCHER: link do vídeo],
API publicada [PREENCHER: URL pública da API, se houver].
