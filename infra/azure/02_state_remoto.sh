#!/usr/bin/env bash
# =====================================================================
#  AcessaCidade — 02. State remoto do Terraform (Azure Storage)
# =====================================================================
#  Classificação dos comandos deste script:
#    az account show / az ad signed-in-user show / az storage account show ... [SOMENTE LEITURA]
#    az group create ........................................ [CRIA RECURSOS/CUSTO] (grupo: sem custo)
#    az storage account create ............................... [CRIA RECURSOS/CUSTO] (centavos/mês)
#    az storage container create ............................. [CRIA RECURSOS/CUSTO]
#    az role assignment create ............................... [CRIA RECURSOS/CUSTO] (permissão; sem custo)
#  Uso:
#    STORAGE_ACCOUNT="acessacidadetf<sufixo>" ./infra/azure/02_state_remoto.sh
# =====================================================================
set -euo pipefail
: "${STORAGE_ACCOUNT:?Defina STORAGE_ACCOUNT (3-24 minúsculas/números, único na Azure)}"
RESOURCE_GROUP="${RESOURCE_GROUP:-rg-acessacidade-tfstate}"
CONTAINER="${CONTAINER:-tfstate}"
LOCATION="${LOCATION:-brazilsouth}"

# [SOMENTE LEITURA]
SUB_ID="$(az account show --query id --output tsv)"
USER_ID="$(az ad signed-in-user show --query id --output tsv)"

# [CRIA RECURSOS/CUSTO]
az group create --name "$RESOURCE_GROUP" --location "$LOCATION" --tags projeto=AcessaCidade finalidade=terraform-state --output none

# [CRIA RECURSOS/CUSTO]
az storage account create --name "$STORAGE_ACCOUNT" --resource-group "$RESOURCE_GROUP" --location "$LOCATION" \
  --sku Standard_LRS --kind StorageV2 --min-tls-version TLS1_2 --allow-blob-public-access false \
  --allow-shared-key-access false --https-only true --output none

# [CRIA RECURSOS/CUSTO] permissão de dados (Terraform usa Entra ID: use_azuread_auth=true)
SCOPE="/subscriptions/${SUB_ID}/resourceGroups/${RESOURCE_GROUP}/providers/Microsoft.Storage/storageAccounts/${STORAGE_ACCOUNT}"
az role assignment create --assignee-object-id "$USER_ID" --assignee-principal-type User \
  --role "Storage Blob Data Contributor" --scope "$SCOPE" --output none

echo "Aguardando 60 s para a permissão propagar..."
sleep 60

# [CRIA RECURSOS/CUSTO]
az storage container create --name "$CONTAINER" --account-name "$STORAGE_ACCOUNT" --auth-mode login --output none

# [SOMENTE LEITURA]
az storage account show --name "$STORAGE_ACCOUNT" --resource-group "$RESOURCE_GROUP" \
  --query "{Nome:name, TLS:minimumTlsVersion, BlobPublico:allowBlobPublicAccess}" --output table

cat <<EOF

Crie os GitHub Secrets (Settings > Secrets and variables > Actions):
  TFSTATE_RESOURCE_GROUP  = ${RESOURCE_GROUP}
  TFSTATE_STORAGE_ACCOUNT = ${STORAGE_ACCOUNT}
  TFSTATE_CONTAINER       = ${CONTAINER}
  TFSTATE_KEY             = acessacidade.prod.tfstate
E, para uso local, 06-Secure-DevOps-Cloud/terraform/backend.hcl (fora do Git) a partir de backend.hcl.example.
EOF
