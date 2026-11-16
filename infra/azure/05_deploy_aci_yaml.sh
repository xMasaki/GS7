#!/usr/bin/env bash
# =====================================================================
#  AcessaCidade — 05. (ALTERNATIVA ao Terraform fase 2) Deploy do ACI via template YAML
# =====================================================================
#  Classificação dos comandos deste script:
#    python render_aci_template.py ............................ [SOMENTE LEITURA] (arquivo local temporário)
#    az acr show / az identity show / az container show ....... [SOMENTE LEITURA]
#    az container create --file ............................... [CRIA RECURSOS/CUSTO] (cobrança por segundo)
#  O caminho oficial é o Terraform; não use os dois para o MESMO container group.
#  Segredos: exporte ADMIN_TOKEN, PIPELINE_TOKEN e (opcional) OPENROUTER_API_KEY na sessão antes de rodar.
#  Uso:
#    RESOURCE_GROUP=<rg> ACR_NAME=<acr> IDENTITY_NAME=<id> TAG=<tag> DNS_LABEL=<rótulo> ./infra/azure/05_deploy_aci_yaml.sh
# =====================================================================
set -euo pipefail
: "${RESOURCE_GROUP:?}" "${ACR_NAME:?}" "${IDENTITY_NAME:?}" "${TAG:?}" "${DNS_LABEL:?}"
ACI_NAME="${ACI_NAME:-aci-acessacidade-prod}"
RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
if [ -x "$RAIZ/.venv/bin/python" ]; then PY="$RAIZ/.venv/bin/python"; elif [ -x "$RAIZ/.venv/Scripts/python.exe" ]; then PY="$RAIZ/.venv/Scripts/python.exe"; else PY="python3"; fi

# [SOMENTE LEITURA]
export ACR_LOGIN_SERVER="$(az acr show --name "$ACR_NAME" --query loginServer --output tsv)"
export IDENTITY_ID="$(az identity show --name "$IDENTITY_NAME" --resource-group "$RESOURCE_GROUP" --query id --output tsv)"
export AZ_LOCATION="${LOCATION:-brazilsouth}" ACI_NAME IMAGE_NAME="${IMAGE_NAME:-acessacidade}" IMAGE_TAG="$TAG" DNS_LABEL

SAIDA="$(mktemp -t aci-acessacidade-XXXXXX.yaml)"
trap 'rm -f "$SAIDA"' EXIT

# [SOMENTE LEITURA] renderiza fora do repositório
"$PY" "$RAIZ/infra/azure/render_aci_template.py" --saida "$SAIDA"

# [CRIA RECURSOS/CUSTO]
az container create --resource-group "$RESOURCE_GROUP" --file "$SAIDA" --output none

# [SOMENTE LEITURA]
FQDN="$(az container show --resource-group "$RESOURCE_GROUP" --name "$ACI_NAME" --query ipAddress.fqdn --output tsv)"
echo "URL pública: http://${FQDN}:8000   Health: http://${FQDN}:8000/health"
