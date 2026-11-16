# Evidências necessárias — Disciplina 06 (Deploy Blindado)

Salve os prints em `06-Secure-DevOps-Cloud/docs/evidencias/` com os nomes sugeridos (PNG).
Nenhum print pode mostrar segredo: confira antes de salvar (tokens, chave do OpenRouter,
IDs completos de assinatura/tenant — corte ou borre).

| # | Critério (14 pts) | Evidência | Nome do arquivo sugerido | Como obter |
|---|---|---|---|---|
| 1 | Container (2,0) | `docker compose ps` com `app` **healthy** | `01_compose_ps_healthy.png` | `docker compose up -d --build; docker compose ps` |
| 2 | Container | Usuário não root na imagem | `02_imagem_usuario_10001.png` | `docker compose exec app id` → `uid=10001` |
| 3 | Container | Trivy image sem CRITICAL/HIGH corrigível | `03_trivy_image_ok.png` | log do job `imagem` no Actions |
| 4 | IaC (3,0) | `terraform apply` concluído (fase 1 e fase 2) | `04_terraform_apply_fase1.png`, `05_terraform_apply_fase2.png` | job `deploy` ou terminal |
| 5 | IaC | Portal Azure: Resource Group com ACR, identidade e ACI | `06_portal_resource_group.png` | Portal → Resource groups → `rg-acessacidade-prod` |
| 6 | IaC | ACI → Networking/Properties mostrando **somente a porta 8000** | `07_aci_porta_8000.png` | Portal → Container instances → Properties |
| 7 | IaC | State fora do repositório (container `tfstate` na Storage) | `08_tfstate_storage.png` | Portal → Storage account → Containers → `tfstate` |
| 8 | IaC | `.gitignore` com `*.tfstate` / `*.tfvars` e repositório sem esses arquivos | `09_gitignore_tfstate.png` | GitHub → arquivo `.gitignore` |
| 9 | Pipeline (4,0) | Execução **verde** com todos os jobs (testes, gitleaks, semgrep, iac, imagem, deploy) | `10_actions_verde.png` | GitHub → Actions |
| 10 | Pipeline | Execução **barrada** (motivo visível) | `11_actions_barrada.png` | `DEMONSTRACAO_EXECUCAO_BARRADA.md` |
| 11 | Pipeline | Execução **corrigida** | `12_actions_corrigida.png` | idem |
| 12 | Pipeline | GitHub Secrets cadastrados (somente os **nomes**) | `13_github_secrets.png` | Settings → Secrets and variables → Actions / Environments → production |
| 13 | Pipeline | Federated credential (OIDC) no Entra ID | `14_oidc_federated_credential.png` | Entra ID → App registrations → `gh-acessacidade-deploy` |
| 14 | MVP | URL pública funcionando no navegador | `15_url_publica.png` | `http://<fqdn>:8000` |
| 15 | MVP | `/health` respondendo `ok` | `16_health_publico.png` | `http://<fqdn>:8000/health` |
| 16 | Observabilidade (3,0) | Dashboard Grafana com os 4 sinais de ouro **com dados** | `17_grafana_sinais_de_ouro.png` | `OBSERVABILIDADE.md` §4.3 |
| 17 | Observabilidade | Prometheus Targets UP (local ou Azure) | `18_prometheus_targets.png` | http://127.0.0.1:9090/targets |
| 18 | Observabilidade | Alerta **FIRING** no Prometheus | `19_alerta_firing.png` | `OBSERVABILIDADE.md` §4.1/4.2 |
| 19 | Observabilidade | Alerta no Alertmanager | `20_alertmanager.png` | http://127.0.0.1:9093 |
| 20 | Documentação (2,0) | Print/print da calculadora de custos | `21_calculadora_custos.png` | Azure Pricing Calculator |
| 21 | Custos | Cost Management com gasto real do período | `22_cost_management.png` | Portal → Cost Management |

## Links que entram no PDF (todos clicáveis)

| Item | Link |
|---|---|
| Repositório público | [PREENCHER: https://github.com/<owner>/<repo>] |
| URL pública do MVP | [PREENCHER: http://<fqdn>:8000] |
| Execução verde (com deploy) | [PREENCHER: URL da execução no Actions] |
| Execução barrada | [PREENCHER] |
| Execução corrigida | [PREENCHER] |
| Vídeo (opcional) da demonstração do alerta | [PREENCHER] |
