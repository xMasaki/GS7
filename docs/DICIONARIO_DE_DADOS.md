# AcessaCidade — Dicionário de dados consolidado

> Todos os dados do produto, da entrada do cidadão até a camada Gold. Fontes de verdade: o schema real em
> `app/backend/acessacidade_api/db.py`, a exportação em `app/backend/acessacidade_api/services/export.py`,
> o contrato [`CONTRATOS_DE_INTEGRACAO.md`](CONTRATOS_DE_INTEGRACAO.md) (§3, §4.1, §4.7, §4.8) e o
> dicionário detalhado do pipeline [`02-Big-Data-Architecture/docs/DICIONARIO_DE_DADOS.md`](../02-Big-Data-Architecture/docs/DICIONARIO_DE_DADOS.md).
>
> Todos os dados de demonstração são **simulados** (cidade fictícia "Cidade Exemplo", `simulado=true`,
> `origem=SIMULADO`, `origem_dado=SIMULADO`); as fotos de teste são **sintéticas**.

## Classificação LGPD usada neste documento

| Classe | Significado | Tratamento |
|---|---|---|
| **PESSOAL** | Identifica ou pode identificar uma pessoa | Opcional, guardado só no SQLite, nunca retornado pela API, nunca exportado, nunca registrado em log |
| **PESSOAL INDIRETO** | Pode levar a uma pessoa se combinado (ex.: foto, texto livre, local exato) | Minimizado: foto sem EXIF/GPS e com rostos borrados; texto livre não vai para a Gold; orientação na tela para não escrever dados pessoais |
| **OPERACIONAL** | Dado da ocorrência ou do processo, sem identificar pessoa | Público na API (é o objetivo do serviço) |
| **TÉCNICO** | Controle interno do sistema | Não exposto, ou exposto só como derivado |
| **AGREGADO** | Contagens e percentuais | Público; sem dados pessoais nem texto livre |

Mapeamento completo (inventário, fluxo, bases legais sugeridas, minimização, direitos do titular): `06-Secure-DevOps-Cloud/docs/LGPD_MAPEAMENTO_DADOS_PESSOAIS.md`.

---

## 1. Banco operacional SQLite (`DATA_DIR/acessacidade.db`)

Criado por migração idempotente (`Database.migrar()`), `PRAGMA journal_mode = WAL`, `foreign_keys = ON`.
Versão do schema: **1**. O arquivo fica em `data/runtime/` (ignorado pelo Git) ou em `DATABASE_PATH`.

### 1.1 Tabela `denuncias`

| Coluna | Tipo SQLite | Nulo? | Restrição / regra | Exposta na API? | LGPD |
|---|---|---|---|---|---|
| `id` | INTEGER | não | `PRIMARY KEY AUTOINCREMENT` | sim | OPERACIONAL |
| `protocolo` | TEXT | sim* | `UNIQUE`; `AC-{ANO}-{id com 6 dígitos}` (regex `^AC-\d{4}-\d{6}$`) | sim | OPERACIONAL |
| `criado_em` | TEXT | não | ISO 8601 UTC (`2026-11-14T13:22:05Z`) | sim | OPERACIONAL |
| `atualizado_em` | TEXT | não | ISO 8601 UTC | sim | OPERACIONAL |
| `nome` | TEXT | sim | até 80 caracteres; apelido/identificação fictícia permitida | **nunca** | **PESSOAL** |
| `logradouro` | TEXT | não | 3–120 caracteres | sim | OPERACIONAL (local do problema, não da pessoa) |
| `numero` | TEXT | sim | até 10 caracteres (`120`, `S/N`) | sim | OPERACIONAL |
| `bairro` | TEXT | não | 2–80 caracteres | sim | OPERACIONAL |
| `cidade` | TEXT | não | até 80; vazio → `CIDADE_PADRAO` (ou "Não informada") | sim | OPERACIONAL |
| `ponto_referencia` | TEXT | sim | até 150 | sim | PESSOAL INDIRETO (texto livre) |
| `tipo_obstaculo` | TEXT | não | `CHECK` com as 8 chaves do contrato §3.1 | sim | OPERACIONAL |
| `descricao` | TEXT | não | 10–1000 caracteres | sim | PESSOAL INDIRETO (texto livre) |
| `impacto` | TEXT | não | `CHECK` com as 4 chaves do contrato §3.2 | sim | OPERACIONAL |
| `latitude` | REAL | sim | −90..90; junto com `longitude` ou nenhuma | sim | PESSOAL INDIRETO (local exato) |
| `longitude` | REAL | sim | −180..180 | sim | PESSOAL INDIRETO (local exato) |
| `status` | TEXT | não | `CHECK` com as 5 chaves do contrato §3.3 | sim | OPERACIONAL |
| `origem` | TEXT | não | `CHECK IN ('WEB','RPA','SIMULADO','API')` | sim | OPERACIONAL |
| `simulado` | INTEGER | não | 0/1, padrão 0 | sim (booleano) | TÉCNICO |
| `consentimento` | INTEGER | não | padrão 1; o registro só é aceito com consentimento verdadeiro | não | TÉCNICO (prova do aceite) |
| `imagem_dir` | TEXT | sim | pasta em `DATA_DIR/uploads/<uuid>/` com as 7 etapas JPEG | não (vira `possui_imagem` e URLs) | TÉCNICO |
| `visao_json` | TEXT | sim | resultado da triagem serializado (`classificacao`, `rotulo`, `pontuacao`, `explicacao`, `metricas`, `deteccoes`, `versao_algoritmo`, `aviso`) | sim (objeto `visao`) | OPERACIONAL |
| `visao_classificacao` | TEXT | sim | `POSSIBLE_POTHOLE`, `NOT_IDENTIFIED`, `INCONCLUSIVE` ou nulo (sem foto) | sim | OPERACIONAL |
| `visao_pontuacao` | REAL | sim | 0..1, pontuação heurística (**não é probabilidade**) | sim | OPERACIONAL |
| `revisao_humana` | TEXT | sim | `CONFIRMADO`, `DESCARTADO` ou nulo | sim | OPERACIONAL |

\* `protocolo` é preenchido logo após o `INSERT` (depende do `id`).
Índices: `criado_em`, `status`, `bairro`, `tipo_obstaculo`, `simulado`.

### 1.2 Tabela `historico_status`

| Coluna | Tipo | Nulo? | Regra | LGPD |
|---|---|---|---|---|
| `id` | INTEGER | não | `PRIMARY KEY AUTOINCREMENT` | TÉCNICO |
| `denuncia_id` | INTEGER | não | `REFERENCES denuncias(id) ON DELETE CASCADE`; índice | TÉCNICO |
| `status` | TEXT | não | chave do contrato §3.3 | OPERACIONAL |
| `alterado_em` | TEXT | não | ISO 8601 UTC | OPERACIONAL |
| `observacao` | TEXT | sim | obrigatória para `ENCAMINHADA` e `RESOLVIDA` | OPERACIONAL (escrita pela equipe) |

### 1.3 Tabela `schema_version`

| Coluna | Tipo | Regra |
|---|---|---|
| `versao` | INTEGER | `PRIMARY KEY` (versão aplicada da migração) |
| `aplicada_em` | TEXT | ISO 8601 UTC |

### 1.4 Arquivos de execução em `DATA_DIR` (não versionados)

| Caminho | Conteúdo | LGPD |
|---|---|---|
| `uploads/<uuid>/original.jpg` | Foto **sanitizada** (re-codificada sem EXIF/GPS, redimensionada, rostos borrados); o arquivo bruto nunca é salvo | PESSOAL INDIRETO (minimizada) |
| `uploads/<uuid>/{cinza,filtrada,contraste,bordas,mascara,contornos}.jpg` | Etapas intermediárias da triagem | PESSOAL INDIRETO (minimizada) |
| `gold_snapshot.json` | Último snapshot Gold publicado pelo pipeline (§5) | AGREGADO |

---

## 2. Objeto público `Denuncia` (respostas da API)

Formato completo no contrato §4.1. Resumo dos campos e da origem de cada um:

| Campo | Origem | Observação |
|---|---|---|
| `id`, `protocolo`, `criado_em`, `atualizado_em` | colunas homônimas | |
| `logradouro`, `numero`, `bairro`, `cidade`, `ponto_referencia`, `descricao`, `latitude`, `longitude` | colunas homônimas | |
| `tipo_obstaculo` + `tipo_obstaculo_rotulo` | coluna + rótulo do contrato §3.1 | |
| `impacto` + `impacto_rotulo` | coluna + rótulo §3.2 | |
| `status` + `status_rotulo` | coluna + rótulo §3.3 | |
| `origem` | coluna | `WEB`, `RPA`, `SIMULADO`, `API` |
| `simulado` | coluna (0/1 → booleano) | selo SIMULADO na interface |
| `possui_imagem` | derivado de `imagem_dir` | |
| `visao` | `visao_json` + URLs `/api/denuncias/{id}/imagens/{etapa}` | `null` sem foto; inclui o `aviso` de triagem inicial |
| `revisao_humana` | coluna | |
| `historico` | tabela `historico_status` | **somente** no detalhe `GET /api/denuncias/{ref}` |
| `mensagem` | gerado | somente na resposta 201 do `POST /api/denuncias` |

**Nunca** aparecem: `nome`, `consentimento`, `imagem_dir`, caminhos de disco.

---

## 3. Exportação para o pipeline — `GET /api/export/denuncias?formato=csv` (`X-Pipeline-Token`)

21 colunas, nesta ordem (CSV UTF-8 com cabeçalho; `formato=json` devolve `{"colunas", "linhas", "exportado_em"}`):

| # | Coluna | Formato | LGPD |
|---|---|---|---|
| 1 | `id` | inteiro | OPERACIONAL |
| 2 | `protocolo` | `AC-AAAA-NNNNNN` | OPERACIONAL |
| 3 | `criado_em` | ISO 8601 UTC | OPERACIONAL |
| 4 | `atualizado_em` | ISO 8601 UTC | OPERACIONAL |
| 5 | `logradouro` | texto | OPERACIONAL |
| 6 | `numero` | texto | OPERACIONAL |
| 7 | `bairro` | texto | OPERACIONAL |
| 8 | `cidade` | texto | OPERACIONAL |
| 9 | `ponto_referencia` | texto livre | PESSOAL INDIRETO |
| 10 | `tipo_obstaculo` | chave §3.1 | OPERACIONAL |
| 11 | `descricao` | texto livre | PESSOAL INDIRETO |
| 12 | `impacto` | chave §3.2 | OPERACIONAL |
| 13 | `latitude` | decimal com ponto ou vazio | PESSOAL INDIRETO |
| 14 | `longitude` | decimal com ponto ou vazio | PESSOAL INDIRETO |
| 15 | `status` | chave §3.3 | OPERACIONAL |
| 16 | `origem` | chave §3.5 | OPERACIONAL |
| 17 | `simulado` | `true` / `false` | TÉCNICO |
| 18 | `possui_imagem` | `true` / `false` | OPERACIONAL |
| 19 | `visao_classificacao` | chave §3.4 ou vazio | OPERACIONAL |
| 20 | `visao_pontuacao` | 0..1 ou vazio | OPERACIONAL |
| 21 | `revisao_humana` | `CONFIRMADO`, `DESCARTADO` ou vazio | OPERACIONAL |

Sem nome do denunciante (verificado por `app/backend/tests/test_api_pipeline.py::test_export_csv_e_json_sem_nome`).
O pipeline salva a resposta sem alteração em `data/exports/denuncias_api_<timestamp>.csv` (ignorado pelo Git).

---

## 4. Fonte simulada do pipeline — `data/samples/denuncias_simuladas.csv`

Arquivo **propositalmente "bagunçado"** (gerado por script com semente fixa, 271 linhas) para exercitar a limpeza.
Tem as **21 colunas da exportação** (com grafias, formatos de data, vírgula decimal e rótulos variados) **mais 2**:

| Coluna extra | Conteúdo | LGPD |
|---|---|---|
| `nome_denunciante` | Nome **simulado** ("Pessoa Simulada 060") — existe para demonstrar a minimização: só a RAW o guarda; a Bronze mantém apenas `flag_possui_nome` | PESSOAL (simulado) |
| `origem_dado` | Sempre `SIMULADO` | TÉCNICO |

O `protocolo` usa o prefixo `SIM-` (não colide com protocolos reais `AC-`). Descrição da geração:
`data/samples/LEIAME_denuncias_simuladas.md`.

---

## 5. Camadas do pipeline (DuckDB `data/processed/warehouse/acessacidade.duckdb`)

Resumo; colunas, tipos e regras (RN-xx) no [dicionário detalhado do pipeline](../02-Big-Data-Architecture/docs/DICIONARIO_DE_DADOS.md)
e em `02-Big-Data-Architecture/docs/REGRAS_DE_NEGOCIO.md`. Volumes de uma execução real local (`--sem-api`, só fonte simulada).

| Camada | Tabelas | O que acontece | Volume (`--sem-api`) | LGPD |
|---|---|---|---|---|
| **RAW** | `raw.denuncias_simuladas`, `raw.denuncias_app`, `raw.log_cargas` | Cópia fiel, tudo `VARCHAR`, + metadados de linhagem (`_source_file`, `_ingested_at`, `_row_id`, `_batch_id`) | 271 linhas | contém `nome_denunciante` **simulado** (só aqui) |
| **BRONZE** | `bronze.denuncias` | Tipos, datas em ISO UTC, coordenadas (vírgula/ponto), ausentes, deduplicação técnica, flags de qualidade; nome substituído por `flag_possui_nome` | 260 linhas | sem nome |
| **SILVER** | `silver.denuncias`, `silver.denuncias_duplicadas`, tabelas de referência | Padroniza categorias, bairros, status, impacto e visão para as chaves do contrato; deduplicação de negócio (mesmo endereço + tipo + dia); `registro_valido` | 250 denúncias únicas (211 válidas); 10 quase-duplicatas | texto livre mantido, sem nome |
| **GOLD** | `gold.denuncias_por_bairro`, `gold.denuncias_por_categoria`, `gold.denuncias_por_periodo` (mensal e semanal), `gold.denuncias_por_status`, `gold.resultado_visao`, `gold.qualidade_registros` | Somente `registro_valido = true`; agregados; exportados em `data/processed/gold/*.csv` | — | **AGREGADO**: sem dados pessoais nem texto livre |

### 5.1 Snapshot Gold (`gold_snapshot.json` → `POST /api/pipeline/gold` → `GET /api/indicadores/analiticos`)

| Chave | Conteúdo |
|---|---|
| `disponivel`, `gerado_em`, `execucao_id`, `inclui_simulados` | Metadados da execução |
| `fontes` | `[{"nome", "linhas"}]` — fonte simulada e exportação da API |
| `denuncias_por_bairro` | `bairro`, `total`, `possiveis_buracos` |
| `denuncias_por_categoria` | `categoria`, `rotulo`, `total` |
| `denuncias_por_periodo` | `periodo` (`AAAA-MM`), `total` |
| `denuncias_por_status` | `status`, `rotulo`, `total` |
| `resultado_visao` | `classificacao`, `rotulo`, `total` |
| `qualidade` | `linhas_raw`, `linhas_bronze`, `duplicatas_removidas`, `datas_invalidas`, `coordenadas_invalidas`, `campos_obrigatorios_ausentes`, `percentual_registros_validos` + extras `linhas_silver`, `duplicatas_negocio_removidas`, `registros_validos` |
| `denuncias_por_semana` | extra: `periodo` (`AAAA-Www`), `total` |

As chaves extras estão registradas como desvio aceito no contrato §12.

---

## 6. Indicadores operacionais — `GET /api/indicadores`

Calculados em tempo real sobre o SQLite (contrato §4.6): `total`, `possiveis_buracos`, `inconclusivas`,
`nao_identificadas`, `sem_imagem`, listas `por_categoria`, `por_bairro`, `por_status`, `por_resultado_visao`
(inclui a chave `SEM_IMAGEM`, ver §12 do contrato), `por_origem`, `por_dia`, `recentes` (até 5 `Denuncia`),
`inclui_simulados`, `gerado_em`. Classe LGPD: **AGREGADO** (os `recentes` seguem as regras do objeto público).

## 7. Outros conjuntos de dados do repositório

| Caminho | Conteúdo | Natureza |
|---|---|---|
| `app/backend/acessacidade_api/seed/denuncias_demo.json` | Seed de demonstração (`SEED_DEMO_DATA=true`), nunca com `ENCAMINHADA`/`RESOLVIDA` | Simulado |
| `data/samples/fotos/` | Imagens de teste da visão (pasta `SEED_FOTOS_DIR`) | Sintéticas |
| `data/processed/relatorio_qualidade.json` / `.md` | Relatório de qualidade do pipeline | Derivado de simulados |
| `05-Robotic-Process-Automation/spreadsheet/denuncias_para_cadastro_SIMULADAS.xlsx` | Entrada do robô UiPath | Simulado |
| `03-Business-Intelligence-Startup/dashboard/AcessaCidade_indicadores.xlsx` | Gold exportada para Excel/Power BI | Derivado de simulados |
