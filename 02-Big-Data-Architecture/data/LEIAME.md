# 02-Big-Data-Architecture/data — onde estão os dados do pipeline

Esta pasta existe para seguir a estrutura pedida para a disciplina, mas **os dados ficam na pasta `data/` da
raiz do repositório**, compartilhada com o backend, a visão computacional e o BI (um só produto, uma só base).
O pipeline lê e grava lá por padrão (`PIPELINE_DATA_DIR`, ver `src/acessacidade_pipeline/config.py`).

| Camada / uso | Caminho (a partir da raiz) | Versionado? |
|---|---|---|
| Fonte simulada (RAW) | [`data/samples/denuncias_simuladas.csv`](../../data/samples/denuncias_simuladas.csv) — dados **SIMULADOS**, ver [`LEIAME_denuncias_simuladas.md`](../../data/samples/LEIAME_denuncias_simuladas.md) | sim |
| Exportações da API (RAW) | `data/exports/denuncias_api_*.csv` | não (gerado a cada execução com API) |
| Warehouse DuckDB (RAW, BRONZE, SILVER, GOLD) | `data/processed/warehouse/acessacidade.duckdb` | não |
| GOLD em CSV/JSON (consumida pelo painel e pelo BI) | [`data/processed/gold/`](../../data/processed/gold/) | sim |
| Relatório de qualidade | [`data/processed/relatorio_qualidade.md`](../../data/processed/relatorio_qualidade.md) | sim |

Para gravar os dados em outra pasta (por exemplo, para não alterar os arquivos versionados durante um
teste), defina `PIPELINE_DATA_DIR` antes de rodar o pipeline (ver `docs/INSTRUCOES_EXECUCAO.md`).
