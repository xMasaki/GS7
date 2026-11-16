# Dicionário de dados — pipeline AcessaCidade (raw → bronze → silver → gold)

Warehouse: DuckDB em `data/processed/warehouse/acessacidade.duckdb` (schemas `raw`, `bronze`, `silver`, `gold`).
Arquivos Gold: `data/processed/gold/*.csv` e `data/processed/gold/gold_snapshot.json`.
Regras citadas (RN-xx) estão em [REGRAS_DE_NEGOCIO.md](REGRAS_DE_NEGOCIO.md). Enumerações (chaves/rótulos) seguem as
seções 3.1–3.6 de `docs/CONTRATOS_DE_INTEGRACAO.md`.

> Os volumes indicados são os de uma execução real sem a API (`--sem-api`) sobre a fonte **simulada**
> (ver `docs/evidencias/execucao_local_runner.log`). Mudam quando a exportação da API é incluída.

Convenções: **Origem** = de onde vem o valor; **Regra** = transformação aplicada. `NULL` = valor ausente.

---

## 1. Camada RAW (cópia fiel, schema-on-read)

Todas as colunas de origem são `VARCHAR` exatamente como no arquivo (leitura `all_varchar`); nenhuma limpeza,
tipagem ou deduplicação. Carga *full refresh* a cada execução.

### 1.1 `raw.denuncias_simuladas` — fonte 1 (`data/samples/denuncias_simuladas.csv`, 271 linhas)

| Coluna | Tipo | Descrição | Origem | Regra |
|---|---|---|---|---|
| id | VARCHAR | Identificador no sistema legado fictício | CSV | nenhuma |
| protocolo | VARCHAR | Protocolo do legado (`SIM-2026-000123`) | CSV | nenhuma |
| criado_em | VARCHAR | Data/hora de registro em formatos variados | CSV | nenhuma |
| atualizado_em | VARCHAR | Data/hora da última atualização | CSV | nenhuma |
| logradouro | VARCHAR | Rua/avenida (com abreviações e grafias variadas) | CSV | nenhuma |
| numero | VARCHAR | Número do imóvel de referência (`S/N`, `120 a`...) | CSV | nenhuma |
| bairro | VARCHAR | Bairro com grafias variadas | CSV | nenhuma |
| cidade | VARCHAR | Cidade (sempre a fictícia "Cidade Exemplo", com variações) | CSV | nenhuma |
| ponto_referencia | VARCHAR | Ponto de referência livre | CSV | nenhuma |
| tipo_obstaculo | VARCHAR | Tipo do problema em texto livre/chave/rótulo | CSV | nenhuma |
| descricao | VARCHAR | Descrição livre do problema | CSV | nenhuma |
| impacto | VARCHAR | Impacto em texto livre/chave/rótulo | CSV | nenhuma |
| latitude | VARCHAR | Latitude como texto (vírgula ou ponto) | CSV | nenhuma |
| longitude | VARCHAR | Longitude como texto (vírgula ou ponto) | CSV | nenhuma |
| status | VARCHAR | Situação com variações de grafia | CSV | nenhuma |
| origem | VARCHAR | Canal de origem | CSV | nenhuma |
| simulado | VARCHAR | Indicador de dado simulado (`1`, `true`, `TRUE`...) | CSV | nenhuma |
| possui_imagem | VARCHAR | Indicador de fotografia anexada | CSV | nenhuma |
| visao_classificacao | VARCHAR | Resultado da triagem por visão computacional (variações, vazio) | CSV | nenhuma |
| visao_pontuacao | VARCHAR | Pontuação da triagem (0–1, vírgula ou ponto) | CSV | nenhuma |
| revisao_humana | VARCHAR | Revisão humana (`confirmado`, `descartado`, vazio) | CSV | nenhuma |
| nome_denunciante | VARCHAR | **Dado pessoal simulado** ("Pessoa Simulada 017"); existe só na RAW | CSV | não passa para a Bronze (LGPD) |
| origem_dado | VARCHAR | Sempre `SIMULADO` | CSV | nenhuma |
| _source_file | VARCHAR | Caminho relativo do arquivo de origem | pipeline | metadado de linhagem |
| _ingested_at | TIMESTAMP | Instante (UTC) da carga | pipeline | metadado de linhagem |
| _row_id | BIGINT | Número da linha no arquivo (1..n), na ordem original | pipeline | metadado de linhagem |
| _batch_id | VARCHAR | Identificador da execução (`manual__...` ou run_id do Airflow) | pipeline | metadado de linhagem |

### 1.2 `raw.denuncias_app` — fonte 2 (exportação da API, `data/exports/denuncias_api_<timestamp>.csv`)

Mesmas 21 colunas da exportação do contrato 4.7 (`id` … `revisao_humana`, todas `VARCHAR`, **sem** nome do
denunciante e sem `origem_dado`) + `_source_file`, `_ingested_at`, `_row_id`, `_batch_id` como em 1.1.
Fica **vazia (0 linhas)** quando a API ou o `PIPELINE_TOKEN` não estão disponíveis (o pipeline segue só com a fonte 1).

### 1.3 `raw.log_cargas` — auditoria das cargas (uma linha por fonte e lote)

| Coluna | Tipo | Descrição |
|---|---|---|
| _batch_id | VARCHAR | Execução |
| fonte | VARCHAR | `denuncias_simuladas.csv` ou `api_export` |
| tabela | VARCHAR | Tabela RAW de destino |
| arquivo | VARCHAR | Arquivo carregado (relativo a `data/`), `NULL` se não houve |
| linhas | BIGINT | Linhas carregadas |
| status | VARCHAR | `OK`, `PULADA` (API/token não configurados ou `--sem-api`) ou `FALHOU` (API indisponível, 401/403, CSV fora do contrato) — motivo em `mensagem` |
| mensagem | VARCHAR | Detalhe legível |
| carregado_em | TIMESTAMP | Instante da carga (UTC) |

---

## 2. Camada BRONZE — `bronze.denuncias` (260 linhas)

União das duas fontes RAW, tipada, sem duplicatas técnicas, com problemas **sinalizados** (não resolvidos).
Sem regras de negócio: bairro, tipo, impacto e status continuam com a grafia original (apenas `trim`).

| Coluna | Tipo | Descrição | Origem | Regra |
|---|---|---|---|---|
| fonte | VARCHAR | `denuncias_simuladas.csv` ou `api_export` | pipeline | constante por fonte |
| id_origem | BIGINT | id da fonte | raw.id | `TRY_CAST(trim(id) AS BIGINT)` |
| protocolo | VARCHAR | Protocolo | raw.protocolo | `NULLIF(trim(),'')` |
| criado_em | TIMESTAMP | Registro em UTC | raw.criado_em | `parse_data_multi` (ISO, dd/mm/aaaa, dd-mm-aaaa hh:mm, "14 de outubro de 2026"; sem fuso = horário de Brasília → UTC); irreconhecível → NULL |
| atualizado_em | TIMESTAMP | Atualização em UTC | raw.atualizado_em | `parse_data_multi` |
| logradouro, numero, bairro, cidade, ponto_referencia, tipo_obstaculo, descricao, impacto, status, origem, visao_classificacao, revisao_humana | VARCHAR | Texto original | raw | `NULLIF(trim(),'')` (sem padronização) |
| latitude | DOUBLE | Latitude | raw.latitude | `parse_coordenada` (vírgula→ponto); NULL se fora de −90..90 ou par inválido |
| longitude | DOUBLE | Longitude | raw.longitude | `parse_coordenada`; NULL se fora de −180..180 ou par inválido |
| simulado | BOOLEAN | Dado simulado | raw.simulado | `parse_booleano` (`1/true/sim/...`) |
| possui_imagem | BOOLEAN | Tem fotografia | raw.possui_imagem | `parse_booleano`; valor irreconhecível → NULL |
| visao_pontuacao | DOUBLE | Pontuação da triagem | raw.visao_pontuacao | `parse_decimal`; NULL se fora de 0..1 |
| origem_dado | VARCHAR | `SIMULADO` (fonte 1) ou NULL (fonte 2) | raw | `NULLIF(trim(),'')` |
| flag_possui_nome | BOOLEAN | A linha de origem tinha nome do denunciante | raw.nome_denunciante | **minimização LGPD**: só o indicador passa |
| flag_data_ausente | BOOLEAN | `criado_em` vazio na origem | raw | |
| flag_data_invalida | BOOLEAN | `criado_em` informado mas não reconhecido | raw | |
| flag_coordenada_ausente | BOOLEAN | latitude e longitude vazias | raw | |
| flag_coordenada_invalida | BOOLEAN | coordenada informada mas não numérica, incompleta ou fora da faixa | raw | |
| flag_pontuacao_invalida | BOOLEAN | pontuação informada mas inválida | raw | |
| flag_logradouro_ausente, flag_bairro_ausente, flag_tipo_ausente, flag_descricao_ausente, flag_impacto_ausente | BOOLEAN | campo obrigatório vazio | raw | |
| flag_campo_obrigatorio_ausente | BOOLEAN | algum dos obrigatórios (logradouro, bairro, tipo, descrição, impacto, data) vazio | derivada | OR das flags acima |
| _source_file, _ingested_at, _row_id, _batch_id | — | linhagem herdada da RAW | raw | |

Dedup técnico: `row_number() OVER (PARTITION BY <todas as colunas de origem> ORDER BY _row_id) = 1`, por fonte
(11 duplicatas exatas removidas na execução de referência).

---

## 3. Camada SILVER

### 3.1 `silver.denuncias` — uma linha por denúncia única (250 linhas; 211 válidas)

| Coluna | Tipo | Descrição | Origem | Regra |
|---|---|---|---|---|
| chave_denuncia | VARCHAR | Chave técnica estável `<fonte>:<_row_id 6 dígitos>` | bronze | |
| fonte, id_origem, protocolo | — | como na Bronze | bronze | |
| criado_em | TIMESTAMP | Registro (UTC) | bronze | RN-09: NULL se < 2020-01-01 ou > execução + 1 dia |
| data_registro | DATE | Data **local** (UTC−3) do registro | criado_em | RN-09 |
| ano_mes | VARCHAR | `AAAA-MM` | data_registro | |
| semana_iso | VARCHAR | `AAAA-Www` (semana ISO) | data_registro | |
| atualizado_em | TIMESTAMP | Atualização (UTC) | bronze | |
| logradouro | VARCHAR | Logradouro com espaços normalizados | bronze | `limpar_espacos` |
| logradouro_normalizado | VARCHAR | sem acento, minúsculo, `av`→`avenida`, `r`→`rua`... | bronze | RN-03 |
| numero | VARCHAR | `S/N` ou número compactado em maiúsculas | bronze | RN-03 |
| bairro | VARCHAR | Bairro padronizado (nome oficial do dicionário ou "Título" se desconhecido) | bronze | RN-01 |
| bairro_original | VARCHAR | Grafia recebida (auditoria) | bronze | |
| cidade | VARCHAR | `Cidade Exemplo` ou `Não informada` | bronze | RN-02 |
| ponto_referencia, descricao | VARCHAR | Texto com espaços normalizados | bronze | |
| tipo_obstaculo | VARCHAR | Chave do contrato 3.1 (NULL se não reconhecido) | bronze | RN-04 |
| tipo_obstaculo_rotulo | VARCHAR | Rótulo do contrato 3.1 | ref | |
| impacto / impacto_rotulo | VARCHAR | Chave/rótulo do contrato 3.2 | bronze | RN-05 |
| status / status_rotulo | VARCHAR | Chave/rótulo do contrato 3.3 (ausente/irreconhecível → `RECEBIDA`) | bronze | RN-06 |
| origem | VARCHAR | `WEB`, `RPA`, `SIMULADO`, `API` (contrato 3.5) | bronze | RN-08 |
| dado_simulado | BOOLEAN | `simulado` OU `origem_dado=SIMULADO` OU origem `SIMULADO` | bronze | RN-08 |
| possui_imagem | BOOLEAN | Tem fotografia (se ausente: deduzido da existência de classificação) | bronze | RN-07 |
| visao_classificacao | VARCHAR | Chave do contrato 3.4; NULL quando não há foto | bronze | RN-07 |
| visao_rotulo | VARCHAR | Rótulo 3.4; `Sem fotografia (não analisada)` quando NULL | ref | |
| visao_pontuacao | DOUBLE | Pontuação só quando há foto e classificação | bronze | RN-07 |
| revisao_humana | VARCHAR | `CONFIRMADO`, `DESCARTADO` ou NULL (contrato 3.6) | bronze | |
| latitude / longitude | DOUBLE | Só quando dentro do Brasil | bronze | RN-10 |
| chave_endereco | VARCHAR | `logradouro_normalizado|numero|bairro normalizado` | derivada | RN-11 |
| flag_possui_nome | BOOLEAN | herdada da Bronze | bronze | |
| flag_bairro_nao_padronizado | BOOLEAN | bairro fora do dicionário | derivada | RN-01 |
| flag_tipo_nao_reconhecido / flag_impacto_nao_reconhecido | BOOLEAN | texto informado sem mapeamento | derivada | RN-04/05 |
| flag_status_inferido | BOOLEAN | status assumido como `RECEBIDA` | derivada | RN-06 |
| flag_visao_inconsistente | BOOLEAN | classificação informada com `possui_imagem=false` | derivada | RN-07 |
| flag_coordenada_invalida | BOOLEAN | herdada da Bronze | bronze | |
| flag_coordenada_fora_area | BOOLEAN | coordenada válida mas fora do Brasil | derivada | RN-10 |
| flag_data_invalida | BOOLEAN | data ausente, irreconhecível ou implausível | derivada | RN-09 |
| registro_valido | BOOLEAN | atende à regra de registro válido | derivada | RN-12 |
| motivos_invalidade | VARCHAR | motivos separados por `; ` (NULL se válido) | derivada | RN-12 |
| _row_id, _batch_id | — | linhagem | bronze | |

### 3.2 `silver.denuncias_duplicadas` — quase-duplicatas removidas (10 linhas)

Mesmas colunas de `silver.denuncias` + `chave_denuncia_mantida` (registro que permaneceu). Auditoria da RN-11.

### 3.3 Tabelas de referência

| Tabela | Colunas | Conteúdo |
|---|---|---|
| silver.ref_tipo_obstaculo | chave, rotulo, ordem | contrato 3.1 (8 linhas) |
| silver.ref_impacto | chave, rotulo, ordem | contrato 3.2 (4) |
| silver.ref_status | chave, rotulo, ordem | contrato 3.3 (5) |
| silver.ref_visao_classificacao | chave, rotulo, ordem | contrato 3.4 (4, incl. sem fotografia) |
| silver.ref_bairros | chave_normalizada, bairro_oficial | dicionário RN-01 (8 bairros fictícios) |

---

## 4. Camada GOLD (somente `registro_valido = true`, RN-13; sem dados pessoais nem texto livre)

Cada tabela também é exportada como `data/processed/gold/<nome>.csv` (UTF-8, cabeçalho).

### 4.1 `gold.denuncias_por_bairro`
| Coluna | Tipo | Descrição |
|---|---|---|
| bairro | VARCHAR | Bairro padronizado |
| total | BIGINT | Denúncias válidas |
| possiveis_buracos | BIGINT | Com `visao_classificacao = POSSIBLE_POTHOLE` |
| impede_passagem | BIGINT | Com `impacto = IMPEDE_PASSAGEM` |
| com_fotografia | BIGINT | Com `possui_imagem = true` |
| percentual | DOUBLE | % do total válido (1 casa) |

### 4.2 `gold.denuncias_por_categoria`
| Coluna | Tipo | Descrição |
|---|---|---|
| categoria | VARCHAR | Chave do contrato 3.1 (todas as 8, inclusive com zero) |
| rotulo | VARCHAR | Rótulo do contrato |
| total | BIGINT | Denúncias válidas |
| possiveis_buracos | BIGINT | Com `POSSIBLE_POTHOLE` |
| percentual | DOUBLE | % do total válido |

### 4.3 `gold.denuncias_por_periodo`
| Coluna | Tipo | Descrição |
|---|---|---|
| granularidade | VARCHAR | `mensal` ou `semanal` |
| periodo | VARCHAR | `AAAA-MM` (mensal) ou `AAAA-Www` (semana ISO) |
| inicio_periodo | DATE | 1º dia do mês / segunda-feira da semana |
| total | BIGINT | Denúncias válidas registradas no período (data local) |
| possiveis_buracos | BIGINT | Com `POSSIBLE_POTHOLE` |

### 4.4 `gold.denuncias_por_status`
| Coluna | Tipo | Descrição |
|---|---|---|
| status | VARCHAR | Chave do contrato 3.3 (todas as 5) |
| rotulo | VARCHAR | Rótulo |
| total | BIGINT | Denúncias válidas |
| percentual | DOUBLE | % do total válido |

### 4.5 `gold.resultado_visao`
| Coluna | Tipo | Descrição |
|---|---|---|
| classificacao | VARCHAR | `POSSIBLE_POTHOLE`, `NOT_IDENTIFIED`, `INCONCLUSIVE` ou NULL (sem fotografia) |
| rotulo | VARCHAR | Rótulo do contrato 3.4 |
| total | BIGINT | Denúncias válidas |
| percentual | DOUBLE | % do total válido |

### 4.6 `gold.qualidade_registros`
| Coluna | Tipo | Descrição |
|---|---|---|
| ordem | INTEGER | Ordem de exibição |
| metrica | VARCHAR | `linhas_raw`, `linhas_bronze`, `duplicatas_removidas`, `datas_invalidas`, `coordenadas_invalidas`, `campos_obrigatorios_ausentes`, `percentual_registros_validos`, `linhas_silver`, `duplicatas_negocio_removidas`, `registros_validos` |
| valor | DOUBLE | Valor da métrica |
| descricao | VARCHAR | Definição em português |

### 4.7 `gold_snapshot.json` (contrato 4.8)

| Campo | Tipo | Conteúdo |
|---|---|---|
| disponivel | bool | sempre `true` |
| gerado_em | string ISO 8601 UTC | instante da geração |
| execucao_id | string | `_batch_id` da execução |
| inclui_simulados | bool | `true` se algum registro válido é simulado |
| fontes | lista `{nome, linhas}` | `denuncias_simuladas.csv` e `api_export` com linhas na RAW |
| denuncias_por_bairro | lista `{bairro, total, possiveis_buracos}` | de 4.1 |
| denuncias_por_categoria | lista `{categoria, rotulo, total}` | de 4.2 |
| denuncias_por_periodo | lista `{periodo, total}` | de 4.3, granularidade mensal |
| denuncias_por_status | lista `{status, rotulo, total}` | de 4.4 |
| resultado_visao | lista `{classificacao, rotulo, total}` | de 4.5 |
| qualidade | objeto | `linhas_raw`, `linhas_bronze`, `duplicatas_removidas`, `datas_invalidas`, `coordenadas_invalidas`, `campos_obrigatorios_ausentes`, `percentual_registros_validos` (contrato) + extensões `linhas_silver`, `duplicatas_negocio_removidas`, `registros_validos` |
| denuncias_por_semana | lista `{periodo, total}` | **extensão** (não exigida pelo contrato): série semanal ISO |

### 4.8 Relatório de qualidade — `data/processed/relatorio_qualidade.json` / `.md`

Contagens por camada, soma de cada flag Bronze/Silver, motivos de invalidade (RN-12), resultado da extração da API e
lista de verificações automáticas (`verificacao`, `ok`, `detalhe`) com a situação final `APROVADO`/`REPROVADO`.
