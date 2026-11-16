<#
  AcessaCidade - Disciplina 05 (RPA) - monta o ZIP de entrega.

  Conteudo do ZIP:
    RELATORIO_RPA_AcessaCidade.pdf      (entrega/RELATORIO_RPA_AcessaCidade.pdf)
    link_video.txt                      (entrega/link_video.txt - criado pela equipe)
    UiPath/AcessaCidade.RPA/...         (sem .local, .objects, .project, .screenshots, .tmh, ~$*)
    planilhas/*.xlsx                    (assessment, entrada simulada, saida gerada pelo robo se existir)
    process-mapping/*.bpmn, *.svg       (As-Is e To-Be)
    evidencias/*                        (prints, se existirem)

  O script NAO cria o link do video nem o PDF: apenas avisa quando faltam.

  Uso (PowerShell, na raiz do repositorio):
    powershell -ExecutionPolicy Bypass -File .\05-Robotic-Process-Automation\scripts\gerar_zip_entrega.ps1
    (parametros opcionais: -Saida "C:\caminho\AcessaCidade_RPA_entrega.zip"  -PermitirIncompleto)

  Sem -PermitirIncompleto, o script termina com codigo 2 se o PDF ou o link estiverem faltando
  (o ZIP NAO e gerado). Com -PermitirIncompleto, gera um ZIP de conferencia mesmo assim.
#>
param(
    [string]$Saida = "",
    [switch]$PermitirIncompleto
)

$ErrorActionPreference = "Stop"
$Base = Split-Path -Parent $PSScriptRoot          # 05-Robotic-Process-Automation
$Entrega = Join-Path $Base "entrega"
if ([string]::IsNullOrWhiteSpace($Saida)) { $Saida = Join-Path $Entrega "AcessaCidade_RPA_entrega.zip" }

$Pdf = Join-Path $Entrega "RELATORIO_RPA_AcessaCidade.pdf"
$Link = Join-Path $Entrega "link_video.txt"
$Projeto = Join-Path $Base "UiPath\AcessaCidade.RPA"
$Planilhas = Join-Path $Base "spreadsheet"
$Mapeamento = Join-Path $Base "process-mapping"
$Evidencias = Join-Path $Base "evidencias"

$avisos = @()

# ---------------- verificacoes ----------------
if (-not (Test-Path $Pdf)) {
    $avisos += "PDF ausente: $Pdf  (gere com scripts\gerar_pdf_relatorio.py depois de preencher o relatorio)"
}
if (-not (Test-Path $Link)) {
    $avisos += "Link do video ausente: crie $Link com o link (YouTube nao listado / Drive) - uma linha."
} else {
    $conteudo = (Get-Content -Path $Link -Raw -Encoding UTF8)
    if ($null -eq $conteudo) { $conteudo = "" }
    $conteudo = $conteudo.Trim()
    if ($conteudo -eq "" -or $conteudo -match "PREENCHER" -or $conteudo -notmatch "^https?://") {
        $avisos += "link_video.txt existe mas nao contem um link http(s) valido (ou ainda tem [PREENCHER])."
    }
}
if (-not (Test-Path (Join-Path $Projeto "project.json"))) {
    throw "Projeto UiPath nao encontrado em $Projeto"
}
if (-not (Test-Path (Join-Path $Planilhas "denuncias_resultado_RPA.xlsx"))) {
    $avisos += "Planilha de saida do robo (spreadsheet\denuncias_resultado_RPA.xlsx) ainda nao existe - execute o robo no UiPath Studio."
}
$prints = @()
if (Test-Path $Evidencias) { $prints = Get-ChildItem -Path $Evidencias -File -Include *.png,*.jpg,*.jpeg -Recurse }
if ($prints.Count -eq 0) { $avisos += "Nenhum print em $Evidencias (ver docs\EVIDENCIAS_NECESSARIAS.md)." }

if ($avisos.Count -gt 0) {
    Write-Host "ATENCAO - itens pendentes:" -ForegroundColor Yellow
    foreach ($a in $avisos) { Write-Host "  - $a" -ForegroundColor Yellow }
    $bloqueante = (-not (Test-Path $Pdf)) -or ($avisos -match "Link do video|link_video")
    if ($bloqueante -and -not $PermitirIncompleto) {
        Write-Host "ZIP NAO gerado (PDF e/ou link do video faltando). Use -PermitirIncompleto para gerar um ZIP de conferencia." -ForegroundColor Red
        exit 2
    }
}

# ---------------- montagem ----------------
$Temp = Join-Path ([System.IO.Path]::GetTempPath()) ("acessacidade_rpa_zip_" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $Temp | Out-Null
try {
    if (Test-Path $Pdf) { Copy-Item $Pdf -Destination $Temp }
    if (Test-Path $Link) { Copy-Item $Link -Destination $Temp }

    $excluir = @(".local", ".objects", ".project", ".screenshots", ".tmh")
    $destProj = Join-Path $Temp "UiPath\AcessaCidade.RPA"
    Get-ChildItem -Path $Projeto -Recurse -File -Force | ForEach-Object {
        $rel = $_.FullName.Substring($Projeto.Length).TrimStart("\")
        $primeiro = $rel.Split("\")[0]
        if ($excluir -contains $primeiro) { return }
        if ($_.Name -like '~$*') { return }
        $alvo = Join-Path $destProj $rel
        New-Item -ItemType Directory -Path (Split-Path -Parent $alvo) -Force | Out-Null
        Copy-Item $_.FullName -Destination $alvo
    }

    $destPlan = Join-Path $Temp "planilhas"
    New-Item -ItemType Directory -Path $destPlan | Out-Null
    Get-ChildItem -Path $Planilhas -File -Filter *.xlsx | Where-Object { $_.Name -notlike '~$*' } |
        ForEach-Object { Copy-Item $_.FullName -Destination $destPlan }

    $destMap = Join-Path $Temp "process-mapping"
    New-Item -ItemType Directory -Path $destMap | Out-Null
    Get-ChildItem -Path $Mapeamento -File | Where-Object { $_.Extension -in ".bpmn", ".svg", ".png" } |
        ForEach-Object { Copy-Item $_.FullName -Destination $destMap }

    if ($prints.Count -gt 0) {
        $destEv = Join-Path $Temp "evidencias"
        New-Item -ItemType Directory -Path $destEv | Out-Null
        $prints | ForEach-Object { Copy-Item $_.FullName -Destination $destEv }
    }

    New-Item -ItemType Directory -Path (Split-Path -Parent $Saida) -Force | Out-Null
    if (Test-Path $Saida) { Remove-Item $Saida -Force -Confirm:$false }
    Compress-Archive -Path (Join-Path $Temp "*") -DestinationPath $Saida -CompressionLevel Optimal

    $qtd = (Get-ChildItem -Path $Temp -Recurse -File).Count
    $tam = [math]::Round((Get-Item $Saida).Length / 1KB, 1)
    Write-Host "ZIP gerado: $Saida  ($qtd arquivos, $tam KB)" -ForegroundColor Green
    if ($avisos.Count -gt 0) { Write-Host "ZIP INCOMPLETO - resolva os itens pendentes antes de entregar no Teams." -ForegroundColor Yellow }
} finally {
    Remove-Item $Temp -Recurse -Force -Confirm:$false -ErrorAction SilentlyContinue
}
