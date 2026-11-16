#!/usr/bin/env bash
# =====================================================================
#  AcessaCidade — 06. Status, logs e diagnóstico do container (ACI)
# =====================================================================
#  Classificação dos comandos deste script:
#    az container show / az container logs / az container attach ... [SOMENTE LEITURA]
#    curl /health ................................................... [SOMENTE LEITURA]
#  Diagnóstico interativo (não existe porta SSH/administrativa aberta):
#    az container exec --resource-group <rg> --name <aci> --exec-command "/bin/sh"   [SOMENTE LEITURA*]
#  Uso:
#    RESOURCE_GROUP=<rg> ACI_NAME=<aci> [ACOMPANHAR=1] ./infra/azure/06_status_logs.sh
# =====================================================================
set -euo pipefail
: "${RESOURCE_GROUP:?Defina RESOURCE_GROUP}"
ACI_NAME="${ACI_NAME:-aci-acessacidade-prod}"

# [SOMENTE LEITURA]
az container show --resource-group "$RESOURCE_GROUP" --name "$ACI_NAME" \
  --query "{Estado:instanceView.state, FQDN:ipAddress.fqdn, IP:ipAddress.ip, Portas:ipAddress.ports[].port, Reinicios:containers[0].instanceView.restartCount, Imagem:containers[0].image}" \
  --output table
# [SOMENTE LEITURA]
az container show --resource-group "$RESOURCE_GROUP" --name "$ACI_NAME" \
  --query "containers[0].instanceView.events[-10:].{Hora:lastTimestamp, Tipo:type, Mensagem:message}" --output table
# [SOMENTE LEITURA]
az container logs --resource-group "$RESOURCE_GROUP" --name "$ACI_NAME"

# [SOMENTE LEITURA]
FQDN="$(az container show --resource-group "$RESOURCE_GROUP" --name "$ACI_NAME" --query ipAddress.fqdn --output tsv)"
curl -fsS --max-time 15 "http://${FQDN}:8000/health" && echo || echo "Health check falhou"

if [ "${ACOMPANHAR:-0}" = "1" ]; then
  # [SOMENTE LEITURA]
  az container attach --resource-group "$RESOURCE_GROUP" --name "$ACI_NAME"
fi
