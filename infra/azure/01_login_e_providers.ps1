<#
=====================================================================
 AcessaCidade — 01. Login, assinatura e registro de Resource Providers
=====================================================================
 Classificação dos comandos deste script:
   az version / az account list / az account show / az provider show ... [SOMENTE LEITURA]
   az login ........................................ [SOMENTE LEITURA] (autentica o CLI; não cria nada)
   az account set .................................. [SOMENTE LEITURA] (muda só a assinatura ativa no CLI local)
   az provider register ............................ [CRIA RECURSOS/CUSTO] — habilita o namespace na
                                                     assinatura; NÃO tem custo direto e é idempotente
 Pré-requisito: Azure CLI instalada (https://learn.microsoft.com/cli/azure/install-azure-cli)
 Uso:
   .\infra\azure\01_login_e_providers.ps1 -SubscriptionId "<id da assinatura>"
=====================================================================
#>
param(
    [string]$SubscriptionId = $env:ARM_SUBSCRIPTION_ID
)
$ErrorActionPreference = "Stop"

# [SOMENTE LEITURA] versão do CLI
az version --output table

# [SOMENTE LEITURA] login interativo (abre o navegador)
az login --output none

# [SOMENTE LEITURA] lista as assinaturas disponíveis (ex.: "Azure for Students")
az account list --query "[].{Nome:name, Id:id, Padrao:isDefault, Estado:state}" --output table

if ($SubscriptionId) {
    # [SOMENTE LEITURA] seleciona a assinatura no CLI local
    az account set --subscription $SubscriptionId
}
# [SOMENTE LEITURA] confirma a assinatura ativa
az account show --query "{Assinatura:name, Id:id, Tenant:tenantId}" --output table

$namespaces = @(
    "Microsoft.ContainerInstance",
    "Microsoft.ContainerRegistry",
    "Microsoft.ManagedIdentity",
    "Microsoft.OperationalInsights",
    "Microsoft.Storage"
)
foreach ($ns in $namespaces) {
    # [CRIA RECURSOS/CUSTO] registra o provider (sem custo direto; idempotente)
    az provider register --namespace $ns --output none
}

# [SOMENTE LEITURA] estado do registro (aguarde todos ficarem "Registered")
foreach ($ns in $namespaces) {
    az provider show --namespace $ns --query "{Namespace:namespace, Estado:registrationState}" --output tsv
}
Write-Host "Se algum estiver 'Registering', aguarde 1-3 minutos e rode novamente apenas o bloco de 'az provider show'."
