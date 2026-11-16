#!/usr/bin/env bash
# =====================================================================
#  AcessaCidade — 01. Login, assinatura e registro de Resource Providers
# =====================================================================
#  Classificação dos comandos deste script:
#    az version / az account list / az account show / az provider show ... [SOMENTE LEITURA]
#    az login ........................................ [SOMENTE LEITURA] (autentica o CLI; não cria nada)
#    az account set .................................. [SOMENTE LEITURA] (muda só a assinatura ativa no CLI local)
#    az provider register ............................ [CRIA RECURSOS/CUSTO] — habilita o namespace na
#                                                      assinatura; NÃO tem custo direto e é idempotente
#  Uso:
#    SUBSCRIPTION_ID="<id da assinatura>" ./infra/azure/01_login_e_providers.sh
# =====================================================================
set -euo pipefail
SUBSCRIPTION_ID="${SUBSCRIPTION_ID:-${ARM_SUBSCRIPTION_ID:-}}"

# [SOMENTE LEITURA]
az version --output table
# [SOMENTE LEITURA] login interativo (use --use-device-code em máquinas sem navegador)
az login --output none
# [SOMENTE LEITURA]
az account list --query "[].{Nome:name, Id:id, Padrao:isDefault, Estado:state}" --output table

if [ -n "$SUBSCRIPTION_ID" ]; then
  # [SOMENTE LEITURA] seleciona a assinatura no CLI local
  az account set --subscription "$SUBSCRIPTION_ID"
fi
# [SOMENTE LEITURA]
az account show --query "{Assinatura:name, Id:id, Tenant:tenantId}" --output table

NAMESPACES="Microsoft.ContainerInstance Microsoft.ContainerRegistry Microsoft.ManagedIdentity Microsoft.OperationalInsights Microsoft.Storage"
for ns in $NAMESPACES; do
  # [CRIA RECURSOS/CUSTO] registra o provider (sem custo direto; idempotente)
  az provider register --namespace "$ns" --output none
done

# [SOMENTE LEITURA] aguarde todos ficarem "Registered"
for ns in $NAMESPACES; do
  az provider show --namespace "$ns" --query "{Namespace:namespace, Estado:registrationState}" --output tsv
done
echo "Se algum estiver 'Registering', aguarde 1-3 minutos e rode novamente apenas o laço de 'az provider show'."
