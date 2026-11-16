# AcessaCidade — Relatório de entrega: Secure DevOps Tools & Cloud Computing

**Atividade:** Deploy Blindado · **FIAP Global Solution 2026.2 — CitizenTech (ODS 11)** · **14 pontos**
**Equipe:** [PREENCHER: nomes e RMs dos integrantes] · **Turma:** [PREENCHER]
**Data:** [PREENCHER]

> Fonte do **PDF único** entregue no portal. Antes de exportar: substitua todos os [PREENCHER],
> insira os prints de `evidencias/` nos locais indicados e confira que **todos os links são clicáveis**.

## Links da entrega

| Item | Link |
|---|---|
| Repositório público (Dockerfile, workflow, Terraform) | [PREENCHER: https://github.com/<owner>/<repo>] |
| URL pública do MVP | [PREENCHER: http://<fqdn>:8000] |
| Ficha Técnica do MVP (README) | [PREENCHER: link para o README da raiz] |
| Pipeline — execução verde com deploy | [PREENCHER] |
| Pipeline — execução barrada | [PREENCHER] |
| Pipeline — execução corrigida | [PREENCHER] |

## 1. Arquitetura

Diagrama: `ARQUITETURA_CLOUD.md` (Mermaid — exportar como imagem para o PDF).
[PREENCHER: inserir imagem do diagrama]

Resumo: GitHub → GitHub Actions (testes, Gitleaks, Semgrep, Terraform validate/test, Trivy config,
build + Trivy image + smoke test) → push da imagem testada (tag = SHA) no **Azure Container Registry**
→ **Azure Container Instances** criado por **Terraform** (state remoto no Azure Storage) → cidadão
acessa `http://<fqdn>:8000`. Prometheus/Grafana locais coletam `/metrics` da URL pública.

## 2. Container e IaC (5,0)

| Requisito | Como foi atendido | Evidência |
|---|---|---|
| Dockerfile enxuto | Multi-stage; `python:3.11-slim-bookworm`; só venv + código de runtime; pip/setuptools/wheel removidos; `.dockerignore` exclui testes, docs, outras disciplinas | `06-Secure-DevOps-Cloud/docker/Dockerfile` · [PREENCHER: tamanho da imagem `docker image ls`] |
| Usuário não root | `USER 10001:10001`; código pertence ao root (somente leitura); só `DATA_DIR` gravável | print 02 |
| Sem segredo na imagem | Nenhum `ENV`/`ARG` sensível (teste automatizado + verificação no CI + Trivy `--scanners secret`) | print 03 |
| Stack com docker compose | `docker-compose.yml`: app endurecido (`read_only`, `cap_drop: ALL`, `no-new-privileges`, healthcheck) + profile `monitoring` | print 01 |
| Nuvem por Terraform | `06-Secure-DevOps-Cloud/terraform` (azurerm ~> 4.0): RG, ACR (admin off), identidade gerenciada + AcrPull, ACI | prints 04–06 |
| State e .tfvars fora do repo | Backend `azurerm` parcial (`-backend-config`), `.gitignore` bloqueia `*.tfstate`/`*.tfvars` | prints 07–08 |
| Porta admin nunca aberta para 0.0.0.0/0 | ACI não tem SSH/RDP; única porta exposta 8000/TCP (validação na variável + teste) | print 07 |

## 3. Pipeline DevSecOps (4,0)

| Requisito | Como foi atendido | Evidência |
|---|---|---|
| Build, Gitleaks, Semgrep e Trivy a cada push | `on: push: branches: ["**"]` + PR; jobs `gitleaks`, `semgrep`, `iac` (Trivy config), `imagem` (build + Trivy image) | print 10 |
| Segredos em GitHub Secrets | `AZURE_*`, `TFSTATE_*`, `ADMIN_TOKEN`, `PIPELINE_TOKEN`, `OPENROUTER_API_KEY`; OIDC sem client secret | prints 12–13 |
| Deploy automático | Job `deploy` (push na main, environment `production`) — Terraform fase 1/2 + smoke test | print 10 |
| Execução barrada e corrigida | Token fictício `acd_demo_…` detectado pela regra `acessacidade-demo-token` | prints 11–12 |

## 4. Observabilidade (3,0)

Dashboard "AcessaCidade — Sinais de Ouro": latência p50/p95/p99, tráfego por rota, erros 4xx/5xx (req/s e %),
saturação (em andamento, memória, CPU) + métricas de negócio. Alerta disparado: [PREENCHER: qual —
`AcessaCidadeMuitas4xx` ou `AcessaCidadeIndisponivel`], em [PREENCHER: data/hora].
[PREENCHER: prints 16–19]

## 5. Documentação (2,0)

| Item | Documento |
|---|---|
| Diagrama | `ARQUITETURA_CLOUD.md` |
| Responsabilidade compartilhada | `RESPONSABILIDADE_COMPARTILHADA.md` |
| Dados pessoais (LGPD) | `LGPD_MAPEAMENTO_DADOS_PESSOAIS.md` |
| Estimativa de custo | `ESTIMATIVA_DE_CUSTOS.md` (+ print da calculadora: [PREENCHER]) |
| README reproduzível | `06-Secure-DevOps-Cloud/README.md` e README da raiz |

**Custo estimado (referência East US, conferir):** ≈ US$ 10,80 (7 dias), ≈ US$ 21,50 (14 dias),
≈ US$ 46,00/mês. Valor conferido para a região usada: [PREENCHER]. Gasto real no período: [PREENCHER: Cost Management].

## 6. Limitações e próximos passos

- **Armazenamento efêmero** no ACI (SQLite e fotos são perdidos ao recriar o container) → Azure Files ou PostgreSQL + Blob.
- **Sem HTTPS nativo** → Azure Container Apps ou Application Gateway/Front Door com TLS e WAF.
- `/metrics` público (sem dados pessoais) → rede privada ou Azure Monitor managed Prometheus.
- Monitoramento local → Azure Managed Grafana / alertas com notificação.

## 7. Resultados reais da validação local

Ver `evidencias/validacoes_locais.md` (Terraform fmt/validate/test, Trivy config e fs, Gitleaks, Semgrep, pytest).
