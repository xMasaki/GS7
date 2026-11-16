# AcessaCidade — Contratos de Integração entre Componentes

> Documento normativo. Todos os componentes do AcessaCidade (frontend, backend, visão computacional,
> helper de IA, pipeline de dados, RPA, DevOps) seguem os nomes, formatos e caminhos definidos aqui.
> Qualquer mudança de contrato deve ser feita **primeiro neste arquivo** e depois nos componentes.

---

## 1. Visão geral e decisões de arquitetura

| Decisão | Escolha | Justificativa |
|---|---|---|
| Produto | Um único sistema web responsivo (SPA) servido pelo próprio backend | Uma URL pública, um container, deploy simples na Azure (ACI) |
| Frontend | HTML + CSS + JavaScript puro (ES modules), sem build e sem CDN | Leve em celulares de entrada, funciona sem dependências externas, CSP restritiva |
| Backend | Python 3.11 + FastAPI + Uvicorn | Documentação OpenAPI automática (`/docs`), mesmo ecossistema da visão computacional |
| Banco operacional | SQLite (arquivo em `DATA_DIR`) | Suficiente para o MVP; sem servidor; trocável por PostgreSQL no futuro |
| Visão computacional | OpenCV clássico (sem redes neurais) | Explicável, roda em CPU, alinhado ao conteúdo da disciplina |
| IA generativa | API compatível com OpenAI via OpenRouter, com modo alternativo baseado em regras | Chave fora do código; o sistema continua útil sem a API |
| Dados analíticos | DuckDB + Pandas, camadas Raw → Bronze → Silver → Gold | Reaproveita o notebook da Aula 06 |
| Orquestração | Apache Airflow 2.10.5 (Python 3.11, via Docker) + runner local equivalente | Airflow não roda nativamente no Windows |
| Observabilidade | `prometheus_client` no backend + Prometheus + Grafana | 4 métricas de ouro e alertas |
| Nuvem | Azure Container Registry + Azure Container Instances via Terraform | Reaproveita o exercício de referência (Calango TI) |

---

## 2. Estrutura do repositório e responsabilidade de cada pasta

```text
(raiz do repositório)
├── app/backend/acessacidade_api/        # API FastAPI (pacote Python)
├── app/backend/tests/                   # testes da API (test_api_*.py)
├── app/frontend/                        # SPA estática (index.html, css/, js/)
├── 01-Generative-AI-Engineering/src/acessacidade_helper/   # pacote do helper de IA
├── 01-Generative-AI-Engineering/prompts/                   # prompts lidos em tempo de execução
├── 02-Big-Data-Architecture/src/acessacidade_pipeline/     # pacote do pipeline
├── 02-Big-Data-Architecture/dags/                          # DAG do Airflow
├── 04-Applied-Computer-Vision/src/acessacidade_vision/     # pacote de visão computacional
├── 05-Robotic-Process-Automation/UiPath/AcessaCidade.RPA/  # projeto UiPath
├── 06-Secure-DevOps-Cloud/docker/Dockerfile                # imagem da aplicação
├── 06-Secure-DevOps-Cloud/terraform/                       # IaC Azure
├── 06-Secure-DevOps-Cloud/monitoring/                      # Prometheus, Grafana, alertas
├── .github/workflows/                                      # CI/CD DevSecOps
├── docker-compose.yml                                      # app (+ monitoramento via profile)
├── data/samples/   data/exports/   data/processed/
└── docs/
```

### 2.1 Importação dos pacotes (sem duplicar código)

Os pacotes ficam nas pastas das disciplinas e são **importados** pelo backend:

| Pacote | Caminho no repositório | Usado por |
|---|---|---|
| `acessacidade_api` | `app/backend` | uvicorn, testes |
| `acessacidade_helper` | `01-Generative-AI-Engineering/src` | backend (`POST /api/assistente`) |
| `acessacidade_pipeline` | `02-Big-Data-Architecture/src` | DAG do Airflow, runner local |
| `acessacidade_vision` | `04-Applied-Computer-Vision/src` | backend (`POST /api/visao/analisar`, `POST /api/denuncias`) |

- Testes: `pytest.ini` da raiz já configura o `pythonpath` com essas quatro pastas.
- Execução local: `acessacidade_api/__init__.py` insere automaticamente `01-.../src` e `04-.../src`
  no `sys.path` quando os pacotes não estão importáveis (raiz do repositório = `Path(__file__).resolve().parents[3]`).
- Docker: `PYTHONPATH=/app/app/backend:/app/01-Generative-AI-Engineering/src:/app/04-Applied-Computer-Vision/src`.

### 2.2 Ambiente Python

- Python **3.11** (o mesmo da imagem Docker e da imagem do Airflow `apache/airflow:2.10.5-python3.11`).
- Venv na raiz: `.venv` — `python -m pip install -r requirements-dev.txt`.
- Testes: `python -m pytest` na raiz. Nomes de arquivos de teste **únicos** por componente:
  `test_api_*.py`, `test_helper_*.py`, `test_pipeline_*.py`, `test_vision_*.py`, `test_rpa_*.py`,
  `test_devops_*.py`, `test_maker_*.py`.

---

## 3. Domínio: enumerações (chave → rótulo exibido)

As **chaves** trafegam na API e no banco. Os **rótulos** aparecem na interface (e são o texto visível
das opções dos `<select>`, usado pelo UiPath).

### 3.1 `tipo_obstaculo`

| Chave | Rótulo |
|---|---|
| `BURACO_CALCADA` | Buraco na calçada |
| `BURACO_VIA` | Buraco na via ou travessia |
| `CALCADA_DANIFICADA` | Calçada quebrada ou desnivelada |
| `RAMPA_IRREGULAR` | Rampa ausente ou irregular |
| `PISO_TATIL` | Piso tátil ausente ou danificado |
| `OBSTACULO_FIXO` | Obstáculo fixo (poste, lixeira, placa) |
| `OBSTACULO_TEMPORARIO` | Obstáculo temporário (entulho, veículo, obra) |
| `OUTRO` | Outro |

### 3.2 `impacto`

| Chave | Rótulo |
|---|---|
| `IMPEDE_PASSAGEM` | Impede a passagem |
| `DIFICULTA_PASSAGEM` | Dificulta a passagem |
| `RISCO_QUEDA` | Risco de queda ou acidente |
| `BAIXO_IMPACTO` | Baixo impacto |

### 3.3 `status`

| Chave | Rótulo | Significado (usado também pelo helper) |
|---|---|---|
| `RECEBIDA` | Recebida | A denúncia foi registrada no AcessaCidade. |
| `EM_ANALISE` | Em análise | A equipe do AcessaCidade está verificando as informações. |
| `AGUARDANDO_REVISAO` | Aguardando revisão | A triagem automática da foto terminou e uma pessoa precisa revisar o resultado. |
| `ENCAMINHADA` | Encaminhada | A equipe registrou que a ocorrência foi encaminhada ao responsável. |
| `RESOLVIDA` | Resolvida | A equipe registrou a ocorrência como resolvida. **Não representa confirmação de órgão público.** |

Regras:
- Ao criar: `RECEBIDA` (histórico: "Denúncia registrada").
- Se havia foto e a triagem rodou: muda automaticamente para `AGUARDANDO_REVISAO`
  (histórico: "Triagem automática da fotografia concluída; aguardando revisão humana").
- Demais mudanças **somente** via `PATCH /api/denuncias/{id}/status` com `X-Admin-Token`.
- `RESOLVIDA` e `ENCAMINHADA` exigem `observacao` não vazia.
- Dados de demonstração (seed) **nunca** usam `ENCAMINHADA` nem `RESOLVIDA`.

### 3.4 `visao.classificacao`

| Chave | Rótulo |
|---|---|
| `POSSIBLE_POTHOLE` | Possível buraco identificado |
| `NOT_IDENTIFIED` | Nenhum indício suficiente de buraco |
| `INCONCLUSIVE` | Análise inconclusiva |
| *(nulo)* | Sem fotografia (não analisada) |

### 3.5 `origem`

`WEB` (formulário), `RPA` (robô UiPath), `SIMULADO` (seed de demonstração), `API` (chamada direta).

### 3.6 `revisao_humana`

`null` (não revisada), `CONFIRMADO` (pessoa confirmou o problema na foto), `DESCARTADO` (pessoa descartou).

### 3.7 Protocolo

`AC-{ANO}-{ID com 6 dígitos}` — exemplo: `AC-2026-000012`. Regex: `^AC-\d{4}-\d{6}$`.

---

## 4. API REST (backend)

Base: mesma origem do frontend. Documentação interativa: `GET /docs`. JSON em UTF-8, campos em
português `snake_case`. Erros: `{"detail": "mensagem em português"}` (padrão FastAPI) com status HTTP adequado.

| Método | Rota | Descrição | Auth |
|---|---|---|---|
| GET | `/health` | Saúde da aplicação | — |
| GET | `/metrics` | Métricas Prometheus | — |
| GET | `/api/meta/opcoes` | Enumerações com rótulos (seção 3) | — |
| GET | `/api/denuncias` | Lista paginada | — |
| POST | `/api/denuncias` | Cria denúncia (multipart, foto opcional) | rate limit |
| GET | `/api/denuncias/{ref}` | Detalhe por id numérico **ou** protocolo | — |
| GET | `/api/denuncias/{id}/imagens/{etapa}` | Imagem JPEG de uma etapa da triagem | — |
| PATCH | `/api/denuncias/{id}/status` | Altera status / revisão humana | `X-Admin-Token` |
| POST | `/api/visao/analisar` | Analisa uma foto sem salvar nada | rate limit |
| GET | `/api/indicadores` | Indicadores operacionais (tempo real, SQLite) | — |
| GET | `/api/indicadores/analiticos` | Último snapshot Gold publicado pelo pipeline | — |
| POST | `/api/pipeline/gold` | Pipeline publica o snapshot Gold | `X-Pipeline-Token` |
| GET | `/api/export/denuncias?formato=csv\|json` | Exportação anonimizada para o pipeline | `X-Pipeline-Token` |
| POST | `/api/assistente` | Pergunta ao AcessaCidade Helper | rate limit |

Se `ADMIN_TOKEN`/`PIPELINE_TOKEN` estiverem vazios, as rotas protegidas respondem **403**
("funcionalidade desativada neste ambiente"). Token errado → **401**. Comparação com `secrets.compare_digest`.

### 4.1 Objeto `Denuncia` (resposta pública — nunca contém o nome do denunciante)

```json
{
  "id": 12,
  "protocolo": "AC-2026-000012",
  "criado_em": "2026-11-14T13:22:05Z",
  "atualizado_em": "2026-11-14T13:22:06Z",
  "logradouro": "Rua Exemplo",
  "numero": "120",
  "bairro": "Centro",
  "cidade": "Cidade Exemplo",
  "ponto_referencia": "Em frente ao ponto de ônibus",
  "tipo_obstaculo": "BURACO_CALCADA",
  "tipo_obstaculo_rotulo": "Buraco na calçada",
  "descricao": "Buraco de aproximadamente 40 cm ...",
  "impacto": "IMPEDE_PASSAGEM",
  "impacto_rotulo": "Impede a passagem",
  "latitude": null,
  "longitude": null,
  "status": "AGUARDANDO_REVISAO",
  "status_rotulo": "Aguardando revisão",
  "origem": "WEB",
  "simulado": false,
  "possui_imagem": true,
  "visao": {
    "classificacao": "POSSIBLE_POTHOLE",
    "rotulo": "Possível buraco identificado",
    "pontuacao": 0.72,
    "explicacao": ["Região escura com área de 8,4% da imagem ...", "..."],
    "metricas": {"...": "..."},
    "deteccoes": [{"x": 120, "y": 80, "largura": 200, "altura": 140, "area_px": 21000}],
    "imagens": {
      "original": "/api/denuncias/12/imagens/original",
      "cinza": "/api/denuncias/12/imagens/cinza",
      "filtrada": "/api/denuncias/12/imagens/filtrada",
      "contraste": "/api/denuncias/12/imagens/contraste",
      "bordas": "/api/denuncias/12/imagens/bordas",
      "mascara": "/api/denuncias/12/imagens/mascara",
      "contornos": "/api/denuncias/12/imagens/contornos"
    },
    "versao_algoritmo": "1.0.0",
    "aviso": "Triagem automática inicial. Não substitui avaliação técnica; requer revisão humana."
  },
  "revisao_humana": null,
  "historico": [
    {"status": "RECEBIDA", "status_rotulo": "Recebida", "alterado_em": "...", "observacao": "Denúncia registrada"}
  ]
}
```

- `visao` é `null` quando não houve foto.
- `historico` aparece **apenas** no detalhe (`GET /api/denuncias/{ref}`), não na listagem.
- Etapas válidas de imagem (ordem de exibição): `original`, `cinza`, `filtrada`, `contraste`, `bordas`, `mascara`, `contornos`.

### 4.2 `POST /api/denuncias` — `multipart/form-data`

| Campo | Obrigatório | Regra |
|---|---|---|
| `nome` | não | até 80 caracteres; pode ser apelido/identificação fictícia; **nunca** retornado pela API |
| `logradouro` | sim | 3–120 caracteres |
| `numero` | não | até 10 caracteres (ex.: "120", "S/N") |
| `bairro` | sim | 2–80 caracteres |
| `cidade` | não | até 80; vazio → `CIDADE_PADRAO` (ou "Não informada") |
| `ponto_referencia` | não | até 150 |
| `tipo_obstaculo` | sim | chave da seção 3.1 |
| `descricao` | sim | 10–1000 caracteres |
| `impacto` | sim | chave da seção 3.2 |
| `latitude` / `longitude` | não | números; ambos ou nenhum; lat −90..90, lon −180..180 |
| `consentimento` | sim | deve ser `true` (aceite dos termos de uso da foto e dos dados) |
| `origem` | não | `WEB` (padrão) ou `RPA` |
| `foto` | não | JPEG/PNG/WEBP, até `MAX_UPLOAD_MB`; validada por decodificação real, não pela extensão |

Resposta **201**: objeto `Denuncia` (com `historico`) + campo `mensagem`.
Erros de validação: **422** com `detail` em português legível.

### 4.3 `GET /api/denuncias`

Query: `status`, `bairro` (contém, sem diferenciar maiúsculas), `tipo_obstaculo`, `protocolo`,
`incluir_simulados` (padrão `true`), `pagina` (≥1, padrão 1), `limite` (1–100, padrão 20).
Ordenação: mais recentes primeiro.
Resposta: `{"itens": [Denuncia...], "total": 37, "pagina": 1, "limite": 20}`.

### 4.4 `PATCH /api/denuncias/{id}/status` (header `X-Admin-Token`)

Corpo JSON: `{"status": "EM_ANALISE", "observacao": "texto", "revisao_humana": "CONFIRMADO" | "DESCARTADO" | null}`.
Retorna a `Denuncia` atualizada (com `historico`).

### 4.5 `POST /api/visao/analisar` — `multipart/form-data` com campo `foto`

Não persiste nada. Resposta:
```json
{
  "classificacao": "INCONCLUSIVE", "rotulo": "Análise inconclusiva", "pontuacao": 0.41,
  "explicacao": ["..."], "metricas": {...}, "deteccoes": [...],
  "imagens": {"original": "data:image/jpeg;base64,...", "cinza": "data:...", "...": "..."},
  "versao_algoritmo": "1.0.0",
  "aviso": "Triagem automática inicial. Não substitui avaliação técnica; requer revisão humana."
}
```

### 4.6 `GET /api/indicadores?incluir_simulados=true`

```json
{
  "total": 37,
  "possiveis_buracos": 9,
  "inconclusivas": 6,
  "nao_identificadas": 10,
  "sem_imagem": 12,
  "por_categoria": [{"chave": "BURACO_CALCADA", "rotulo": "Buraco na calçada", "total": 11}],
  "por_bairro": [{"chave": "Centro", "rotulo": "Centro", "total": 8}],
  "por_status": [{"chave": "RECEBIDA", "rotulo": "Recebida", "total": 10}],
  "por_resultado_visao": [{"chave": "POSSIBLE_POTHOLE", "rotulo": "Possível buraco identificado", "total": 9}],
  "por_origem": [{"chave": "WEB", "rotulo": "WEB", "total": 20}],
  "por_dia": [{"data": "2026-11-10", "total": 3}],
  "recentes": [Denuncia, ...até 5],
  "inclui_simulados": true,
  "gerado_em": "2026-11-14T13:30:00Z"
}
```

### 4.7 Exportação para o pipeline — `GET /api/export/denuncias?formato=csv` (header `X-Pipeline-Token`)

Colunas (ordem fixa; **sem nome do denunciante**):
`id, protocolo, criado_em, atualizado_em, logradouro, numero, bairro, cidade, ponto_referencia,
tipo_obstaculo, descricao, impacto, latitude, longitude, status, origem, simulado, possui_imagem,
visao_classificacao, visao_pontuacao, revisao_humana`

- `criado_em`/`atualizado_em`: ISO 8601 UTC. `simulado`/`possui_imagem`: `true`/`false`.
- `formato=json` → `{"colunas": [...], "linhas": [{...}], "exportado_em": "..."}`.

### 4.8 Snapshot Gold — `POST /api/pipeline/gold` (header `X-Pipeline-Token`) e `GET /api/indicadores/analiticos`

O backend valida apenas que o corpo é um objeto JSON com `gerado_em` e salva em `DATA_DIR/gold_snapshot.json`.
`GET /api/indicadores/analiticos` → o snapshot salvo, ou `{"disponivel": false, "mensagem": "..."}` (200) se não houver.

```json
{
  "disponivel": true,
  "gerado_em": "2026-11-14T13:40:00Z",
  "execucao_id": "manual__2026-11-14T13:39:00",
  "inclui_simulados": true,
  "fontes": [{"nome": "denuncias_simuladas.csv", "linhas": 240}, {"nome": "api_export", "linhas": 12}],
  "denuncias_por_bairro": [{"bairro": "Centro", "total": 30, "possiveis_buracos": 7}],
  "denuncias_por_categoria": [{"categoria": "BURACO_CALCADA", "rotulo": "Buraco na calçada", "total": 50}],
  "denuncias_por_periodo": [{"periodo": "2026-10", "total": 80}],
  "denuncias_por_status": [{"status": "RECEBIDA", "rotulo": "Recebida", "total": 60}],
  "resultado_visao": [{"classificacao": "POSSIBLE_POTHOLE", "rotulo": "Possível buraco identificado", "total": 40}],
  "qualidade": {
    "linhas_raw": 252, "linhas_bronze": 240, "duplicatas_removidas": 12,
    "datas_invalidas": 5, "coordenadas_invalidas": 7, "campos_obrigatorios_ausentes": 9,
    "percentual_registros_validos": 91.7
  }
}
```

### 4.9 `POST /api/assistente`

Requisição:
```json
{
  "mensagem": "O que significa aguardando revisão?",
  "modo": "geral",
  "protocolo": "AC-2026-000012",
  "contexto_tela": "consulta",
  "historico": [{"papel": "usuario", "texto": "..."}, {"papel": "assistente", "texto": "..."}]
}
```
- `modo`: `geral` (padrão), `descricao` (ajudar a escrever a descrição do obstáculo), `explicar_resultado`.
- `protocolo` opcional; se ausente, o backend procura um protocolo no texto da mensagem (regex da seção 3.7).
- `historico`: no máximo as 6 últimas mensagens; cada texto até 1000 caracteres; `mensagem` 1–1000 caracteres.

Resposta:
```json
{
  "resposta": "texto em português",
  "fonte": "llm",
  "modelo": "openai/gpt-4o-mini",
  "denuncia_referenciada": "AC-2026-000012",
  "avisos": ["..."]
}
```
- `fonte`: `llm` (resposta do modelo) ou `fallback` (respostas baseadas em regras — sem chave, timeout ou erro da API).

### 4.10 `GET /health`

```json
{"status": "ok", "versao": "1.0.0", "ambiente": "development",
 "componentes": {"banco": "ok", "visao": "ok", "assistente": "llm" | "fallback"}}
```
Retorna 200 quando o banco responde; 503 com `"status": "degradado"` caso contrário.

---

## 5. Interface do pacote de visão computacional (`acessacidade_vision`)

```python
from acessacidade_vision import (
    analyze_image, sanitize_image, validate_image_bytes,
    AnalysisResult, VisionError, ALGORITHM_VERSION, STAGE_ORDER, CLASS_LABELS,
)

validate_image_bytes(data: bytes, max_bytes: int) -> None      # levanta VisionError(code, message_pt)
sanitize_image(data: bytes, *, max_side: int = 1600, blur_faces: bool = True) -> bytes
    # decodifica, remove metadados EXIF/GPS (re-encode JPEG), redimensiona, borra rostos (Haar cascade)
analyze_image(data: bytes) -> AnalysisResult

AnalysisResult:
    classification: str            # POSSIBLE_POTHOLE | NOT_IDENTIFIED | INCONCLUSIVE
    label: str                     # rótulo em português (seção 3.4)
    score: float                   # 0..1 — pontuação heurística, NÃO é probabilidade
    reasons: list[str]             # explicações em português
    metrics: dict                  # serializável em JSON (brilho, contraste, nitidez, área, etc.)
    detections: list[dict]         # {"x","y","largura","altura","area_px", ...}
    stages: dict[str, numpy.ndarray]   # chaves de STAGE_ORDER
    algorithm_version: str
    def to_dict(self) -> dict      # tudo menos `stages`, com chaves em português:
        # {"classificacao","rotulo","pontuacao","explicacao","metricas","deteccoes","versao_algoritmo","aviso"}
    def encode_stages(self, ext: str = ".jpg", quality: int = 85) -> dict[str, bytes]

STAGE_ORDER = ("original", "cinza", "filtrada", "contraste", "bordas", "mascara", "contornos")
```

O backend: valida → sanitiza → analisa → grava `encode_stages()` em
`DATA_DIR/uploads/<uuid>/<etapa>.jpg` (a "original" salva é a imagem **sanitizada**, nunca o arquivo bruto).

---

## 6. Interface do helper de IA (`acessacidade_helper`)

```python
from acessacidade_helper import AssistantService, AssistantRequest, AssistantResponse, extract_protocol

svc = AssistantService.from_env()     # OPENROUTER_API_KEY, OPENROUTER_MODEL, OPENROUTER_BASE_URL, ASSISTANT_TIMEOUT_SECONDS
svc.llm_enabled -> bool

req = AssistantRequest(
    mensagem: str,
    modo: str = "geral",                 # geral | descricao | explicar_resultado
    historico: list[dict] = [],          # [{"papel": "usuario"|"assistente", "texto": str}]
    denuncia: dict | None = None,        # objeto Denuncia público (seção 4.1) já buscado pelo backend
    protocolo_solicitado: str | None = None,   # protocolo pedido pelo usuário (mesmo se não encontrado)
    indicadores: dict | None = None,     # resumo de /api/indicadores (opcional)
    opcoes: dict | None = None,          # enumerações (seção 3)
    contexto_tela: str | None = None,
)
resp: AssistantResponse = svc.answer(req)
resp.resposta: str; resp.fonte: "llm" | "fallback"; resp.modelo: str | None; resp.avisos: list[str]
extract_protocol(texto: str) -> str | None
```

- O helper **não acessa o banco**: o backend busca a denúncia e a entrega no `AssistantRequest`.
- Se `protocolo_solicitado` foi informado e `denuncia` é `None`, a resposta deve dizer que o protocolo não foi encontrado — nunca inventar.
- Prompts lidos de `01-Generative-AI-Engineering/prompts/*.md` (caminho resolvido a partir do pacote; sobrescrevível por `ASSISTANT_PROMPTS_DIR`).

---

## 7. Frontend — rotas e identificadores estáveis (usados pelo UiPath)

SPA com rotas por hash:

| Rota | Tela |
|---|---|
| `#/` | Início (propósito, problema, botão registrar, indicadores resumidos, recentes, ODS 11) |
| `#/registrar` | Formulário de denúncia (aceita `?canal=rpa` → envia `origem=RPA`, ex.: `#/registrar?canal=rpa`) |
| `#/denuncia/{protocolo}` | Detalhe + análise da fotografia (todas as etapas) + histórico |
| `#/analise` | Testar a triagem de uma foto sem registrar denúncia |
| `#/consultar` | Consulta/listagem com filtros e busca por protocolo |
| `#/assistente` | AcessaCidade Helper (chat) |
| `#/painel` | Dashboard de indicadores (operacionais + analíticos do pipeline) |
| `#/revisao` | Área da equipe (token) para revisar e mudar status |
| `#/sobre` | Sobre, privacidade/LGPD, limites da triagem, ODS |

Identificadores do formulário (`id` = seletor primário; também `name` e `data-rpa` iguais ao campo da API):

| Elemento | `id` | `name` / `data-rpa` |
|---|---|---|
| formulário | `form-denuncia` | — |
| Nome | `campo-nome` | `nome` |
| Logradouro | `campo-logradouro` | `logradouro` |
| Número | `campo-numero` | `numero` |
| Bairro | `campo-bairro` | `bairro` |
| Cidade | `campo-cidade` | `cidade` |
| Ponto de referência | `campo-referencia` | `ponto_referencia` |
| Tipo de obstáculo (`<select>`, texto visível = rótulo 3.1) | `campo-tipo` | `tipo_obstaculo` |
| Descrição (`<textarea>`) | `campo-descricao` | `descricao` |
| Impacto (`<select>`, texto visível = rótulo 3.2) | `campo-impacto` | `impacto` |
| Latitude / Longitude | `campo-latitude` / `campo-longitude` | `latitude` / `longitude` |
| Fotografia (`<input type=file>`) | `campo-foto` | `foto` |
| Consentimento (checkbox) | `campo-consentimento` | `consentimento` |
| Botão enviar | `botao-enviar` | — |
| Caixa de sucesso | `resultado-envio` | — |
| Protocolo gerado (texto exato do protocolo) | `protocolo-gerado` | — |
| Caixa de erro | `erro-envio` | — |
| Botão "registrar outra" | `botao-nova-denuncia` | — |

Após o envio bem-sucedido, o formulário fica oculto e `#resultado-envio` aparece com `#protocolo-gerado`
e um link para `#/denuncia/{protocolo}`. `#botao-nova-denuncia` limpa e reexibe o formulário (o robô usa
esse botão ou recarrega a URL entre registros).

---

## 8. Dados

| Caminho | Conteúdo | Versionado? |
|---|---|---|
| `data/samples/denuncias_simuladas.csv` | Fonte simulada "bagunçada" para o pipeline (gerada por script com semente fixa, coluna `origem_dado=SIMULADO`) | sim |
| `data/samples/fotos/` | Imagens sintéticas de teste (geradas por script, identificadas como SINTÉTICAS) | sim |
| `data/exports/` | Exportações da API feitas pelo pipeline | não |
| `data/processed/` | Saídas Gold em CSV/JSON (para dashboard e BI) | sim (pequenas) |
| `data/runtime/` | SQLite + uploads em execução | **não** |
| `app/backend/acessacidade_api/seed/denuncias_demo.json` | Seed de demonstração (limpo, `simulado=true`) | sim |

**Dados simulados** sempre identificados (`simulado=true` / `origem=SIMULADO` / `origem_dado=SIMULADO`) e
usando a cidade fictícia **"Cidade Exemplo"**. Nada de nomes reais de pessoas. Nenhuma afirmação sobre ruas reais.

---

## 9. Variáveis de ambiente

Ver `.env.example` (fonte de verdade). Principais: `APP_ENV`, `APP_PORT`, `DATA_DIR`, `DATABASE_PATH`,
`MAX_UPLOAD_MB`, `SEED_DEMO_DATA`, `CIDADE_PADRAO`, `RATE_LIMIT_PER_MINUTE`, `ALLOWED_ORIGINS`,
`ADMIN_TOKEN`, `PIPELINE_TOKEN`, `OPENROUTER_API_KEY`, `OPENROUTER_MODEL`, `OPENROUTER_BASE_URL`,
`ASSISTANT_TIMEOUT_SECONDS`, `ACESSACIDADE_API_URL`, `FRONTEND_DIR` (padrão `app/frontend`).

---

## 10. Observabilidade — métricas expostas em `/metrics`

| Métrica | Tipo | Rótulos | Sinal de ouro |
|---|---|---|---|
| `acessacidade_http_requests_total` | Counter | `method`, `route`, `status` | Tráfego / Erros |
| `acessacidade_http_request_duration_seconds` | Histogram | `method`, `route` | Latência |
| `acessacidade_http_requests_in_progress` | Gauge | — | Saturação |
| `acessacidade_denuncias_criadas_total` | Counter | `origem`, `tem_foto` | Negócio |
| `acessacidade_visao_classificacoes_total` | Counter | `classificacao` | Negócio |
| `acessacidade_visao_duracao_seconds` | Histogram | — | Latência (CV) |
| `acessacidade_assistente_respostas_total` | Counter | `fonte` | Negócio |
| `process_*` (padrão do client: CPU, memória) | — | — | Saturação |

`route` usa o **template** da rota (ex.: `/api/denuncias/{ref}`), nunca o caminho com IDs, para evitar alta cardinalidade.

---

## 11. Segurança e LGPD (regras para todos os componentes)

- Nenhum segredo no código ou no Git; tudo por variável de ambiente / GitHub Secrets.
- Nome do denunciante: opcional, armazenado apenas no SQLite, nunca retornado nem exportado.
- Fotos: validadas por decodificação, re-encode (remove EXIF/GPS), redimensionadas, rostos borrados.
- Logs não registram nome, chave de API nem conteúdo completo de fotos.
- Cabeçalhos de segurança: CSP `default-src 'self'; img-src 'self' data: blob:; style-src 'self'; script-src 'self'; connect-src 'self'; frame-ancestors 'none'`,
  `X-Content-Type-Options: nosniff`, `Referrer-Policy: no-referrer`, `X-Frame-Options: DENY`,
  `Permissions-Policy: camera=(), microphone=(), geolocation=(self)`.
- Triagem de imagem é **apoio**, não decisão: revisão humana sempre disponível.
- O AcessaCidade **não é serviço oficial do governo**; status "Resolvida" é registro da equipe, não confirmação de órgão público.

---

## 12. Desvios aceitos e detalhes de implementação

Diferenças entre o texto original deste contrato e o que os componentes implementaram, **conferidas no
código** em 15/11/2026 e aceitas pela integração. Todas são aditivas ou mais tolerantes: nenhum consumidor
que siga as seções 1–11 quebra. Em caso de dúvida, vale o comportamento descrito aqui.

### 12.1 Formato real de `GET /api/meta/opcoes` (complementa §3 e §4)

Fonte: `app/backend/acessacidade_api/domain.py::opcoes` (rota em `routes/meta.py`). Cada enumeração é uma
**lista ordenada** de `{"chave", "rotulo"}`; `status` e `origem` trazem também `significado`:

```json
{
  "tipo_obstaculo": [{"chave": "BURACO_CALCADA", "rotulo": "Buraco na calçada"}, "..."],
  "impacto": [{"chave": "IMPEDE_PASSAGEM", "rotulo": "Impede a passagem"}, "..."],
  "status": [{"chave": "RECEBIDA", "rotulo": "Recebida", "significado": "A denúncia foi registrada no AcessaCidade."}, "..."],
  "classificacao_visao": [{"chave": "POSSIBLE_POTHOLE", "rotulo": "Possível buraco identificado"}, "..."],
  "origem": [{"chave": "WEB", "rotulo": "WEB", "significado": "Formulário web"}, "..."],
  "revisao_humana": [{"chave": "CONFIRMADO", "rotulo": "Pessoa confirmou o problema na foto"}, "..."],
  "etapas_imagem": ["original", "cinza", "filtrada", "contraste", "bordas", "mascara", "contornos"],
  "max_upload_mb": 5.0,
  "formatos_foto": ["image/jpeg", "image/png", "image/webp"],
  "aviso_triagem": "Triagem automática inicial. Não substitui avaliação técnica; requer revisão humana."
}
```

- A chave da classificação da visão é `classificacao_visao` (não `visao.classificacao`).
- `max_upload_mb` reflete a variável `MAX_UPLOAD_MB` do ambiente.

### 12.2 Chave extra `SEM_IMAGEM` em `por_resultado_visao` (§4.6)

`GET /api/indicadores` inclui em `por_resultado_visao` o item
`{"chave": "SEM_IMAGEM", "rotulo": "Sem fotografia (não analisada)", "total": N}` para as denúncias sem foto
(no banco, `visao_classificacao` é nulo). O valor é o mesmo do campo `sem_imagem`. `SEM_IMAGEM` **não** é
um valor válido de `visao_classificacao` no banco nem na exportação.

### 12.3 Chaves extras do snapshot Gold (§4.8)

Geradas por `02-Big-Data-Architecture/src/acessacidade_pipeline/gold.py`; o backend armazena e devolve o
objeto sem filtrar:

| Chave | Onde | Significado |
|---|---|---|
| `qualidade.linhas_silver` | `qualidade` | Denúncias únicas na Silver após a deduplicação de negócio |
| `qualidade.duplicatas_negocio_removidas` | `qualidade` | Quase-duplicatas removidas na Silver (mesmo endereço + tipo + dia, RN-11) |
| `qualidade.registros_validos` | `qualidade` | Denúncias únicas válidas, usadas nos agregados Gold |
| `denuncias_por_semana` | raiz | Série semanal ISO: `[{"periodo": "AAAA-Www", "total": N}]` |

Detalhes de cálculo: `duplicatas_removidas` = `linhas_raw − linhas_bronze` (duplicatas **técnicas**, linhas
idênticas) e `percentual_registros_validos` = `registros_validos ÷ linhas_silver × 100` (RN-12). O próprio
pipeline já envia `"disponivel": true`; `denuncias_por_periodo` contém só a granularidade mensal (`AAAA-MM`).

### 12.4 Respostas de `POST /api/pipeline/gold` (§4.8)

- **200** `{"mensagem": "Snapshot Gold publicado com sucesso.", "gerado_em": "<o gerado_em recebido>"}`.
- **413** se o corpo passar de 5 MB; **422** se não for JSON UTF-8 válido, não for objeto, ou não tiver
  `gerado_em` (texto não vazio); **401/403** conforme §4 (token).
- A gravação em `DATA_DIR/gold_snapshot.json` é atômica (arquivo temporário + `os.replace`).
- `GET /api/indicadores/analiticos` devolve o objeto salvo com `"disponivel": true` sobrescrito; se o
  arquivo faltar ou estiver ilegível, `{"disponivel": false, "mensagem": "..."}` com status 200.

### 12.5 CSP específica da página `/docs` (§11)

O middleware só acrescenta a CSP padrão quando a resposta ainda não tem uma. A página `/docs` (Swagger UI,
`main.py::_docs_html`) define a sua própria, válida **apenas** nela:

```text
default-src 'self'; img-src 'self' data: https://fastapi.tiangolo.com;
style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net;
script-src 'self' https://cdn.jsdelivr.net 'sha256-<hash do script inline exato>';
connect-src 'self'; frame-ancestors 'none'
```

O hash é calculado em tempo de execução sobre o script inline gerado pelo FastAPI. Todas as demais rotas
(SPA e API) mantêm a CSP padrão do §11, sem CDN e sem `unsafe-inline`. `/docs` precisa de internet para
carregar o Swagger UI do CDN jsDelivr.

### 12.6 Leniências de entrada em `POST /api/denuncias` (§4.2) e na listagem (§4.3)

Fonte: `services/denuncias.py::validar_entrada` e `routes/denuncias.py`.

| Campo | O contrato dizia | A implementação também aceita |
|---|---|---|
| `consentimento` | deve ser `true` | sem diferenciar maiúsculas: `true`, `1`, `on`, `sim`, `yes`, `s`, `y`, `t`. Valores negativos (`false`, `0`, `off`, `nao`, `não`, `no`, `n`, `f`) recebem a mensagem "é necessário aceitar os termos"; outros valores, "valor inválido" |
| `tipo_obstaculo`, `impacto`, `origem` | chave exata | chave sem diferenciar maiúsculas e com espaços nas pontas (convertida para maiúsculas); `origem` vazia → `WEB` |
| `latitude`, `longitude` | números | vírgula decimal (`-23,55`); vazio = não informado; `NaN`/infinito rejeitados |
| Campos de texto | limites de tamanho | espaços nas pontas removidos e espaços internos repetidos reduzidos a um (exceto `descricao`, que só perde os das pontas); os limites valem depois disso |
| `foto` | arquivo opcional | campo de arquivo enviado vazio pelo navegador = sem foto; texto não vazio no campo `foto` → 422 |
| Filtros `status`, `tipo_obstaculo`, `protocolo` (GET) | chave exata | sem diferenciar maiúsculas; `bairro` vazio é ignorado |

Formato do erro 422 de validação: `detail` é uma **lista**
`[{"loc": ["body", "<campo>"], "campo": "<campo>", "msg": "<mensagem em português>", "type": "value_error"}]`
(todos os erros de uma vez, consumida por `extrairDetalhes()` do frontend). Erros de imagem e de regra de
negócio simples continuam como texto em `detail`.

### 12.7 Variável `SEED_FOTOS_DIR` (§9)

Pasta das imagens **sintéticas** usadas pelo seed de demonstração (`SEED_DEMO_DATA=true`) para gerar a
triagem das denúncias simuladas. Padrão: `data/samples/fotos` (resolvido a partir da raiz do repositório);
vazio no `.env.example`. É interna e opcional — só precisa ser definida se a imagem Docker ou o ambiente
guardar as fotos sintéticas em outro caminho.
