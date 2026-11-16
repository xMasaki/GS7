# Observabilidade — 4 sinais de ouro e alertas

A aplicação expõe métricas Prometheus em `GET /metrics` (contrato, seção 10). Prometheus,
Alertmanager e Grafana rodam **localmente** (docker compose, profile `monitoring`) e podem coletar
tanto do container local quanto do **MVP publicado na Azure** — o que a GS permite explicitamente.

## 1. Métricas e sinais de ouro

| Sinal de ouro | Métrica (contrato) | Consulta usada no dashboard |
|---|---|---|
| **Latência** | `acessacidade_http_request_duration_seconds` (histogram) | `histogram_quantile(0.5/0.95/0.99, sum by (le) (rate(..._bucket[5m])))` |
| **Tráfego** | `acessacidade_http_requests_total` (counter) | `sum by (route) (rate(...[5m]))` |
| **Erros** | `acessacidade_http_requests_total{status=~"4..|5.."}` | taxa 4xx/5xx em req/s e % do total |
| **Saturação** | `acessacidade_http_requests_in_progress`, `process_resident_memory_bytes`, `process_cpu_seconds_total` | em andamento, memória residente, `rate(process_cpu_seconds_total[5m])` |
| Negócio | `acessacidade_denuncias_criadas_total`, `acessacidade_visao_classificacoes_total`, `acessacidade_assistente_respostas_total`, `acessacidade_visao_duracao_seconds` | denúncias/hora, classificações da triagem, respostas do assistente por fonte (`llm`/`fallback`) |

Dashboard provisionado automaticamente: **AcessaCidade → "AcessaCidade — Sinais de Ouro"**
(`monitoring/grafana/dashboards/acessacidade-golden-signals.json`, também definido como página inicial).

## 2. Alertas (`monitoring/prometheus/alert_rules.yml`)

| Alerta | Condição | `for` | Severidade |
|---|---|---|---|
| `AcessaCidadeIndisponivel` | `up == 0` (alvo não responde ao scrape) | 1m | critical |
| `AcessaCidadeTaxaErros5xxAlta` | > 5% das requisições com 5xx | 2m | critical |
| `AcessaCidadeLatenciaP95Alta` | p95 > 2 s | 5m | warning |
| `AcessaCidadeMuitas4xx` | > 0,5 resposta 4xx por segundo (30/min) | 1m | warning |
| `AcessaCidadeSaturacaoMemoria` | memória residente > 1,2 GB (limite do ACI: 1,5 GB) | 5m | warning |

Alertmanager (`monitoring/alertmanager/alertmanager.yml`) recebe os alertas e os exibe em
http://127.0.0.1:9093. Não há envio para e-mail/Slack configurado (evita guardar credenciais);
para notificar, acrescente um receiver com a URL de webhook guardada **fora do Git**.

## 3. Subir o monitoramento

Pré-requisito: Docker Desktop com Compose ≥ 2.24 e um arquivo `.env` na raiz com a senha do Grafana
(o `.env` não vai para o Git):

```powershell
Copy-Item .env.example .env          # se ainda não existir
Add-Content .env "GRAFANA_ADMIN_PASSWORD=<senha forte escolhida pela equipe>"
```

> O Grafana **recusa iniciar** sem `GRAFANA_ADMIN_PASSWORD` (não existe senha padrão embutida).

### 3.1 Aplicação local + monitoramento

```powershell
docker compose --profile monitoring up -d --build
docker compose ps                     # app "healthy"; prometheus, grafana, alertmanager "running"
```

| Serviço | URL (somente nesta máquina) |
|---|---|
| AcessaCidade | http://localhost:8000 |
| Prometheus | http://127.0.0.1:9090 (Status → Targets: `acessacidade-local` UP) |
| Alertmanager | http://127.0.0.1:9093 |
| Grafana | http://127.0.0.1:3000 (usuário `admin` ou `GRAFANA_ADMIN_USER`; senha do `.env`) |

### 3.2 Monitorar o MVP publicado na Azure

1. Pegue o FQDN: `terraform -chdir=06-Secure-DevOps-Cloud/terraform output -raw container_fqdn`.
2. Edite `06-Secure-DevOps-Cloud/monitoring/prometheus/prometheus.azure.yml` e troque o marcador
   `[PREENCHER ...]` pelo `<fqdn>:8000`.
3. No `.env`: `PROMETHEUS_CONFIG=prometheus.azure.yml`.
4. `docker compose --profile monitoring up -d prometheus alertmanager grafana` (sem subir o app local).
5. Prometheus → Status → Targets: `acessacidade-azure` **UP**.

## 4. Demonstrar um alerta disparado (roteiro seguro)

### 4.1 Alerta de 4xx (não derruba nada)

```powershell
.\.venv\Scripts\python.exe scripts\gerar_trafego_demo.py --url http://localhost:8000 --duracao 240 --modo erros404
# para o MVP na Azure: --url http://<fqdn>:8000
```

O script consulta protocolos **inexistentes** (somente leitura; nada é gravado) a ~3 req/s.

1. Prometheus → **Alerts**: `AcessaCidadeMuitas4xx` passa de *inactive* → *pending* (≈ 1–2 min) → **firing** (após mais 1 min). **Print.**
2. Alertmanager (http://127.0.0.1:9093): o alerta aparece listado. **Print.**
3. Grafana → painel "Taxa de erros 4xx e 5xx" e "Erros por rota e status" mostram o pico. **Print.**
4. Ao terminar o script o alerta volta a *inactive* em poucos minutos.

### 4.2 Alerta de indisponibilidade (local)

```powershell
docker compose stop app               # simula queda
# aguarde ~1,5 min: Prometheus → Alerts → AcessaCidadeIndisponivel = FIRING (print)
docker compose start app              # recupera; o alerta é resolvido
```

Na Azure, a forma equivalente (só se a equipe aceitar alguns minutos fora do ar, **nunca no período de correção**):
`az container stop -g rg-acessacidade-prod -n aci-acessacidade-prod` e depois `az container start ...`.

### 4.3 Tráfego normal para popular o dashboard

```powershell
.\.venv\Scripts\python.exe scripts\gerar_trafego_demo.py --url http://localhost:8000 --duracao 300 --modo normal --com-visao
```

Painéis de latência (p50/p95/p99), tráfego por rota, saturação e triagem por imagem ganham dados.
**Print do dashboard completo** com os 4 sinais.

## 5. Validação feita sem Docker

Sem Docker na máquina de desenvolvimento, a configuração foi validada por testes
(`06-Secure-DevOps-Cloud/tests/test_devops_observabilidade.py`): YAML/JSON válidos, regras
obrigatórias presentes, métricas iguais às do contrato e datasource do Grafana coerente.
A execução real (Prometheus coletando, alerta disparado) depende do Docker Desktop — ver
`PENDENCIAS_E_ACOES_MANUAIS.txt`.
