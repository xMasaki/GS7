# Dashboard de indicadores — AcessaCidade

O dashboard do MVP é a tela **`#/painel`** do próprio site AcessaCidade (mesma URL pública do MVP). Ele reúne dois
tipos de indicador, cada um com uma fonte e uma camada diferente:

| Seção do painel | Endpoint | Camada / fonte | Atualização |
|---|---|---|---|
| **Indicadores operacionais** | `GET /api/indicadores?incluir_simulados=true` | Banco operacional (SQLite) do backend | Tempo real: cada denúncia nova entra na hora |
| **Indicadores analíticos** | `GET /api/indicadores/analiticos` | Camada **Gold** do pipeline de dados (disciplina 02), publicada como `gold_snapshot.json` | A cada execução do pipeline (Airflow ou runner local) |

Este diretório complementa o painel com:

- a **definição de cada KPI** (fórmula, fonte, camada) — abaixo;
- o script **`exportar_gold_para_excel.py`**, que transforma os CSVs Gold em uma pasta de trabalho Excel
  (`AcessaCidade_indicadores.xlsx`) com gráficos nativos, para análise em Excel ou importação no Power BI (opcional).

> **Dados simulados.** Enquanto não houver uso real, a maior parte dos números vem do seed de demonstração e do CSV
> simulado do pipeline (`simulado=true`, `origem=SIMULADO`, cidade fictícia "Cidade Exemplo"). O painel e a planilha
> exibem esse aviso. Esses números demonstram o funcionamento; **não** são evidência de impacto.

## 1. Arquitetura do fluxo de dados até o dashboard

```text
Cidadão ──► POST /api/denuncias ──► SQLite (operacional) ──► GET /api/indicadores ──────────────┐
                                        │                                                       │
                                        └─► GET /api/export/denuncias (X-Pipeline-Token)        ├─► #/painel
                                                     │                                          │
data/samples/denuncias_simuladas.csv ─┐              ▼                                          │
                                      └─► Pipeline (disciplina 02): Raw → Bronze → Silver → Gold│
                                                     │                                          │
                                                     ├─► data/processed/gold/*.csv ─► exportar_gold_para_excel.py ─► AcessaCidade_indicadores.xlsx (Excel / Power BI)
                                                     └─► POST /api/pipeline/gold ─► gold_snapshot.json ─► GET /api/indicadores/analiticos ─┘
```

## 2. Definição dos KPIs

### 2.1 Operacionais (`GET /api/indicadores`, tempo real)

| KPI | Campo / fórmula | Fonte | Camada | Leitura |
|---|---|---|---|---|
| Total de denúncias | `total` | SQLite | Operacional | Volume registrado (com ou sem simulados, conforme `incluir_simulados`) |
| Possíveis buracos | `possiveis_buracos` = nº com `visao.classificacao = POSSIBLE_POTHOLE` | SQLite | Operacional | Triagem heurística — **requer revisão humana** |
| Inconclusivas | `inconclusivas` (`INCONCLUSIVE`) | SQLite | Operacional | Foto sem informação suficiente |
| Nenhum indício | `nao_identificadas` (`NOT_IDENTIFIED`) | SQLite | Operacional | Triagem não achou indício de buraco (não significa ausência de problema) |
| Sem imagem | `sem_imagem` (`visao` nulo) | SQLite | Operacional | Denúncias enviadas sem foto |
| **% com foto analisada** | (`total` − `sem_imagem`) ÷ `total` | SQLite | Operacional (derivado) | Adoção da foto pelo cidadão |
| Por categoria | `por_categoria[]` (chave, rótulo, total) | SQLite | Operacional | Tipos de obstáculo (seção 3.1 do contrato) |
| Por bairro | `por_bairro[]` | SQLite | Operacional | Onde estão as barreiras |
| Por status | `por_status[]` | SQLite | Operacional | Andamento (Recebida → Em análise → Aguardando revisão → Encaminhada → Resolvida) |
| Por resultado da triagem | `por_resultado_visao[]` | SQLite | Operacional | Distribuição das classificações |
| Por origem | `por_origem[]` (WEB, RPA, API, SIMULADO) | SQLite | Operacional | Canal de entrada (inclui o robô RPA) |
| Por dia | `por_dia[]` (data, total) | SQLite | Operacional | Tendência diária |
| Recentes | `recentes[]` (até 5) | SQLite | Operacional | Últimas denúncias |

### 2.2 Analíticos (`GET /api/indicadores/analiticos`, camada Gold)

| KPI | Campo do snapshot / tabela Gold | Colunas | Leitura |
|---|---|---|---|
| Denúncias por bairro | `denuncias_por_bairro` / `gold.denuncias_por_bairro` | `bairro, total, possiveis_buracos` | Priorização territorial; **% de possíveis buracos por bairro** = `possiveis_buracos ÷ total` |
| Denúncias por categoria | `denuncias_por_categoria` / `gold.denuncias_por_categoria` | `categoria, rotulo, total` | Tipos de barreira mais frequentes |
| Denúncias por período | `denuncias_por_periodo` / `gold.denuncias_por_periodo` | `periodo, total` (mês `AAAA-MM`) | Tendência mensal |
| Denúncias por status | `denuncias_por_status` / `gold.denuncias_por_status` | `status, rotulo, total` | Andamento consolidado |
| Resultado da triagem | `resultado_visao` / `gold.resultado_visao` | `classificacao, rotulo, total` | Distribuição consolidada |
| Qualidade dos dados | `qualidade` | `linhas_raw, linhas_bronze, duplicatas_removidas, datas_invalidas, coordenadas_invalidas, campos_obrigatorios_ausentes, percentual_registros_validos` | Confiabilidade da base (Raw → Bronze) |
| Fontes | `fontes[]` | `nome, linhas` | Linhagem: quanto veio do CSV simulado e quanto da API |

### 2.3 KPIs de negócio/impacto que **não** estão no painel (e onde obtê-los)

| KPI | Fórmula | Onde obter hoje |
|---|---|---|
| Tempo médio de triagem automática | `acessacidade_visao_duracao_seconds_sum ÷ _count` | `/metrics` (Prometheus/Grafana — disciplina 06) |
| % revisadas por humano | `revisao_humana` não nulo ÷ denúncias com foto | Coluna `revisao_humana` da exportação do pipeline (não agregada na Gold no contrato atual) |
| Tempo até encaminhamento | data de `ENCAMINHADA` no histórico − `criado_em` | Histórico individual (`GET /api/denuncias/{ref}`) — **não há agregado no contrato atual** |
| Tempo para registrar (antes × depois) | média por participante | Teste de usabilidade (`../pitch/registro_testes_usuarios_TEMPLATE.xlsx`) |

Definições completas e método de medição: `../business-model/METRICAS_E_IMPACTO.md`.

## 3. Como atualizar

### 3.1 Painel do site (`#/painel`)

- **Operacionais:** nada a fazer; atualizam a cada nova denúncia (recarregue a tela).
- **Analíticos:** rode o pipeline da disciplina 02 (runner local ou DAG do Airflow — ver `02-Big-Data-Architecture/README.md`).
  Ao final, o pipeline publica o snapshot em `POST /api/pipeline/gold` (requer `PIPELINE_TOKEN` configurado no backend e no pipeline)
  e grava os CSVs em `data/processed/gold/`. Recarregue `#/painel`.
- Se o painel mostrar "dados analíticos indisponíveis", o snapshot ainda não foi publicado (`{"disponivel": false}`).

### 3.2 Planilha Excel / Power BI

Na raiz do repositório (Windows PowerShell):

```powershell
.\.venv\Scripts\python.exe 03-Business-Intelligence-Startup\dashboard\exportar_gold_para_excel.py
```

- Lê `data/processed/gold/*.csv` (aceita os nomes `denuncias_por_bairro.csv`, `gold_denuncias_por_bairro.csv` ou
  `gold.denuncias_por_bairro.csv`, e assim por diante) e, se existir, `gold_snapshot.json` (metadados e qualidade).
- Gera `03-Business-Intelligence-Startup/dashboard/AcessaCidade_indicadores.xlsx` com as abas
  **Leia-me, Resumo, Bairros, Categorias, Periodo, Status, Triagem_da_foto, Qualidade** e gráficos nativos do Excel.
- Outra pasta/arquivo: `--gold-dir <pasta> --saida <arquivo.xlsx>`.
- Sem dados Gold: o script sai com código **2** e explica como gerar os dados rodando o pipeline.
- CSV com colunas diferentes do contrato: sai com código **3** e lista as colunas esperadas.

**Power BI (opcional):** Power BI Desktop › **Obter dados › Pasta de Trabalho do Excel** › selecione
`AcessaCidade_indicadores.xlsx` › marque as abas `Bairros`, `Categorias`, `Periodo`, `Status`, `Triagem_da_foto` ›
**Carregar**. Recrie os visuais (barras por bairro, linha por período). Para atualizar: rode o script e clique em **Atualizar** no Power BI.

## 4. Testes

```powershell
.\.venv\Scripts\python.exe -m pytest 03-Business-Intelligence-Startup\tests
```

Os testes criam CSVs Gold **sintéticos** em pasta temporária (nomes e colunas do contrato, seção 4.8) e verificam
abas, gráficos, fórmulas e mensagens de erro.
