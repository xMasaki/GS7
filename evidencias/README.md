# evidencias/ — onde guardar as provas da entrega

> Evidência é **registro real** do que foi feito: print, log, vídeo, foto. Nada aqui pode ser montado,
> editado para parecer outra coisa ou "simulado sem aviso". Dados de demonstração aparecem nos prints
> como **SIMULADOS** (selo na interface); fotos de teste da visão são **sintéticas**.
>
> Antes de salvar qualquer print, confira que **não aparece**: token (`ADMIN_TOKEN`, `PIPELINE_TOKEN`),
> chave `OPENROUTER_API_KEY`, senha, conteúdo do `.env`, e-mail/CPF/telefone, rosto ou placa de veículo
> de terceiros. Prints com segredo **não** vão para o Git — refaça o print.

## 1. O que já existe

| Pasta | Conteúdo | Origem |
|---|---|---|
| [`mvp_local/`](mvp_local/LEIAME.md) | 25 capturas (16 em 1280 px + 9 em 390 px) de todas as telas do MVP | Execução **local** e **automatizada** em 15/11/2026 (backend real em `127.0.0.1`, Edge headless via Playwright, `e2e_acessacidade.py`: 199/199 verificações OK). Dados simulados; assistente em modo básico (sem chave de IA). **Não substitui** as evidências da URL pública |

Evidências já existentes dentro das disciplinas (citadas pelos respectivos relatórios):

| Disciplina | Arquivo | O que é |
|---|---|---|
| 02 | `02-Big-Data-Architecture/docs/evidencias/execucao_local_runner.log` | Log real do pipeline local (`--sem-api`) |
| 02 | `02-Big-Data-Architecture/docs/evidencias/execucao_com_api.log` | Log real do pipeline contra a API **local** (15/11/2026): 28 linhas exportadas da API (seed simulado), Gold publicada com HTTP 200 |
| 06 | `06-Secure-DevOps-Cloud/docs/evidencias/validacoes_locais.md` | Resultados reais de Gitleaks, Semgrep, Trivy e Terraform rodados localmente |

## 2. Estrutura sugerida

**Regra:** se a disciplina já define uma pasta de evidências própria (coluna "Pasta principal"), salve lá —
é o caminho que o relatório/PDF da disciplina cita. As subpastas desta raiz (já criadas, com `.gitkeep`)
servem para o que **não tem lugar definido** na disciplina e para as provas comuns ao MVP publicado.

| Subpasta aqui | Pasta principal (citada pela disciplina) | O que produzir | Lista detalhada |
|---|---|---|---|
| `01_genai/` | **esta** (o `PENDENCIAS` da 01 manda salvar em `evidencias\`) | Prints do `#/assistente` com `fonte: llm` (com chave) e `fonte: fallback` (sem chave), resposta a protocolo inexistente, tentativa de prompt injection recusada | `01-Generative-AI-Engineering/docs/PLANO_DE_TESTES_E_EVIDENCIAS.md` |
| `02_bigdata/` | `02-Big-Data-Architecture/docs/evidencias/` | Prints do Airflow (DAG, Graph, logs das 6 tarefas), log da execução com a API, Gold no painel | `02-Big-Data-Architecture/docs/EVIDENCIAS_NECESSARIAS.md` |
| `03_bi_startup/` | `03-Business-Intelligence-Startup/pitch/evidencias/` | Registro dos testes de usabilidade (com consentimento), prints da demo, link do vídeo-pitch | `03-Business-Intelligence-Startup/pitch/LISTA_DE_EVIDENCIAS.md` |
| `04_visao/` | **esta** (os documentos da 04 citam `evidencias/visao_*.png`) | `visao_analise_<data>.png`, `visao_denuncia_<data>.png`, `visao_inconclusiva_<data>.png` na URL pública | `04-Applied-Computer-Vision/docs/EVIDENCIAS_NECESSARIAS.md` |
| `05_rpa/` | `05-Robotic-Process-Automation/evidencias/` | Print do assessment, AS-IS/TO-BE, robô no UiPath Studio, planilha de saída com protocolos (vai no ZIP) | `05-Robotic-Process-Automation/docs/EVIDENCIAS_NECESSARIAS.md` |
| `06_devops/` | `06-Secure-DevOps-Cloud/docs/evidencias/` | GitHub Actions (verde, barrada, corrigida), Terraform plan/apply, portal Azure, Grafana, alerta disparado, custo | `06-Secure-DevOps-Cloud/docs/EVIDENCIAS_NECESSARIAS.md` |
| `07_maker/` | `07-Project-Based-Maker-Lab/docs/fotos/` (criar) | Fotos do local e do objeto original, medição, laser cortando, peças impressas, protótipo montado, página do MakerWorld | `07-Project-Based-Maker-Lab/docs/FOTOS_A_REALIZAR.md` |
| `mvp_publico/` | **esta** | As mesmas telas de `mvp_local/`, mas na **URL pública** (barra de endereço visível), com data/hora | Repetir o roteiro de `mvp_local/LEIAME.md` contra a URL pública |

Para gerar as capturas da URL pública automaticamente (mesmo script do `mvp_local`):

```powershell
.\.venv\Scripts\python.exe app/frontend/tests_e2e/e2e_acessacidade.py --url [PREENCHER: URL pública do MVP] --shots evidencias/mvp_publico
```

O script cria denúncias de teste identificadas como tal; depois de rodá-lo contra a URL pública, registre
os protocolos criados e, se necessário, marque-os pela área da equipe (`#/revisao`).

## 3. Nomes de arquivo

`<disciplina>_<o-que-mostra>_<AAAA-MM-DD>.png` — ex.: `06_actions_barrada_2026-11-17.png`. Use os nomes
sugeridos nas listas de cada disciplina quando existirem. Vídeos **não** ficam no Git: publique (link
público ou não listado) e registre o link no `links_entrega.yaml` / relatório da disciplina.
