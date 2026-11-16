# Modelo de responsabilidade compartilhada — AcessaCidade na Azure

Na nuvem, a segurança é dividida: o provedor (Microsoft Azure) protege **a nuvem**; a equipe
protege **o que coloca na nuvem**. Quanto mais gerenciado o serviço, mais responsabilidades passam
para o provedor. O AcessaCidade usa **Azure Container Instances (ACI)** — um serviço de containers
sem servidor (CaaS), entre IaaS e PaaS.

## 1. Comparação por modelo de serviço

Legenda: **A** = Azure · **E** = Equipe AcessaCidade · **A/E** = compartilhada

| Responsabilidade | IaaS (VM) | ACI — usado no MVP | PaaS (App Service / Container Apps) |
|---|---|---|---|
| Datacenter, energia, rede física, hardware | A | A | A |
| Hipervisor e isolamento entre clientes | A | A | A |
| Sistema operacional do host e patches | **E** | A | A |
| Runtime de containers / orquestração | **E** | A | A |
| Rede: IP público, DNS, portas expostas | E | **E** (definidas no Terraform: só 8000) | A/E |
| Porta administrativa (SSH/RDP) | **E** (precisa restringir) | não existe | não existe |
| TLS/HTTPS | E | **E** (não nativo — limitação documentada) | A/E (certificado gerenciado) |
| Imagem do container (base, pacotes, CVEs) | E | **E** (Dockerfile + Trivy no CI) | E (se usar container) |
| Código da aplicação (vulnerabilidades) | E | **E** (Semgrep, testes) | E |
| Segredos (tokens, chave do OpenRouter) | E | **E** (GitHub Secrets → `secure_environment_variables`) | E |
| Identidade e acesso (Entra ID, RBAC) | A/E | **A/E** (Azure fornece; equipe configura OIDC, AcrPull, menor privilégio) | A/E |
| Dados e classificação (LGPD) | E | **E** | E |
| Backup e persistência dos dados | E | **E** (no MVP é efêmero — ver limitação) | A/E |
| Logs e monitoramento | E | **A/E** (Azure guarda logs do container; equipe opera Prometheus/Grafana e alertas) | A/E |
| Disponibilidade da plataforma (SLA) | A | A | A |
| Disponibilidade da aplicação (probes, restart) | E | **A/E** (Azure reinicia; equipe define probes `/health`) | A/E |
| Custos e limpeza de recursos | E | **E** | E |

## 2. O que a equipe faz, na prática

| Controle | Onde está |
|---|---|
| Imagem mínima, não root, sem segredo | `06-Secure-DevOps-Cloud/docker/Dockerfile` |
| Varredura de vulnerabilidades da imagem e do IaC | Jobs `imagem` e `iac` (Trivy) |
| Segredo vazado barra o pipeline | Job `gitleaks` + `.gitleaks.toml` |
| SAST | Job `semgrep` + `.semgrep/acessacidade.yml` |
| Menor privilégio no CI | `permissions: contents: read`; `id-token: write` só no deploy; federated credential restrita ao environment `production` |
| Sem credencial de longa duração | OIDC (azure/login) em vez de client secret; ACR sem usuário admin |
| Superfície mínima | Uma porta (8000); sem SSH/RDP; monitoramento só em `127.0.0.1` |
| State protegido | Storage Account sem chave compartilhada, HTTPS only; `*.tfstate`/`*.tfvars` no `.gitignore` |
| Dados pessoais | `LGPD_MAPEAMENTO_DADOS_PESSOAIS.md` |

## 3. O que é da Azure

- Segurança física dos datacenters, rede de backbone, hardware e hipervisor.
- Patches do sistema operacional e do runtime dos hosts que executam o ACI.
- Isolamento entre containers de clientes diferentes (sandbox Hyper-V do ACI).
- Disponibilidade do Entra ID, do ACR e do ACI conforme os SLAs publicados.
- Criptografia em repouso do armazenamento da plataforma (imagens no ACR, state no Storage).

> Referência conceitual: documentação "Shared responsibility in the cloud" da Microsoft
> ([PREENCHER: link da documentação oficial consultado pela equipe]).
