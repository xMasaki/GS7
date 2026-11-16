<#
.SYNOPSIS
    Gera de uma vez os PDFs de entrega das 7 disciplinas do AcessaCidade.

.DESCRIPTION
    Chama o gerador de PDF de cada disciplina (os mesmos scripts documentados em cada pasta) e grava
    todos os PDFs em UMA pasta (padrão: entregas\pdf, na raiz do repositório):

      01  01-Generative-AI-Engineering\docs\gerar_pdf_relatorio.py      -> AcessaCidade_01_GenAI.pdf
      02  02-Big-Data-Architecture\docs\gerar_pdf_relatorio.py          -> AcessaCidade_02_BigData.pdf
      03  03-Business-Intelligence-Startup\scripts\gerar_pdf_entrega.py -> AcessaCidade_03_BI_Startup.pdf
      04  04-Applied-Computer-Vision\docs\gerar_pdf_relatorio.py        -> AcessaCidade_04_Visao.pdf
      05  05-Robotic-Process-Automation\scripts\gerar_pdf_relatorio.py  -> AcessaCidade_05_RPA.pdf
      06  tools\gerar_pdf_markdown.py  (docs\RELATORIO_ENTREGA_DEVOPS.md) -> AcessaCidade_06_DevOps.pdf
      07  tools\gerar_pdf_markdown.py  (docs\RELATORIO_ENTREGA_MAKER.md)  -> AcessaCidade_07_Maker.pdf

    Links: 01, 03 e 04 leem os links reais de docs\links_entrega.yaml de cada pasta; 06 e 07 usam
    -RepoUrl para transformar links relativos em links clicáveis do GitHub. Enquanto houver
    [PREENCHER], os PDFs são RASCUNHOS (o script avisa). Use -Estrito para a versão final:
    01, 03, 04, 06 e 07 falham se faltar link ou restar [PREENCHER] (02 e 05 apenas avisam).

    Versionamento: os PDFs FINAIS em entregas\pdf podem ser versionados (o repositório público
    serve de cópia de segurança e de referência para os professores). Rascunhos NÃO devem ir para
    o Git: gere-os fora do repositório com -Saida (ex.: $env:TEMP\acessacidade_pdfs).

    Pré-requisitos: venv .venv com requirements-dev.txt instalado (markdown, pypdf, playwright, pyyaml)
    e Microsoft Edge instalado. 02 e os diagramas Mermaid de 06/07 precisam de internet (CDN jsDelivr).

.PARAMETER Saida
    Pasta de destino dos PDFs (padrão: entregas\pdf na raiz do repositório).

.PARAMETER Disciplinas
    Lista das disciplinas a gerar (padrão: 01,02,03,04,05,06,07).

.PARAMETER RepoUrl
    URL https:// do repositório público no GitHub (sem barra no final), usada por 06 e 07.

.PARAMETER Estrito
    Repassa --estrito aos geradores que o suportam (entrega final).

.EXAMPLE
    .\tools\gerar_todos_pdfs.ps1 -Saida "$env:TEMP\acessacidade_pdfs"
    .\tools\gerar_todos_pdfs.ps1 -Disciplinas 06,07
    .\tools\gerar_todos_pdfs.ps1 -RepoUrl https://github.com/<conta>/<repositorio> -Estrito

.NOTES
    Se a execução de scripts estiver bloqueada:
      powershell -ExecutionPolicy Bypass -File .\tools\gerar_todos_pdfs.ps1
#>
[CmdletBinding()]
param(
    [string]$Saida = "",
    [string[]]$Disciplinas = @("01", "02", "03", "04", "05", "06", "07"),
    [string]$RepoUrl = "",
    [switch]$Estrito
)

$ErrorActionPreference = "Stop"
$Raiz = Split-Path -Parent $PSScriptRoot
Set-Location $Raiz
$env:PYTHONIOENCODING = "utf-8"

$Python = Join-Path $Raiz ".venv\Scripts\python.exe"
if (-not (Test-Path $Python)) {
    Write-Host "ERRO: venv não encontrado em $Python. Crie com: py -3.11 -m venv .venv ; .\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt" -ForegroundColor Red
    exit 2
}
if (-not $Saida) { $Saida = Join-Path $Raiz "entregas\pdf" }
New-Item -ItemType Directory -Force -Path $Saida | Out-Null
$Saida = (Resolve-Path $Saida).Path

$Generico = "tools\gerar_pdf_markdown.py"
$Rodape = "AcessaCidade · FIAP Global Solution 2026.2 · CitizenTech (ODS 11)"

# Cada item: código, nome do PDF, script, argumentos extras, aceita --estrito?
$Tarefas = @(
    @{ Id = "01"; Pdf = "AcessaCidade_01_GenAI.pdf"; Script = "01-Generative-AI-Engineering\docs\gerar_pdf_relatorio.py"; Args = @(); Estrito = $true },
    @{ Id = "02"; Pdf = "AcessaCidade_02_BigData.pdf"; Script = "02-Big-Data-Architecture\docs\gerar_pdf_relatorio.py"; Args = @(); Estrito = $false },
    @{ Id = "03"; Pdf = "AcessaCidade_03_BI_Startup.pdf"; Script = "03-Business-Intelligence-Startup\scripts\gerar_pdf_entrega.py"; Args = @(); Estrito = $true },
    @{ Id = "04"; Pdf = "AcessaCidade_04_Visao.pdf"; Script = "04-Applied-Computer-Vision\docs\gerar_pdf_relatorio.py"; Args = @(); Estrito = $true },
    @{ Id = "05"; Pdf = "AcessaCidade_05_RPA.pdf"; Script = "05-Robotic-Process-Automation\scripts\gerar_pdf_relatorio.py"; Args = @(); Estrito = $false },
    @{ Id = "06"; Pdf = "AcessaCidade_06_DevOps.pdf"; Script = $Generico; Estrito = $true;
       Args = @("06-Secure-DevOps-Cloud\docs\RELATORIO_ENTREGA_DEVOPS.md", "--titulo", "AcessaCidade — Secure DevOps Tools & Cloud Computing", "--rodape", $Rodape) },
    @{ Id = "07"; Pdf = "AcessaCidade_07_Maker.pdf"; Script = $Generico; Estrito = $true;
       Args = @("07-Project-Based-Maker-Lab\docs\RELATORIO_ENTREGA_MAKER.md", "--titulo", "AcessaCidade — Project-Based Maker Lab", "--rodape", $Rodape) }
)

$Resultados = @()
foreach ($t in $Tarefas) {
    if ($Disciplinas -notcontains $t.Id) { continue }
    $destino = Join-Path $Saida $t.Pdf
    $argumentos = @($t.Script) + $t.Args + @("--saida", $destino)
    if ($t.Script -eq $Generico -and $RepoUrl) { $argumentos += @("--repo-url", $RepoUrl) }
    if ($Estrito -and $t.Estrito) { $argumentos += "--estrito" }

    Write-Host ""
    Write-Host "=== [$($t.Id)] $($t.Script) -> $destino" -ForegroundColor Cyan
    & $Python @argumentos
    $codigo = $LASTEXITCODE
    $ok = ($codigo -eq 0) -and (Test-Path $destino) -and ((Get-Item $destino).Length -gt 0)
    $Resultados += [pscustomobject]@{ Disciplina = $t.Id; Arquivo = $t.Pdf; Codigo = $codigo; Gerado = $ok }
}

Write-Host ""
Write-Host "=== Resumo (pasta: $Saida)" -ForegroundColor Cyan
$Resultados | Format-Table -AutoSize | Out-String | Write-Host
$falhas = @($Resultados | Where-Object { -not $_.Gerado })
if ($falhas.Count -gt 0) {
    Write-Host "Falharam: $(($falhas | ForEach-Object { $_.Disciplina }) -join ', ')" -ForegroundColor Red
    exit 1
}
Write-Host "Todos os PDFs pedidos foram gerados. Confira os avisos de [PREENCHER] acima antes da entrega final." -ForegroundColor Green
exit 0
