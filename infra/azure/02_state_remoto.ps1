<#
=====================================================================
 AcessaCidade — 02. State remoto do Terraform (Azure Storage)
=====================================================================
 Classificação dos comandos deste script:
   az account show / az ad signed-in-user show / az storage account show ... [SOMENTE LEITURA]
   az group create ........................................ [CRIA RECURSOS/CUSTO] (grupo: sem custo)
   az storage account create ............................... [CRIA RECURSOS/CUSTO] (centavos/mês: poucos KB de state)
   az storage container create ............................. [CRIA RECURSOS/CUSTO]
   az role assignment create ............................... [CRIA RECURSOS/CUSTO] (permissão; sem custo)

 Por que: o state NÃO pode ficar no repositório. O state remoto permite que o
 GitHub Actions e a equipe usem o mesmo estado, com bloqueio (lease) do blob.
 O grupo do state é SEPARADO do grupo da aplicação: a limpeza da aplicação
 (terraform destroy) não apaga o state.

 Uso:
   .\infra\azure\02_state_remoto.ps1 -StorageAccount "acessacidadetf<sufixo>" [-Location brazilsouth]
 (nome da storage account: 3-24 caracteres, minúsculas e números, único na Azure)
=====================================================================
#>
param(
    [Parameter(Mandatory = $true)][string]$StorageAccount,
    [string]$ResourceGroup = "rg-acessacidade-tfstate",
    [string]$Container = "tfstate",
    [string]$Location = "brazilsouth"
)
$ErrorActionPreference = "Stop"

# [SOMENTE LEITURA]
$subId = az account show --query id --output tsv
$userId = az ad signed-in-user show --query id --output tsv

# [CRIA RECURSOS/CUSTO]
az group create --name $ResourceGroup --location $Location --tags projeto=AcessaCidade finalidade=terraform-state --output none

# [CRIA RECURSOS/CUSTO] conta de armazenamento endurecida (TLS 1.2, sem acesso público a blobs, sem chave compartilhada)
az storage account create --name $StorageAccount --resource-group $ResourceGroup --location $Location `
    --sku Standard_LRS --kind StorageV2 --min-tls-version TLS1_2 --allow-blob-public-access false `
    --allow-shared-key-access false --https-only true --output none

# [CRIA RECURSOS/CUSTO] permissão de dados para você (Terraform usa Entra ID: use_azuread_auth=true)
$scope = "/subscriptions/$subId/resourceGroups/$ResourceGroup/providers/Microsoft.Storage/storageAccounts/$StorageAccount"
az role assignment create --assignee-object-id $userId --assignee-principal-type User `
    --role "Storage Blob Data Contributor" --scope $scope --output none

Write-Host "Aguardando 60 s para a permissão propagar..."
Start-Sleep -Seconds 60

# [CRIA RECURSOS/CUSTO]
az storage container create --name $Container --account-name $StorageAccount --auth-mode login --output none

# [SOMENTE LEITURA]
az storage account show --name $StorageAccount --resource-group $ResourceGroup --query "{Nome:name, TLS:minimumTlsVersion, BlobPublico:allowBlobPublicAccess}" --output table

Write-Host ""
Write-Host "Crie os GitHub Secrets (Settings > Secrets and variables > Actions):"
Write-Host "  TFSTATE_RESOURCE_GROUP  = $ResourceGroup"
Write-Host "  TFSTATE_STORAGE_ACCOUNT = $StorageAccount"
Write-Host "  TFSTATE_CONTAINER       = $Container"
Write-Host "  TFSTATE_KEY             = acessacidade.prod.tfstate"
Write-Host "E, para uso local, 06-Secure-DevOps-Cloud/terraform/backend.hcl (fora do Git) a partir de backend.hcl.example."
