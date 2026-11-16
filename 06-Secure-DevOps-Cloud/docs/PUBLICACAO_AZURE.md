# Publicação do AcessaCidade na Azure — passo a passo

> Caminho oficial: **Terraform** (`06-Secure-DevOps-Cloud/terraform`) executado pelo **GitHub Actions**.
> Este guia mostra também a execução manual (primeira vez ou contingência).
> Cada comando está marcado como **[SOMENTE LEITURA]**, **[CRIA RECURSOS/CUSTO]** ou
> **[REMOVE RECURSOS — NÃO EXECUTAR ANTES DO FIM DA CORREÇÃO]**.
> Nenhum valor abaixo é real: substitua os marcadores `<...>` e [PREENCHER].

## 0. Pré-requisitos (na máquina da equipe)

| Ferramenta | Versão usada na validação | Download |
|---|---|---|
| Azure CLI | 2.60 ou superior | https://learn.microsoft.com/cli/azure/install-azure-cli |
| Terraform | 1.9.8 (mínimo 1.6) | https://developer.hashicorp.com/terraform/install |
| Docker Desktop (opcional — dá para usar `az acr build` sem Docker) | 4.x com Compose ≥ 2.24 | https://www.docker.com/products/docker-desktop/ |
| Git + conta GitHub | — | https://git-scm.com |

Abra o **PowerShell** na raiz do repositório (pasta que contém `docker-compose.yml`).

## 1. Conta, assinatura e providers

```powershell
az login                                        # [SOMENTE LEITURA] abre o navegador
az account list --output table                  # [SOMENTE LEITURA]
az account set --subscription "<id da assinatura>"   # [SOMENTE LEITURA]
.\infra\azure\01_login_e_providers.ps1 -SubscriptionId "<id da assinatura>"
```

O script registra (sem custo) os providers `Microsoft.ContainerInstance`, `Microsoft.ContainerRegistry`,
`Microsoft.ManagedIdentity` e `Microsoft.OperationalInsights` e mostra o estado de cada um
(`Registered` = pronto).

> Região: o padrão é `brazilsouth` (latência menor para o público). Se a assinatura de estudante
> recusar a região ou o custo for maior que o crédito, use `eastus` (variável `location`).

## 2. State remoto do Terraform (uma vez)

```powershell
.\infra\azure\02_state_remoto.ps1 -StorageAccount "acessacidadetf<sufixo>" -Location brazilsouth   # [CRIA RECURSOS/CUSTO] centavos/mês
```

Cria `rg-acessacidade-tfstate`, a Storage Account (sem chave compartilhada, HTTPS only) e o
container `tfstate`, e imprime os valores dos secrets `TFSTATE_*`. Depois:

```powershell
Copy-Item 06-Secure-DevOps-Cloud\terraform\backend.hcl.example 06-Secure-DevOps-Cloud\terraform\backend.hcl
# edite backend.hcl com o nome da storage account (backend.hcl está no .gitignore)
```

## 3. Terraform — fase 1 (Resource Group, ACR, identidade)

```powershell
cd 06-Secure-DevOps-Cloud\terraform
$env:ARM_SUBSCRIPTION_ID = "<id da assinatura>"
terraform init -backend-config=backend.hcl            # [SOMENTE LEITURA] baixa providers e conecta ao state
terraform fmt -check -recursive; terraform validate   # [SOMENTE LEITURA]
terraform plan -var="deploy_container=false"          # [SOMENTE LEITURA] mostra o que será criado
terraform apply -var="deploy_container=false"         # [CRIA RECURSOS/CUSTO] RG + ACR Basic + identidade + AcrPull
terraform output                                      # [SOMENTE LEITURA] acr_name, acr_login_server...
```

Opcional: copie `terraform.tfvars.example` para `terraform.tfvars` (fora do Git) para fixar
`location`, `name_suffix` e tags. **Nunca** escreva tokens no tfvars — use variáveis de ambiente
`TF_VAR_admin_token`, `TF_VAR_pipeline_token`, `TF_VAR_openrouter_api_key`.

## 4. Enviar a imagem para o ACR

Sem Docker local (build na nuvem, ACR Tasks):

```powershell
$acr = terraform output -raw acr_name
cd ..\..
.\infra\azure\04_build_push_imagem.ps1 -AcrName $acr -Tag "<tag, ex.: sha curto do commit>"           # [CRIA RECURSOS/CUSTO]
```

Com Docker local: acrescente `-Modo Docker` (faz `docker build`, `az acr login` e `docker push`).
Se a assinatura bloquear ACR Tasks (`TasksOperationsNotAllowed`), use o modo Docker ou deixe o CI fazer o push.

## 5. Terraform — fase 2 (Azure Container Instances)

```powershell
cd 06-Secure-DevOps-Cloud\terraform
$env:TF_VAR_admin_token    = (python -c "import secrets; print(secrets.token_urlsafe(32))")
$env:TF_VAR_pipeline_token = (python -c "import secrets; print(secrets.token_urlsafe(32))")
$env:TF_VAR_openrouter_api_key = ""        # opcional: sem chave o assistente usa o modo alternativo
terraform apply -var="deploy_container=true" -var="image_tag=<mesma tag do passo 4>"   # [CRIA RECURSOS/CUSTO]
terraform output app_url      # http://<dns>.<região>.azurecontainer.io:8000
terraform output health_url
```

Guarde os tokens gerados em um cofre de senhas da equipe e cadastre os mesmos valores nos GitHub
Secrets (`ADMIN_TOKEN`, `PIPELINE_TOKEN`), senão o próximo deploy do CI troca os valores.

## 6. Testar a URL pública

```powershell
$url = terraform output -raw app_url
Invoke-RestMethod "$url/health"            # [SOMENTE LEITURA] espera status "ok"
Start-Process $url                         # abre a SPA no navegador
(Invoke-WebRequest "$url/metrics").Content | Select-String acessacidade_http_requests_total
```

Porta: **somente 8000/TCP** está exposta. Não existe SSH/RDP. Não use `https://` (o ACI não tem
TLS nativo — limitação documentada em `ARQUITETURA_CLOUD.md`).

## 7. Logs e diagnóstico

```powershell
.\infra\azure\06_status_logs.ps1 -ResourceGroup "rg-acessacidade-prod" -AciName "aci-acessacidade-prod"            # [SOMENTE LEITURA]
.\infra\azure\06_status_logs.ps1 -ResourceGroup "rg-acessacidade-prod" -AciName "aci-acessacidade-prod" -Acompanhar  # az container attach
az container show -g rg-acessacidade-prod -n aci-acessacidade-prod --query "{estado:instanceView.state,fqdn:ipAddress.fqdn,portas:ipAddress.ports}" -o json   # [SOMENTE LEITURA]
```

Problemas comuns:

| Sintoma | Causa provável | Ação |
|---|---|---|
| `InaccessibleImage` / falha no pull | Imagem/tag inexistente no ACR ou AcrPull ainda propagando | Conferir `az acr repository show-tags`; aguardar 1–2 min e reaplicar a fase 2 |
| Container reiniciando | `/health` falhando (probe) ou erro na inicialização | `az container logs`; testar a mesma imagem localmente com `docker compose up` |
| `DnsNameLabelAlreadyInUse` | Rótulo DNS já usado na região | Definir `dns_name_label` ou `name_suffix` diferente |
| `MissingSubscriptionRegistration` | Provider não registrado | Rodar o passo 1 novamente |

## 8. Publicação automática (CI/CD)

Depois de validar manualmente, configure o deploy automático: `CI_CD_DEVSECOPS.md`
(OIDC com `infra/azure/03_oidc_github.ps1`, GitHub Secrets/Variables e environment `production`).
O workflow usa o **mesmo state remoto**, então manual e CI não divergem.

## 9. Alternativa sem Terraform (YAML do ACI)

`infra/aci-deployment.template.yaml` + `infra/azure/05_deploy_aci_yaml.ps1` (reproduz o exercício
Calango TI com `az container create --file`). Não misture com o Terraform no mesmo Resource Group
(o Terraform recriaria o container). Detalhes em `infra/README.md`.

## 10. Limpeza — SOMENTE depois da correção e da nota

```powershell
# [REMOVE RECURSOS — NÃO EXECUTAR ANTES DO FIM DA CORREÇÃO]
cd 06-Secure-DevOps-Cloud\terraform
terraform destroy -var="deploy_container=true" -var="image_tag=<tag>"
cd ..\..
.\infra\azure\99_limpeza.ps1 -ResourceGroupApp "rg-acessacidade-prod" -ResourceGroupState rg-acessacidade-tfstate -AppRegistration gh-acessacidade-deploy
```

Depois: desative `AZURE_DEPLOY_ENABLED` (Variable do GitHub) para o próximo push não recriar tudo
e confira em Cost Management que não há mais cobrança.
