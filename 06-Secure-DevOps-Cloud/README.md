# 06 — Secure DevOps Tools & Cloud Computing · "Deploy Blindado"

Componente **Produção** do AcessaCidade: o MVP empacotado em container, a nuvem descrita em
Terraform, um pipeline que barra segredo vazado e vulnerabilidade antes do deploy, e
observabilidade com os 4 sinais de ouro e alertas.

## Ficha Técnica do MVP (resumo)

| Campo | AcessaCidade |
|---|---|
| Nome do produto | **AcessaCidade** |
| Cidadão e território | Pessoas com deficiência, cadeirantes, pessoas com mobilidade reduzida e idosos que circulam por calçadas e espaços públicos urbanos (demonstração com a cidade fictícia "Cidade Exemplo") |
| Problema, em uma frase | Buracos, calçadas danificadas e obstáculos impedem a circulação segura e não há um canal simples para registrar e acompanhar esses problemas |
| Proposta de valor | Registrar a denúncia pelo celular com foto, receber uma triagem automática por visão computacional e acompanhar o status por protocolo |
| Arquitetura: componentes | SPA (HTML/CSS/JS) + API FastAPI em um container; visão computacional OpenCV; assistente de IA (OpenRouter + modo alternativo por regras); pipeline Raw→Bronze→Silver→Gold (DuckDB/Airflow); BI; RPA (UiPath); Azure ACR + ACI via Terraform; GitHub Actions DevSecOps; Prometheus/Grafana |
| Fontes de dados | Denúncias registradas pelos cidadãos; base **simulada** identificada (`origem_dado=SIMULADO`) para o pipeline e a demonstração |
| Modelos de IA utilizados | Visão computacional clássica (OpenCV, sem redes neurais); LLM via OpenRouter (modelo configurável, padrão `openai/gpt-4o-mini`) com alternativa por regras |
| URL do MVP e repositório | [PREENCHER: http://<fqdn>:8000] · [PREENCHER: https://github.com/<owner>/<repo>] |
| Indicadores de impacto | [PREENCHER: indicadores definidos pela equipe — ex.: denúncias registradas, tempo até a triagem, % resolvidas] |
| ODS conectados | ODS 11 — Cidades e comunidades sustentáveis [PREENCHER: outros ODS escolhidos pela equipe] |

## O que tem nesta pasta

| Pasta/arquivo | Conteúdo |
|---|---|
| `docker/Dockerfile` | Imagem multi-stage, não root (UID 10001), sem segredos, HEALTHCHECK |
| `terraform/` | IaC Azure: RG, ACR (admin off), identidade gerenciada (AcrPull), ACI (porta 8000), Log Analytics opcional; `tests/*.tftest.hcl` com provider simulado |
| `monitoring/` | Prometheus (local e Azure), regras de alerta, Alertmanager, Grafana (datasource + dashboard dos sinais de ouro) |
| `github-actions/` | `requirements-ci.txt` e explicação dos workflows (que ficam em `.github/workflows/`) |
| `tools/testar_regras_semgrep.py` | Teste das regras Semgrep da equipe |
| `tests/test_devops_*.py` | Testes automatizados de Dockerfile, compose, workflow, Terraform e observabilidade |
| `docs/` | Arquitetura, responsabilidade compartilhada, LGPD, custos, publicação, CI/CD, observabilidade, execução barrada, evidências, relatório |
| `PENDENCIAS_E_ACOES_MANUAIS.txt` | O que falta fazer (ações que dependem da equipe) |

Fora desta pasta (também da disciplina 06): `docker-compose.yml`, `.dockerignore`, `.gitleaks.toml`,
`.semgrep/`, `.github/workflows/ci-devsecops.yml`, `infra/` (YAML do ACI + scripts `az`),
`scripts/run_local.*` e `scripts/gerar_trafego_demo.py`.

## Como reproduzir

### 1. Sem Docker (desenvolvimento)

```powershell
python -m venv .venv; .\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\scripts\run_local.ps1            # http://127.0.0.1:8000   (Git Bash/Linux: ./scripts/run_local.sh)
```

### 2. Com Docker Compose

```powershell
Copy-Item .env.example .env        # opcional para o app; obrigatório para o Grafana
docker compose up -d --build       # http://localhost:8000
docker compose --profile monitoring up -d --build   # + Prometheus :9090, Grafana :3000, Alertmanager :9093 (só 127.0.0.1)
```

Para o Grafana, acrescente `GRAFANA_ADMIN_PASSWORD=<senha forte>` ao `.env` (não há senha padrão).

### 3. Na Azure

Passo a passo em [`docs/PUBLICACAO_AZURE.md`](docs/PUBLICACAO_AZURE.md): providers → state remoto →
Terraform fase 1 → push da imagem (`docker` ou `az acr build`) → Terraform fase 2 → URL pública.
Deploy automático: [`docs/CI_CD_DEVSECOPS.md`](docs/CI_CD_DEVSECOPS.md).

### 4. Testes e varreduras

```powershell
.\.venv\Scripts\python.exe -m pytest 06-Secure-DevOps-Cloud\tests
terraform -chdir=06-Secure-DevOps-Cloud\terraform init -backend=false
terraform -chdir=06-Secure-DevOps-Cloud\terraform validate
terraform -chdir=06-Secure-DevOps-Cloud\terraform test
gitleaks dir . --config .gitleaks.toml --redact
trivy config 06-Secure-DevOps-Cloud\docker
```

Resultados reais: [`docs/evidencias/validacoes_locais.md`](docs/evidencias/validacoes_locais.md).

## Decisões de segurança (resumo)

- Imagem: multi-stage, slim, sem pip na imagem final, UID 10001, só `DATA_DIR` gravável.
- Compose: `read_only`, `tmpfs /tmp`, `cap_drop: ALL`, `no-new-privileges`, limites de memória/PIDs; monitoramento só em `127.0.0.1`.
- Nuvem: ACR sem admin; pull por identidade gerenciada; segredos em `secure_environment_variables`; **somente a porta 8000**; **nenhuma porta administrativa** (ACI não tem SSH/RDP).
- CI: menor privilégio, OIDC (sem senha de longa duração), ferramentas com versão fixa, deploy só da imagem que passou no Trivy e no smoke test.

## Limitações (MVP) e evolução

| Limitação | Evolução |
|---|---|
| ACI com **armazenamento efêmero**: SQLite e fotos se perdem ao recriar o container | Azure Files no container group, ou PostgreSQL gerenciado + Blob Storage |
| **Sem HTTPS nativo** no ACI | Azure Container Apps (TLS gerenciado) ou Application Gateway/Front Door |
| Monitoramento roda na máquina da equipe | Azure Monitor managed Prometheus + Managed Grafana |
