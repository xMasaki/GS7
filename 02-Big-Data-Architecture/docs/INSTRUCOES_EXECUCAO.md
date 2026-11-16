# Instruções de execução — pipeline de dados AcessaCidade

Todos os comandos partem da **raiz do repositório** (`GS7-4ESPR`). Python **3.11**.

## Variáveis de ambiente

| Variável | Padrão | Uso |
|---|---|---|
| `PIPELINE_DATA_DIR` | `<raiz>/data` | onde ficam `samples/`, `exports/` e `processed/` |
| `PIPELINE_WAREHOUSE_PATH` | `<PIPELINE_DATA_DIR>/processed/warehouse/acessacidade.duckdb` | arquivo DuckDB |
| `ACESSACIDADE_API_URL` | vazio (sem integração) | URL da API (ex.: `http://localhost:8000`) |
| `PIPELINE_TOKEN` | vazio (sem integração) | mesmo valor configurado no backend (`.env`) |
| `PIPELINE_HTTP_TIMEOUT` | `20` | segundos |

Sem `ACESSACIDADE_API_URL` **ou** sem `PIPELINE_TOKEN`, a extração da API e a publicação são puladas com aviso no
log, e o pipeline roda somente com a fonte simulada.

## 1. Windows — runner local (sem Airflow)

```powershell
cd C:\caminho\para\GS7-4ESPR
python -m venv .venv                      # se ainda não existir (Python 3.11)
.\.venv\Scripts\python.exe -m pip install -r requirements.txt -r requirements-dev.txt
$env:PYTHONPATH = "02-Big-Data-Architecture/src"

# (opcional) regenerar a fonte simulada — sempre igual (semente fixa)
.\.venv\Scripts\python.exe -m acessacidade_pipeline.simulate

# pipeline completo só com a fonte simulada, gravando o log
.\.venv\Scripts\python.exe -m acessacidade_pipeline --sem-api --log-arquivo 02-Big-Data-Architecture/docs/evidencias/execucao_local_runner.log
```

Com a API do AcessaCidade rodando (ver README da raiz) e o mesmo `PIPELINE_TOKEN` do backend:

```powershell
$env:ACESSACIDADE_API_URL = "http://localhost:8000"
$env:PIPELINE_TOKEN = "<valor do PIPELINE_TOKEN do seu .env>"
.\.venv\Scripts\python.exe -m acessacidade_pipeline --log-arquivo 02-Big-Data-Architecture/docs/evidencias/execucao_com_api.log
```

Resultado esperado: log terminando em `Resumo: {...'situacao_qualidade': 'APROVADO'}`; arquivos atualizados em
`data/processed/gold/` e `data/processed/relatorio_qualidade.md`; com API, `Publicação: OK` e o snapshot visível em
`GET {API}/api/indicadores/analiticos`.

Opções: `--execucao-id <id>`, `--nivel-log DEBUG|INFO|WARNING|ERROR`, `--sem-api`.

### Testes

```powershell
.\.venv\Scripts\python.exe -m pytest 02-Big-Data-Architecture/tests
```

Os testes usam pastas temporárias (não alteram `data/processed/`), simulam a API com `httpx.MockTransport` e
verificam a DAG com um *stub* de `airflow.decorators` (o Airflow não é necessário para os testes).

### Notebook

```powershell
.\.venv\Scripts\python.exe 02-Big-Data-Architecture/notebooks/executar_notebook.py
```
(executa com `nbclient` usando o kernel `python3` do `.venv` e salva o `.ipynb` com as saídas; ou abra no
VS Code/Jupyter com o kernel do `.venv` e execute todas as células). O notebook grava no mesmo warehouse e em
`data/processed`, como o runner. Feche o notebook antes de rodar o runner/Airflow (o DuckDB aceita um escritor por vez).

## 2. Docker Desktop — Airflow 2.10.5 (Windows/macOS/Linux)

Detalhes em [`../airflow/README.md`](../airflow/README.md).

```powershell
cd 02-Big-Data-Architecture\airflow
docker compose --env-file ..\..\.env -f docker-compose.airflow.yml up -d
docker compose -f docker-compose.airflow.yml exec airflow cat /opt/airflow/standalone_admin_password.txt
```

UI em http://127.0.0.1:8080 (usuário `admin`) → ativar `acessacidade_elt_pipeline` → **Trigger DAG**.
Para a API rodando no Windows ser alcançada pelo container, suba o backend escutando em `0.0.0.0:8000`
(`uvicorn ... --host 0.0.0.0`) ou defina `ACESSACIDADE_API_URL_AIRFLOW` no `.env` com a URL pública da API.

## 3. Linux nativo ou WSL2 (Ubuntu) — Airflow via pip com constraints

> O Airflow 2.10.5 **não** roda no Windows nativo e **não** suporta Python 3.13/3.14 — use Python 3.11 no Linux/WSL.

```bash
cd /caminho/para/GS7-4ESPR
python3.11 -m venv .venv-airflow && source .venv-airflow/bin/activate
C=https://raw.githubusercontent.com/apache/airflow/constraints-2.10.5/constraints-3.11.txt
pip install "apache-airflow==2.10.5" --constraint "$C"
pip install "duckdb==1.1.3" --constraint "$C"     # pandas/httpx já vêm com o Airflow
export AIRFLOW_HOME=$HOME/airflow-acessacidade AIRFLOW__CORE__LOAD_EXAMPLES=false
export AIRFLOW__CORE__DAGS_FOLDER=$PWD/02-Big-Data-Architecture/dags
export PYTHONPATH=$PWD/02-Big-Data-Architecture/src PIPELINE_DATA_DIR=$PWD/data
airflow dags test acessacidade_elt_pipeline      # execução completa no terminal
airflow standalone                               # UI em http://localhost:8080
```

Runner local no Linux/WSL (sem Airflow): `pip install -r 02-Big-Data-Architecture/requirements-pipeline.txt`
e `PYTHONPATH=02-Big-Data-Architecture/src python -m acessacidade_pipeline --sem-api`.

## Problemas comuns

| Sintoma | Causa / solução |
|---|---|
| `IO Error: Could not set lock on file ... acessacidade.duckdb` | outro processo (notebook aberto, Airflow, runner) está com o warehouse aberto: feche-o e repita |
| `[extract] API PULADA: PIPELINE_TOKEN não configurado` | defina `PIPELINE_TOKEN` (igual ao do backend) |
| `API respondeu 401` / `403` | token diferente do backend / backend com `PIPELINE_TOKEN` vazio |
| `API indisponível em http://host.docker.internal:8000` | API não está rodando ou escuta só em 127.0.0.1 |
| `ModuleNotFoundError: acessacidade_pipeline` | defina `PYTHONPATH=02-Big-Data-Architecture/src` |
