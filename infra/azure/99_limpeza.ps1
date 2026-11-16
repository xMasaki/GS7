<#
=====================================================================
 AcessaCidade — 99. LIMPEZA DOS RECURSOS NA AZURE
=====================================================================
 [REMOVE RECURSOS — NÃO EXECUTAR ANTES DO FIM DA CORREÇÃO]

 A URL pública do MVP precisa ficar no ar durante a correção (até uma semana
 após 19/11). Só rode este script DEPOIS que a nota for publicada.

 Classificação dos comandos deste script:
   az group show / az group list ............................ [SOMENTE LEITURA]
   terraform destroy ........................................ [REMOVE RECURSOS — NÃO EXECUTAR ANTES DO FIM DA CORREÇÃO]
   az group delete .......................................... [REMOVE RECURSOS — NÃO EXECUTAR ANTES DO FIM DA CORREÇÃO]
   az ad app delete ......................................... [REMOVE RECURSOS — NÃO EXECUTAR ANTES DO FIM DA CORREÇÃO]

 Ordem recomendada:
   1) terraform destroy (remove ACI, ACR, identidade, Log Analytics e o RG da aplicação)
   2) (opcional) apagar o grupo do state (rg-acessacidade-tfstate)
   3) (opcional) apagar a App Registration do GitHub (gh-acessacidade-deploy)
 O script pede que você DIGITE o nome de cada grupo para confirmar.

 Uso:
   .\infra\azure\99_limpeza.ps1 -ResourceGroupApp "<rg da aplicação>" [-ResourceGroupState rg-acessacidade-tfstate] [-AppRegistration gh-acessacidade-deploy]
=====================================================================
#>
param(
    [Parameter(Mandatory = $true)][string]$ResourceGroupApp,
    [string]$ResourceGroupState = "",
    [string]$AppRegistration = ""
)
$ErrorActionPreference = "Stop"

Write-Warning "ESTE SCRIPT APAGA RECURSOS. A URL do MVP deixará de funcionar."
$ok = Read-Host "A correção da GS já terminou? Digite SIM para continuar"
if ($ok -ne "SIM") { Write-Host "Cancelado."; exit 0 }

# [SOMENTE LEITURA]
az group list --query "[?starts_with(name, 'rg-acessacidade')].{Nome:name, Local:location}" --output table

$confirma = Read-Host "Digite o nome do grupo da aplicação ($ResourceGroupApp) para apagar"
if ($confirma -eq $ResourceGroupApp) {
    $tfDir = Join-Path $PSScriptRoot "..\..\06-Secure-DevOps-Cloud\terraform"
    if ((Get-Command terraform -ErrorAction SilentlyContinue) -and (Test-Path (Join-Path $tfDir ".terraform"))) {
        # [REMOVE RECURSOS — NÃO EXECUTAR ANTES DO FIM DA CORREÇÃO]
        terraform -chdir="$tfDir" destroy -var deploy_container=true
    } else {
        # [REMOVE RECURSOS — NÃO EXECUTAR ANTES DO FIM DA CORREÇÃO]
        az group delete --name $ResourceGroupApp --yes
    }
} else {
    Write-Host "Nome não confere; grupo da aplicação mantido."
}

if ($ResourceGroupState) {
    $c2 = Read-Host "Digite o nome do grupo do state ($ResourceGroupState) para apagar (o histórico do Terraform será perdido)"
    if ($c2 -eq $ResourceGroupState) {
        # [REMOVE RECURSOS — NÃO EXECUTAR ANTES DO FIM DA CORREÇÃO]
        az group delete --name $ResourceGroupState --yes
    }
}

if ($AppRegistration) {
    # [SOMENTE LEITURA]
    $appId = az ad app list --display-name $AppRegistration --query "[0].appId" --output tsv
    if ($appId) {
        $c3 = Read-Host "Digite o nome da App Registration ($AppRegistration) para apagar"
        if ($c3 -eq $AppRegistration) {
            # [REMOVE RECURSOS — NÃO EXECUTAR ANTES DO FIM DA CORREÇÃO]
            az ad app delete --id $appId
        }
    }
}
Write-Host "Confira no portal (Grupos de recursos e Custos) se nada ficou cobrando."
