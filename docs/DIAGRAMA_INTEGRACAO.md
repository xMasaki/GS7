# AcessaCidade — Diagramas de integração

> Como os componentes das 7 disciplinas formam **um único produto**. Os nomes de rotas, campos e arquivos
> seguem o contrato normativo [`CONTRATOS_DE_INTEGRACAO.md`](CONTRATOS_DE_INTEGRACAO.md). A visão textual
> da arquitetura está em [`ARQUITETURA_GERAL.md`](ARQUITETURA_GERAL.md).
>
> Os diagramas usam **Mermaid** (o GitHub desenha automaticamente). Os 5 blocos deste arquivo foram
> conferidos em 15/11/2026 renderizando-os com Mermaid 10.9.1 no Microsoft Edge (sem erro de sintaxe).
> A seção 6 separa as integrações **testadas de verdade** das que **dependem de ação manual**.

## 1. Arquitetura geral

```mermaid
flowchart LR
  subgraph Usuarios["Quem usa"]
    CID["Cidadão<br/>celular ou computador"]
    EQ["Equipe AcessaCidade<br/>revisão humana"]
    ONG["Associações e ONGs<br/>planilhas Excel"]
  end

  subgraph Fisico["07 · Maker Lab"]
    PLACA["Placa acessível no ponto de ônibus<br/>alto contraste, relevo, Braille, QR Code"]
  end

  subgraph App["Aplicação: um container, uma URL"]
    FE["Frontend SPA<br/>app/frontend<br/>HTML + CSS + JS puro"]
    API["Backend FastAPI<br/>app/backend/acessacidade_api"]
    CV["04 · acessacidade_vision<br/>OpenCV clássico"]
    HLP["01 · acessacidade_helper<br/>prompts + guardrails + fallback"]
    DB[("SQLite<br/>DATA_DIR/acessacidade.db")]
    UP[("Imagens das etapas<br/>DATA_DIR/uploads")]
    GS[("gold_snapshot.json<br/>DATA_DIR")]
  end

  LLM[("OpenRouter LLM<br/>opcional, exige chave")]

  subgraph Dados["02 · Big Data"]
    PIPE["Pipeline ELT<br/>Raw → Bronze → Silver → Gold<br/>DuckDB + Pandas"]
    AF["Airflow 2.10.5<br/>DAG acessacidade_elt_pipeline"]
    CSV[("data/samples/<br/>denuncias_simuladas.csv")]
    GOLD[("data/processed/gold")]
  end

  RPA["05 · Robô UiPath"]
  BI["03 · BI<br/>Lean Canvas, pitch,<br/>Excel / Power BI"]

  subgraph Ops["06 · DevOps e nuvem"]
    GHA["GitHub Actions<br/>pytest, Gitleaks, Semgrep, Trivy"]
    TF["Terraform<br/>RG + ACR + ACI"]
    PROM["Prometheus + Alertmanager<br/>+ Grafana"]
  end

  CID --> FE
  PLACA -- "QR abre #/registrar" --> FE
  EQ -- "#/revisao com X-Admin-Token" --> FE
  ONG --> RPA
  RPA -- "preenche #/registrar?canal=rpa" --> FE
  FE -- "REST /api/*" --> API
  API --> CV
  API --> HLP
  HLP -. "somente com chave" .-> LLM
  API --> DB
  API --> UP
  API --> GS
  AF --> PIPE
  CSV --> PIPE
  PIPE -- "GET /api/export/denuncias<br/>X-Pipeline-Token" --> API
  PIPE -- "POST /api/pipeline/gold<br/>X-Pipeline-Token" --> API
  PIPE --> GOLD
  GOLD --> BI
  GHA -- "build + deploy" --> TF
  TF -- "cria e atualiza" --> App
  PROM -- "scrape /metrics" --> API
```

## 2. Comunicação entre componentes — registro de uma denúncia com foto

```mermaid
sequenceDiagram
  autonumber
  actor C as Cidadão
  participant F as Frontend SPA (#/registrar)
  participant A as Backend FastAPI
  participant V as acessacidade_vision
  participant D as SQLite
  participant U as DATA_DIR/uploads
  participant M as /metrics (Prometheus)

  C->>F: preenche o formulário, anexa a foto e aceita o consentimento
  F->>F: valida campos obrigatórios no navegador (mensagens em português)
  F->>A: POST /api/denuncias (multipart/form-data)
  A->>A: rate limit, limite de corpo e validação dos campos (422 em português)
  A->>V: validate_image_bytes(foto, MAX_UPLOAD_MB)
  V-->>A: ok ou VisionError (422 / 413)
  A->>V: sanitize_image: remove EXIF/GPS, redimensiona, borra rostos
  A->>V: analyze_image(imagem sanitizada)
  V-->>A: AnalysisResult: classificação, pontuação heurística, explicação, 7 etapas
  A->>U: grava original sanitizada + cinza, filtrada, contraste, bordas, mascara, contornos
  A->>D: INSERT denuncias (status RECEBIDA) + historico_status
  A->>D: status AGUARDANDO_REVISAO + histórico da triagem
  A->>M: contadores de denúncias e de classificações
  A-->>F: 201 Denuncia + protocolo AC-AAAA-NNNNNN + mensagem
  F-->>C: mostra o protocolo (#protocolo-gerado) e o link do detalhe
  C->>F: abre #/denuncia/{protocolo}
  F->>A: GET /api/denuncias/{protocolo} e GET /api/denuncias/{id}/imagens/{etapa}
  A-->>F: detalhe com histórico e as 7 imagens JPEG
  Note over A,V: A triagem é apoio. O status muda para Encaminhada ou Resolvida<br/>somente pela equipe, via PATCH com X-Admin-Token.
```

## 3. Fluxo de dados — da aplicação ao painel analítico

```mermaid
flowchart LR
  subgraph APP["Aplicação"]
    S1[("SQLite<br/>tabela denuncias")]
    EXP["GET /api/export/denuncias?formato=csv<br/>sem nome do denunciante"]
    POST["POST /api/pipeline/gold"]
    SNAP[("DATA_DIR/gold_snapshot.json")]
    ANA["GET /api/indicadores/analiticos"]
    OPE["GET /api/indicadores<br/>tempo real"]
    PAINEL["#/painel<br/>operacional + analítico"]
  end

  subgraph PIPE["Pipeline 02 · DuckDB"]
    E1[("data/exports/<br/>denuncias_api_timestamp.csv")]
    E2[("data/samples/<br/>denuncias_simuladas.csv")]
    RAW["RAW<br/>cópia fiel + metadados de carga<br/>raw.denuncias_app, raw.denuncias_simuladas, raw.log_cargas"]
    BRZ["BRONZE<br/>tipos, datas ISO UTC, coordenadas,<br/>ausentes, dedup técnica, flags<br/>nome descartado: só flag_possui_nome"]
    SIL["SILVER<br/>categorias, bairros, status, impacto,<br/>dedup de negócio, registro_valido"]
    GLD["GOLD<br/>por bairro, categoria, período,<br/>status, resultado da visão, qualidade<br/>sem dados pessoais nem texto livre"]
    OUT[("data/processed/gold/*.csv<br/>gold_snapshot.json<br/>relatorio_qualidade")]
  end

  XLS["03 · dashboard/exportar_gold_para_excel.py<br/>AcessaCidade_indicadores.xlsx"]

  S1 --> EXP --> E1 --> RAW
  E2 --> RAW
  RAW --> BRZ --> SIL --> GLD --> OUT
  OUT --> POST --> SNAP --> ANA --> PAINEL
  S1 --> OPE --> PAINEL
  OUT --> XLS
```

## 4. Fluxo do cidadão

```mermaid
flowchart TD
  A["Encontra uma barreira na calçada<br/>ou vê a placa no ponto de ônibus"] --> B{"Como chega ao AcessaCidade?"}
  B -- "lê o QR Code da placa" --> C["#/registrar"]
  B -- "abre o site" --> I["#/ Início<br/>propósito, indicadores, recentes, ODS 11"]
  I --> C
  C --> D["Preenche endereço, tipo, impacto e descrição<br/>nome opcional; foto opcional; consentimento"]
  D --> E{"Dados válidos?"}
  E -- "não" --> D2["Mensagens de erro junto aos campos"] --> D
  E -- "sim" --> F["Recebe o protocolo AC-AAAA-NNNNNN"]
  F --> G{"Enviou foto?"}
  G -- "sim" --> H["Triagem automática inicial<br/>possível buraco / nenhum indício / inconclusiva<br/>status Aguardando revisão"]
  G -- "não" --> H2["Status Recebida"]
  H --> J["#/denuncia/protocolo<br/>vê as 7 etapas da imagem e a explicação"]
  H2 --> J
  J --> K["#/consultar<br/>acompanha o status pelo protocolo"]
  J --> L["#/assistente<br/>tira dúvidas em linguagem simples"]
  K --> M["Equipe revisa em #/revisao:<br/>Em análise, Encaminhada ou Resolvida<br/>registro da equipe, não confirmação de órgão público"]
  M --> K
```

## 5. Relação entre as 7 disciplinas

```mermaid
flowchart TB
  P(("AcessaCidade<br/>MVP único · ODS 11"))
  D1["01 · Generative AI<br/>Inteligência: AcessaCidade Helper"]
  D2["02 · Big Data<br/>Dados: pipeline Raw → Gold + Airflow"]
  D3["03 · BI & Startup<br/>Negócio: Lean Canvas, pitch, painel, Ficha Técnica"]
  D4["04 · Computer Vision<br/>Visão: triagem da foto com OpenCV"]
  D5["05 · RPA<br/>Automação: robô UiPath planilha → formulário"]
  D6["06 · DevOps & Cloud<br/>Produção: Docker, CI/CD, Terraform, Azure, observabilidade"]
  D7["07 · Maker Lab<br/>Físico: placa acessível com QR Code"]

  D1 -- "POST /api/assistente" --> P
  D4 -- "POST /api/denuncias com foto<br/>POST /api/visao/analisar" --> P
  D2 -- "export + snapshot Gold" --> P
  D5 -- "cadastra pelo formulário<br/>origem=RPA" --> P
  D7 -- "QR leva a #/registrar" --> P
  D6 -- "publica e monitora" --> P
  D3 -- "modelo de negócio e métricas<br/>sobre o produto" --> P
  D2 -- "Gold alimenta" --> D3
  D4 -- "resultado da visão<br/>vira indicador" --> D2
  D1 -- "explica o resultado<br/>da triagem" --> D4
  D6 -- "URL pública usada por" --> D5
  D6 -- "URL pública usada no QR de" --> D7
```

## 6. Integrações: o que é funcional e testado × o que depende de ação manual

Resultados reais da verificação de 15/11/2026 (máquina local, Windows 11): `python -m pytest` na raiz
→ **492 passed** (reconferido na auditoria); teste ponta a ponta `app/frontend/tests_e2e/e2e_acessacidade.py` (Playwright + Edge)
contra o backend real → **201/201 verificações OK** na auditoria (199/199 na execução que gerou as capturas em [`evidencias/mvp_local/`](../evidencias/mvp_local/LEIAME.md)).

| # | Integração | Contrato | Situação | Como foi verificado / o que falta |
|---|---|---|---|---|
| 1 | Frontend SPA ↔ Backend (todas as telas) | §4, §7 | **Funcional e testada** | E2E 199/199 (início, registrar, detalhe, consultar, análise, assistente, painel, revisão, sobre, 404; 1280 px e 390 px; sem erro de console/CSP) + `app/backend/tests/test_api_*.py` |
| 2 | Backend → Visão: registro com foto | §4.2, §5 | **Funcional e testada** | `test_api_denuncias.py::test_criar_com_foto_sintetica`; E2E; smoke real com uvicorn: `POST /api/denuncias` com foto sintética → 201, `AGUARDANDO_REVISAO`, 7 imagens servidas. Só com imagens **sintéticas** (fotos reais: ação manual, disciplina 04) |
| 3 | Backend → Visão: análise avulsa | §4.5 | **Funcional e testada** | `test_api_pipeline.py::test_visao_analisar_nao_persiste` e `::test_visao_analisar_rejeita_nao_imagem_e_ausencia`; E2E (`#/analise`) |
| 4 | Backend → Helper (modo alternativo por regras) | §4.9, §6 | **Funcional e testada** | `test_api_assistente.py` (fallback, protocolo existente, protocolo inexistente não inventado, rate limit) + `01-Generative-AI-Engineering/tests/`; E2E (`fonte: fallback`) |
| 5 | Helper → LLM real (OpenRouter) | §6 | **Depende de ação manual** | Cliente testado com respostas simuladas (`test_helper_llm_client.py`); chamada real exige `OPENROUTER_API_KEY` da equipe — ver `01-Generative-AI-Engineering/PENDENCIAS_E_ACOES_MANUAIS.txt` |
| 6 | Pipeline → Backend: exportação e publicação Gold | §4.7, §4.8 | **Funcional e testada** | `test_api_pipeline.py::test_export_csv_e_json_sem_nome`, `::test_gold_publicar_e_consultar`; `02-.../tests/test_pipeline_api.py` (API simulada); execução real do pipeline contra a API local na sessão do E2E, com a Gold exibida no painel (`09b_painel_analitico_desktop.png`) |
| 7 | Pipeline local sem API (`--sem-api`) | — | **Funcional e testada** | RAW 271 → BRONZE 260 → SILVER 250; 10/10 checagens de qualidade OK; notebook executado com nbclient |
| 8 | Airflow → Pipeline (DAG) | — | **Depende de ação manual** | Estrutura da DAG testada com stub (`test_pipeline_dag.py`); Airflow real exige Docker/WSL2 — ver `02-Big-Data-Architecture/PENDENCIAS_E_ACOES_MANUAIS.txt` |
| 9 | Gold → Excel/Power BI (03) | — | **Implementada, mas não testada** | Script `03-Business-Intelligence-Startup/dashboard/exportar_gold_para_excel.py`; a pasta 03 não tem testes automatizados |
| 10 | Robô UiPath → Formulário web | §7 | **Depende de ação manual** | Estrutura do XAML e uso dos `id` do contrato verificados estaticamente (`test_rpa_artefatos.py`); o caminho do robô (`#/registrar?canal=rpa` → `origem=RPA`) foi exercitado pelo E2E com navegador, **não** pelo UiPath. Execução no UiPath Studio: manual |
| 11 | Prometheus ← `/metrics` | §10 | **Parcial** | Nomes das métricas e rota templated testados (`test_api_basico.py::test_metricas_nomes_e_rota_templated`); configuração de Prometheus/Grafana/alertas validada estaticamente (`test_devops_observabilidade.py`). Subir a stack e disparar o alerta: manual (Docker) |
| 12 | Docker / Docker Compose | — | **Depende de ação manual** | Dockerfile verificado estaticamente (`test_devops_container.py`) e por Trivy config (0 achados). `docker build`/`compose up` não executados (sem Docker na máquina) |
| 13 | GitHub Actions (CI/CD DevSecOps) | — | **Depende de ação manual** | Ferramentas rodadas localmente com os mesmos alvos: Gitleaks (no leaks found), Semgrep (0 achados), Trivy fs (0 HIGH/CRITICAL), Terraform validate/test. O workflow só roda depois do push no GitHub |
| 14 | Terraform → Azure (ACR + ACI) | — | **Depende de ação manual** | `terraform fmt`, `validate` (Success) e `terraform test` (3 passed, provider simulado). `apply` exige assinatura Azure — ver `06-Secure-DevOps-Cloud/docs/PUBLICACAO_AZURE.md` |
| 15 | Placa (QR Code) → `#/registrar` | §7 | **Depende de ação manual** | Gerador `07-.../laser-cut/gerar_qrcode.py` pronto; o QR definitivo só pode ser gerado com a URL pública real (não foi inventada). Fabricação: manual |

Legenda: **Funcional e testada** = executada nesta máquina com resultado real registrado;
**Implementada, mas não testada** = código pronto sem teste automatizado; **Parcial** = parte testada,
parte manual; **Depende de ação manual** = exige ferramenta, conta ou credencial que não existia no ambiente.
