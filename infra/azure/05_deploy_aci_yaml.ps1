<#
=====================================================================
 AcessaCidade — 05. (ALTERNATIVA ao Terraform fase 2) Deploy do ACI via template YAML
=====================================================================
 Classificação dos comandos deste script:
   python render_aci_template.py ............................ [SOMENTE LEITURA] (gera arquivo local temporário)
   az acr show / az identity show / az container show ....... [SOMENTE LEITURA]
   az container create --file ............................... [CRIA RECURSOS/CUSTO] (ACI cobra por segundo
                                                              de vCPU e de GB de memória enquanto existir)

 ATENÇÃO: o caminho oficial é o Terraform (06-Secure-DevOps-Cloud/terraform).
 Não use os dois para o MESMO container group (o Terraform tentaria recriar).
 Use este script só se precisar publicar sem Terraform (ex.: reproduzir o exercício).

 Segredos: defina na sessão ANTES de rodar (não ficam em arquivo do repositório):
   $env:ADMIN_TOKEN = "<gere com: python -c 'import secrets; print(secrets.token_urlsafe(32))'>"
   $env:PIPELINE_TOKEN = "<idem>"
   $env:OPENROUTER_API_KEY = "<opcional>"
 Uso:
   .\infra\azure\05_deploy_aci_yaml.ps1 -ResourceGroup "<rg>" -AcrName "<acr>" -IdentityName "<identidade>" `
       -Tag "<tag>" -DnsLabel "<rótulo dns único>"
=====================================================================
#>
param(
    [Parameter(Mandatory = $true)][string]$ResourceGroup,
    [Parameter(Mandatory = $true)][string]$AcrName,
    [Parameter(Mandatory = $true)][string]$IdentityName,
    [Parameter(Mandatory = $true)][string]$Tag,
    [Parameter(Mandatory = $true)][string]$DnsLabel,
    [string]$AciName = "aci-acessacidade-prod",
    [string]$Location = "brazilsouth",
    [string]$ImageName = "acessacidade"
)
$ErrorActionPreference = "Stop"
$Raiz = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$Python = Join-Path $Raiz ".venv\Scripts\python.exe"
if (-not (Test-Path $Python)) { $Python = "python" }

# [SOMENTE LEITURA]
$env:ACR_LOGIN_SERVER = az acr show --name $AcrName --query loginServer --output tsv
$env:IDENTITY_ID = az identity show --name $IdentityName --resource-group $ResourceGroup --query id --output tsv
$env:AZ_LOCATION = $Location
$env:ACI_NAME = $AciName
$env:IMAGE_NAME = $ImageName
$env:IMAGE_TAG = $Tag
$env:DNS_LABEL = $DnsLabel

$saida = Join-Path ([IO.Path]::GetTempPath()) ("aci-acessacidade-" + [guid]::NewGuid().ToString("N") + ".yaml")
try {
    # [SOMENTE LEITURA] renderiza fora do repositório
    & $Python (Join-Path $Raiz "infra\azure\render_aci_template.py") --saida $saida
    if ($LASTEXITCODE -ne 0) { throw "Falha ao renderizar o template." }

    # [CRIA RECURSOS/CUSTO]
    az container create --resource-group $ResourceGroup --file $saida --output none
} finally {
    if (Test-Path $saida) { Remove-Item $saida -Force }
}

# [SOMENTE LEITURA]
$fqdn = az container show --resource-group $ResourceGroup --name $AciName --query ipAddress.fqdn --output tsv
Write-Host "URL pública: http://${fqdn}:8000   Health: http://${fqdn}:8000/health"
