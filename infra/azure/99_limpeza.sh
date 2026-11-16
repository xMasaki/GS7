#!/usr/bin/env bash
# =====================================================================
#  AcessaCidade — 99. LIMPEZA DOS RECURSOS NA AZURE
# =====================================================================
#  [REMOVE RECURSOS — NÃO EXECUTAR ANTES DO FIM DA CORREÇÃO]
#  A URL pública do MVP precisa ficar no ar durante a correção.
#
#  Classificação dos comandos deste script:
#    az group list / az ad app list ........................... [SOMENTE LEITURA]
#    terraform destroy ........................................ [REMOVE RECURSOS — NÃO EXECUTAR ANTES DO FIM DA CORREÇÃO]
#    az group delete .......................................... [REMOVE RECURSOS — NÃO EXECUTAR ANTES DO FIM DA CORREÇÃO]
#    az ad app delete ......................................... [REMOVE RECURSOS — NÃO EXECUTAR ANTES DO FIM DA CORREÇÃO]
#  Uso:
#    RG_APP=<rg da aplicação> [RG_STATE=rg-acessacidade-tfstate] [APP_REGISTRATION=gh-acessacidade-deploy] ./infra/azure/99_limpeza.sh
# =====================================================================
set -euo pipefail
: "${RG_APP:?Defina RG_APP}"
RG_STATE="${RG_STATE:-}"
APP_REGISTRATION="${APP_REGISTRATION:-}"
TF_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../06-Secure-DevOps-Cloud/terraform" && pwd)"

echo "ATENÇÃO: este script APAGA recursos. A URL do MVP deixará de funcionar."
read -r -p "A correção da GS já terminou? Digite SIM para continuar: " OK
[ "$OK" = "SIM" ] || { echo "Cancelado."; exit 0; }

# [SOMENTE LEITURA]
az group list --query "[?starts_with(name, 'rg-acessacidade')].{Nome:name, Local:location}" --output table

read -r -p "Digite o nome do grupo da aplicação (${RG_APP}) para apagar: " C1
if [ "$C1" = "$RG_APP" ]; then
  if command -v terraform >/dev/null 2>&1 && [ -d "$TF_DIR/.terraform" ]; then
    # [REMOVE RECURSOS — NÃO EXECUTAR ANTES DO FIM DA CORREÇÃO]
    terraform -chdir="$TF_DIR" destroy -var deploy_container=true
  else
    # [REMOVE RECURSOS — NÃO EXECUTAR ANTES DO FIM DA CORREÇÃO]
    az group delete --name "$RG_APP" --yes
  fi
else
  echo "Nome não confere; grupo da aplicação mantido."
fi

if [ -n "$RG_STATE" ]; then
  read -r -p "Digite o nome do grupo do state (${RG_STATE}) para apagar: " C2
  # [REMOVE RECURSOS — NÃO EXECUTAR ANTES DO FIM DA CORREÇÃO]
  [ "$C2" = "$RG_STATE" ] && az group delete --name "$RG_STATE" --yes
fi

if [ -n "$APP_REGISTRATION" ]; then
  # [SOMENTE LEITURA]
  APP_ID="$(az ad app list --display-name "$APP_REGISTRATION" --query "[0].appId" --output tsv)"
  if [ -n "$APP_ID" ]; then
    read -r -p "Digite o nome da App Registration (${APP_REGISTRATION}) para apagar: " C3
    # [REMOVE RECURSOS — NÃO EXECUTAR ANTES DO FIM DA CORREÇÃO]
    [ "$C3" = "$APP_REGISTRATION" ] && az ad app delete --id "$APP_ID"
  fi
fi
echo "Confira no portal (Grupos de recursos e Gerenciamento de Custos) se nada ficou cobrando."
