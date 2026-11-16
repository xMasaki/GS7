<#
=====================================================================
 AcessaCidade — 06. Status, logs e diagnóstico do container (ACI)
=====================================================================
 Classificação dos comandos deste script:
   az container show ........................................ [SOMENTE LEITURA]
   az container logs ........................................ [SOMENTE LEITURA]
   az container attach ...................................... [SOMENTE LEITURA] (acompanha a saída; Ctrl+C sai)
   Invoke-WebRequest /health ................................ [SOMENTE LEITURA]
 Diagnóstico interativo (sem porta SSH aberta — não existe porta administrativa):
   az container exec --resource-group <rg> --name <aci> --exec-command "/bin/sh"   [SOMENTE LEITURA*]
   (*abre um shell DENTRO do container via API da Azure; use só para inspeção)

 Uso:
   .\infra\azure\06_status_logs.ps1 -ResourceGroup "<rg>" -AciName "<aci>" [-Acompanhar]
 Nomes: terraform -chdir=06-Secure-DevOps-Cloud/terraform output
=====================================================================
#>
param(
    [Parameter(Mandatory = $true)][string]$ResourceGroup,
    [string]$AciName = "aci-acessacidade-prod",
    [switch]$Acompanhar
)
$ErrorActionPreference = "Stop"

# [SOMENTE LEITURA] estado, reinícios e endereço
az container show --resource-group $ResourceGroup --name $AciName `
    --query "{Estado:instanceView.state, FQDN:ipAddress.fqdn, IP:ipAddress.ip, Portas:ipAddress.ports[].port, Reinicios:containers[0].instanceView.restartCount, Imagem:containers[0].image}" `
    --output table

# [SOMENTE LEITURA] eventos recentes (pull da imagem, probes, reinícios)
az container show --resource-group $ResourceGroup --name $AciName `
    --query "containers[0].instanceView.events[-10:].{Hora:lastTimestamp, Tipo:type, Mensagem:message}" --output table

# [SOMENTE LEITURA] logs
az container logs --resource-group $ResourceGroup --name $AciName

# [SOMENTE LEITURA] health check
$fqdn = az container show --resource-group $ResourceGroup --name $AciName --query ipAddress.fqdn --output tsv
try {
    $r = Invoke-WebRequest -Uri "http://${fqdn}:8000/health" -UseBasicParsing -TimeoutSec 15
    Write-Host "Health: HTTP $($r.StatusCode) $($r.Content)"
} catch {
    Write-Warning "Health check falhou: $($_.Exception.Message)"
}

if ($Acompanhar) {
    # [SOMENTE LEITURA]
    az container attach --resource-group $ResourceGroup --name $AciName
}
