# Pipeline DevSecOps — GitHub Actions

Arquivo: `.github/workflows/ci-devsecops.yml` (o GitHub só executa workflows dessa pasta).

## 1. Quando roda

| Evento | Jobs executados |
|---|---|
| `push` em qualquer branch | testes, gitleaks, semgrep, iac, imagem |
| `pull_request` | testes, gitleaks, semgrep, iac, imagem |
| `workflow_dispatch` (botão "Run workflow") | os mesmos |
| `push` na `main` **e** Variable `AZURE_DEPLOY_ENABLED = true` | todos os anteriores **+ deploy** (só se todos passarem) |

Execuções da mesma branch se cancelam (exceto na `main`); o deploy tem fila própria (`deploy-production`, sem cancelamento).

## 2. Jobs

| Job | O que faz | Barra o pipeline quando |
|---|---|---|
| `testes` | `pip install -r 06-Secure-DevOps-Cloud/github-actions/requirements-ci.txt` + `python -m pytest` (todas as disciplinas; sem cadquery/playwright) | Algum teste falha |
| `gitleaks` | Gitleaks 8.21.2 (binário oficial com checksum) em **todo o histórico** (`fetch-depth: 0`), regras padrão + `.gitleaks.toml` | Qualquer segredo encontrado (inclui o token fictício `acd_demo_...` da demonstração) |
| `semgrep` | Semgrep 1.185.0: testa as regras da equipe e varre com `p/python`, `p/javascript`, `p/secrets`, `p/dockerfile` e `.semgrep/` | Achado de severidade ERROR/WARNING (`--error`) |
| `iac` | `terraform fmt -check`, `init -backend=false`, `validate`, `test` (provider simulado) + Trivy config no Dockerfile e no Terraform | Erro de formatação/validação, teste do Terraform, ou má configuração CRITICAL/HIGH |
| `imagem` | `docker build`; confere USER não root e ausência de variáveis sensíveis; Trivy image (vuln + secret); smoke test do container endurecido (`/health`, `/`, `/metrics`) | Imagem root, CVE CRITICAL/HIGH **com correção disponível** (`--ignore-unfixed`), segredo na imagem, ou `/health` sem resposta |
| `deploy` | OIDC → Terraform fase 1 (só na primeira vez) → push da **mesma imagem testada** (tag = SHA do commit) → Terraform fase 2 → smoke test na URL pública | Qualquer passo falha |

Relatórios (pytest JUnit, SARIF do Gitleaks com valores mascarados, SARIF do Semgrep) ficam em
**Actions → execução → Artifacts** por 14 dias.

## 3. GitHub Secrets e Variables (nomes exatos)

Settings → Secrets and variables → Actions. Prefira cadastrar no **environment `production`**
(Settings → Environments → production) para que só o job de deploy os veja.

| Tipo | Nome | Conteúdo | Origem |
|---|---|---|---|
| Secret | `AZURE_CLIENT_ID` | Application (client) ID do app registration do CI | saída de `infra/azure/03_oidc_github.ps1` |
| Secret | `AZURE_TENANT_ID` | Directory (tenant) ID | idem |
| Secret | `AZURE_SUBSCRIPTION_ID` | ID da assinatura | idem |
| Secret | `TFSTATE_RESOURCE_GROUP` | `rg-acessacidade-tfstate` | saída de `02_state_remoto.ps1` |
| Secret | `TFSTATE_STORAGE_ACCOUNT` | nome da storage account do state | idem |
| Secret | `TFSTATE_CONTAINER` | `tfstate` | idem |
| Secret | `TFSTATE_KEY` | `acessacidade.prod.tfstate` | idem |
| Secret | `ADMIN_TOKEN` | token longo aleatório (`python -c "import secrets; print(secrets.token_urlsafe(32))"`) | gerado pela equipe |
| Secret | `PIPELINE_TOKEN` | outro token aleatório | gerado pela equipe |
| Secret | `OPENROUTER_API_KEY` | chave do OpenRouter (opcional; vazio = modo alternativo) | painel do OpenRouter |
| Variable | `AZURE_DEPLOY_ENABLED` | `true` para ligar o deploy; qualquer outro valor desliga | equipe |
| Variable | `AZURE_LOCATION` | opcional (padrão `brazilsouth`) | equipe |
| Variable | `AZURE_NAME_SUFFIX` | opcional, 3–8 minúsculas/números (fixa nomes do ACR/DNS) | equipe |

> Alternativa sem OIDC (menos segura): secret `AZURE_CREDENTIALS` com o JSON do service principal
> (`az ad sp create-for-rbac --sdk-auth`) e `creds: ${{ secrets.AZURE_CREDENTIALS }}` no
> `azure/login`; o Terraform precisaria de `ARM_CLIENT_SECRET`. O projeto usa OIDC para não ter
> segredo de longa duração.

## 4. OIDC (federated credential) — passo a passo

1. Publique o repositório no GitHub e anote `<owner>/<repo>`.
2. Crie o state remoto (`.\infra\azure\02_state_remoto.ps1 -StorageAccount "<nome>"`).
3. Execute `.\infra\azure\03_oidc_github.ps1 -Repositorio "<owner>/<repo>" -StorageAccount "<nome>"`. Ele:
   - cria o app registration `gh-acessacidade-deploy` e o service principal;
   - cria a **federated credential** com `issuer = https://token.actions.githubusercontent.com`,
     `subject = repo:<owner>/<repo>:environment:production`, `audience = api://AzureADTokenExchange`;
   - atribui **Contributor** na assinatura (criar RG/ACR/ACI), **Role Based Access Control Administrator
     com condição** que só permite atribuir a função AcrPull (necessário para o `azurerm_role_assignment`),
     e **Storage Blob Data Contributor** na storage account do state;
   - imprime `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID`.
4. GitHub → Settings → Environments → **New environment** → `production` (opcional: required reviewers
   para aprovação manual do deploy).
5. Cadastre os secrets da tabela acima e a Variable `AZURE_DEPLOY_ENABLED = true`.
6. Faça um push na `main` (ou Actions → CI DevSecOps → Run workflow na `main`).
7. Acompanhe: o job `deploy` mostra a URL no resumo da execução e no environment `production`.

Portal (alternativa ao script): Microsoft Entra ID → App registrations → New registration →
Certificates & secrets → **Federated credentials** → Add credential → cenário "GitHub Actions
deploying Azure resources" → Organization/Repository → Entity type **Environment** → `production`.

## 5. Como reproduzir as ferramentas localmente (Windows)

```powershell
# Gitleaks (diretório de trabalho, valores mascarados)
gitleaks dir . --config .gitleaks.toml --redact
# Semgrep (no Windows, use Python 3.11 + pip install semgrep; ou WSL/Docker)
semgrep scan --config p/python --config p/javascript --config p/secrets --config p/dockerfile --config .semgrep/ --exclude .semgrep/tests --error
python 06-Secure-DevOps-Cloud\tools\testar_regras_semgrep.py
# Trivy
trivy config 06-Secure-DevOps-Cloud\docker
trivy config --skip-dirs 06-Secure-DevOps-Cloud\terraform\.terraform 06-Secure-DevOps-Cloud\terraform
trivy fs --scanners vuln requirements.txt
# Terraform
terraform -chdir=06-Secure-DevOps-Cloud\terraform init -backend=false
terraform -chdir=06-Secure-DevOps-Cloud\terraform validate
terraform -chdir=06-Secure-DevOps-Cloud\terraform test
```

Resultados reais da validação local: `evidencias/validacoes_locais.md`.

## 6. Execução barrada e corrigida

Roteiro seguro (token fictício, Semgrep e Trivy como alternativas): `DEMONSTRACAO_EXECUCAO_BARRADA.md`.
