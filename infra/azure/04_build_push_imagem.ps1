<#
=====================================================================
 AcessaCidade — 04. Build e push da imagem para o Azure Container Registry
=====================================================================
 Classificação dos comandos deste script:
   az acr show / az acr repository show-tags ................ [SOMENTE LEITURA]
   az acr login ............................................. [SOMENTE LEITURA] (token temporário no Docker local)
   az acr build ............................................. [CRIA RECURSOS/CUSTO] (ACR Tasks: build na nuvem,
                                                              cobrado por tempo de build; NÃO exige Docker local)
   docker build / docker push ............................... [CRIA RECURSOS/CUSTO] (armazenamento no ACR)

 Pré-requisito: fase 1 do Terraform aplicada (ACR existe). Nome do ACR:
   terraform -chdir=06-Secure-DevOps-Cloud/terraform output -raw acr_name

 Modos:
   -Modo AcrBuild  (padrão) — sem Docker local: envia o contexto (respeitando
                    .dockerignore) e o ACR constrói a imagem.
                    Algumas assinaturas gratuitas/estudantis bloqueiam ACR Tasks
                    ("TasksOperationsNotAllowed"); nesse caso use -Modo Docker.
   -Modo Docker    — build local com Docker Desktop e push.

 Uso (na raiz do repositório):
   .\infra\azure\04_build_push_imagem.ps1 -AcrName "<acr>" -Tag "<tag>" [-Modo Docker]
=====================================================================
#>
param(
    [Parameter(Mandatory = $true)][string]$AcrName,
    [string]$Tag = "",
    [ValidateSet("AcrBuild", "Docker")][string]$Modo = "AcrBuild",
    [string]$ImageName = "acessacidade"
)
$ErrorActionPreference = "Stop"
$Raiz = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Set-Location $Raiz

if (-not $Tag) {
    $Tag = (git rev-parse --short=12 HEAD 2>$null)
    if (-not $Tag) { $Tag = "manual-" + (Get-Date -Format "yyyyMMddHHmm") }
}
$Dockerfile = "06-Secure-DevOps-Cloud/docker/Dockerfile"

# [SOMENTE LEITURA]
$loginServer = az acr show --name $AcrName --query loginServer --output tsv
$imagem = "$loginServer/${ImageName}:$Tag"
Write-Host "Imagem: $imagem"

if ($Modo -eq "AcrBuild") {
    # [CRIA RECURSOS/CUSTO] build na nuvem (não precisa de Docker)
    az acr build --registry $AcrName --image "${ImageName}:$Tag" --file $Dockerfile `
        --build-arg "VCS_REF=$Tag" .
} else {
    # [CRIA RECURSOS/CUSTO] build local + push
    docker build -f $Dockerfile -t $imagem --build-arg "VCS_REF=$Tag" .
    # [SOMENTE LEITURA] autentica o Docker no ACR com token temporário do Entra ID
    az acr login --name $AcrName
    docker push $imagem
}

# [SOMENTE LEITURA]
az acr repository show-tags --name $AcrName --repository $ImageName --orderby time_desc --top 5 --output table
Write-Host ""
Write-Host "Próximo passo (fase 2): terraform apply -var deploy_container=true -var image_tag=$Tag"
