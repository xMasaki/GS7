#!/usr/bin/env bash
# =====================================================================
#  AcessaCidade — 03. Identidade do GitHub Actions na Azure (OIDC, sem senha)
# =====================================================================
#  Classificação dos comandos deste script:
#    az account show / az ad sp show ......................... [SOMENTE LEITURA]
#    az ad app create / az ad sp create ....................... [CRIA RECURSOS/CUSTO] (identidade; sem custo)
#    az ad app federated-credential create .................... [CRIA RECURSOS/CUSTO] (confiança OIDC; sem custo)
#    az role assignment create ................................ [CRIA RECURSOS/CUSTO] (permissões; sem custo)
#  Detalhes e justificativa das permissões: ver 03_oidc_github.ps1 e
#  06-Secure-DevOps-Cloud/docs/CI_CD_DEVSECOPS.md
#  Uso:
#    REPOSITORIO="<owner>/<repo>" STORAGE_ACCOUNT="<storage do state>" ./infra/azure/03_oidc_github.sh
# =====================================================================
set -euo pipefail
: "${REPOSITORIO:?Defina REPOSITORIO=<owner>/<repo>}"
: "${STORAGE_ACCOUNT:?Defina STORAGE_ACCOUNT (storage account do state)}"
STATE_RESOURCE_GROUP="${STATE_RESOURCE_GROUP:-rg-acessacidade-tfstate}"
NOME_APP="${NOME_APP:-gh-acessacidade-deploy}"
ENVIRONMENT="${ENVIRONMENT:-production}"

# [SOMENTE LEITURA]
SUB_ID="$(az account show --query id --output tsv)"
TENANT_ID="$(az account show --query tenantId --output tsv)"

# [CRIA RECURSOS/CUSTO]
APP_ID="$(az ad app create --display-name "$NOME_APP" --query appId --output tsv)"
az ad sp create --id "$APP_ID" --output none
# [SOMENTE LEITURA]
SP_OBJECT_ID="$(az ad sp show --id "$APP_ID" --query id --output tsv)"

# [CRIA RECURSOS/CUSTO] credencial federada restrita ao environment do repositório
FIC_FILE="$(mktemp)"
cat > "$FIC_FILE" <<EOF
{"name": "github-${ENVIRONMENT}",
 "issuer": "https://token.actions.githubusercontent.com",
 "subject": "repo:${REPOSITORIO}:environment:${ENVIRONMENT}",
 "description": "GitHub Actions - AcessaCidade - environment ${ENVIRONMENT}",
 "audiences": ["api://AzureADTokenExchange"]}
EOF
az ad app federated-credential create --id "$APP_ID" --parameters "@${FIC_FILE}" --output none
rm -f "$FIC_FILE"

# [CRIA RECURSOS/CUSTO] permissões
az role assignment create --assignee-object-id "$SP_OBJECT_ID" --assignee-principal-type ServicePrincipal \
  --role "Contributor" --scope "/subscriptions/${SUB_ID}" --output none

# AcrPull = 7f951dda-4ed3-4680-a7ca-43fe172d538d (função interna da Azure)
CONDICAO="((!(ActionMatches{'Microsoft.Authorization/roleAssignments/write'})) OR (@Request[Microsoft.Authorization/roleAssignments:RoleDefinitionId] ForAnyOfAnyValues:GuidEquals {7f951dda-4ed3-4680-a7ca-43fe172d538d})) AND ((!(ActionMatches{'Microsoft.Authorization/roleAssignments/delete'})) OR (@Resource[Microsoft.Authorization/roleAssignments:RoleDefinitionId] ForAnyOfAnyValues:GuidEquals {7f951dda-4ed3-4680-a7ca-43fe172d538d}))"
az role assignment create --assignee-object-id "$SP_OBJECT_ID" --assignee-principal-type ServicePrincipal \
  --role "Role Based Access Control Administrator" --scope "/subscriptions/${SUB_ID}" \
  --condition "$CONDICAO" --condition-version "2.0" --output none

ST_SCOPE="/subscriptions/${SUB_ID}/resourceGroups/${STATE_RESOURCE_GROUP}/providers/Microsoft.Storage/storageAccounts/${STORAGE_ACCOUNT}"
az role assignment create --assignee-object-id "$SP_OBJECT_ID" --assignee-principal-type ServicePrincipal \
  --role "Storage Blob Data Contributor" --scope "$ST_SCOPE" --output none

cat <<EOF

Crie os GitHub Secrets (Settings > Secrets and variables > Actions > Secrets):
  AZURE_CLIENT_ID       = ${APP_ID}
  AZURE_TENANT_ID       = ${TENANT_ID}
  AZURE_SUBSCRIPTION_ID = ${SUB_ID}
Crie o environment '${ENVIRONMENT}' (Settings > Environments) e a Variable AZURE_DEPLOY_ENABLED=true quando quiser ativar o deploy.
EOF
