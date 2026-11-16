# AcessaCidade — Arquitetura geral

> Visão consolidada do produto para as 7 disciplinas. Os formatos exatos (rotas, campos, enumerações,
> variáveis) estão no contrato normativo [`CONTRATOS_DE_INTEGRACAO.md`](CONTRATOS_DE_INTEGRACAO.md);
> os diagramas Mermaid, em [`DIAGRAMA_INTEGRACAO.md`](DIAGRAMA_INTEGRACAO.md); os dados, em
> [`DICIONARIO_DE_DADOS.md`](DICIONARIO_DE_DADOS.md). Resumo para a banca: [`FICHA_TECNICA_MVP.md`](FICHA_TECNICA_MVP.md).
>
> O AcessaCidade **não é um serviço oficial do governo**. A triagem automática da foto é **apoio inicial**
> e sempre exige revisão humana; o sistema nunca afirma que uma calçada ou rota é acessível.

## 1. Princípio: um único produto

O AcessaCidade é **um** sistema web: uma SPA servida pelo próprio backend FastAPI, em **um** container e
**uma** URL. As disciplinas não criam sistemas paralelos — cada uma entrega um componente que é
importado pelo backend (pacotes Python), conversa com ele por REST (pipeline, robô, Prometheus) ou leva
o cidadão até ele (placa com QR Code). Nenhuma funcionalidade tem duas implementações.

## 2. Componentes

| Componente | Disciplina | Onde | Papel | Como se integra |
|---|---|---|---|---|
| Frontend SPA | base comum | `app/frontend/` | Telas Início, Registrar, Detalhe/Análise da foto, Consultar, Testar análise, Assistente, Painel, Revisão, Sobre | Servida pelo backend na mesma origem; chama `/api/*` |
| Backend API | base comum | `app/backend/acessacidade_api/` | Regras de negócio, validação, persistência, segurança, métricas | FastAPI + Uvicorn; importa os pacotes 01 e 04 |
| Banco operacional | base comum | `DATA_DIR/acessacidade.db` | Denúncias e histórico de status | SQLite (stdlib), migração idempotente (`db.py`) |
| Visão computacional | 04 | `04-Applied-Computer-Vision/src/acessacidade_vision/` | Valida, sanitiza (EXIF/GPS, rostos borrados) e tria a foto em 7 etapas | Importado pelo backend (`POST /api/denuncias`, `POST /api/visao/analisar`) |
| AcessaCidade Helper | 01 | `01-Generative-AI-Engineering/src/acessacidade_helper/` + `prompts/` | Assistente em linguagem simples, com guardrails e modo alternativo por regras | Importado pelo backend (`POST /api/assistente`); LLM via OpenRouter só com chave |
| Pipeline de dados | 02 | `02-Big-Data-Architecture/src/acessacidade_pipeline/`, `dags/` | ELT Raw → Bronze → Silver → Gold em DuckDB | Lê `GET /api/export/denuncias`; publica `POST /api/pipeline/gold` (`X-Pipeline-Token`) |
| Negócio e BI | 03 | `03-Business-Intelligence-Startup/` | Lean Canvas, modelo de negócio, métricas, pitch; exportação da Gold para Excel | Usa o painel `#/painel` e os CSV da Gold |
| Robô RPA | 05 | `05-Robotic-Process-Automation/UiPath/AcessaCidade.RPA/` | Lê planilha Excel e cadastra cada linha no formulário web | Abre `#/registrar?canal=rpa` (URL configurável) e usa os `id` estáveis do contrato §7 |
| Entrega e operação | 06 | `06-Secure-DevOps-Cloud/`, `.github/workflows/`, `docker-compose.yml`, `infra/` | Imagem Docker, CI/CD DevSecOps, Terraform Azure, Prometheus/Grafana | Constrói e publica o container; coleta `/metrics` |
| Placa acessível | 07 | `07-Project-Based-Maker-Lab/` | Redesign da placa do ponto de ônibus (laser + 3D) com QR Code | O QR leva a `#/registrar` na URL pública (a gerar quando ela existir) |

## 3. Stack e justificativas

| Camada | Escolha | Por quê |
|---|---|---|
| Linguagem | Python 3.11 | Mesma versão no venv, na imagem Docker (`python:3.11-slim-bookworm`) e na imagem do Airflow (`apache/airflow:2.10.5-python3.11`) |
| API | FastAPI 0.162.0 + Starlette 1.10.0 + Uvicorn 0.54.0 + python-multipart 0.0.33 | OpenAPI automática em `/docs`; versões atualizadas para zerar CVEs HIGH/CRITICAL no Trivy |
| Frontend | HTML + CSS + JavaScript puro (ES modules), sem build e sem CDN | Leve em celulares de entrada; permite CSP restritiva (`script-src 'self'`) |
| Banco | SQLite | Sem servidor, suficiente para o MVP; trocável por PostgreSQL |
| Visão | OpenCV clássico (`opencv-python-headless`) + NumPy, sem rede neural | Explicável passo a passo, roda em CPU, alinhado à disciplina |
| IA generativa | API compatível com OpenAI via OpenRouter (modelo configurável, padrão `openai/gpt-4o-mini`) | Chave fora do código; com falha ou sem chave, o modo alternativo por regras responde |
| Dados | DuckDB + Pandas | Reaproveita o notebook da Aula 06 (`Aula_06_ELT_Raw_Bronze.ipynb`) |
| Orquestração | Apache Airflow 2.10.5 (Docker) + runner local equivalente (`python -m acessacidade_pipeline`) | O Airflow não roda nativamente no Windows; o runner executa as mesmas funções da DAG |
| Observabilidade | `prometheus_client` + Prometheus + Alertmanager + Grafana | Quatro sinais de ouro e alertas |
| Nuvem | Azure Container Registry + Azure Container Instances, via Terraform | Um container, custo baixo, reaproveita o exercício de referência |
| CI/CD | GitHub Actions: pytest, Gitleaks, Semgrep, Terraform validate/test, Trivy, build + smoke test, deploy por OIDC | Barra segredos, código inseguro e imagens vulneráveis antes do deploy |

## 4. Implantação

### 4.1 Local, sem Docker (verificado)

```powershell
# Windows PowerShell, na raiz do repositório
.\.venv\Scripts\python.exe -m uvicorn acessacidade_api.main:app --app-dir app/backend --host 127.0.0.1 --port 8000
# ou: .\scripts\run_local.ps1   (carrega .env e define o PYTHONPATH)
```

Linux/macOS: `./scripts/run_local.sh`. Abra `http://127.0.0.1:8000/` (aplicação), `/docs` (API) e `/health`.
O backend acrescenta sozinho `01-.../src` e `04-.../src` ao `sys.path` quando necessário (contrato §2.1).

### 4.2 Docker / Docker Compose (preparado, não executado nesta máquina)

- `06-Secure-DevOps-Cloud/docker/Dockerfile`: multi-stage, `python:3.11-slim-bookworm`, usuário **não root**
  `10001:10001`, `EXPOSE 8000`, `HEALTHCHECK` em `/health`.
- `docker compose up -d --build` sobe a aplicação em `8000`; `docker compose --profile monitoring up -d --build`
  acrescenta Prometheus, Alertmanager (`127.0.0.1:9093`) e Grafana (`127.0.0.1:3000`).
- Não havia Docker nesta máquina; o CI faz `docker build`, Trivy image e smoke test. Ver
  `06-Secure-DevOps-Cloud/PENDENCIAS_E_ACOES_MANUAIS.txt`.

### 4.3 Azure Container Instances (preparado, depende de ação manual)

- Terraform em `06-Secure-DevOps-Cloud/terraform/`: Resource Group, ACR (`admin_enabled = false`),
  identidade gerenciada com `AcrPull`, Container Group Linux com IP público, `dns_name_label`, porta única
  `8000`, probes de liveness/readiness em `/health`, Log Analytics opcional. Valores padrão: 1 vCPU, 1,5 GB.
- Segredos (`ADMIN_TOKEN`, `PIPELINE_TOKEN`, `OPENROUTER_API_KEY`) entram como `secure_environment_variables`
  a partir de GitHub Secrets ou variáveis da sessão; o state do Terraform fica fora do repositório.
- Alternativa manual equivalente: `infra/aci-deployment.template.yaml` + scripts `infra/azure/` (ver
  [`infra/README.md`](../infra/README.md)). Passo a passo: `06-Secure-DevOps-Cloud/docs/PUBLICACAO_AZURE.md`.
- URL pública: [PREENCHER: URL pública do MVP — saída `app_url` do Terraform após o deploy real].

## 5. Segurança

- **Segredos**: nada no código nem no Git; `.env` ignorado, `.env.example` sem valores. Gitleaks (diretório)
  sem vazamentos; Semgrep (p/python, p/javascript, p/secrets, p/dockerfile + regras `.semgrep`) sem achados.
- **Rotas protegidas**: `PATCH /api/denuncias/{id}/status` (`X-Admin-Token`), exportação e publicação Gold
  (`X-Pipeline-Token`). Token vazio → 403 (função desativada); token errado → 401; comparação com
  `secrets.compare_digest`.
- **Entrada**: rate limit por IP (`RATE_LIMIT_PER_MINUTE`, 429 com `Retry-After`), limite de corpo, foto
  validada por decodificação real (não pela extensão), limite `MAX_UPLOAD_MB`, erro 500 genérico sem stacktrace.
- **Cabeçalhos**: CSP restritiva (`default-src 'self'`…, `frame-ancestors 'none'`), `X-Content-Type-Options`,
  `Referrer-Policy: no-referrer`, `X-Frame-Options: DENY`, `Permissions-Policy`. A página `/docs` tem CSP própria
  (contrato §12).
- **Container**: usuário não root, sem porta administrativa; Trivy config do Dockerfile e Terraform sem achados.
- **LGPD**: nome do denunciante opcional, guardado só no SQLite e nunca retornado nem exportado; fotos
  re-codificadas sem EXIF/GPS e com rostos borrados; logs em JSON sem nome, chave ou foto; Gold sem dados
  pessoais nem texto livre. Mapeamento completo: `06-Secure-DevOps-Cloud/docs/LGPD_MAPEAMENTO_DADOS_PESSOAIS.md`
  e classificação por campo em [`DICIONARIO_DE_DADOS.md`](DICIONARIO_DE_DADOS.md).

## 6. Observabilidade

- `GET /metrics` (formato Prometheus) com tráfego, erros, latência e saturação, além de métricas de negócio
  (denúncias criadas, classificações da visão, respostas do assistente por fonte) — contrato §10. O rótulo
  `route` usa o template da rota para evitar alta cardinalidade.
- `GET /health`: 200 `ok` ou 503 `degradado`; usado pelo `HEALTHCHECK` do Docker e pelas probes do ACI.
- Logs estruturados em JSON lines (`logging_config.py`).
- Prometheus, regras de alerta, Alertmanager e dashboard Grafana em `06-Secure-DevOps-Cloud/monitoring/`;
  gerador de tráfego para disparar o alerta: `scripts/gerar_trafego_demo.py`. Detalhes:
  `06-Secure-DevOps-Cloud/docs/OBSERVABILIDADE.md`. A stack não foi executada nesta máquina (sem Docker).

## 7. Limitações conhecidas (declaradas)

| Limitação | Consequência | Caminho de evolução |
|---|---|---|
| **SQLite e fotos em armazenamento efêmero no ACI** (`/app/data/runtime` dentro do container) | Recriar o container apaga as denúncias reais; o seed de demonstração é recriado | Azure Files montado no container group, ou PostgreSQL gerenciado + Blob Storage |
| **Sem HTTPS no ACI** (HTTP na porta 8000) | Tráfego sem criptografia; navegador marca "não seguro" | Azure Container Apps (TLS gerenciado) ou Application Gateway / Front Door |
| **Triagem avaliada só com imagens sintéticas** | Não existe medida de desempenho com fotos reais; nenhuma acurácia é declarada | Coleta de fotos reais com consentimento e rotulagem manual (disciplina 04) |
| **LLM sem chave no ambiente** | O assistente responde em modo alternativo por regras (`fonte: fallback`) | Configurar `OPENROUTER_API_KEY` (disciplina 01) |
| Rate limit em memória | Vale por processo; reinício zera os contadores | Gateway/API Management se houver várias réplicas |
| Uma réplica | Sem alta disponibilidade | Container Apps com réplicas e banco externo |
| Dados de demonstração simulados (Cidade Exemplo) | Indicadores do painel não são impacto real | Piloto com usuários reais (disciplina 03) |
| Airflow, Docker, Azure, GitHub Actions, UiPath Studio e fabricação não executados neste ambiente | Evidências desses itens ainda não existem | Ações manuais em cada `PENDENCIAS_E_ACOES_MANUAIS.txt` e em `PASSO_A_PASSO_PARA_CONCLUIR_O_PROJETO.txt` |
