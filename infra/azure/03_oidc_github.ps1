<#
=====================================================================
 AcessaCidade — 03. Identidade do GitHub Actions na Azure (OIDC, sem senha)
=====================================================================
 Classificação dos comandos deste script:
   az account show / az ad app list / az ad sp show ......... [SOMENTE LEITURA]
   az ad app create / az ad sp create ....................... [CRIA RECURSOS/CUSTO] (identidade; sem custo)
   az ad app federated-credential create .................... [CRIA RECURSOS/CUSTO] (confiança OIDC; sem custo)
   az role assignment create ................................ [CRIA RECURSOS/CUSTO] (permissões; sem custo)

 O que cria:
   - App Registration "gh-acessacidade-deploy" + Service Principal
   - Credencial federada: somente o environment "production" do SEU repositório
     (subject repo:<owner>/<repo>:environment:production) pode obter token.
     Nenhum segredo/senha é gerado.
   - Permissões (menor privilégio viável para o Terraform deste projeto):
       * Contributor na assinatura (cria RG, ACR, identidade, ACI)
       * Role Based Access Control Administrator na assinatura, com CONDIÇÃO:
         só pode criar/remover atribuições da função AcrPull
       * Storage Blob Data Contributor na storage account do state

 Observação: contas Azure for Students em tenants de universidades podem ser
 impedidas de criar App Registrations. Nesse caso veja a alternativa em
 06-Secure-DevOps-Cloud/docs/CI_CD_DEVSECOPS.md (seção "Plano B").

 Uso:
   .\infra\azure\03_oidc_github.ps1 -Repositorio "<owner>/<repo>" -StorageAccount "<storage do state>"
=====================================================================
#>
param(
    [Parameter(Mandatory = $true)][string]$Repositorio,
    [Parameter(Mandatory = $true)][string]$StorageAccount,
    [string]$StateResourceGroup = "rg-acessacidade-tfstate",
    [string]$NomeApp = "gh-acessacidade-deploy",
    [string]$Environment = "production"
)
$ErrorActionPreference = "Stop"

# [SOMENTE LEITURA]
$subId = az account show --query id --output tsv
$tenantId = az account show --query tenantId --output tsv

# [CRIA RECURSOS/CUSTO] App Registration + Service Principal
$appId = az ad app create --display-name $NomeApp --query appId --output tsv
az ad sp create --id $appId --output none
# [SOMENTE LEITURA]
$spObjectId = az ad sp show --id $appId --query id --output tsv

# [CRIA RECURSOS/CUSTO] credencial federada (OIDC) restrita ao environment do repositório
$fic = @{
    name        = "github-$Environment"
    issuer      = "https://token.actions.githubusercontent.com"
    subject     = "repo:${Repositorio}:environment:$Environment"
    description = "GitHub Actions - AcessaCidade - environment $Environment"
    audiences   = @("api://AzureADTokenExchange")
} | ConvertTo-Json -Compress
$ficFile = Join-Path ([IO.Path]::GetTempPath()) "acessacidade-fic.json"
Set-Content -Path $ficFile -Value $fic -Encoding utf8
az ad app federated-credential create --id $appId --parameters "@$ficFile" --output none
Remove-Item $ficFile -Force

# [CRIA RECURSOS/CUSTO] permissões
az role assignment create --assignee-object-id $spObjectId --assignee-principal-type ServicePrincipal `
    --role "Contributor" --scope "/subscriptions/$subId" --output none

# AcrPull = 7f951dda-4ed3-4680-a7ca-43fe172d538d (função interna da Azure)
$condicao = "((!(ActionMatches{'Microsoft.Authorization/roleAssignments/write'})) OR (@Request[Microsoft.Authorization/roleAssignments:RoleDefinitionId] ForAnyOfAnyValues:GuidEquals {7f951dda-4ed3-4680-a7ca-43fe172d538d})) AND ((!(ActionMatches{'Microsoft.Authorization/roleAssignments/delete'})) OR (@Resource[Microsoft.Authorization/roleAssignments:RoleDefinitionId] ForAnyOfAnyValues:GuidEquals {7f951dda-4ed3-4680-a7ca-43fe172d538d}))"
az role assignment create --assignee-object-id $spObjectId --assignee-principal-type ServicePrincipal `
    --role "Role Based Access Control Administrator" --scope "/subscriptions/$subId" `
    --condition $condicao --condition-version "2.0" --output none

$stScope = "/subscriptions/$subId/resourceGroups/$StateResourceGroup/providers/Microsoft.Storage/storageAccounts/$StorageAccount"
az role assignment create --assignee-object-id $spObjectId --assignee-principal-type ServicePrincipal `
    --role "Storage Blob Data Contributor" --scope $stScope --output none

Write-Host ""
Write-Host "Crie os GitHub Secrets (Settings > Secrets and variables > Actions > Secrets):"
Write-Host "  AZURE_CLIENT_ID       = $appId"
Write-Host "  AZURE_TENANT_ID       = $tenantId"
Write-Host "  AZURE_SUBSCRIPTION_ID = $subId"
Write-Host "(são identificadores, não senhas; ainda assim mantenha-os como Secrets)"
Write-Host "Crie o environment '$Environment' (Settings > Environments) e a Variable AZURE_DEPLOY_ENABLED=true quando quiser ativar o deploy."
