# Estimativa de custos — AcessaCidade na Azure

> **Aviso importante:** os preços abaixo são **valores de referência** da tabela pública
> pay-as-you-go da Azure para a região **East US (Leste dos EUA)**, em dólares, conforme conhecidos
> pela equipe (tabela de 2025). Preços mudam e variam por região — a região padrão do projeto,
> **Brazil South**, costuma ser **mais cara**. Antes de publicar, confira e substitua os valores na
> [Azure Pricing Calculator](https://azure.microsoft.com/pricing/calculator/) e anexe o print ao PDF.
> Data da conferência: [PREENCHER: dd/mm/aaaa] · Região conferida: [PREENCHER].

## 1. Recursos e preços unitários de referência

| Recurso | Configuração no Terraform | Preço de referência (East US) | Observação |
|---|---|---|---|
| Azure Container Instances (Linux) — vCPU | `container_cpu = 1` | US$ 0,0000135 por vCPU-segundo (≈ US$ 0,0486/h) | Cobrança por segundo enquanto o container existe |
| Azure Container Instances (Linux) — memória | `container_memory = 1.5` | US$ 0,0000015 por GB-segundo (≈ US$ 0,0054/GB-h) | 1,5 GB ≈ US$ 0,0081/h |
| Azure Container Registry | `acr_sku = "Basic"` | ≈ US$ 0,167/dia (≈ US$ 5,00/mês), 10 GB incluídos | Cobrado por dia enquanto o registro existe |
| ACR Tasks (`az acr build`, opcional) | só se usar build na nuvem | ≈ US$ 0,0001 por segundo de build | Um build de ~5 min ≈ US$ 0,03 |
| Storage Account (state do Terraform) | LRS, poucos KB | centavos por mês | Desprezível |
| Log Analytics (opcional) | `enable_log_analytics = false` (padrão) | ≈ US$ 2,30 por GB ingerido; primeiros 5 GB/mês por conta de cobrança sem custo | `daily_quota_gb = 1` limita o gasto |
| Saída de dados (egress) | — | Primeiros 100 GB/mês gratuitos | MVP fica muito abaixo |
| GitHub Actions | repositório público | Sem custo em runners hospedados para repositório público | — |
| Prometheus / Grafana | locais (docker compose) | Sem custo de nuvem | Rodam na máquina da equipe |

## 2. Cálculo (1 vCPU + 1,5 GB, ligado 24 horas por dia)

Custo/hora do ACI = 0,0486 (vCPU) + 1,5 × 0,0054 (memória) = **US$ 0,0567/h** → **US$ 1,36/dia**.

| Cenário | ACI | ACR Basic | Storage/egress | **Total estimado (East US)** |
|---|---|---|---|---|
| 7 dias (período de correção curto) | US$ 9,53 | US$ 1,17 | < US$ 0,10 | **≈ US$ 10,80** |
| 14 dias (período de correção longo) | US$ 19,05 | US$ 2,33 | < US$ 0,10 | **≈ US$ 21,50** |
| 30 dias (mensal) | US$ 40,82 | US$ 5,00 | < US$ 0,20 | **≈ US$ 46,00** |
| Log Analytics ligado (adicional, mensal) | — | — | — | ≈ US$ 0 (até 5 GB) a US$ 2,30/GB excedente |

Brazil South: [PREENCHER: valores conferidos na calculadora para 7, 14 e 30 dias].
Conversão para reais: [PREENCHER: cotação do dia] — não usar cotação inventada.

## 3. Créditos e como evitar surpresas

- **Azure for Students**: crédito anual em dólares para estudantes, sem cartão de crédito
  ([PREENCHER: valor do crédito exibido no portal da conta da equipe]). O MVP de 14 dias cabe
  com folga no crédito típico do programa — confirme no portal (Cost Management → Credits).
- Crie um **orçamento com alerta** (Cost Management → Budgets) de, por exemplo, US$ 10, com aviso em 50% e 90%.
- Reduza custo sem perder a avaliação: `container_memory = 1` (se a aplicação couber — validar
  com o painel de memória do Grafana) e manter Log Analytics desligado.
- **Não remova os recursos antes do fim da correção** (a URL pública faz parte da entrega).
  Depois da nota, execute a limpeza (`infra/azure/99_limpeza.*` ou `terraform destroy`) — o
  ACR Basic e o ACI cobram enquanto existirem.

## 4. Comparação com alternativas (para a evolução)

| Alternativa | Por que considerar | Custo relativo (qualitativo) |
|---|---|---|
| Azure Container Apps (Consumption) | HTTPS gerenciado, escala a zero | Pode ser menor que ACI 24/7 com pouco tráfego (cota gratuita mensal) |
| App Service B1 Linux | HTTPS, slots, domínio | Custo fixo mensal maior que ACI pequeno |
| AKS | Produção com várias réplicas | Muito maior para um MVP |
