# Inventário dos marcadores PREENCHER

> Gerado em 15/11/2026 por varredura automática do repositório (somente leitura). Neste documento o marcador aparece como ‹PREENCHER› para que ele próprio não conte como pendência. Rode a varredura de novo depois de preencher para recalcular.

## 1. Números

- **678 ocorrências** em **97 arquivos**.
- **228 textos literais distintos** (ex.: ‹PREENCHER: URL_MVP› e ‹PREENCHER: URL pública do MVP› contam como dois).
- **237 campos lógicos** depois de agrupar duplicatas (o mesmo dado pedido em vários arquivos ou em formatos gerados): **235 exigem ação** e **2 podem permanecer**.
- **39 tipos de informação** diferentes a obter (nome da equipe, integrantes, URL do MVP, medidas do Maker Lab, etc.): é o número de decisões/fontes realmente distintas.
- Dos 488 marcadores que exigem ação, **76** são apenas 3 links finais (MVP, repositório, vídeo) repetidos em vários documentos.

| # | Categoria | Ocorrências | Arquivos | Campos lógicos |
|---|---|---:|---:|---:|
| 1 | Dados pessoais da equipe | 85 | 21 | 3 |
| 2 | URLs e links finais | 52 | 25 | 6 |
| 3 | Evidências (prints, fotos, vídeos) | 23 | 13 | 23 |
| 4 | Dados obtidos por testes reais | 109 | 24 | 63 |
| 5 | Dados obtidos por implantação Azure | 51 | 33 | 4 |
| 6 | Dados obtidos por UiPath | 14 | 2 | 14 |
| 7 | Dados obtidos por Maker Lab | 110 | 10 | 103 |
| 8 | Licença e informações administrativas | 38 | 19 | 13 |
| 9 | Pode permanecer como placeholder | 190 | 42 | 2 |
| 10 | Pode ser preenchido automaticamente pelo projeto | 6 | 4 | 6 |
| | **Total** | **678** | **97** | **237** |

Fronteira entre as categorias 2 e 5: link de plataforma externa (GitHub, YouTube, MakerWorld, Onshape, Actions) é **2**; o que só existe depois do deploy ou vem de medição na Azure/Docker (URL do MVP, FQDN, custo real, alerta disparado) é **5**. A categoria 9 reúne as menções ao marcador em código, testes, instruções, modelos (`.example`, CSV de rótulos) e nos arquivos PENDENCIAS e no guia.

## 2. Campos lógicos (agrupados)

| Prioridade | Cat. | Campo | Valor esperado | Por que ficou pendente | Ocorrências | Onde (amostra) |
|---|---:|---|---|---|---:|---|
| P1 | 1 | Integrantes: nome completo, RM, papel e turma | Nome completo + RM de 5 integrantes (ou quantos forem) e papel de cada um | Dados pessoais reais da equipe; o projeto não os conhece | 74 | `README.md`, `RELATORIO_ENTREGA_GENAI.md`, `RELATORIO_ENTREGA_BIGDATA.md` +13 |
| P1 | 1 | Nome da equipe/startup | Texto livre escolhido pela equipe | Só a equipe sabe; não pode ser inventado | 10 | `RELATORIO_ENTREGA_GENAI.md`, `RELATORIO_ENTREGA_BIGDATA.md`, `LEAN_CANVAS.html` +7 |
| P1 | 1 | Responsável pela privacidade (encarregado) | Nome de um integrante | Dado pessoal da equipe | 1 | `LGPD_MAPEAMENTO_DADOS_PESSOAIS.md` |
| P1 | 8 | Requisitos/critérios oficiais confirmados com o professor | Texto dos critérios, data e canal da confirmação | PDF oficial da disciplina 01 está 'TBD'; só o professor define | 5 | `README.md`, `RELATORIO_ENTREGA_GENAI.md`, `README.md` +2 |
| P1 | 8 | Política de retenção/exclusão e base legal LGPD | Prazo de guarda (ex.: até o fim da avaliação), forma de exclusão, base legal (art. 7º) | Decisão da equipe com impacto jurídico; texto aparece na tela Sobre | 4 | `LGPD_MAPEAMENTO_DADOS_PESSOAIS.md`, `sobre.js` |
| P1 | 8 | Canal de contato da equipe (e-mail institucional) | E-mail ou canal que exista de fato | Decisão da equipe; não se inventa e-mail | 3 | `TERMO_CONSENTIMENTO_MODELO.md`, `LGPD_MAPEAMENTO_DADOS_PESSOAIS.md`, `sobre.js` |
| P1 | 8 | Licença do repositório | Ex.: MIT + arquivo LICENSE | Escolha da equipe | 1 | `README.md` |
| P2 | 2 | URL do repositório público no GitHub | https://github.com/<conta>/<repositório> | O repositório ainda não foi publicado (decisão e conta da equipe) | 20 | `README.md`, `RELATORIO_ENTREGA_GENAI.md`, `links_entrega.yaml` +15 |
| P2 | 2 | URL das execuções do GitHub Actions (barrada e corrigida) | https://github.com/<conta>/<repo>/actions/runs/<id> | Só existe depois do push e das duas execuções reais | 5 | `DEMONSTRACAO_EXECUCAO_BARRADA.md`, `EVIDENCIAS_NECESSARIAS.md` |
| P2 | 5 | URL pública do MVP (saída app_url do Terraform / FQDN do ACI) | http://<fqdn>:8000 (ou domínio próprio) | Só existe depois do deploy real na Azure, que depende de conta e créditos da equipe | 35 | `README.md`, `RELATORIO_ENTREGA_GENAI.md`, `links_entrega.yaml` +27 |
| P2 | 5 | FQDN do container no Prometheus (scrape do Azure) | <dns-label>.brazilsouth.azurecontainer.io:8000 | Vem do deploy; o arquivo é um modelo | 2 | `prometheus.azure.yml` |
| P2 | 8 | Aviso na interface sobre envio de perguntas ao provedor LLM | Confirmar texto do aviso | Ver achado: a interface hoje só avisa 'não escreva dados pessoais' (chat.js:320); não menciona o provedor externo | 1 | `LGPD_MAPEAMENTO_DADOS_PESSOAIS.md` |
| P3 | 3 | Prints, fotos e imagens de evidência (23 itens distintos) | Arquivo de imagem real salvo na pasta indicada | Evidência real não pode ser gerada pelo projeto | 23 | `PLANO_DE_TESTES_E_EVIDENCIAS.md`, `RELATORIO_ENTREGA_BIGDATA.md`, `MODELO_DE_NEGOCIO.md` +10 |
| P3 | 4 | Validação do Lean Canvas (entrevistas/CP1, canais, preço, ativos) (29 itens distintos) | O que a equipe realmente aprendeu, por bloco | Hipóteses ainda não validadas; nada foi inventado | 62 | `PLANO_DE_TESTES_E_EVIDENCIAS.md`, `ESTRATEGIA_DE_PRECO.md`, `LEAN_CANVAS.html` +9 |
| P3 | 4 | Resultados de teste de usabilidade com usuários (n, tempos, SUS, conclusão) (16 itens distintos) | Valores da planilha registro_testes_usuarios preenchida | Exige pessoas reais e consentimento; proibido inventar | 19 | `RISCOS_E_LIMITES.md`, `LEAN_CANVAS.html`, `LEAN_CANVAS.md` +7 |
| P3 | 4 | Dados públicos de contexto (IBGE/Censo/DATASUS/legislação) com fonte (12 itens distintos) | Número + link da fonte + data de acesso | Exige consulta e conferência na fonte oficial | 12 | `ESTRATEGIA_DE_PRECO.md`, `MODELO_DE_NEGOCIO.md`, `ANALISE_CONCORRENCIA.md` +3 |
| P3 | 4 | Exemplos, custo e ajustes com LLM real | Saída de gerar_exemplos_llm.py com chave real; custo em US$ e tokens | Exige OPENROUTER_API_KEY da equipe | 7 | `README.md`, `ENGENHARIA_DE_PROMPTS.md`, `PLANO_DE_TESTES_E_EVIDENCIAS.md` +2 |
| P3 | 4 | Território onde a equipe observou o problema (cidade/bairro/data) | Cidade/bairros reais observados | Observação de campo da equipe | 4 | `DOCUMENTO_DE_ENTREGA_BI.md`, `LISTA_DE_CENAS.md`, `README.md` +1 |
| P3 | 4 | Premissas do business case a medir/levantar (volume, tempo manual, salário) (3 itens distintos) | Valores medidos/levantados pela equipe | Levantamento real com associações/cronometragem | 3 | `BUSINESS_CASE.md` |
| P3 | 4 | Resultado da comparação com fotos reais rotuladas manualmente | Números do RELATORIO_COMPARACAO (base REAL) | Não há fotos reais; proibido inventar acurácia | 2 | `DOCUMENTACAO_TECNICA_TRANSFORMACOES.md`, `RELATORIO_COMPARACAO.md` |
| P3 | 5 | Dados medidos na Azure/Docker (tamanho da imagem, alerta disparado, custo real, região, crédito) | Valores lidos do portal/CLI no momento | Exigem Docker/Azure reais; medir é obrigatório, não estimar | 12 | `ESTIMATIVA_DE_CUSTOS.md`, `RELATORIO_ENTREGA_DEVOPS.md` |
| P3 | 5 | Conferência na URL pública (rotas, /health, assistente) | Data, responsável e resultado | Depende do deploy | 2 | `INTEGRACAO.md`, `RELATORIO_ENTREGA_VISAO.md` |
| P3 | 6 | Resultados da execução real no UiPath Studio (tempo, ajustes, conclusão) (14 itens distintos) | Medidas e observações da execução | O Studio não existe nesta máquina; XAML nunca foi executado | 14 | `BUSINESS_CASE.md`, `RELATORIO_RPA.md` |
| P3 | 7 | Diagnóstico, medidas, fabricação e testes no mundo físico (83 itens distintos) | Medidas, local, data e resultados reais | Exige visita, laboratório e protótipo físico | 87 | `CROQUI_MEDIDAS.md`, `DIAGNOSTICO_OBJETO_ORIGINAL.md`, `FABRICACAO.md` +5 |
| P3 | 8 | Revisão do assessment RPA pela equipe (%, resultado final, cotação UiPath) (4 itens distintos) | Percentual final revisado e cotação oficial | Decisão/consulta da equipe | 4 | `BUSINESS_CASE.md`, `RELATORIO_RPA.md`, `ROTEIRO_VIDEO_RPA.md` |
| P4 | 2 | Link do vídeo-pitch/demonstração (público ou não listado) | https://youtu.be/... | O vídeo ainda não foi gravado | 21 | `README.md`, `RELATORIO_ENTREGA_GENAI.md`, `links_entrega.yaml` +16 |
| P4 | 2 | Link da página do modelo no MakerWorld | https://makerworld.com/... | Só existe após publicar (conta Bambu Lab) com fotos reais | 3 | `MAKERWORLD_PUBLICACAO.md`, `RELATORIO_ENTREGA_MAKER.md` |
| P4 | 2 | Link do documento Onshape | https://cad.onshape.com/documents/... | Depende de conta e do import dos STEP | 2 | `RELATORIO_ENTREGA_MAKER.md`, `TUTORIAL_ONSHAPE.md` |
| P4 | 7 | Peça de terceiros (nome, autor, link, licença) (20 itens distintos) | Dados da peça escolhida no MakerWorld | Bônus: só existe depois de escolher e imprimir a peça | 23 | `README.md`, `BONUS_PECA_TERCEIROS.md`, `MAKERWORLD_PUBLICACAO.md` +1 |
| P5 | 2 | Link da documentação oficial consultada | URL da documentação Azure/Microsoft consultada | A equipe deve citar o que realmente consultou | 1 | `RESPONSABILIDADE_COMPARTILHADA.md` |
| P5 | 8 | Data de envio/entrega/conferência | dd/mm/aaaa | Só se sabe na hora do envio | 10 | `RELATORIO_ENTREGA_GENAI.md`, `RELATORIO_ENTREGA_BIGDATA.md`, `ROTEIRO_PITCH.md` +6 |
| P5 | 8 | Responsável e prazo dos próximos passos | Nome e data de cada tarefa | Definidos pela equipe | 5 | `PROXIMOS_PASSOS.md` |
| P5 | 8 | Preço vigente e política de privacidade do provedor LLM | Valores e política citados na data da entrega | Consulta externa com data | 4 | `README.md`, `RELATORIO_ENTREGA_GENAI.md`, `RISCOS_E_LIMITES.md` +1 |
| P5 | 8 | Valores de calculadora e cotação do dia | Valores copiados da calculadora de preços Azure e cotação oficial do dia | Consulta externa com data; preço/câmbio inventado seria falso | 1 | `ESTIMATIVA_DE_CUSTOS.md` |
| P5 | 10 | Indicadores de impacto e ODS conectados (README 06) (2 itens distintos) | Copiar da Ficha Técnica: seção 4 (indicadores) e seção 5 (ODS 11, 10, 9) | Já definidos em docs/FICHA_TECNICA_MVP.md | 2 | `README.md` |
| P5 | 10 | Valor da estimativa de custo da disciplina 06 (modelo de negócio) | ≈ US$ 10,80 (7 dias) e ≈ US$ 21,50 (14 dias), estimativa com premissas | Valor já calculado em 06/docs/ESTIMATIVA_DE_CUSTOS.md (continua sendo estimativa, a conferir na calculadora) | 1 | `MODELO_DE_NEGOCIO.md` |
| P5 | 10 | Mascaramento automático na descrição (LGPD) | Rostos borrados e EXIF/GPS removidos nas fotos (privacy.py); texto livre não é mascarado | Está implementado e testado em 04/acessacidade_vision/privacy.py | 1 | `LGPD_MAPEAMENTO_DADOS_PESSOAIS.md` |
| P5 | 10 | Link para o README da raiz (Ficha Técnica) | README.md da raiz (vira link no GitHub via --repo-url) | O arquivo existe; basta referenciar | 1 | `RELATORIO_ENTREGA_DEVOPS.md` |
| P5 | 10 | Imagem do diagrama de arquitetura de nuvem | Diagrama Mermaid de 06/docs/ARQUITETURA_CLOUD.md (o gerador de PDF já desenha Mermaid) | O diagrama já existe no projeto | 1 | `RELATORIO_ENTREGA_DEVOPS.md` |
| P9 | 9 | Menção ao marcador em instrução/código/teste/modelo | Nenhum — deve permanecer | É o texto que o gerador de PDF e os testes procuram, ou explica como preencher | 156 | `acessacidade.py`, `PENDENCIAS_E_ACOES_MANUAIS.txt`, `RELATORIO_ENTREGA_GENAI.md` +36 |
| P9 | 9 | Placeholder de arquivo-modelo (.example / template CSV) | Nenhum no modelo; o valor vai na cópia local | Modelos precisam do placeholder (tfvars, backend.hcl, CSV de rótulos) | 34 | `rotulos_manuais_reais_TEMPLATE.csv`, `backend.hcl.example`, `terraform.tfvars.example` |

## 3. Lista de preenchimento por prioridade

### P1 — Decisões e dados da equipe (fazer ANTES do deploy: entram no código/imagem e destravam o resto)

- [ ] **Integrantes: nome completo, RM, papel e turma** — 74 ocorrência(s) em 16 arquivo(s). Esperado: Nome completo + RM de 5 integrantes (ou quantos forem) e papel de cada um.
- [ ] **Nome da equipe/startup** — 10 ocorrência(s) em 10 arquivo(s). Esperado: Texto livre escolhido pela equipe.
- [ ] **Responsável pela privacidade (encarregado)** — 1 ocorrência(s) em 1 arquivo(s). Esperado: Nome de um integrante.
- [ ] **Requisitos/critérios oficiais confirmados com o professor** — 5 ocorrência(s) em 5 arquivo(s). Esperado: Texto dos critérios, data e canal da confirmação.
- [ ] **Política de retenção/exclusão e base legal LGPD** — 4 ocorrência(s) em 2 arquivo(s). Esperado: Prazo de guarda (ex.: até o fim da avaliação), forma de exclusão, base legal (art. 7º).
- [ ] **Canal de contato da equipe (e-mail institucional)** — 3 ocorrência(s) em 3 arquivo(s). Esperado: E-mail ou canal que exista de fato.
- [ ] **Licença do repositório** — 1 ocorrência(s) em 1 arquivo(s). Esperado: Ex.: MIT + arquivo LICENSE.

### P2 — Publicação (repositório público, deploy Azure, CI): geram as URLs

- [ ] **URL do repositório público no GitHub** — 20 ocorrência(s) em 18 arquivo(s). Esperado: https://github.com/<conta>/<repositório>.
- [ ] **URL das execuções do GitHub Actions (barrada e corrigida)** — 5 ocorrência(s) em 2 arquivo(s). Esperado: https://github.com/<conta>/<repo>/actions/runs/<id>.
- [ ] **URL pública do MVP (saída app_url do Terraform / FQDN do ACI)** — 35 ocorrência(s) em 30 arquivo(s). Esperado: http://<fqdn>:8000 (ou domínio próprio).
- [ ] **FQDN do container no Prometheus (scrape do Azure)** — 2 ocorrência(s) em 1 arquivo(s). Esperado: <dns-label>.brazilsouth.azurecontainer.io:8000.
- [ ] **Aviso na interface sobre envio de perguntas ao provedor LLM** — 1 ocorrência(s) em 1 arquivo(s). Esperado: Confirmar texto do aviso.

### P3 — Evidências e dados reais (testes, UiPath, Maker Lab, LLM, prints)

- [ ] **Prints, fotos e imagens de evidência** — 23 ocorrência(s) em 13 arquivo(s). Esperado: Arquivo de imagem real salvo na pasta indicada.
- [ ] **Validação do Lean Canvas (entrevistas/CP1, canais, preço, ativos)** — 62 ocorrência(s) em 12 arquivo(s). Esperado: O que a equipe realmente aprendeu, por bloco.
- [ ] **Resultados de teste de usabilidade com usuários (n, tempos, SUS, conclusão)** — 19 ocorrência(s) em 10 arquivo(s). Esperado: Valores da planilha registro_testes_usuarios preenchida.
- [ ] **Dados públicos de contexto (IBGE/Censo/DATASUS/legislação) com fonte** — 12 ocorrência(s) em 6 arquivo(s). Esperado: Número + link da fonte + data de acesso.
- [ ] **Exemplos, custo e ajustes com LLM real** — 7 ocorrência(s) em 5 arquivo(s). Esperado: Saída de gerar_exemplos_llm.py com chave real; custo em US$ e tokens.
- [ ] **Território onde a equipe observou o problema (cidade/bairro/data)** — 4 ocorrência(s) em 4 arquivo(s). Esperado: Cidade/bairros reais observados.
- [ ] **Premissas do business case a medir/levantar (volume, tempo manual, salário)** — 3 ocorrência(s) em 1 arquivo(s). Esperado: Valores medidos/levantados pela equipe.
- [ ] **Resultado da comparação com fotos reais rotuladas manualmente** — 2 ocorrência(s) em 2 arquivo(s). Esperado: Números do RELATORIO_COMPARACAO (base REAL).
- [ ] **Dados medidos na Azure/Docker (tamanho da imagem, alerta disparado, custo real, região, crédito)** — 12 ocorrência(s) em 2 arquivo(s). Esperado: Valores lidos do portal/CLI no momento.
- [ ] **Conferência na URL pública (rotas, /health, assistente)** — 2 ocorrência(s) em 2 arquivo(s). Esperado: Data, responsável e resultado.
- [ ] **Resultados da execução real no UiPath Studio (tempo, ajustes, conclusão)** — 14 ocorrência(s) em 2 arquivo(s). Esperado: Medidas e observações da execução.
- [ ] **Diagnóstico, medidas, fabricação e testes no mundo físico** — 87 ocorrência(s) em 8 arquivo(s). Esperado: Medidas, local, data e resultados reais.
- [ ] **Revisão do assessment RPA pela equipe (%, resultado final, cotação UiPath)** — 4 ocorrência(s) em 3 arquivo(s). Esperado: Percentual final revisado e cotação oficial.

### P4 — Vídeos e links finais de plataformas externas

- [ ] **Link do vídeo-pitch/demonstração (público ou não listado)** — 21 ocorrência(s) em 19 arquivo(s). Esperado: https://youtu.be/....
- [ ] **Link da página do modelo no MakerWorld** — 3 ocorrência(s) em 2 arquivo(s). Esperado: https://makerworld.com/....
- [ ] **Link do documento Onshape** — 2 ocorrência(s) em 2 arquivo(s). Esperado: https://cad.onshape.com/documents/....
- [ ] **Peça de terceiros (nome, autor, link, licença)** — 23 ocorrência(s) em 4 arquivo(s). Esperado: Dados da peça escolhida no MakerWorld.

### P5 — Fechamento (datas, cotações, consultas e geração dos PDFs)

- [ ] **Link da documentação oficial consultada** — 1 ocorrência(s) em 1 arquivo(s). Esperado: URL da documentação Azure/Microsoft consultada.
- [ ] **Data de envio/entrega/conferência** — 10 ocorrência(s) em 9 arquivo(s). Esperado: dd/mm/aaaa.
- [ ] **Responsável e prazo dos próximos passos** — 5 ocorrência(s) em 1 arquivo(s). Esperado: Nome e data de cada tarefa.
- [ ] **Preço vigente e política de privacidade do provedor LLM** — 4 ocorrência(s) em 4 arquivo(s). Esperado: Valores e política citados na data da entrega.
- [ ] **Valores de calculadora e cotação do dia** — 1 ocorrência(s) em 1 arquivo(s). Esperado: Valores copiados da calculadora de preços Azure e cotação oficial do dia.
- [ ] **Indicadores de impacto e ODS conectados (README 06)** — 2 ocorrência(s) em 1 arquivo(s). Esperado: Copiar da Ficha Técnica: seção 4 (indicadores) e seção 5 (ODS 11, 10, 9).
- [ ] **Valor da estimativa de custo da disciplina 06 (modelo de negócio)** — 1 ocorrência(s) em 1 arquivo(s). Esperado: ≈ US$ 10,80 (7 dias) e ≈ US$ 21,50 (14 dias), estimativa com premissas.
- [ ] **Mascaramento automático na descrição (LGPD)** — 1 ocorrência(s) em 1 arquivo(s). Esperado: Rostos borrados e EXIF/GPS removidos nas fotos (privacy.py); texto livre não é mascarado.
- [ ] **Link para o README da raiz (Ficha Técnica)** — 1 ocorrência(s) em 1 arquivo(s). Esperado: README.md da raiz (vira link no GitHub via --repo-url).
- [ ] **Imagem do diagrama de arquitetura de nuvem** — 1 ocorrência(s) em 1 arquivo(s). Esperado: Diagrama Mermaid de 06/docs/ARQUITETURA_CLOUD.md (o gerador de PDF já desenha Mermaid).

Ordem entre os grupos: **P1** (dá para fazer hoje; só depende da equipe) → **P2** (publicar o repositório e fazer o deploy) → **P3 e P4** em paralelo, uma pessoa por frente → **P5** (gerar os PDFs com `tools\gerar_todos_pdfs.ps1 -Estrito`, que lista o que sobrou).

## 4. O que pode ser substituído automaticamente agora (sem inventar nada)

### 4.1 O valor já existe no projeto (categoria 10)

| Arquivo:linha | O que colocar | Fonte no projeto | Ressalva |
|---|---|---|---|
| `03-Business-Intelligence-Startup/business-model/MODELO_DE_NEGOCIO.md:105` | ≈ US$ 10,80 (7 dias) e ≈ US$ 21,50 (14 dias), como estimativa com premissas | `06-Secure-DevOps-Cloud/docs/ESTIMATIVA_DE_CUSTOS.md` | Continua sendo estimativa: conferir na calculadora Azure |
| `06-Secure-DevOps-Cloud/README.md:19` | Indicadores (seção 4) e ODS 11 (11.7, 11.2, 11.3), 10 (10.2) e 9 (9.1) da Ficha | `docs/FICHA_TECNICA_MVP.md`, seções 4 e 5 | A equipe pode trocar os ODS secundários |
| `06-Secure-DevOps-Cloud/README.md:20` | Indicadores (seção 4) e ODS 11 (11.7, 11.2, 11.3), 10 (10.2) e 9 (9.1) da Ficha | `docs/FICHA_TECNICA_MVP.md`, seções 4 e 5 | A equipe pode trocar os ODS secundários |
| `06-Secure-DevOps-Cloud/docs/LGPD_MAPEAMENTO_DADOS_PESSOAIS.md:13` | Rostos frontais borrados e EXIF/GPS removidos nas fotos; o texto livre **não** é mascarado | `04-Applied-Computer-Vision/src/acessacidade_vision/privacy.py` e README raiz (Segurança e LGPD) | Citar a limitação (só rostos frontais) |
| `06-Secure-DevOps-Cloud/docs/RELATORIO_ENTREGA_DEVOPS.md:16` | Link para o README da raiz | `README.md` | No PDF só vira link do GitHub com `--repo-url` |
| `06-Secure-DevOps-Cloud/docs/RELATORIO_ENTREGA_DEVOPS.md:24` | Diagrama Mermaid de nuvem (já existe) no lugar da imagem | `06-Secure-DevOps-Cloud/docs/ARQUITETURA_CLOUD.md` (2 diagramas) | O gerador de PDF já desenha Mermaid |

### 4.2 Propagação automática (um valor da equipe, depois é script)

- **Links de vídeo, MVP e repositório:** 43 ocorrências já são trocadas sozinhas pelos geradores de PDF das pastas 01, 03 e 04 a partir de `docs/links_entrega.yaml`; basta preencher 3 linhas por pasta.
- **Lean Canvas:** `LEAN_CANVAS.md` e `LEAN_CANVAS.html` (41 ocorrências) são **gerados**: edite só `business-model/lean_canvas.json` e rode `scripts/gerar_lean_canvas.py`.
- **Valores repetidos em vários arquivos** (preencher uma vez e propagar com um substituidor): nome da equipe (10×), integrantes, RMs e papéis (74×), URL do repositório (20×), URL do MVP (35×), vídeo (21×). Isso já está resolvido por `tools/preencher_marcadores.py`: lê `dados_entrega.yaml`, mostra preview e diff, pede confirmação, grava com backup e gera `docs/RELATORIO_PREENCHIMENTO.md` (não preenche o que estiver vazio nem marcadores sem correspondência exata).

### 4.3 O que não deve ser preenchido automaticamente

Nomes, RMs, URLs, custos reais, resultados de teste, medidas, datas de envio, licença, retenção e contato: qualquer valor aqui seria inventado.

## 5. Achados

1. **Aviso LGPD na interface não atendido:** a linha da LGPD que pede "confirmar o aviso na interface" não está satisfeita. O chat só diz "Não escreva dados pessoais" (`app/frontend/js/components/chat.js:320`) e a tela Sobre não cita o provedor externo (OpenRouter) quando a chave está ativa. É correção de código, não preenchimento.
2. **Bloqueia o deploy:** retenção e contato em `app/frontend/js/views/sobre.js` (2 ocorrências, pendência 06 D14) entram na imagem Docker.
3. **CSV de coleta real:** os 30 marcadores de `rotulos_manuais_reais_TEMPLATE.csv` são modelo e devem permanecer; a cópia sem `_TEMPLATE` é que recebe os dados.
4. **Disciplina 01:** o relatório só fecha depois de confirmar os requisitos com o professor (o PDF oficial está TBD).

## 6. Apêndice: todas as ocorrências

| Arquivo:linha | Texto | Cat. | Campo lógico |
|---|---|---:|---|
| `.semgrep/tests/acessacidade.py:48` | ‹PREENCHER] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `01-Generative-AI-Engineering/PENDENCIAS_E_ACOES_MANUAIS.txt:43` | ‹PREENCHER] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `01-Generative-AI-Engineering/PENDENCIAS_E_ACOES_MANUAIS.txt:63` | ‹PREENCHER] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `01-Generative-AI-Engineering/PENDENCIAS_E_ACOES_MANUAIS.txt:66` | ‹PREENCHER] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `01-Generative-AI-Engineering/PENDENCIAS_E_ACOES_MANUAIS.txt:93` | ‹PREENCHER] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `01-Generative-AI-Engineering/PENDENCIAS_E_ACOES_MANUAIS.txt:109` | ‹PREENCHER] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `01-Generative-AI-Engineering/PENDENCIAS_E_ACOES_MANUAIS.txt:176` | ‹PREENCHER] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `01-Generative-AI-Engineering/PENDENCIAS_E_ACOES_MANUAIS.txt:179` | ‹PREENCHER] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `01-Generative-AI-Engineering/README.md:8` | ‹PREENCHER: requisitos confirmados com o professor e data] | 8 | Requisitos/critérios oficiais confirmados com o professor |
| `01-Generative-AI-Engineering/README.md:139` | ‹PREENCHER: confirmar o preço vigente na página do modelo no site do OpenRouter na data da | 8 | Preço vigente e política de privacidade do provedor LLM |
| `01-Generative-AI-Engineering/README.md:152` | ‹PREENCHER: custo real observado após gerar os exemplos com LLM] | 4 | Exemplos, custo e ajustes com LLM real |
| `01-Generative-AI-Engineering/README.md:195` | ‹PREENCHER: URL pública do repositório GitHub] | 2 | URL do repositório público no GitHub |
| `01-Generative-AI-Engineering/README.md:196` | ‹PREENCHER: URL pública do MVP] | 5 | URL pública do MVP (saída app_url do Terraform / FQDN do ACI) |
| `01-Generative-AI-Engineering/README.md:197` | ‹PREENCHER: link do vídeo] | 2 | Link do vídeo-pitch/demonstração (público ou não listado) |
| `01-Generative-AI-Engineering/README.md:198` | ‹PREENCHER: nomes e RMs dos integrantes] | 1 | Integrantes: nome completo, RM, papel e turma |
| `01-Generative-AI-Engineering/docs/ENGENHARIA_DE_PROMPTS.md:108` | ‹PREENCHER: ajustes de prompt feitos após observar respostas reais do LLM, se houver] | 4 | Exemplos, custo e ajustes com LLM real |
| `01-Generative-AI-Engineering/docs/INTEGRACAO.md:140` | ‹PREENCHER: data e responsável pela verificação na URL pública] | 5 | Conferência na URL pública (rotas, /health, assistente) |
| `01-Generative-AI-Engineering/docs/PLANO_DE_TESTES_E_EVIDENCIAS.md:92` | ‹PREENCHER: data da geração e modelo usado] | 4 | Exemplos, custo e ajustes com LLM real |
| `01-Generative-AI-Engineering/docs/PLANO_DE_TESTES_E_EVIDENCIAS.md:93` | ‹PREENCHER: custo em US$ e tokens] | 4 | Exemplos, custo e ajustes com LLM real |
| `01-Generative-AI-Engineering/docs/PLANO_DE_TESTES_E_EVIDENCIAS.md:94` | ‹PREENCHER: nome do arquivo] | 3 | Prints, fotos e imagens de evidência |
| `01-Generative-AI-Engineering/docs/PLANO_DE_TESTES_E_EVIDENCIAS.md:95` | ‹PREENCHER] | 3 | Prints, fotos e imagens de evidência |
| `01-Generative-AI-Engineering/docs/PLANO_DE_TESTES_E_EVIDENCIAS.md:96` | ‹PREENCHER] | 3 | Prints, fotos e imagens de evidência |
| `01-Generative-AI-Engineering/docs/PLANO_DE_TESTES_E_EVIDENCIAS.md:97` | ‹PREENCHER: resultado real, com consentimento] | 4 | Validação do Lean Canvas (entrevistas/CP1, canais, preço, ativos) |
| `01-Generative-AI-Engineering/docs/RELATORIO_ENTREGA_GENAI.md:6` | ‹PREENCHER: nome da equipe] | 1 | Nome da equipe/startup |
| `01-Generative-AI-Engineering/docs/RELATORIO_ENTREGA_GENAI.md:6` | ‹PREENCHER: nomes e RMs dos integrantes] | 1 | Integrantes: nome completo, RM, papel e turma |
| `01-Generative-AI-Engineering/docs/RELATORIO_ENTREGA_GENAI.md:7` | ‹PREENCHER: data de envio] | 8 | Data de envio/entrega/conferência |
| `01-Generative-AI-Engineering/docs/RELATORIO_ENTREGA_GENAI.md:12` | ‹PREENCHER: requisitos confirmados com o professor, data e canal da confirmação; | 8 | Requisitos/critérios oficiais confirmados com o professor |
| `01-Generative-AI-Engineering/docs/RELATORIO_ENTREGA_GENAI.md:19` | ‹PREENCHER: URL_REPOSITORIO] | 2 | URL do repositório público no GitHub |
| `01-Generative-AI-Engineering/docs/RELATORIO_ENTREGA_GENAI.md:20` | ‹PREENCHER: URL_REPOSITORIO] | 2 | URL do repositório público no GitHub |
| `01-Generative-AI-Engineering/docs/RELATORIO_ENTREGA_GENAI.md:21` | ‹PREENCHER: URL_MVP] | 5 | URL pública do MVP (saída app_url do Terraform / FQDN do ACI) |
| `01-Generative-AI-Engineering/docs/RELATORIO_ENTREGA_GENAI.md:22` | ‹PREENCHER: URL_VIDEO] | 2 | Link do vídeo-pitch/demonstração (público ou não listado) |
| `01-Generative-AI-Engineering/docs/RELATORIO_ENTREGA_GENAI.md:119` | ‹PREENCHER: gerar com `examples/gerar_exemplos_llm.py` usando a chave | 4 | Exemplos, custo e ajustes com LLM real |
| `01-Generative-AI-Engineering/docs/RELATORIO_ENTREGA_GENAI.md:127` | ‹PREENCHER: confirmar preço vigente no | 8 | Preço vigente e política de privacidade do provedor LLM |
| `01-Generative-AI-Engineering/docs/RELATORIO_ENTREGA_GENAI.md:129` | ‹PREENCHER: custo real observado] | 4 | Exemplos, custo e ajustes com LLM real |
| `01-Generative-AI-Engineering/docs/RELATORIO_ENTREGA_GENAI.md:156` | ‹PREENCHER] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `01-Generative-AI-Engineering/docs/RISCOS_E_LIMITES.md:17` | ‹PREENCHER: custo real observado] | 4 | Exemplos, custo e ajustes com LLM real |
| `01-Generative-AI-Engineering/docs/RISCOS_E_LIMITES.md:18` | ‹PREENCHER: resultado de teste com usuário real, se feito] | 4 | Resultados de teste de usabilidade com usuários (n, tempos, SUS, concl |
| `01-Generative-AI-Engineering/docs/RISCOS_E_LIMITES.md:29` | ‹PREENCHER: conferir e citar a política de privacidade/retenção do OpenRouter e do provedo | 8 | Preço vigente e política de privacidade do provedor LLM |
| `01-Generative-AI-Engineering/docs/gerar_pdf_relatorio.py:3` | ‹PREENCHER: URL_VIDEO] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `01-Generative-AI-Engineering/docs/gerar_pdf_relatorio.py:4` | ‹PREENCHER: URL_MVP] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `01-Generative-AI-Engineering/docs/gerar_pdf_relatorio.py:4` | ‹PREENCHER: URL_REPOSITORIO] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `01-Generative-AI-Engineering/docs/gerar_pdf_relatorio.py:12` | ‹PREENCHER] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `01-Generative-AI-Engineering/docs/gerar_pdf_relatorio.py:39` | ‹PREENCHER: URL_VIDEO] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `01-Generative-AI-Engineering/docs/gerar_pdf_relatorio.py:40` | ‹PREENCHER: URL_MVP] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `01-Generative-AI-Engineering/docs/gerar_pdf_relatorio.py:41` | ‹PREENCHER: URL_REPOSITORIO] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `01-Generative-AI-Engineering/docs/gerar_pdf_relatorio.py:45` | ‹PREENCHER[^\] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `01-Generative-AI-Engineering/docs/gerar_pdf_relatorio.py:152` | ‹PREENCHER] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `01-Generative-AI-Engineering/docs/gerar_pdf_relatorio.py:163` | ‹PREENCHER] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `01-Generative-AI-Engineering/docs/gerar_pdf_relatorio.py:165` | ‹PREENCHER] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `01-Generative-AI-Engineering/docs/links_entrega.yaml:4` | ‹PREENCHER: URL_VIDEO] | 2 | Link do vídeo-pitch/demonstração (público ou não listado) |
| `01-Generative-AI-Engineering/docs/links_entrega.yaml:4` | ‹PREENCHER: URL_MVP] | 5 | URL pública do MVP (saída app_url do Terraform / FQDN do ACI) |
| `01-Generative-AI-Engineering/docs/links_entrega.yaml:5` | ‹PREENCHER: URL_REPOSITORIO] | 2 | URL do repositório público no GitHub |
| `02-Big-Data-Architecture/PENDENCIAS_E_ACOES_MANUAIS.txt:183` | ‹PREENCHER: ...] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `02-Big-Data-Architecture/PENDENCIAS_E_ACOES_MANUAIS.txt:189` | ‹PREENCHER] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `02-Big-Data-Architecture/PENDENCIAS_E_ACOES_MANUAIS.txt:198` | ‹PREENCHER] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `02-Big-Data-Architecture/PENDENCIAS_E_ACOES_MANUAIS.txt:216` | ‹PREENCHER: link do video] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `02-Big-Data-Architecture/PENDENCIAS_E_ACOES_MANUAIS.txt:233` | ‹PREENCHER: URL do repositorio] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `02-Big-Data-Architecture/README.md:57` | ‹PREENCHER: conferir e colar aqui os critérios oficiais] | 8 | Requisitos/critérios oficiais confirmados com o professor |
| `02-Big-Data-Architecture/docs/EVIDENCIAS_NECESSARIAS.md:34` | ‹PREENCHER: URL do repositório] | 2 | URL do repositório público no GitHub |
| `02-Big-Data-Architecture/docs/EVIDENCIAS_NECESSARIAS.md:34` | ‹PREENCHER: link do vídeo] | 2 | Link do vídeo-pitch/demonstração (público ou não listado) |
| `02-Big-Data-Architecture/docs/EVIDENCIAS_NECESSARIAS.md:35` | ‹PREENCHER: URL pública da API, se houver] | 5 | URL pública do MVP (saída app_url do Terraform / FQDN do ACI) |
| `02-Big-Data-Architecture/docs/RELATORIO_ENTREGA_BIGDATA.md:9` | ‹PREENCHER: nome da equipe] | 1 | Nome da equipe/startup |
| `02-Big-Data-Architecture/docs/RELATORIO_ENTREGA_BIGDATA.md:10` | ‹PREENCHER: integrante 1 — RM] | 1 | Integrantes: nome completo, RM, papel e turma |
| `02-Big-Data-Architecture/docs/RELATORIO_ENTREGA_BIGDATA.md:10` | ‹PREENCHER: integrante 2 — RM] | 1 | Integrantes: nome completo, RM, papel e turma |
| `02-Big-Data-Architecture/docs/RELATORIO_ENTREGA_BIGDATA.md:10` | ‹PREENCHER: integrante 3 — RM] | 1 | Integrantes: nome completo, RM, papel e turma |
| `02-Big-Data-Architecture/docs/RELATORIO_ENTREGA_BIGDATA.md:10` | ‹PREENCHER: integrante 4 — RM] | 1 | Integrantes: nome completo, RM, papel e turma |
| `02-Big-Data-Architecture/docs/RELATORIO_ENTREGA_BIGDATA.md:10` | ‹PREENCHER: integrante 5 — RM] | 1 | Integrantes: nome completo, RM, papel e turma |
| `02-Big-Data-Architecture/docs/RELATORIO_ENTREGA_BIGDATA.md:11` | ‹PREENCHER: URL do repositório] | 2 | URL do repositório público no GitHub |
| `02-Big-Data-Architecture/docs/RELATORIO_ENTREGA_BIGDATA.md:12` | ‹PREENCHER: link do vídeo] | 2 | Link do vídeo-pitch/demonstração (público ou não listado) |
| `02-Big-Data-Architecture/docs/RELATORIO_ENTREGA_BIGDATA.md:13` | ‹PREENCHER: URL pública da API] | 5 | URL pública do MVP (saída app_url do Terraform / FQDN do ACI) |
| `02-Big-Data-Architecture/docs/RELATORIO_ENTREGA_BIGDATA.md:14` | ‹PREENCHER: data de entrega] | 8 | Data de envio/entrega/conferência |
| `02-Big-Data-Architecture/docs/RELATORIO_ENTREGA_BIGDATA.md:83` | ‹PREENCHER: prints da UI Graph/Grid/logs — ver `docs/EVIDENCIAS_NECESSARIAS.md`] | 3 | Prints, fotos e imagens de evidência |
| `02-Big-Data-Architecture/docs/RELATORIO_ENTREGA_BIGDATA.md:103` | ‹PREENCHER: prints/vídeo] | 3 | Prints, fotos e imagens de evidência |
| `02-Big-Data-Architecture/docs/RELATORIO_ENTREGA_BIGDATA.md:104` | ‹PREENCHER: conferir critérios publicados pela professora] | 8 | Requisitos/critérios oficiais confirmados com o professor |
| `02-Big-Data-Architecture/docs/gerar_pdf_relatorio.py:11` | ‹PREENCHER: ...] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `02-Big-Data-Architecture/docs/gerar_pdf_relatorio.py:52` | ‹PREENCHER", relatorio)) | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `02-Big-Data-Architecture/docs/gerar_pdf_relatorio.py:87` | ‹PREENCHER] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `03-Business-Intelligence-Startup/PENDENCIAS_E_ACOES_MANUAIS.txt:14` | ‹PREENCHER] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `03-Business-Intelligence-Startup/PENDENCIAS_E_ACOES_MANUAIS.txt:54` | ‹PREENCHER] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `03-Business-Intelligence-Startup/PENDENCIAS_E_ACOES_MANUAIS.txt:72` | ‹PREENCHER] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `03-Business-Intelligence-Startup/PENDENCIAS_E_ACOES_MANUAIS.txt:85` | ‹PREENCHER] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `03-Business-Intelligence-Startup/PENDENCIAS_E_ACOES_MANUAIS.txt:89` | ‹PREENCHER] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `03-Business-Intelligence-Startup/PENDENCIAS_E_ACOES_MANUAIS.txt:96` | ‹PREENCHER: Integrante". | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `03-Business-Intelligence-Startup/PENDENCIAS_E_ACOES_MANUAIS.txt:97` | ‹PREENCHER: Integrante N] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `03-Business-Intelligence-Startup/PENDENCIAS_E_ACOES_MANUAIS.txt:99` | ‹PREENCHER] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `03-Business-Intelligence-Startup/PENDENCIAS_E_ACOES_MANUAIS.txt:160` | ‹PREENCHER] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `03-Business-Intelligence-Startup/README.md:10` | ‹PREENCHER] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `03-Business-Intelligence-Startup/README.md:80` | ‹PREENCHER] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `03-Business-Intelligence-Startup/README.md:95` | ‹PREENCHER] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `03-Business-Intelligence-Startup/README.md:107` | ‹PREENCHER: URL_VIDEO] | 2 | Link do vídeo-pitch/demonstração (público ou não listado) |
| `03-Business-Intelligence-Startup/README.md:108` | ‹PREENCHER: URL_MVP] | 5 | URL pública do MVP (saída app_url do Terraform / FQDN do ACI) |
| `03-Business-Intelligence-Startup/README.md:109` | ‹PREENCHER: URL_REPOSITORIO] | 2 | URL do repositório público no GitHub |
| `03-Business-Intelligence-Startup/README.md:110` | ‹PREENCHER: nomes, RMs e papéis] | 1 | Integrantes: nome completo, RM, papel e turma |
| `03-Business-Intelligence-Startup/business-model/ESTRATEGIA_DE_PRECO.md:39` | ‹PREENCHER: dado obtido em entrevista] | 4 | Dados públicos de contexto (IBGE/Censo/DATASUS/legislação) com fonte |
| `03-Business-Intelligence-Startup/business-model/ESTRATEGIA_DE_PRECO.md:42` | ‹PREENCHER: entrevistas de preço realizadas (quantas, com que perfil, o que mudou) — ou "n | 4 | Validação do Lean Canvas (entrevistas/CP1, canais, preço, ativos) |
| `03-Business-Intelligence-Startup/business-model/LEAN_CANVAS.html:58` | ‹PREENCHER: nome da equipe / startup] | 1 | Nome da equipe/startup |
| `03-Business-Intelligence-Startup/business-model/LEAN_CANVAS.html:62` | ‹PREENCHER: o que foi validado no CP1/entrevistas sobre a dor (quantas pessoas, perfis, fr | 4 | Validação do Lean Canvas (entrevistas/CP1, canais, preço, ativos) |
| `03-Business-Intelligence-Startup/business-model/LEAN_CANVAS.html:62` | ‹PREENCHER: segmentos entrevistados no CP1 e o que mudou (ex.: priorização entre prefeitur | 4 | Validação do Lean Canvas (entrevistas/CP1, canais, preço, ativos) |
| `03-Business-Intelligence-Startup/business-model/LEAN_CANVAS.html:62` | ‹PREENCHER: reação de cidadãos e de possíveis clientes à proposta de valor; frases das ent | 4 | Validação do Lean Canvas (entrevistas/CP1, canais, preço, ativos) |
| `03-Business-Intelligence-Startup/business-model/LEAN_CANVAS.html:62` | ‹PREENCHER: o que foi testado no protótipo/MVP 0/MVP 1 e com quem; o que mudou na solução  | 4 | Validação do Lean Canvas (entrevistas/CP1, canais, preço, ativos) |
| `03-Business-Intelligence-Startup/business-model/LEAN_CANVAS.html:62` | ‹PREENCHER: canais já testados (ex.: divulgação em grupo de associação) e resultado real] | 4 | Validação do Lean Canvas (entrevistas/CP1, canais, preço, ativos) |
| `03-Business-Intelligence-Startup/business-model/LEAN_CANVAS.html:62` | ‹PREENCHER: disposição a pagar ouvida em entrevistas (se houver) e o que mudou no modelo d | 4 | Validação do Lean Canvas (entrevistas/CP1, canais, preço, ativos) |
| `03-Business-Intelligence-Startup/business-model/LEAN_CANVAS.html:62` | ‹PREENCHER: custo real observado da nuvem/LLM durante o MVP, se medido, e premissas revist | 4 | Resultados de teste de usabilidade com usuários (n, tempos, SUS, concl |
| `03-Business-Intelligence-Startup/business-model/LEAN_CANVAS.html:62` | ‹PREENCHER: quais métricas já foram medidas de verdade (ex.: teste de usabilidade) e quais | 4 | Validação do Lean Canvas (entrevistas/CP1, canais, preço, ativos) |
| `03-Business-Intelligence-Startup/business-model/LEAN_CANVAS.html:62` | ‹PREENCHER: algum ativo que a equipe realmente já tenha (ex.: rede de contatos com associa | 4 | Validação do Lean Canvas (entrevistas/CP1, canais, preço, ativos) |
| `03-Business-Intelligence-Startup/business-model/LEAN_CANVAS.md:4` | ‹PREENCHER: nome da equipe / startup] | 1 | Nome da equipe/startup |
| `03-Business-Intelligence-Startup/business-model/LEAN_CANVAS.md:16` | ‹PREENCHER: o que foi validado no CP1/entrevistas sobre a dor (quantas pessoas, perfis, fr | 4 | Validação do Lean Canvas (entrevistas/CP1, canais, preço, ativos) |
| `03-Business-Intelligence-Startup/business-model/LEAN_CANVAS.md:17` | ‹PREENCHER: segmentos entrevistados no CP1 e o que mudou (ex.: priorização entre prefeitur | 4 | Validação do Lean Canvas (entrevistas/CP1, canais, preço, ativos) |
| `03-Business-Intelligence-Startup/business-model/LEAN_CANVAS.md:18` | ‹PREENCHER: reação de cidadãos e de possíveis clientes à proposta de valor; frases das ent | 4 | Validação do Lean Canvas (entrevistas/CP1, canais, preço, ativos) |
| `03-Business-Intelligence-Startup/business-model/LEAN_CANVAS.md:19` | ‹PREENCHER: o que foi testado no protótipo/MVP 0/MVP 1 e com quem; o que mudou na solução  | 4 | Validação do Lean Canvas (entrevistas/CP1, canais, preço, ativos) |
| `03-Business-Intelligence-Startup/business-model/LEAN_CANVAS.md:20` | ‹PREENCHER: canais já testados (ex.: divulgação em grupo de associação) e resultado real] | 4 | Validação do Lean Canvas (entrevistas/CP1, canais, preço, ativos) |
| `03-Business-Intelligence-Startup/business-model/LEAN_CANVAS.md:21` | ‹PREENCHER: disposição a pagar ouvida em entrevistas (se houver) e o que mudou no modelo d | 4 | Validação do Lean Canvas (entrevistas/CP1, canais, preço, ativos) |
| `03-Business-Intelligence-Startup/business-model/LEAN_CANVAS.md:22` | ‹PREENCHER: custo real observado da nuvem/LLM durante o MVP, se medido, e premissas revist | 4 | Resultados de teste de usabilidade com usuários (n, tempos, SUS, concl |
| `03-Business-Intelligence-Startup/business-model/LEAN_CANVAS.md:23` | ‹PREENCHER: quais métricas já foram medidas de verdade (ex.: teste de usabilidade) e quais | 4 | Validação do Lean Canvas (entrevistas/CP1, canais, preço, ativos) |
| `03-Business-Intelligence-Startup/business-model/LEAN_CANVAS.md:24` | ‹PREENCHER: algum ativo que a equipe realmente já tenha (ex.: rede de contatos com associa | 4 | Validação do Lean Canvas (entrevistas/CP1, canais, preço, ativos) |
| `03-Business-Intelligence-Startup/business-model/LEAN_CANVAS.md:29` | ‹PREENCHER: o que foi validado no CP1/entrevistas sobre a dor (quantas pessoas, perfis, fr | 4 | Validação do Lean Canvas (entrevistas/CP1, canais, preço, ativos) |
| `03-Business-Intelligence-Startup/business-model/LEAN_CANVAS.md:45` | ‹PREENCHER: segmentos entrevistados no CP1 e o que mudou (ex.: priorização entre prefeitur | 4 | Validação do Lean Canvas (entrevistas/CP1, canais, preço, ativos) |
| `03-Business-Intelligence-Startup/business-model/LEAN_CANVAS.md:59` | ‹PREENCHER: reação de cidadãos e de possíveis clientes à proposta de valor; frases das ent | 4 | Validação do Lean Canvas (entrevistas/CP1, canais, preço, ativos) |
| `03-Business-Intelligence-Startup/business-model/LEAN_CANVAS.md:71` | ‹PREENCHER: o que foi testado no protótipo/MVP 0/MVP 1 e com quem; o que mudou na solução  | 4 | Validação do Lean Canvas (entrevistas/CP1, canais, preço, ativos) |
| `03-Business-Intelligence-Startup/business-model/LEAN_CANVAS.md:81` | ‹PREENCHER: canais já testados (ex.: divulgação em grupo de associação) e resultado real] | 4 | Validação do Lean Canvas (entrevistas/CP1, canais, preço, ativos) |
| `03-Business-Intelligence-Startup/business-model/LEAN_CANVAS.md:90` | ‹PREENCHER: disposição a pagar ouvida em entrevistas (se houver) e o que mudou no modelo d | 4 | Validação do Lean Canvas (entrevistas/CP1, canais, preço, ativos) |
| `03-Business-Intelligence-Startup/business-model/LEAN_CANVAS.md:100` | ‹PREENCHER: custo real observado da nuvem/LLM durante o MVP, se medido, e premissas revist | 4 | Resultados de teste de usabilidade com usuários (n, tempos, SUS, concl |
| `03-Business-Intelligence-Startup/business-model/LEAN_CANVAS.md:110` | ‹PREENCHER: quais métricas já foram medidas de verdade (ex.: teste de usabilidade) e quais | 4 | Validação do Lean Canvas (entrevistas/CP1, canais, preço, ativos) |
| `03-Business-Intelligence-Startup/business-model/LEAN_CANVAS.md:120` | ‹PREENCHER: algum ativo que a equipe realmente já tenha (ex.: rede de contatos com associa | 4 | Validação do Lean Canvas (entrevistas/CP1, canais, preço, ativos) |
| `03-Business-Intelligence-Startup/business-model/LEAN_CANVAS.md:143` | ‹PREENCHER: hipótese do primeiro canvas] | 4 | Validação do Lean Canvas (entrevistas/CP1, canais, preço, ativos) |
| `03-Business-Intelligence-Startup/business-model/LEAN_CANVAS.md:143` | ‹PREENCHER: evidência real] | 4 | Validação do Lean Canvas (entrevistas/CP1, canais, preço, ativos) |
| `03-Business-Intelligence-Startup/business-model/LEAN_CANVAS.md:143` | ‹PREENCHER: decisão] | 4 | Validação do Lean Canvas (entrevistas/CP1, canais, preço, ativos) |
| `03-Business-Intelligence-Startup/business-model/LEAN_CANVAS.md:144` | ‹PREENCHER] | 4 | Validação do Lean Canvas (entrevistas/CP1, canais, preço, ativos) |
| `03-Business-Intelligence-Startup/business-model/LEAN_CANVAS.md:144` | ‹PREENCHER: nº de entrevistas, perfis — sem nomes] | 4 | Validação do Lean Canvas (entrevistas/CP1, canais, preço, ativos) |
| `03-Business-Intelligence-Startup/business-model/LEAN_CANVAS.md:144` | ‹PREENCHER] | 4 | Validação do Lean Canvas (entrevistas/CP1, canais, preço, ativos) |
| `03-Business-Intelligence-Startup/business-model/LEAN_CANVAS.md:145` | ‹PREENCHER] | 4 | Validação do Lean Canvas (entrevistas/CP1, canais, preço, ativos) |
| `03-Business-Intelligence-Startup/business-model/LEAN_CANVAS.md:145` | ‹PREENCHER] | 4 | Validação do Lean Canvas (entrevistas/CP1, canais, preço, ativos) |
| `03-Business-Intelligence-Startup/business-model/LEAN_CANVAS.md:145` | ‹PREENCHER] | 4 | Validação do Lean Canvas (entrevistas/CP1, canais, preço, ativos) |
| `03-Business-Intelligence-Startup/business-model/LEAN_CANVAS.md:146` | ‹PREENCHER] | 4 | Validação do Lean Canvas (entrevistas/CP1, canais, preço, ativos) |
| `03-Business-Intelligence-Startup/business-model/LEAN_CANVAS.md:146` | ‹PREENCHER: teste de usabilidade registrado em pitch/registro_testes_usuarios_TEMPLATE.xls | 4 | Resultados de teste de usabilidade com usuários (n, tempos, SUS, concl |
| `03-Business-Intelligence-Startup/business-model/LEAN_CANVAS.md:146` | ‹PREENCHER] | 4 | Validação do Lean Canvas (entrevistas/CP1, canais, preço, ativos) |
| `03-Business-Intelligence-Startup/business-model/METRICAS_E_IMPACTO.md:6` | ‹PREENCHER: resultados reais] | 4 | Validação do Lean Canvas (entrevistas/CP1, canais, preço, ativos) |
| `03-Business-Intelligence-Startup/business-model/METRICAS_E_IMPACTO.md:70` | ‹PREENCHER: tempo médio antes × depois, taxa de conclusão, SUS médio, nº e perfil dos part | 4 | Resultados de teste de usabilidade com usuários (n, tempos, SUS, concl |
| `03-Business-Intelligence-Startup/business-model/MODELO_DE_NEGOCIO.md:105` | ‹PREENCHER: valor da estimativa de custo da disciplina 06] | 10 | Valor da estimativa de custo da disciplina 06 (modelo de negócio) |
| `03-Business-Intelligence-Startup/business-model/MODELO_DE_NEGOCIO.md:160` | ‹PREENCHER: resultados reais dos testes, quando houver] | 4 | Validação do Lean Canvas (entrevistas/CP1, canais, preço, ativos) |
| `03-Business-Intelligence-Startup/business-model/MODELO_DE_NEGOCIO.md:189` | ‹PREENCHER: número de pessoas com 60 anos ou mais — Censo 2022/IBGE — com link da fonte] | 4 | Dados públicos de contexto (IBGE/Censo/DATASUS/legislação) com fonte |
| `03-Business-Intelligence-Startup/business-model/MODELO_DE_NEGOCIO.md:191` | ‹PREENCHER: dado + fonte (IBGE, estimativas populacionais)] | 4 | Dados públicos de contexto (IBGE/Censo/DATASUS/legislação) com fonte |
| `03-Business-Intelligence-Startup/business-model/MODELO_DE_NEGOCIO.md:194` | ‹PREENCHER: cidade/bairros onde a equipe observou o problema, com fotos próprias] | 3 | Prints, fotos e imagens de evidência |
| `03-Business-Intelligence-Startup/business-model/lean_canvas.json:6` | ‹PREENCHER: nome da equipe / startup] | 1 | Nome da equipe/startup |
| `03-Business-Intelligence-Startup/business-model/lean_canvas.json:26` | ‹PREENCHER: o que foi validado no CP1/entrevistas sobre a dor (quantas pessoas, perfis, fr | 4 | Validação do Lean Canvas (entrevistas/CP1, canais, preço, ativos) |
| `03-Business-Intelligence-Startup/business-model/lean_canvas.json:38` | ‹PREENCHER: o que foi testado no protótipo/MVP 0/MVP 1 e com quem; o que mudou na solução  | 4 | Validação do Lean Canvas (entrevistas/CP1, canais, preço, ativos) |
| `03-Business-Intelligence-Startup/business-model/lean_canvas.json:50` | ‹PREENCHER: quais métricas já foram medidas de verdade (ex.: teste de usabilidade) e quais | 4 | Validação do Lean Canvas (entrevistas/CP1, canais, preço, ativos) |
| `03-Business-Intelligence-Startup/business-model/lean_canvas.json:64` | ‹PREENCHER: reação de cidadãos e de possíveis clientes à proposta de valor; frases das ent | 4 | Validação do Lean Canvas (entrevistas/CP1, canais, preço, ativos) |
| `03-Business-Intelligence-Startup/business-model/lean_canvas.json:74` | ‹PREENCHER: algum ativo que a equipe realmente já tenha (ex.: rede de contatos com associa | 4 | Validação do Lean Canvas (entrevistas/CP1, canais, preço, ativos) |
| `03-Business-Intelligence-Startup/business-model/lean_canvas.json:85` | ‹PREENCHER: canais já testados (ex.: divulgação em grupo de associação) e resultado real] | 4 | Validação do Lean Canvas (entrevistas/CP1, canais, preço, ativos) |
| `03-Business-Intelligence-Startup/business-model/lean_canvas.json:101` | ‹PREENCHER: segmentos entrevistados no CP1 e o que mudou (ex.: priorização entre prefeitur | 4 | Validação do Lean Canvas (entrevistas/CP1, canais, preço, ativos) |
| `03-Business-Intelligence-Startup/business-model/lean_canvas.json:113` | ‹PREENCHER: custo real observado da nuvem/LLM durante o MVP, se medido, e premissas revist | 4 | Resultados de teste de usabilidade com usuários (n, tempos, SUS, concl |
| `03-Business-Intelligence-Startup/business-model/lean_canvas.json:125` | ‹PREENCHER: disposição a pagar ouvida em entrevistas (se houver) e o que mudou no modelo d | 4 | Validação do Lean Canvas (entrevistas/CP1, canais, preço, ativos) |
| `03-Business-Intelligence-Startup/docs/ANALISE_CONCORRENCIA.md:5` | ‹PREENCHER: produto, característica, fonte, data] | 4 | Dados públicos de contexto (IBGE/Censo/DATASUS/legislação) com fonte |
| `03-Business-Intelligence-Startup/docs/DOCUMENTO_DE_ENTREGA_BI.md:5` | ‹PREENCHER: nome da equipe] | 1 | Nome da equipe/startup |
| `03-Business-Intelligence-Startup/docs/DOCUMENTO_DE_ENTREGA_BI.md:9` | ‹PREENCHER: Integrante 1] | 1 | Integrantes: nome completo, RM, papel e turma |
| `03-Business-Intelligence-Startup/docs/DOCUMENTO_DE_ENTREGA_BI.md:9` | ‹PREENCHER] | 4 | Validação do Lean Canvas (entrevistas/CP1, canais, preço, ativos) |
| `03-Business-Intelligence-Startup/docs/DOCUMENTO_DE_ENTREGA_BI.md:9` | ‹PREENCHER] | 4 | Validação do Lean Canvas (entrevistas/CP1, canais, preço, ativos) |
| `03-Business-Intelligence-Startup/docs/DOCUMENTO_DE_ENTREGA_BI.md:10` | ‹PREENCHER: Integrante 2] | 1 | Integrantes: nome completo, RM, papel e turma |
| `03-Business-Intelligence-Startup/docs/DOCUMENTO_DE_ENTREGA_BI.md:10` | ‹PREENCHER] | 4 | Validação do Lean Canvas (entrevistas/CP1, canais, preço, ativos) |
| `03-Business-Intelligence-Startup/docs/DOCUMENTO_DE_ENTREGA_BI.md:10` | ‹PREENCHER] | 4 | Validação do Lean Canvas (entrevistas/CP1, canais, preço, ativos) |
| `03-Business-Intelligence-Startup/docs/DOCUMENTO_DE_ENTREGA_BI.md:11` | ‹PREENCHER: Integrante 3] | 1 | Integrantes: nome completo, RM, papel e turma |
| `03-Business-Intelligence-Startup/docs/DOCUMENTO_DE_ENTREGA_BI.md:11` | ‹PREENCHER] | 4 | Validação do Lean Canvas (entrevistas/CP1, canais, preço, ativos) |
| `03-Business-Intelligence-Startup/docs/DOCUMENTO_DE_ENTREGA_BI.md:11` | ‹PREENCHER] | 4 | Validação do Lean Canvas (entrevistas/CP1, canais, preço, ativos) |
| `03-Business-Intelligence-Startup/docs/DOCUMENTO_DE_ENTREGA_BI.md:12` | ‹PREENCHER: Integrante 4] | 1 | Integrantes: nome completo, RM, papel e turma |
| `03-Business-Intelligence-Startup/docs/DOCUMENTO_DE_ENTREGA_BI.md:12` | ‹PREENCHER] | 4 | Validação do Lean Canvas (entrevistas/CP1, canais, preço, ativos) |
| `03-Business-Intelligence-Startup/docs/DOCUMENTO_DE_ENTREGA_BI.md:12` | ‹PREENCHER] | 4 | Validação do Lean Canvas (entrevistas/CP1, canais, preço, ativos) |
| `03-Business-Intelligence-Startup/docs/DOCUMENTO_DE_ENTREGA_BI.md:13` | ‹PREENCHER: Integrante 5] | 1 | Integrantes: nome completo, RM, papel e turma |
| `03-Business-Intelligence-Startup/docs/DOCUMENTO_DE_ENTREGA_BI.md:13` | ‹PREENCHER] | 4 | Validação do Lean Canvas (entrevistas/CP1, canais, preço, ativos) |
| `03-Business-Intelligence-Startup/docs/DOCUMENTO_DE_ENTREGA_BI.md:13` | ‹PREENCHER] | 4 | Validação do Lean Canvas (entrevistas/CP1, canais, preço, ativos) |
| `03-Business-Intelligence-Startup/docs/DOCUMENTO_DE_ENTREGA_BI.md:19` | ‹PREENCHER: URL_VIDEO] | 2 | Link do vídeo-pitch/demonstração (público ou não listado) |
| `03-Business-Intelligence-Startup/docs/DOCUMENTO_DE_ENTREGA_BI.md:20` | ‹PREENCHER: URL_MVP] | 5 | URL pública do MVP (saída app_url do Terraform / FQDN do ACI) |
| `03-Business-Intelligence-Startup/docs/DOCUMENTO_DE_ENTREGA_BI.md:21` | ‹PREENCHER: URL_REPOSITORIO] | 2 | URL do repositório público no GitHub |
| `03-Business-Intelligence-Startup/docs/DOCUMENTO_DE_ENTREGA_BI.md:39` | ‹PREENCHER: cidade/bairros onde a equipe observou o problema] | 4 | Território onde a equipe observou o problema (cidade/bairro/data) |
| `03-Business-Intelligence-Startup/docs/DOCUMENTO_DE_ENTREGA_BI.md:76` | ‹PREENCHER: nº de participantes e perfil (sem nomes)] | 4 | Resultados de teste de usabilidade com usuários (n, tempos, SUS, concl |
| `03-Business-Intelligence-Startup/docs/DOCUMENTO_DE_ENTREGA_BI.md:77` | ‹PREENCHER: média antes (s) × depois (s)] | 4 | Resultados de teste de usabilidade com usuários (n, tempos, SUS, concl |
| `03-Business-Intelligence-Startup/docs/DOCUMENTO_DE_ENTREGA_BI.md:78` | ‹PREENCHER: %] | 4 | Resultados de teste de usabilidade com usuários (n, tempos, SUS, concl |
| `03-Business-Intelligence-Startup/docs/DOCUMENTO_DE_ENTREGA_BI.md:79` | ‹PREENCHER: média] | 4 | Resultados de teste de usabilidade com usuários (n, tempos, SUS, concl |
| `03-Business-Intelligence-Startup/docs/DOCUMENTO_DE_ENTREGA_BI.md:80` | ‹PREENCHER: lista de protocolos] | 4 | Resultados de teste de usabilidade com usuários (n, tempos, SUS, concl |
| `03-Business-Intelligence-Startup/docs/DOCUMENTO_DE_ENTREGA_BI.md:81` | ‹PREENCHER: sim/não] | 4 | Resultados de teste de usabilidade com usuários (n, tempos, SUS, concl |
| `03-Business-Intelligence-Startup/docs/DOCUMENTO_DE_ENTREGA_BI.md:92` | ‹PREENCHER] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `03-Business-Intelligence-Startup/docs/PROBLEMA_E_CIDADAO.md:5` | ‹PREENCHER: nº de entrevistas, perfis e achados — sem nomes] | 4 | Validação do Lean Canvas (entrevistas/CP1, canais, preço, ativos) |
| `03-Business-Intelligence-Startup/docs/PROBLEMA_E_CIDADAO.md:23` | ‹PREENCHER: dado do Censo 2022/IBGE + link] | 4 | Dados públicos de contexto (IBGE/Censo/DATASUS/legislação) com fonte |
| `03-Business-Intelligence-Startup/docs/PROBLEMA_E_CIDADAO.md:24` | ‹PREENCHER: dado + fonte (ex.: Ministério da Saúde/DATASUS)] | 4 | Dados públicos de contexto (IBGE/Censo/DATASUS/legislação) com fonte |
| `03-Business-Intelligence-Startup/docs/PROBLEMA_E_CIDADAO.md:28` | ‹PREENCHER: cidade/bairros onde a equipe observou o problema, com data das observações e f | 3 | Prints, fotos e imagens de evidência |
| `03-Business-Intelligence-Startup/docs/PROBLEMA_E_CIDADAO.md:66` | ‹PREENCHER: tempo e nº de etapas observados no teste "antes" — ver pitch/ROTEIRO_TESTE_USA | 4 | Resultados de teste de usabilidade com usuários (n, tempos, SUS, concl |
| `03-Business-Intelligence-Startup/docs/PROBLEMA_E_CIDADAO.md:72` | ‹PREENCHER: relato de entrevista ou fonte] | 4 | Dados públicos de contexto (IBGE/Censo/DATASUS/legislação) com fonte |
| `03-Business-Intelligence-Startup/docs/PROBLEMA_E_CIDADAO.md:73` | ‹PREENCHER: dado + fonte] | 4 | Dados públicos de contexto (IBGE/Censo/DATASUS/legislação) com fonte |
| `03-Business-Intelligence-Startup/docs/PROBLEMA_E_CIDADAO.md:74` | ‹PREENCHER: dado obtido em entrevista com gestor, se houver] | 4 | Dados públicos de contexto (IBGE/Censo/DATASUS/legislação) com fonte |
| `03-Business-Intelligence-Startup/docs/PROBLEMA_E_CIDADAO.md:75` | ‹PREENCHER: legislação municipal de calçadas da cidade observada] | 4 | Dados públicos de contexto (IBGE/Censo/DATASUS/legislação) com fonte |
| `03-Business-Intelligence-Startup/docs/PROXIMOS_PASSOS.md:7` | ‹PREENCHER] | 1 | Integrantes: nome completo, RM, papel e turma |
| `03-Business-Intelligence-Startup/docs/PROXIMOS_PASSOS.md:7` | ‹PREENCHER] | 8 | Responsável e prazo dos próximos passos |
| `03-Business-Intelligence-Startup/docs/PROXIMOS_PASSOS.md:8` | ‹PREENCHER] | 1 | Integrantes: nome completo, RM, papel e turma |
| `03-Business-Intelligence-Startup/docs/PROXIMOS_PASSOS.md:8` | ‹PREENCHER] | 8 | Responsável e prazo dos próximos passos |
| `03-Business-Intelligence-Startup/docs/PROXIMOS_PASSOS.md:9` | ‹PREENCHER] | 1 | Integrantes: nome completo, RM, papel e turma |
| `03-Business-Intelligence-Startup/docs/PROXIMOS_PASSOS.md:9` | ‹PREENCHER] | 8 | Responsável e prazo dos próximos passos |
| `03-Business-Intelligence-Startup/docs/PROXIMOS_PASSOS.md:10` | ‹PREENCHER] | 1 | Integrantes: nome completo, RM, papel e turma |
| `03-Business-Intelligence-Startup/docs/PROXIMOS_PASSOS.md:10` | ‹PREENCHER] | 8 | Responsável e prazo dos próximos passos |
| `03-Business-Intelligence-Startup/docs/PROXIMOS_PASSOS.md:11` | ‹PREENCHER] | 1 | Integrantes: nome completo, RM, papel e turma |
| `03-Business-Intelligence-Startup/docs/PROXIMOS_PASSOS.md:11` | ‹PREENCHER] | 8 | Responsável e prazo dos próximos passos |
| `03-Business-Intelligence-Startup/docs/PROXIMOS_PASSOS.md:12` | ‹PREENCHER] | 1 | Integrantes: nome completo, RM, papel e turma |
| `03-Business-Intelligence-Startup/docs/links_entrega.yaml:4` | ‹PREENCHER: URL_VIDEO] | 2 | Link do vídeo-pitch/demonstração (público ou não listado) |
| `03-Business-Intelligence-Startup/docs/links_entrega.yaml:4` | ‹PREENCHER: URL_MVP] | 5 | URL pública do MVP (saída app_url do Terraform / FQDN do ACI) |
| `03-Business-Intelligence-Startup/docs/links_entrega.yaml:4` | ‹PREENCHER: URL_REPOSITORIO] | 2 | URL do repositório público no GitHub |
| `03-Business-Intelligence-Startup/pitch/LISTA_DE_CENAS.md:8` | ‹PREENCHER: bairro/cidade] | 4 | Território onde a equipe observou o problema (cidade/bairro/data) |
| `03-Business-Intelligence-Startup/pitch/LISTA_DE_EVIDENCIAS.md:32` | ‹PREENCHER: tempo médio antes (s) × depois (s), nº de participantes] | 4 | Resultados de teste de usabilidade com usuários (n, tempos, SUS, concl |
| `03-Business-Intelligence-Startup/pitch/LISTA_DE_EVIDENCIAS.md:62` | ‹PREENCHER] | 2 | Link do vídeo-pitch/demonstração (público ou não listado) |
| `03-Business-Intelligence-Startup/pitch/LISTA_DE_EVIDENCIAS.md:63` | ‹PREENCHER] | 5 | URL pública do MVP (saída app_url do Terraform / FQDN do ACI) |
| `03-Business-Intelligence-Startup/pitch/LISTA_DE_EVIDENCIAS.md:64` | ‹PREENCHER] | 2 | URL do repositório público no GitHub |
| `03-Business-Intelligence-Startup/pitch/ROTEIRO_DE_GRAVACAO.md:8` | ‹PREENCHER: URL pública do MVP] | 5 | URL pública do MVP (saída app_url do Terraform / FQDN do ACI) |
| `03-Business-Intelligence-Startup/pitch/ROTEIRO_DE_GRAVACAO.md:31` | ‹PREENCHER: URL] | 5 | URL pública do MVP (saída app_url do Terraform / FQDN do ACI) |
| `03-Business-Intelligence-Startup/pitch/ROTEIRO_DE_GRAVACAO.md:78` | ‹PREENCHER] | 5 | URL pública do MVP (saída app_url do Terraform / FQDN do ACI) |
| `03-Business-Intelligence-Startup/pitch/ROTEIRO_PITCH.md:7` | ‹PREENCHER: ...] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `03-Business-Intelligence-Startup/pitch/ROTEIRO_PITCH.md:14` | ‹PREENCHER: Integrante 1] | 1 | Integrantes: nome completo, RM, papel e turma |
| `03-Business-Intelligence-Startup/pitch/ROTEIRO_PITCH.md:15` | ‹PREENCHER: Integrante 2] | 1 | Integrantes: nome completo, RM, papel e turma |
| `03-Business-Intelligence-Startup/pitch/ROTEIRO_PITCH.md:16` | ‹PREENCHER: Integrante 3] | 1 | Integrantes: nome completo, RM, papel e turma |
| `03-Business-Intelligence-Startup/pitch/ROTEIRO_PITCH.md:16` | ‹PREENCHER: Integrante 4] | 1 | Integrantes: nome completo, RM, papel e turma |
| `03-Business-Intelligence-Startup/pitch/ROTEIRO_PITCH.md:17` | ‹PREENCHER: Integrante 4] | 1 | Integrantes: nome completo, RM, papel e turma |
| `03-Business-Intelligence-Startup/pitch/ROTEIRO_PITCH.md:18` | ‹PREENCHER: Integrante 5] | 1 | Integrantes: nome completo, RM, papel e turma |
| `03-Business-Intelligence-Startup/pitch/ROTEIRO_PITCH.md:19` | ‹PREENCHER: Integrante 1] | 1 | Integrantes: nome completo, RM, papel e turma |
| `03-Business-Intelligence-Startup/pitch/ROTEIRO_PITCH.md:20` | ‹PREENCHER] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `03-Business-Intelligence-Startup/pitch/ROTEIRO_PITCH.md:22` | ‹PREENCHER] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `03-Business-Intelligence-Startup/pitch/ROTEIRO_PITCH.md:24` | ‹PREENCHER] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `03-Business-Intelligence-Startup/pitch/ROTEIRO_PITCH.md:28` | ‹PREENCHER: Integrante 1] | 1 | Integrantes: nome completo, RM, papel e turma |
| `03-Business-Intelligence-Startup/pitch/ROTEIRO_PITCH.md:30` | ‹PREENCHER: foto própria — bairro/cidade] | 3 | Prints, fotos e imagens de evidência |
| `03-Business-Intelligence-Startup/pitch/ROTEIRO_PITCH.md:39` | ‹PREENCHER: uma frase real ouvida em entrevista, com autorização — ou o local observado pe | 4 | Validação do Lean Canvas (entrevistas/CP1, canais, preço, ativos) |
| `03-Business-Intelligence-Startup/pitch/ROTEIRO_PITCH.md:44` | ‹PREENCHER: Integrante 2] | 1 | Integrantes: nome completo, RM, papel e turma |
| `03-Business-Intelligence-Startup/pitch/ROTEIRO_PITCH.md:56` | ‹PREENCHER: Integrante 3] | 1 | Integrantes: nome completo, RM, papel e turma |
| `03-Business-Intelligence-Startup/pitch/ROTEIRO_PITCH.md:56` | ‹PREENCHER: Integrante 4] | 1 | Integrantes: nome completo, RM, papel e turma |
| `03-Business-Intelligence-Startup/pitch/ROTEIRO_PITCH.md:58` | ‹PREENCHER: URL pública do MVP] | 5 | URL pública do MVP (saída app_url do Terraform / FQDN do ACI) |
| `03-Business-Intelligence-Startup/pitch/ROTEIRO_PITCH.md:76` | ‹PREENCHER: Integrante 4] | 1 | Integrantes: nome completo, RM, papel e turma |
| `03-Business-Intelligence-Startup/pitch/ROTEIRO_PITCH.md:89` | ‹PREENCHER: o que o Lean Canvas mudou desde o CP1, em uma frase] | 4 | Validação do Lean Canvas (entrevistas/CP1, canais, preço, ativos) |
| `03-Business-Intelligence-Startup/pitch/ROTEIRO_PITCH.md:92` | ‹PREENCHER: Integrante 5] | 1 | Integrantes: nome completo, RM, papel e turma |
| `03-Business-Intelligence-Startup/pitch/ROTEIRO_PITCH.md:99` | ‹PREENCHER: resultado real do teste com usuários — ex.: "com N participantes, o tempo caiu | 4 | Resultados de teste de usabilidade com usuários (n, tempos, SUS, concl |
| `03-Business-Intelligence-Startup/pitch/ROTEIRO_PITCH.md:104` | ‹PREENCHER: data] | 8 | Data de envio/entrega/conferência |
| `03-Business-Intelligence-Startup/pitch/ROTEIRO_PITCH.md:111` | ‹PREENCHER: Integrante 1 — nome] | 1 | Integrantes: nome completo, RM, papel e turma |
| `03-Business-Intelligence-Startup/pitch/ROTEIRO_PITCH.md:111` | ‹PREENCHER: papel em poucas palavras] | 1 | Integrantes: nome completo, RM, papel e turma |
| `03-Business-Intelligence-Startup/pitch/ROTEIRO_PITCH.md:112` | ‹PREENCHER: Integrante 2 — nome] | 1 | Integrantes: nome completo, RM, papel e turma |
| `03-Business-Intelligence-Startup/pitch/ROTEIRO_PITCH.md:112` | ‹PREENCHER: papel] | 1 | Integrantes: nome completo, RM, papel e turma |
| `03-Business-Intelligence-Startup/pitch/ROTEIRO_PITCH.md:113` | ‹PREENCHER: Integrante 3 — nome] | 1 | Integrantes: nome completo, RM, papel e turma |
| `03-Business-Intelligence-Startup/pitch/ROTEIRO_PITCH.md:113` | ‹PREENCHER: papel] | 1 | Integrantes: nome completo, RM, papel e turma |
| `03-Business-Intelligence-Startup/pitch/ROTEIRO_PITCH.md:114` | ‹PREENCHER: Integrante 4 — nome] | 1 | Integrantes: nome completo, RM, papel e turma |
| `03-Business-Intelligence-Startup/pitch/ROTEIRO_PITCH.md:114` | ‹PREENCHER: papel] | 1 | Integrantes: nome completo, RM, papel e turma |
| `03-Business-Intelligence-Startup/pitch/ROTEIRO_PITCH.md:115` | ‹PREENCHER: Integrante 5 — nome] | 1 | Integrantes: nome completo, RM, papel e turma |
| `03-Business-Intelligence-Startup/pitch/ROTEIRO_PITCH.md:115` | ‹PREENCHER: papel] | 1 | Integrantes: nome completo, RM, papel e turma |
| `03-Business-Intelligence-Startup/pitch/ROTEIRO_PITCH.md:125` | ‹PREENCHER] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `03-Business-Intelligence-Startup/pitch/ROTEIRO_TESTE_USABILIDADE.md:19` | ‹PREENCHER: Integrante] | 1 | Integrantes: nome completo, RM, papel e turma |
| `03-Business-Intelligence-Startup/pitch/ROTEIRO_TESTE_USABILIDADE.md:20` | ‹PREENCHER: Integrante] | 1 | Integrantes: nome completo, RM, papel e turma |
| `03-Business-Intelligence-Startup/pitch/ROTEIRO_TESTE_USABILIDADE.md:24` | ‹PREENCHER: URL] | 5 | URL pública do MVP (saída app_url do Terraform / FQDN do ACI) |
| `03-Business-Intelligence-Startup/pitch/STORYBOARD.md:4` | ‹PREENCHER: nome do integrante N] | 1 | Integrantes: nome completo, RM, papel e turma |
| `03-Business-Intelligence-Startup/pitch/STORYBOARD.md:8` | ‹PREENCHER: foto própria e local] | 3 | Prints, fotos e imagens de evidência |
| `03-Business-Intelligence-Startup/pitch/STORYBOARD.md:11` | ‹PREENCHER] | 4 | Validação do Lean Canvas (entrevistas/CP1, canais, preço, ativos) |
| `03-Business-Intelligence-Startup/pitch/TERMO_CONSENTIMENTO_MODELO.md:5` | ‹PREENCHER: confirmar com o professor se há exigência adicional] | 8 | Requisitos/critérios oficiais confirmados com o professor |
| `03-Business-Intelligence-Startup/pitch/TERMO_CONSENTIMENTO_MODELO.md:8` | ‹PREENCHER: nome da equipe] | 1 | Nome da equipe/startup |
| `03-Business-Intelligence-Startup/pitch/TERMO_CONSENTIMENTO_MODELO.md:8` | ‹PREENCHER: e-mail da equipe] | 8 | Canal de contato da equipe (e-mail institucional) |
| `03-Business-Intelligence-Startup/scripts/gerar_lean_canvas.py:127` | ‹PREENCHER: hipótese do primeiro canvas] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `03-Business-Intelligence-Startup/scripts/gerar_lean_canvas.py:127` | ‹PREENCHER: evidência real] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `03-Business-Intelligence-Startup/scripts/gerar_lean_canvas.py:127` | ‹PREENCHER: decisão] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `03-Business-Intelligence-Startup/scripts/gerar_lean_canvas.py:128` | ‹PREENCHER] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `03-Business-Intelligence-Startup/scripts/gerar_lean_canvas.py:128` | ‹PREENCHER: nº de entrevistas, perfis — sem nomes] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `03-Business-Intelligence-Startup/scripts/gerar_lean_canvas.py:128` | ‹PREENCHER] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `03-Business-Intelligence-Startup/scripts/gerar_lean_canvas.py:129` | ‹PREENCHER] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `03-Business-Intelligence-Startup/scripts/gerar_lean_canvas.py:129` | ‹PREENCHER] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `03-Business-Intelligence-Startup/scripts/gerar_lean_canvas.py:129` | ‹PREENCHER] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `03-Business-Intelligence-Startup/scripts/gerar_lean_canvas.py:130` | ‹PREENCHER] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `03-Business-Intelligence-Startup/scripts/gerar_lean_canvas.py:130` | ‹PREENCHER: teste de usabilidade registrado em pitch/registro_testes_usuarios_TEMPLATE.xls | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `03-Business-Intelligence-Startup/scripts/gerar_lean_canvas.py:130` | ‹PREENCHER] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `03-Business-Intelligence-Startup/scripts/gerar_lean_canvas.py:291` | ‹PREENCHER: caminho em pitch/evidencias/ ou link] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `03-Business-Intelligence-Startup/scripts/gerar_pdf_entrega.py:10` | ‹PREENCHER: URL_VIDEO] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `03-Business-Intelligence-Startup/scripts/gerar_pdf_entrega.py:10` | ‹PREENCHER: URL_MVP] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `03-Business-Intelligence-Startup/scripts/gerar_pdf_entrega.py:10` | ‹PREENCHER: URL_REPOSITORIO] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `03-Business-Intelligence-Startup/scripts/gerar_pdf_entrega.py:15` | ‹PREENCHER] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `03-Business-Intelligence-Startup/scripts/gerar_pdf_entrega.py:41` | ‹PREENCHER: URL_VIDEO] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `03-Business-Intelligence-Startup/scripts/gerar_pdf_entrega.py:42` | ‹PREENCHER: URL_MVP] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `03-Business-Intelligence-Startup/scripts/gerar_pdf_entrega.py:43` | ‹PREENCHER: URL_REPOSITORIO] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `03-Business-Intelligence-Startup/scripts/gerar_pdf_entrega.py:47` | ‹PREENCHER[^\] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `03-Business-Intelligence-Startup/scripts/gerar_pdf_entrega.py:154` | ‹PREENCHER] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `03-Business-Intelligence-Startup/scripts/gerar_pdf_entrega.py:201` | ‹PREENCHER] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `04-Applied-Computer-Vision/PENDENCIAS_E_ACOES_MANUAIS.txt:34` | ‹PREENCHER] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `04-Applied-Computer-Vision/PENDENCIAS_E_ACOES_MANUAIS.txt:54` | ‹PREENCHER] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `04-Applied-Computer-Vision/PENDENCIAS_E_ACOES_MANUAIS.txt:57` | ‹PREENCHER] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `04-Applied-Computer-Vision/PENDENCIAS_E_ACOES_MANUAIS.txt:109` | ‹PREENCHER] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `04-Applied-Computer-Vision/PENDENCIAS_E_ACOES_MANUAIS.txt:153` | ‹PREENCHER] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `04-Applied-Computer-Vision/PENDENCIAS_E_ACOES_MANUAIS.txt:154` | ‹PREENCHER] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `04-Applied-Computer-Vision/docs/DOCUMENTACAO_TECNICA_TRANSFORMACOES.md:342` | ‹PREENCHER: resultado da base real após a coleta e rotulagem] | 4 | Resultado da comparação com fotos reais rotuladas manualmente |
| `04-Applied-Computer-Vision/docs/RELATORIO_ENTREGA_VISAO.md:6` | ‹PREENCHER: nome da equipe] | 1 | Nome da equipe/startup |
| `04-Applied-Computer-Vision/docs/RELATORIO_ENTREGA_VISAO.md:6` | ‹PREENCHER: nomes e RMs de todos os integrantes] | 1 | Integrantes: nome completo, RM, papel e turma |
| `04-Applied-Computer-Vision/docs/RELATORIO_ENTREGA_VISAO.md:7` | ‹PREENCHER: data] | 8 | Data de envio/entrega/conferência |
| `04-Applied-Computer-Vision/docs/RELATORIO_ENTREGA_VISAO.md:13` | ‹PREENCHER: URL_VIDEO] | 2 | Link do vídeo-pitch/demonstração (público ou não listado) |
| `04-Applied-Computer-Vision/docs/RELATORIO_ENTREGA_VISAO.md:14` | ‹PREENCHER: URL_MVP] | 5 | URL pública do MVP (saída app_url do Terraform / FQDN do ACI) |
| `04-Applied-Computer-Vision/docs/RELATORIO_ENTREGA_VISAO.md:15` | ‹PREENCHER: URL_MVP] | 5 | URL pública do MVP (saída app_url do Terraform / FQDN do ACI) |
| `04-Applied-Computer-Vision/docs/RELATORIO_ENTREGA_VISAO.md:16` | ‹PREENCHER: URL_REPOSITORIO] | 2 | URL do repositório público no GitHub |
| `04-Applied-Computer-Vision/docs/RELATORIO_ENTREGA_VISAO.md:168` | ‹PREENCHER: resultado da comparação com fotos reais rotuladas manualmente | 3 | Prints, fotos e imagens de evidência |
| `04-Applied-Computer-Vision/docs/RELATORIO_ENTREGA_VISAO.md:191` | ‹PREENCHER: confirmar na URL pública que as duas rotas funcionam — depende do deploy da di | 5 | Conferência na URL pública (rotas, /health, assistente) |
| `04-Applied-Computer-Vision/docs/ROTEIRO_VIDEO_VISAO.md:17` | ‹PREENCHER: Integrante 1] | 1 | Integrantes: nome completo, RM, papel e turma |
| `04-Applied-Computer-Vision/docs/ROTEIRO_VIDEO_VISAO.md:18` | ‹PREENCHER: Integrante 2] | 1 | Integrantes: nome completo, RM, papel e turma |
| `04-Applied-Computer-Vision/docs/ROTEIRO_VIDEO_VISAO.md:19` | ‹PREENCHER: Integrante 3] | 1 | Integrantes: nome completo, RM, papel e turma |
| `04-Applied-Computer-Vision/docs/ROTEIRO_VIDEO_VISAO.md:19` | ‹PREENCHER: URL_MVP] | 5 | URL pública do MVP (saída app_url do Terraform / FQDN do ACI) |
| `04-Applied-Computer-Vision/docs/ROTEIRO_VIDEO_VISAO.md:20` | ‹PREENCHER: Integrante 4] | 1 | Integrantes: nome completo, RM, papel e turma |
| `04-Applied-Computer-Vision/docs/ROTEIRO_VIDEO_VISAO.md:21` | ‹PREENCHER: Integrante 5] | 1 | Integrantes: nome completo, RM, papel e turma |
| `04-Applied-Computer-Vision/docs/ROTEIRO_VIDEO_VISAO.md:22` | ‹PREENCHER: Integrante 1 ou todos] | 1 | Integrantes: nome completo, RM, papel e turma |
| `04-Applied-Computer-Vision/docs/ROTEIRO_VIDEO_VISAO.md:26` | ‹PREENCHER: Integrante 1] | 1 | Integrantes: nome completo, RM, papel e turma |
| `04-Applied-Computer-Vision/docs/ROTEIRO_VIDEO_VISAO.md:31` | ‹PREENCHER: Integrante 2] | 1 | Integrantes: nome completo, RM, papel e turma |
| `04-Applied-Computer-Vision/docs/ROTEIRO_VIDEO_VISAO.md:37` | ‹PREENCHER: Integrante 3] | 1 | Integrantes: nome completo, RM, papel e turma |
| `04-Applied-Computer-Vision/docs/ROTEIRO_VIDEO_VISAO.md:39` | ‹PREENCHER: URL_MVP] | 5 | URL pública do MVP (saída app_url do Terraform / FQDN do ACI) |
| `04-Applied-Computer-Vision/docs/ROTEIRO_VIDEO_VISAO.md:47` | ‹PREENCHER: Integrante 4] | 1 | Integrantes: nome completo, RM, papel e turma |
| `04-Applied-Computer-Vision/docs/ROTEIRO_VIDEO_VISAO.md:54` | ‹PREENCHER: Integrante 5] | 1 | Integrantes: nome completo, RM, papel e turma |
| `04-Applied-Computer-Vision/docs/ROTEIRO_VIDEO_VISAO.md:59` | ‹PREENCHER: se houver base real rotulada, trocar por: número de fotos reais e resultado da | 3 | Prints, fotos e imagens de evidência |
| `04-Applied-Computer-Vision/docs/ROTEIRO_VIDEO_VISAO.md:61` | ‹PREENCHER: Integrante 1 ou todos] | 1 | Integrantes: nome completo, RM, papel e turma |
| `04-Applied-Computer-Vision/docs/gerar_pdf_relatorio.py:3` | ‹PREENCHER: URL_VIDEO] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `04-Applied-Computer-Vision/docs/gerar_pdf_relatorio.py:4` | ‹PREENCHER: URL_MVP] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `04-Applied-Computer-Vision/docs/gerar_pdf_relatorio.py:4` | ‹PREENCHER: URL_REPOSITORIO] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `04-Applied-Computer-Vision/docs/gerar_pdf_relatorio.py:12` | ‹PREENCHER] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `04-Applied-Computer-Vision/docs/gerar_pdf_relatorio.py:39` | ‹PREENCHER: URL_VIDEO] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `04-Applied-Computer-Vision/docs/gerar_pdf_relatorio.py:40` | ‹PREENCHER: URL_MVP] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `04-Applied-Computer-Vision/docs/gerar_pdf_relatorio.py:41` | ‹PREENCHER: URL_REPOSITORIO] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `04-Applied-Computer-Vision/docs/gerar_pdf_relatorio.py:45` | ‹PREENCHER[^\] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `04-Applied-Computer-Vision/docs/gerar_pdf_relatorio.py:152` | ‹PREENCHER] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `04-Applied-Computer-Vision/docs/gerar_pdf_relatorio.py:163` | ‹PREENCHER] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `04-Applied-Computer-Vision/docs/gerar_pdf_relatorio.py:165` | ‹PREENCHER] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `04-Applied-Computer-Vision/docs/links_entrega.yaml:4` | ‹PREENCHER: URL_VIDEO] | 2 | Link do vídeo-pitch/demonstração (público ou não listado) |
| `04-Applied-Computer-Vision/docs/links_entrega.yaml:4` | ‹PREENCHER: URL_MVP] | 5 | URL pública do MVP (saída app_url do Terraform / FQDN do ACI) |
| `04-Applied-Computer-Vision/docs/links_entrega.yaml:5` | ‹PREENCHER: URL_REPOSITORIO] | 2 | URL do repositório público no GitHub |
| `04-Applied-Computer-Vision/results/RELATORIO_COMPARACAO.md:48` | ‹PREENCHER: resultados da base real, quando existirem] | 4 | Resultado da comparação com fotos reais rotuladas manualmente |
| `04-Applied-Computer-Vision/samples/real/rotulos_manuais_reais_TEMPLATE.csv:2` | ‹PREENCHER: descrição objetiva do que aparece na foto] | 9 | Placeholder de arquivo-modelo (.example / template CSV) |
| `04-Applied-Computer-Vision/samples/real/rotulos_manuais_reais_TEMPLATE.csv:2` | ‹PREENCHER: AAAA-MM-DD] | 9 | Placeholder de arquivo-modelo (.example / template CSV) |
| `04-Applied-Computer-Vision/samples/real/rotulos_manuais_reais_TEMPLATE.csv:2` | ‹PREENCHER: calçada \| travessia \| rampa] | 9 | Placeholder de arquivo-modelo (.example / template CSV) |
| `04-Applied-Computer-Vision/samples/real/rotulos_manuais_reais_TEMPLATE.csv:2` | ‹PREENCHER: sim/não] | 9 | Placeholder de arquivo-modelo (.example / template CSV) |
| `04-Applied-Computer-Vision/samples/real/rotulos_manuais_reais_TEMPLATE.csv:2` | ‹PREENCHER: sim/não] | 9 | Placeholder de arquivo-modelo (.example / template CSV) |
| `04-Applied-Computer-Vision/samples/real/rotulos_manuais_reais_TEMPLATE.csv:2` | ‹PREENCHER: sim/não] | 9 | Placeholder de arquivo-modelo (.example / template CSV) |
| `04-Applied-Computer-Vision/samples/real/rotulos_manuais_reais_TEMPLATE.csv:2` | ‹PREENCHER: nome ou iniciais do integrante] | 9 | Placeholder de arquivo-modelo (.example / template CSV) |
| `04-Applied-Computer-Vision/samples/real/rotulos_manuais_reais_TEMPLATE.csv:2` | ‹PREENCHER: nome ou iniciais] | 9 | Placeholder de arquivo-modelo (.example / template CSV) |
| `04-Applied-Computer-Vision/samples/real/rotulos_manuais_reais_TEMPLATE.csv:2` | ‹PREENCHER: rótulo dado pela segunda pessoa] | 9 | Placeholder de arquivo-modelo (.example / template CSV) |
| `04-Applied-Computer-Vision/samples/real/rotulos_manuais_reais_TEMPLATE.csv:2` | ‹PREENCHER: dúvidas ou condições da foto] | 9 | Placeholder de arquivo-modelo (.example / template CSV) |
| `04-Applied-Computer-Vision/samples/real/rotulos_manuais_reais_TEMPLATE.csv:3` | ‹PREENCHER] | 9 | Placeholder de arquivo-modelo (.example / template CSV) |
| `04-Applied-Computer-Vision/samples/real/rotulos_manuais_reais_TEMPLATE.csv:3` | ‹PREENCHER] | 9 | Placeholder de arquivo-modelo (.example / template CSV) |
| `04-Applied-Computer-Vision/samples/real/rotulos_manuais_reais_TEMPLATE.csv:3` | ‹PREENCHER] | 9 | Placeholder de arquivo-modelo (.example / template CSV) |
| `04-Applied-Computer-Vision/samples/real/rotulos_manuais_reais_TEMPLATE.csv:3` | ‹PREENCHER] | 9 | Placeholder de arquivo-modelo (.example / template CSV) |
| `04-Applied-Computer-Vision/samples/real/rotulos_manuais_reais_TEMPLATE.csv:3` | ‹PREENCHER] | 9 | Placeholder de arquivo-modelo (.example / template CSV) |
| `04-Applied-Computer-Vision/samples/real/rotulos_manuais_reais_TEMPLATE.csv:3` | ‹PREENCHER] | 9 | Placeholder de arquivo-modelo (.example / template CSV) |
| `04-Applied-Computer-Vision/samples/real/rotulos_manuais_reais_TEMPLATE.csv:3` | ‹PREENCHER] | 9 | Placeholder de arquivo-modelo (.example / template CSV) |
| `04-Applied-Computer-Vision/samples/real/rotulos_manuais_reais_TEMPLATE.csv:3` | ‹PREENCHER] | 9 | Placeholder de arquivo-modelo (.example / template CSV) |
| `04-Applied-Computer-Vision/samples/real/rotulos_manuais_reais_TEMPLATE.csv:3` | ‹PREENCHER] | 9 | Placeholder de arquivo-modelo (.example / template CSV) |
| `04-Applied-Computer-Vision/samples/real/rotulos_manuais_reais_TEMPLATE.csv:3` | ‹PREENCHER] | 9 | Placeholder de arquivo-modelo (.example / template CSV) |
| `04-Applied-Computer-Vision/samples/real/rotulos_manuais_reais_TEMPLATE.csv:4` | ‹PREENCHER] | 9 | Placeholder de arquivo-modelo (.example / template CSV) |
| `04-Applied-Computer-Vision/samples/real/rotulos_manuais_reais_TEMPLATE.csv:4` | ‹PREENCHER] | 9 | Placeholder de arquivo-modelo (.example / template CSV) |
| `04-Applied-Computer-Vision/samples/real/rotulos_manuais_reais_TEMPLATE.csv:4` | ‹PREENCHER] | 9 | Placeholder de arquivo-modelo (.example / template CSV) |
| `04-Applied-Computer-Vision/samples/real/rotulos_manuais_reais_TEMPLATE.csv:4` | ‹PREENCHER] | 9 | Placeholder de arquivo-modelo (.example / template CSV) |
| `04-Applied-Computer-Vision/samples/real/rotulos_manuais_reais_TEMPLATE.csv:4` | ‹PREENCHER] | 9 | Placeholder de arquivo-modelo (.example / template CSV) |
| `04-Applied-Computer-Vision/samples/real/rotulos_manuais_reais_TEMPLATE.csv:4` | ‹PREENCHER] | 9 | Placeholder de arquivo-modelo (.example / template CSV) |
| `04-Applied-Computer-Vision/samples/real/rotulos_manuais_reais_TEMPLATE.csv:4` | ‹PREENCHER] | 9 | Placeholder de arquivo-modelo (.example / template CSV) |
| `04-Applied-Computer-Vision/samples/real/rotulos_manuais_reais_TEMPLATE.csv:4` | ‹PREENCHER] | 9 | Placeholder de arquivo-modelo (.example / template CSV) |
| `04-Applied-Computer-Vision/samples/real/rotulos_manuais_reais_TEMPLATE.csv:4` | ‹PREENCHER] | 9 | Placeholder de arquivo-modelo (.example / template CSV) |
| `04-Applied-Computer-Vision/samples/real/rotulos_manuais_reais_TEMPLATE.csv:4` | ‹PREENCHER] | 9 | Placeholder de arquivo-modelo (.example / template CSV) |
| `04-Applied-Computer-Vision/scripts/avaliar_comparacao.py:171` | ‹PREENCHER: resultados da base real, quando existirem] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `05-Robotic-Process-Automation/PENDENCIAS_E_ACOES_MANUAIS.txt:73` | ‹PREENCHER] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `05-Robotic-Process-Automation/PENDENCIAS_E_ACOES_MANUAIS.txt:110` | ‹PREENCHER] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `05-Robotic-Process-Automation/PENDENCIAS_E_ACOES_MANUAIS.txt:140` | ‹PREENCHER: URL pública] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `05-Robotic-Process-Automation/PENDENCIAS_E_ACOES_MANUAIS.txt:244` | ‹PREENCHER: URL pública] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `05-Robotic-Process-Automation/PENDENCIAS_E_ACOES_MANUAIS.txt:297` | ‹PREENCHER" no relatório; PowerShell na raiz do repositório para gerar o PDF. | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `05-Robotic-Process-Automation/PENDENCIAS_E_ACOES_MANUAIS.txt:299` | ‹PREENCHER] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `05-Robotic-Process-Automation/PENDENCIAS_E_ACOES_MANUAIS.txt:302` | ‹PREENCHER] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `05-Robotic-Process-Automation/PENDENCIAS_E_ACOES_MANUAIS.txt:347` | ‹PREENCHER] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `05-Robotic-Process-Automation/README.md:85` | ‹PREENCHER: URL pública] | 5 | URL pública do MVP (saída app_url do Terraform / FQDN do ACI) |
| `05-Robotic-Process-Automation/docs/BUSINESS_CASE.md:5` | ‹PREENCHER: ...] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `05-Robotic-Process-Automation/docs/BUSINESS_CASE.md:48` | ‹PREENCHER: levantar com associações parceiras] | 4 | Premissas do business case a medir/levantar (volume, tempo manual, sal |
| `05-Robotic-Process-Automation/docs/BUSINESS_CASE.md:49` | ‹PREENCHER: cronometrar 10 cadastros manuais] | 4 | Premissas do business case a medir/levantar (volume, tempo manual, sal |
| `05-Robotic-Process-Automation/docs/BUSINESS_CASE.md:50` | ‹PREENCHER: referência salarial da região/organização] | 4 | Premissas do business case a medir/levantar (volume, tempo manual, sal |
| `05-Robotic-Process-Automation/docs/BUSINESS_CASE.md:51` | ‹PREENCHER: medir na primeira execução real] | 6 | Resultados da execução real no UiPath Studio (tempo, ajustes, conclusã |
| `05-Robotic-Process-Automation/docs/BUSINESS_CASE.md:53` | ‹PREENCHER] | 6 | Resultados da execução real no UiPath Studio (tempo, ajustes, conclusã |
| `05-Robotic-Process-Automation/docs/BUSINESS_CASE.md:54` | ‹PREENCHER] | 6 | Resultados da execução real no UiPath Studio (tempo, ajustes, conclusã |
| `05-Robotic-Process-Automation/docs/BUSINESS_CASE.md:55` | ‹PREENCHER: cotação oficial UiPath — não estimada aqui] | 8 | Revisão do assessment RPA pela equipe (%, resultado final, cotação UiP |
| `05-Robotic-Process-Automation/docs/BUSINESS_CASE.md:56` | ‹PREENCHER] | 6 | Resultados da execução real no UiPath Studio (tempo, ajustes, conclusã |
| `05-Robotic-Process-Automation/docs/BUSINESS_CASE.md:102` | ‹PREENCHER: medir na execução real] | 6 | Resultados da execução real no UiPath Studio (tempo, ajustes, conclusã |
| `05-Robotic-Process-Automation/docs/EVIDENCIAS_NECESSARIAS.md:26` | ‹PREENCHER: URL pública] | 5 | URL pública do MVP (saída app_url do Terraform / FQDN do ACI) |
| `05-Robotic-Process-Automation/docs/INSTRUCOES_UIPATH_STUDIO.md:59` | ‹PREENCHER: URL pública — depende da disciplina 06] | 5 | URL pública do MVP (saída app_url do Terraform / FQDN do ACI) |
| `05-Robotic-Process-Automation/docs/INSTRUCOES_ZIP_ENTREGA.md:9` | ‹PREENCHER: ...] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `05-Robotic-Process-Automation/docs/INSTRUCOES_ZIP_ENTREGA.md:25` | ‹PREENCHER] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `05-Robotic-Process-Automation/docs/RELATORIO_RPA.md:5` | ‹PREENCHER: nomes e RMs dos integrantes] | 1 | Integrantes: nome completo, RM, papel e turma |
| `05-Robotic-Process-Automation/docs/RELATORIO_RPA.md:6` | ‹PREENCHER] | 1 | Integrantes: nome completo, RM, papel e turma |
| `05-Robotic-Process-Automation/docs/RELATORIO_RPA.md:6` | ‹PREENCHER] | 8 | Data de envio/entrega/conferência |
| `05-Robotic-Process-Automation/docs/RELATORIO_RPA.md:7` | ‹PREENCHER: link do vídeo] | 2 | Link do vídeo-pitch/demonstração (público ou não listado) |
| `05-Robotic-Process-Automation/docs/RELATORIO_RPA.md:8` | ‹PREENCHER: URL pública da Azure ou "execução local em http://localhost:8000"] | 5 | URL pública do MVP (saída app_url do Terraform / FQDN do ACI) |
| `05-Robotic-Process-Automation/docs/RELATORIO_RPA.md:11` | ‹PREENCHER: ...] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `05-Robotic-Process-Automation/docs/RELATORIO_RPA.md:62` | ‹PREENCHER: resultado final revisado, se mudar] | 8 | Revisão do assessment RPA pela equipe (%, resultado final, cotação UiP |
| `05-Robotic-Process-Automation/docs/RELATORIO_RPA.md:124` | ‹PREENCHER: cotação oficial] | 8 | Revisão do assessment RPA pela equipe (%, resultado final, cotação UiP |
| `05-Robotic-Process-Automation/docs/RELATORIO_RPA.md:161` | ‹PREENCHER] | 6 | Resultados da execução real no UiPath Studio (tempo, ajustes, conclusã |
| `05-Robotic-Process-Automation/docs/RELATORIO_RPA.md:162` | ‹PREENCHER] | 6 | Resultados da execução real no UiPath Studio (tempo, ajustes, conclusã |
| `05-Robotic-Process-Automation/docs/RELATORIO_RPA.md:163` | ‹PREENCHER] | 6 | Resultados da execução real no UiPath Studio (tempo, ajustes, conclusã |
| `05-Robotic-Process-Automation/docs/RELATORIO_RPA.md:164` | ‹PREENCHER] | 6 | Resultados da execução real no UiPath Studio (tempo, ajustes, conclusã |
| `05-Robotic-Process-Automation/docs/RELATORIO_RPA.md:165` | ‹PREENCHER] | 6 | Resultados da execução real no UiPath Studio (tempo, ajustes, conclusã |
| `05-Robotic-Process-Automation/docs/RELATORIO_RPA.md:166` | ‹PREENCHER] | 6 | Resultados da execução real no UiPath Studio (tempo, ajustes, conclusã |
| `05-Robotic-Process-Automation/docs/RELATORIO_RPA.md:169` | ‹PREENCHER] | 6 | Resultados da execução real no UiPath Studio (tempo, ajustes, conclusã |
| `05-Robotic-Process-Automation/docs/RELATORIO_RPA.md:174` | ‹PREENCHER: o que precisou ser ajustado] | 6 | Resultados da execução real no UiPath Studio (tempo, ajustes, conclusã |
| `05-Robotic-Process-Automation/docs/RELATORIO_RPA.md:181` | ‹PREENCHER: conclusão da equipe — ex.: o RPA reduziu o trabalho manual ao tratamento de ex | 6 | Resultados da execução real no UiPath Studio (tempo, ajustes, conclusã |
| `05-Robotic-Process-Automation/docs/RELATORIO_RPA.md:189` | ‹PREENCHER: link do vídeo] | 2 | Link do vídeo-pitch/demonstração (público ou não listado) |
| `05-Robotic-Process-Automation/docs/ROTEIRO_VIDEO_RPA.md:25` | ‹PREENCHER: % final após revisão da equipe — preliminar 79,4 %] | 8 | Revisão do assessment RPA pela equipe (%, resultado final, cotação UiP |
| `05-Robotic-Process-Automation/docs/ROTEIRO_VIDEO_RPA.md:39` | ‹PREENCHER: link do vídeo] | 2 | Link do vídeo-pitch/demonstração (público ou não listado) |
| `05-Robotic-Process-Automation/scripts/gerar_pdf_relatorio.py:7` | ‹PREENCHER: ...] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `05-Robotic-Process-Automation/scripts/gerar_pdf_relatorio.py:10` | ‹PREENCHER] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `05-Robotic-Process-Automation/scripts/gerar_pdf_relatorio.py:70` | ‹PREENCHER") | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `05-Robotic-Process-Automation/scripts/gerar_pdf_relatorio.py:72` | ‹PREENCHER] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `05-Robotic-Process-Automation/scripts/gerar_planilhas.py:229` | ‹PREENCHER: URL pública do MVP] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `05-Robotic-Process-Automation/scripts/gerar_planilhas.py:287` | ‹PREENCHER: volume real após conversa com parceiros] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `05-Robotic-Process-Automation/scripts/gerar_planilhas.py:304` | ‹PREENCHER: tempo cronometrado pela equipe] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `05-Robotic-Process-Automation/scripts/gerar_planilhas.py:358` | ‹PREENCHER: nome do processo] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `05-Robotic-Process-Automation/scripts/gerar_planilhas.py:362` | ‹PREENCHER: preliminar / revisada] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `05-Robotic-Process-Automation/scripts/gerar_planilhas.py:366` | ‹PREENCHER: integrantes da equipe e data da revisão] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `05-Robotic-Process-Automation/scripts/gerar_planilhas.py:379` | ‹PREENCHER] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `05-Robotic-Process-Automation/scripts/gerar_zip_entrega.ps1:51` | ‹PREENCHER] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `05-Robotic-Process-Automation/tests/test_rpa_entrega.py:36` | ‹PREENCHER: link do vídeo] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `06-Secure-DevOps-Cloud/PENDENCIAS_E_ACOES_MANUAIS.txt:39` | ‹PREENCHER] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `06-Secure-DevOps-Cloud/PENDENCIAS_E_ACOES_MANUAIS.txt:214` | ‹PREENCHER] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `06-Secure-DevOps-Cloud/PENDENCIAS_E_ACOES_MANUAIS.txt:230` | ‹PREENCHER] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `06-Secure-DevOps-Cloud/PENDENCIAS_E_ACOES_MANUAIS.txt:232` | ‹PREENCHER] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `06-Secure-DevOps-Cloud/PENDENCIAS_E_ACOES_MANUAIS.txt:238` | ‹PREENCHER] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `06-Secure-DevOps-Cloud/PENDENCIAS_E_ACOES_MANUAIS.txt:253` | ‹PREENCHER] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `06-Secure-DevOps-Cloud/PENDENCIAS_E_ACOES_MANUAIS.txt:258` | ‹PREENCHER". | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `06-Secure-DevOps-Cloud/PENDENCIAS_E_ACOES_MANUAIS.txt:261` | ‹PREENCHER] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `06-Secure-DevOps-Cloud/PENDENCIAS_E_ACOES_MANUAIS.txt:265` | ‹PREENCHER"; o E2E termina com 0 falha(s). | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `06-Secure-DevOps-Cloud/README.md:18` | ‹PREENCHER: http://<fqdn>:8000] | 5 | URL pública do MVP (saída app_url do Terraform / FQDN do ACI) |
| `06-Secure-DevOps-Cloud/README.md:18` | ‹PREENCHER: https://github.com/<owner>/<repo>] | 2 | URL do repositório público no GitHub |
| `06-Secure-DevOps-Cloud/README.md:19` | ‹PREENCHER: indicadores definidos pela equipe — ex.: denúncias registradas, tempo até a tr | 10 | Indicadores de impacto e ODS conectados (README 06) |
| `06-Secure-DevOps-Cloud/README.md:20` | ‹PREENCHER: outros ODS escolhidos pela equipe] | 10 | Indicadores de impacto e ODS conectados (README 06) |
| `06-Secure-DevOps-Cloud/docs/DEMONSTRACAO_EXECUCAO_BARRADA.md:89` | ‹PREENCHER: URL da execução barrada] | 2 | URL das execuções do GitHub Actions (barrada e corrigida) |
| `06-Secure-DevOps-Cloud/docs/DEMONSTRACAO_EXECUCAO_BARRADA.md:89` | ‹PREENCHER: URL da execução corrigida] | 2 | URL das execuções do GitHub Actions (barrada e corrigida) |
| `06-Secure-DevOps-Cloud/docs/ESTIMATIVA_DE_CUSTOS.md:8` | ‹PREENCHER: dd/mm/aaaa] | 8 | Data de envio/entrega/conferência |
| `06-Secure-DevOps-Cloud/docs/ESTIMATIVA_DE_CUSTOS.md:8` | ‹PREENCHER] | 5 | Dados medidos na Azure/Docker (tamanho da imagem, alerta disparado, cu |
| `06-Secure-DevOps-Cloud/docs/ESTIMATIVA_DE_CUSTOS.md:35` | ‹PREENCHER: valores conferidos na calculadora para 7, 14 e 30 dias] | 5 | Dados medidos na Azure/Docker (tamanho da imagem, alerta disparado, cu |
| `06-Secure-DevOps-Cloud/docs/ESTIMATIVA_DE_CUSTOS.md:36` | ‹PREENCHER: cotação do dia] | 8 | Valores de calculadora e cotação do dia |
| `06-Secure-DevOps-Cloud/docs/ESTIMATIVA_DE_CUSTOS.md:41` | ‹PREENCHER: valor do crédito exibido no portal da conta da equipe] | 5 | Dados medidos na Azure/Docker (tamanho da imagem, alerta disparado, cu |
| `06-Secure-DevOps-Cloud/docs/EVIDENCIAS_NECESSARIAS.md:35` | ‹PREENCHER: https://github.com/<owner>/<repo>] | 2 | URL do repositório público no GitHub |
| `06-Secure-DevOps-Cloud/docs/EVIDENCIAS_NECESSARIAS.md:36` | ‹PREENCHER: http://<fqdn>:8000] | 5 | URL pública do MVP (saída app_url do Terraform / FQDN do ACI) |
| `06-Secure-DevOps-Cloud/docs/EVIDENCIAS_NECESSARIAS.md:37` | ‹PREENCHER: URL da execução no Actions] | 2 | URL das execuções do GitHub Actions (barrada e corrigida) |
| `06-Secure-DevOps-Cloud/docs/EVIDENCIAS_NECESSARIAS.md:38` | ‹PREENCHER] | 2 | URL das execuções do GitHub Actions (barrada e corrigida) |
| `06-Secure-DevOps-Cloud/docs/EVIDENCIAS_NECESSARIAS.md:39` | ‹PREENCHER] | 2 | URL das execuções do GitHub Actions (barrada e corrigida) |
| `06-Secure-DevOps-Cloud/docs/EVIDENCIAS_NECESSARIAS.md:40` | ‹PREENCHER] | 2 | Link do vídeo-pitch/demonstração (público ou não listado) |
| `06-Secure-DevOps-Cloud/docs/LGPD_MAPEAMENTO_DADOS_PESSOAIS.md:5` | ‹PREENCHER] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `06-Secure-DevOps-Cloud/docs/LGPD_MAPEAMENTO_DADOS_PESSOAIS.md:12` | ‹PREENCHER: prazo, ex. até a conclusão da denúncia + N dias] | 8 | Política de retenção/exclusão e base legal LGPD |
| `06-Secure-DevOps-Cloud/docs/LGPD_MAPEAMENTO_DADOS_PESSOAIS.md:13` | ‹PREENCHER: se houver mascaramento automático, citar] | 10 | Mascaramento automático na descrição (LGPD) |
| `06-Secure-DevOps-Cloud/docs/LGPD_MAPEAMENTO_DADOS_PESSOAIS.md:17` | ‹PREENCHER: verificar termos e retenção do provedor escolhido] | 8 | Preço vigente e política de privacidade do provedor LLM |
| `06-Secure-DevOps-Cloud/docs/LGPD_MAPEAMENTO_DADOS_PESSOAIS.md:39` | ‹PREENCHER: base escolhida pela equipe] | 8 | Política de retenção/exclusão e base legal LGPD |
| `06-Secure-DevOps-Cloud/docs/LGPD_MAPEAMENTO_DADOS_PESSOAIS.md:59` | ‹PREENCHER: canal de contato da equipe (e-mail institucional)] | 8 | Canal de contato da equipe (e-mail institucional) |
| `06-Secure-DevOps-Cloud/docs/LGPD_MAPEAMENTO_DADOS_PESSOAIS.md:60` | ‹PREENCHER: confirmar o aviso na interface] | 8 | Aviso na interface sobre envio de perguntas ao provedor LLM |
| `06-Secure-DevOps-Cloud/docs/LGPD_MAPEAMENTO_DADOS_PESSOAIS.md:61` | ‹PREENCHER] | 8 | Política de retenção/exclusão e base legal LGPD |
| `06-Secure-DevOps-Cloud/docs/LGPD_MAPEAMENTO_DADOS_PESSOAIS.md:62` | ‹PREENCHER: nome do responsável da equipe] | 1 | Responsável pela privacidade (encarregado) |
| `06-Secure-DevOps-Cloud/docs/OBSERVABILIDADE.md:64` | ‹PREENCHER ...] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `06-Secure-DevOps-Cloud/docs/PUBLICACAO_AZURE.md:7` | ‹PREENCHER] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `06-Secure-DevOps-Cloud/docs/RELATORIO_ENTREGA_DEVOPS.md:4` | ‹PREENCHER: nomes e RMs dos integrantes] | 1 | Integrantes: nome completo, RM, papel e turma |
| `06-Secure-DevOps-Cloud/docs/RELATORIO_ENTREGA_DEVOPS.md:4` | ‹PREENCHER] | 1 | Integrantes: nome completo, RM, papel e turma |
| `06-Secure-DevOps-Cloud/docs/RELATORIO_ENTREGA_DEVOPS.md:5` | ‹PREENCHER] | 8 | Data de envio/entrega/conferência |
| `06-Secure-DevOps-Cloud/docs/RELATORIO_ENTREGA_DEVOPS.md:7` | ‹PREENCHER] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `06-Secure-DevOps-Cloud/docs/RELATORIO_ENTREGA_DEVOPS.md:14` | ‹PREENCHER: https://github.com/<owner>/<repo>] | 2 | URL do repositório público no GitHub |
| `06-Secure-DevOps-Cloud/docs/RELATORIO_ENTREGA_DEVOPS.md:15` | ‹PREENCHER: http://<fqdn>:8000] | 5 | URL pública do MVP (saída app_url do Terraform / FQDN do ACI) |
| `06-Secure-DevOps-Cloud/docs/RELATORIO_ENTREGA_DEVOPS.md:16` | ‹PREENCHER: link para o README da raiz] | 10 | Link para o README da raiz (Ficha Técnica) |
| `06-Secure-DevOps-Cloud/docs/RELATORIO_ENTREGA_DEVOPS.md:17` | ‹PREENCHER] | 5 | Dados medidos na Azure/Docker (tamanho da imagem, alerta disparado, cu |
| `06-Secure-DevOps-Cloud/docs/RELATORIO_ENTREGA_DEVOPS.md:18` | ‹PREENCHER] | 5 | Dados medidos na Azure/Docker (tamanho da imagem, alerta disparado, cu |
| `06-Secure-DevOps-Cloud/docs/RELATORIO_ENTREGA_DEVOPS.md:19` | ‹PREENCHER] | 5 | Dados medidos na Azure/Docker (tamanho da imagem, alerta disparado, cu |
| `06-Secure-DevOps-Cloud/docs/RELATORIO_ENTREGA_DEVOPS.md:24` | ‹PREENCHER: inserir imagem do diagrama] | 10 | Imagem do diagrama de arquitetura de nuvem |
| `06-Secure-DevOps-Cloud/docs/RELATORIO_ENTREGA_DEVOPS.md:35` | ‹PREENCHER: tamanho da imagem `docker image ls`] | 5 | Dados medidos na Azure/Docker (tamanho da imagem, alerta disparado, cu |
| `06-Secure-DevOps-Cloud/docs/RELATORIO_ENTREGA_DEVOPS.md:55` | ‹PREENCHER: qual — | 5 | Dados medidos na Azure/Docker (tamanho da imagem, alerta disparado, cu |
| `06-Secure-DevOps-Cloud/docs/RELATORIO_ENTREGA_DEVOPS.md:56` | ‹PREENCHER: data/hora] | 5 | Dados medidos na Azure/Docker (tamanho da imagem, alerta disparado, cu |
| `06-Secure-DevOps-Cloud/docs/RELATORIO_ENTREGA_DEVOPS.md:57` | ‹PREENCHER: prints 16–19] | 3 | Prints, fotos e imagens de evidência |
| `06-Secure-DevOps-Cloud/docs/RELATORIO_ENTREGA_DEVOPS.md:66` | ‹PREENCHER] | 5 | Dados medidos na Azure/Docker (tamanho da imagem, alerta disparado, cu |
| `06-Secure-DevOps-Cloud/docs/RELATORIO_ENTREGA_DEVOPS.md:70` | ‹PREENCHER] | 5 | Dados medidos na Azure/Docker (tamanho da imagem, alerta disparado, cu |
| `06-Secure-DevOps-Cloud/docs/RELATORIO_ENTREGA_DEVOPS.md:70` | ‹PREENCHER: Cost Management] | 5 | Dados medidos na Azure/Docker (tamanho da imagem, alerta disparado, cu |
| `06-Secure-DevOps-Cloud/docs/RESPONSABILIDADE_COMPARTILHADA.md:55` | ‹PREENCHER: link da documentação oficial consultado pela equipe] | 2 | Link da documentação oficial consultada |
| `06-Secure-DevOps-Cloud/monitoring/prometheus/prometheus.azure.yml:5` | ‹PREENCHER] | 5 | FQDN do container no Prometheus (scrape do Azure) |
| `06-Secure-DevOps-Cloud/monitoring/prometheus/prometheus.azure.yml:32` | ‹PREENCHER: container_fqdn:8000] | 5 | FQDN do container no Prometheus (scrape do Azure) |
| `06-Secure-DevOps-Cloud/monitoring/prometheus/prometheus.yml:44` | ‹PREENCHER: container_fqdn:8000] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `06-Secure-DevOps-Cloud/terraform/backend.hcl.example:6` | ‹PREENCHER: nome da storage account do state] | 9 | Placeholder de arquivo-modelo (.example / template CSV) |
| `06-Secure-DevOps-Cloud/terraform/terraform.tfvars.example:16` | ‹PREENCHER: ID da assinatura Azure] | 9 | Placeholder de arquivo-modelo (.example / template CSV) |
| `06-Secure-DevOps-Cloud/terraform/terraform.tfvars.example:32` | ‹PREENCHER: tag da imagem enviada ao ACR, ex.: SHA do commit] | 9 | Placeholder de arquivo-modelo (.example / template CSV) |
| `06-Secure-DevOps-Cloud/terraform/terraform.tfvars.example:49` | ‹PREENCHER: nome da equipe] | 9 | Placeholder de arquivo-modelo (.example / template CSV) |
| `06-Secure-DevOps-Cloud/tests/test_devops_observabilidade.py:44` | ‹PREENCHER" in texto | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `07-Project-Based-Maker-Lab/PENDENCIAS_E_ACOES_MANUAIS.txt:79` | ‹PREENCHER: url] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `07-Project-Based-Maker-Lab/PENDENCIAS_E_ACOES_MANUAIS.txt:99` | ‹PREENCHER] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `07-Project-Based-Maker-Lab/PENDENCIAS_E_ACOES_MANUAIS.txt:119` | ‹PREENCHER] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `07-Project-Based-Maker-Lab/PENDENCIAS_E_ACOES_MANUAIS.txt:250` | ‹PREENCHER] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `07-Project-Based-Maker-Lab/PENDENCIAS_E_ACOES_MANUAIS.txt:254` | ‹PREENCHER] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `07-Project-Based-Maker-Lab/PENDENCIAS_E_ACOES_MANUAIS.txt:255` | ‹PREENCHER" no PDF; todos os links abrem. | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `07-Project-Based-Maker-Lab/README.md:20` | ‹PREENCHER] | 7 | Peça de terceiros (nome, autor, link, licença) |
| `07-Project-Based-Maker-Lab/README.md:72` | ‹PREENCHER: URL pública do AcessaCidade] | 5 | URL pública do MVP (saída app_url do Terraform / FQDN do ACI) |
| `07-Project-Based-Maker-Lab/docs/BONUS_PECA_TERCEIROS.md:37` | ‹PREENCHER] | 7 | Peça de terceiros (nome, autor, link, licença) |
| `07-Project-Based-Maker-Lab/docs/BONUS_PECA_TERCEIROS.md:38` | ‹PREENCHER] | 7 | Peça de terceiros (nome, autor, link, licença) |
| `07-Project-Based-Maker-Lab/docs/BONUS_PECA_TERCEIROS.md:39` | ‹PREENCHER] | 7 | Peça de terceiros (nome, autor, link, licença) |
| `07-Project-Based-Maker-Lab/docs/BONUS_PECA_TERCEIROS.md:40` | ‹PREENCHER] | 7 | Peça de terceiros (nome, autor, link, licença) |
| `07-Project-Based-Maker-Lab/docs/BONUS_PECA_TERCEIROS.md:41` | ‹PREENCHER] | 7 | Peça de terceiros (nome, autor, link, licença) |
| `07-Project-Based-Maker-Lab/docs/BONUS_PECA_TERCEIROS.md:42` | ‹PREENCHER] | 7 | Peça de terceiros (nome, autor, link, licença) |
| `07-Project-Based-Maker-Lab/docs/BONUS_PECA_TERCEIROS.md:43` | ‹PREENCHER] | 7 | Peça de terceiros (nome, autor, link, licença) |
| `07-Project-Based-Maker-Lab/docs/BONUS_PECA_TERCEIROS.md:44` | ‹PREENCHER] | 7 | Peça de terceiros (nome, autor, link, licença) |
| `07-Project-Based-Maker-Lab/docs/BONUS_PECA_TERCEIROS.md:45` | ‹PREENCHER] | 7 | Peça de terceiros (nome, autor, link, licença) |
| `07-Project-Based-Maker-Lab/docs/COMPARACAO_ANTES_DEPOIS.md:4` | ‹PREENCHER: inserir após a visita e a fabricação — ver `FOTOS_A_REALIZAR.md`] | 3 | Prints, fotos e imagens de evidência |
| `07-Project-Based-Maker-Lab/docs/COMPARACAO_ANTES_DEPOIS.md:43` | ‹PREENCHER: `fotos/local_02_frontal.jpg`] | 3 | Prints, fotos e imagens de evidência |
| `07-Project-Based-Maker-Lab/docs/COMPARACAO_ANTES_DEPOIS.md:43` | ‹PREENCHER: `fotos/prototipo_frontal.jpg`] | 3 | Prints, fotos e imagens de evidência |
| `07-Project-Based-Maker-Lab/docs/COMPARACAO_ANTES_DEPOIS.md:44` | ‹PREENCHER: `fotos/local_06_superficie.jpg`] | 3 | Prints, fotos e imagens de evidência |
| `07-Project-Based-Maker-Lab/docs/COMPARACAO_ANTES_DEPOIS.md:44` | ‹PREENCHER: `fotos/prototipo_tatil_mao.jpg`] | 3 | Prints, fotos e imagens de evidência |
| `07-Project-Based-Maker-Lab/docs/CROQUI_MEDIDAS.md:37` | ‹PREENCHER: foto do croqui preenchido] | 3 | Prints, fotos e imagens de evidência |
| `07-Project-Based-Maker-Lab/docs/CROQUI_MEDIDAS.md:41` | ‹PREENCHER] | 7 | Diagnóstico, medidas, fabricação e testes no mundo físico |
| `07-Project-Based-Maker-Lab/docs/CROQUI_MEDIDAS.md:42` | ‹PREENCHER] | 7 | Diagnóstico, medidas, fabricação e testes no mundo físico |
| `07-Project-Based-Maker-Lab/docs/CROQUI_MEDIDAS.md:43` | ‹PREENCHER] | 7 | Diagnóstico, medidas, fabricação e testes no mundo físico |
| `07-Project-Based-Maker-Lab/docs/CROQUI_MEDIDAS.md:44` | ‹PREENCHER] | 7 | Diagnóstico, medidas, fabricação e testes no mundo físico |
| `07-Project-Based-Maker-Lab/docs/CROQUI_MEDIDAS.md:45` | ‹PREENCHER] | 7 | Diagnóstico, medidas, fabricação e testes no mundo físico |
| `07-Project-Based-Maker-Lab/docs/CROQUI_MEDIDAS.md:46` | ‹PREENCHER] | 7 | Diagnóstico, medidas, fabricação e testes no mundo físico |
| `07-Project-Based-Maker-Lab/docs/CROQUI_MEDIDAS.md:47` | ‹PREENCHER] | 7 | Diagnóstico, medidas, fabricação e testes no mundo físico |
| `07-Project-Based-Maker-Lab/docs/CROQUI_MEDIDAS.md:48` | ‹PREENCHER] | 7 | Diagnóstico, medidas, fabricação e testes no mundo físico |
| `07-Project-Based-Maker-Lab/docs/CROQUI_MEDIDAS.md:49` | ‹PREENCHER] | 7 | Diagnóstico, medidas, fabricação e testes no mundo físico |
| `07-Project-Based-Maker-Lab/docs/CROQUI_MEDIDAS.md:50` | ‹PREENCHER] | 7 | Diagnóstico, medidas, fabricação e testes no mundo físico |
| `07-Project-Based-Maker-Lab/docs/CROQUI_MEDIDAS.md:51` | ‹PREENCHER] | 7 | Diagnóstico, medidas, fabricação e testes no mundo físico |
| `07-Project-Based-Maker-Lab/docs/CROQUI_MEDIDAS.md:52` | ‹PREENCHER] | 7 | Diagnóstico, medidas, fabricação e testes no mundo físico |
| `07-Project-Based-Maker-Lab/docs/DIAGNOSTICO_OBJETO_ORIGINAL.md:4` | ‹PREENCHER] | 7 | Diagnóstico, medidas, fabricação e testes no mundo físico |
| `07-Project-Based-Maker-Lab/docs/DIAGNOSTICO_OBJETO_ORIGINAL.md:12` | ‹PREENCHER: rua/avenida, bairro, cidade] | 7 | Diagnóstico, medidas, fabricação e testes no mundo físico |
| `07-Project-Based-Maker-Lab/docs/DIAGNOSTICO_OBJETO_ORIGINAL.md:13` | ‹PREENCHER: dd/mm/aaaa hh:mm] | 8 | Data de envio/entrega/conferência |
| `07-Project-Based-Maker-Lab/docs/DIAGNOSTICO_OBJETO_ORIGINAL.md:14` | ‹PREENCHER: nomes ou iniciais] | 7 | Diagnóstico, medidas, fabricação e testes no mundo físico |
| `07-Project-Based-Maker-Lab/docs/DIAGNOSTICO_OBJETO_ORIGINAL.md:15` | ‹PREENCHER: link para a pasta de fotos] | 3 | Prints, fotos e imagens de evidência |
| `07-Project-Based-Maker-Lab/docs/DIAGNOSTICO_OBJETO_ORIGINAL.md:16` | ‹PREENCHER: `docs/imagens/croqui_original_preenchido.jpg`] | 7 | Diagnóstico, medidas, fabricação e testes no mundo físico |
| `07-Project-Based-Maker-Lab/docs/DIAGNOSTICO_OBJETO_ORIGINAL.md:28` | ‹PREENCHER] | 7 | Diagnóstico, medidas, fabricação e testes no mundo físico |
| `07-Project-Based-Maker-Lab/docs/DIAGNOSTICO_OBJETO_ORIGINAL.md:29` | ‹PREENCHER] | 7 | Diagnóstico, medidas, fabricação e testes no mundo físico |
| `07-Project-Based-Maker-Lab/docs/DIAGNOSTICO_OBJETO_ORIGINAL.md:30` | ‹PREENCHER] | 7 | Diagnóstico, medidas, fabricação e testes no mundo físico |
| `07-Project-Based-Maker-Lab/docs/DIAGNOSTICO_OBJETO_ORIGINAL.md:31` | ‹PREENCHER] | 7 | Diagnóstico, medidas, fabricação e testes no mundo físico |
| `07-Project-Based-Maker-Lab/docs/DIAGNOSTICO_OBJETO_ORIGINAL.md:32` | ‹PREENCHER] | 7 | Diagnóstico, medidas, fabricação e testes no mundo físico |
| `07-Project-Based-Maker-Lab/docs/DIAGNOSTICO_OBJETO_ORIGINAL.md:33` | ‹PREENCHER] | 7 | Diagnóstico, medidas, fabricação e testes no mundo físico |
| `07-Project-Based-Maker-Lab/docs/DIAGNOSTICO_OBJETO_ORIGINAL.md:34` | ‹PREENCHER] | 7 | Diagnóstico, medidas, fabricação e testes no mundo físico |
| `07-Project-Based-Maker-Lab/docs/DIAGNOSTICO_OBJETO_ORIGINAL.md:47` | ‹PREENCHER: relatos anonimizados, se houver] | 4 | Dados públicos de contexto (IBGE/Censo/DATASUS/legislação) com fonte |
| `07-Project-Based-Maker-Lab/docs/DIAGNOSTICO_OBJETO_ORIGINAL.md:57` | ‹PREENCHER] | 7 | Diagnóstico, medidas, fabricação e testes no mundo físico |
| `07-Project-Based-Maker-Lab/docs/DIAGNOSTICO_OBJETO_ORIGINAL.md:58` | ‹PREENCHER] | 7 | Diagnóstico, medidas, fabricação e testes no mundo físico |
| `07-Project-Based-Maker-Lab/docs/DIAGNOSTICO_OBJETO_ORIGINAL.md:59` | ‹PREENCHER] | 7 | Diagnóstico, medidas, fabricação e testes no mundo físico |
| `07-Project-Based-Maker-Lab/docs/DIAGNOSTICO_OBJETO_ORIGINAL.md:60` | ‹PREENCHER] | 7 | Diagnóstico, medidas, fabricação e testes no mundo físico |
| `07-Project-Based-Maker-Lab/docs/DIAGNOSTICO_OBJETO_ORIGINAL.md:61` | ‹PREENCHER] | 7 | Diagnóstico, medidas, fabricação e testes no mundo físico |
| `07-Project-Based-Maker-Lab/docs/DIAGNOSTICO_OBJETO_ORIGINAL.md:62` | ‹PREENCHER] | 7 | Diagnóstico, medidas, fabricação e testes no mundo físico |
| `07-Project-Based-Maker-Lab/docs/FABRICACAO.md:106` | ‹PREENCHER] | 7 | Diagnóstico, medidas, fabricação e testes no mundo físico |
| `07-Project-Based-Maker-Lab/docs/FABRICACAO.md:107` | ‹PREENCHER] | 7 | Diagnóstico, medidas, fabricação e testes no mundo físico |
| `07-Project-Based-Maker-Lab/docs/FABRICACAO.md:108` | ‹PREENCHER] | 7 | Diagnóstico, medidas, fabricação e testes no mundo físico |
| `07-Project-Based-Maker-Lab/docs/FABRICACAO.md:109` | ‹PREENCHER] | 7 | Diagnóstico, medidas, fabricação e testes no mundo físico |
| `07-Project-Based-Maker-Lab/docs/FABRICACAO.md:110` | ‹PREENCHER] | 7 | Diagnóstico, medidas, fabricação e testes no mundo físico |
| `07-Project-Based-Maker-Lab/docs/FABRICACAO.md:111` | ‹PREENCHER] | 7 | Diagnóstico, medidas, fabricação e testes no mundo físico |
| `07-Project-Based-Maker-Lab/docs/FABRICACAO.md:112` | ‹PREENCHER] | 7 | Diagnóstico, medidas, fabricação e testes no mundo físico |
| `07-Project-Based-Maker-Lab/docs/FABRICACAO.md:113` | ‹PREENCHER] | 7 | Diagnóstico, medidas, fabricação e testes no mundo físico |
| `07-Project-Based-Maker-Lab/docs/FABRICACAO.md:114` | ‹PREENCHER] | 7 | Diagnóstico, medidas, fabricação e testes no mundo físico |
| `07-Project-Based-Maker-Lab/docs/FABRICACAO.md:115` | ‹PREENCHER] | 7 | Diagnóstico, medidas, fabricação e testes no mundo físico |
| `07-Project-Based-Maker-Lab/docs/FABRICACAO.md:116` | ‹PREENCHER] | 7 | Diagnóstico, medidas, fabricação e testes no mundo físico |
| `07-Project-Based-Maker-Lab/docs/FABRICACAO.md:117` | ‹PREENCHER] | 7 | Diagnóstico, medidas, fabricação e testes no mundo físico |
| `07-Project-Based-Maker-Lab/docs/GUIA_FOTOGRAFAR_E_MEDIR.md:40` | ‹PREENCHER: link] | 2 | Link do vídeo-pitch/demonstração (público ou não listado) |
| `07-Project-Based-Maker-Lab/docs/GUIA_FOTOGRAFAR_E_MEDIR.md:49` | ‹PREENCHER] | 7 | Diagnóstico, medidas, fabricação e testes no mundo físico |
| `07-Project-Based-Maker-Lab/docs/GUIA_FOTOGRAFAR_E_MEDIR.md:50` | ‹PREENCHER] | 7 | Diagnóstico, medidas, fabricação e testes no mundo físico |
| `07-Project-Based-Maker-Lab/docs/GUIA_FOTOGRAFAR_E_MEDIR.md:51` | ‹PREENCHER] | 7 | Diagnóstico, medidas, fabricação e testes no mundo físico |
| `07-Project-Based-Maker-Lab/docs/GUIA_FOTOGRAFAR_E_MEDIR.md:52` | ‹PREENCHER] | 7 | Diagnóstico, medidas, fabricação e testes no mundo físico |
| `07-Project-Based-Maker-Lab/docs/GUIA_FOTOGRAFAR_E_MEDIR.md:53` | ‹PREENCHER] | 7 | Diagnóstico, medidas, fabricação e testes no mundo físico |
| `07-Project-Based-Maker-Lab/docs/GUIA_FOTOGRAFAR_E_MEDIR.md:54` | ‹PREENCHER] | 7 | Diagnóstico, medidas, fabricação e testes no mundo físico |
| `07-Project-Based-Maker-Lab/docs/GUIA_FOTOGRAFAR_E_MEDIR.md:55` | ‹PREENCHER] | 7 | Diagnóstico, medidas, fabricação e testes no mundo físico |
| `07-Project-Based-Maker-Lab/docs/GUIA_FOTOGRAFAR_E_MEDIR.md:56` | ‹PREENCHER] | 7 | Diagnóstico, medidas, fabricação e testes no mundo físico |
| `07-Project-Based-Maker-Lab/docs/GUIA_FOTOGRAFAR_E_MEDIR.md:57` | ‹PREENCHER] | 7 | Diagnóstico, medidas, fabricação e testes no mundo físico |
| `07-Project-Based-Maker-Lab/docs/GUIA_FOTOGRAFAR_E_MEDIR.md:58` | ‹PREENCHER] | 7 | Diagnóstico, medidas, fabricação e testes no mundo físico |
| `07-Project-Based-Maker-Lab/docs/GUIA_FOTOGRAFAR_E_MEDIR.md:59` | ‹PREENCHER] | 7 | Diagnóstico, medidas, fabricação e testes no mundo físico |
| `07-Project-Based-Maker-Lab/docs/GUIA_FOTOGRAFAR_E_MEDIR.md:60` | ‹PREENCHER] | 7 | Diagnóstico, medidas, fabricação e testes no mundo físico |
| `07-Project-Based-Maker-Lab/docs/IMPACTO_E_ODS.md:17` | ‹PREENCHER] | 7 | Diagnóstico, medidas, fabricação e testes no mundo físico |
| `07-Project-Based-Maker-Lab/docs/IMPACTO_E_ODS.md:18` | ‹PREENCHER] | 7 | Diagnóstico, medidas, fabricação e testes no mundo físico |
| `07-Project-Based-Maker-Lab/docs/IMPACTO_E_ODS.md:19` | ‹PREENCHER] | 7 | Diagnóstico, medidas, fabricação e testes no mundo físico |
| `07-Project-Based-Maker-Lab/docs/IMPACTO_E_ODS.md:20` | ‹PREENCHER] | 7 | Diagnóstico, medidas, fabricação e testes no mundo físico |
| `07-Project-Based-Maker-Lab/docs/IMPACTO_E_ODS.md:21` | ‹PREENCHER] | 7 | Diagnóstico, medidas, fabricação e testes no mundo físico |
| `07-Project-Based-Maker-Lab/docs/IMPACTO_E_ODS.md:38` | ‹PREENCHER: URL pública] | 5 | URL pública do MVP (saída app_url do Terraform / FQDN do ACI) |
| `07-Project-Based-Maker-Lab/docs/IMPACTO_E_ODS.md:44` | ‹PREENCHER: custo | 7 | Diagnóstico, medidas, fabricação e testes no mundo físico |
| `07-Project-Based-Maker-Lab/docs/MAKERWORLD_PUBLICACAO.md:4` | ‹PREENCHER: link do modelo no MakerWorld] | 2 | Link da página do modelo no MakerWorld |
| `07-Project-Based-Maker-Lab/docs/MAKERWORLD_PUBLICACAO.md:21` | ‹PREENCHER: nome da peça] | 7 | Peça de terceiros (nome, autor, link, licença) |
| `07-Project-Based-Maker-Lab/docs/MAKERWORLD_PUBLICACAO.md:21` | ‹PREENCHER: autor] | 7 | Peça de terceiros (nome, autor, link, licença) |
| `07-Project-Based-Maker-Lab/docs/MAKERWORLD_PUBLICACAO.md:21` | ‹PREENCHER: link] | 7 | Peça de terceiros (nome, autor, link, licença) |
| `07-Project-Based-Maker-Lab/docs/MAKERWORLD_PUBLICACAO.md:21` | ‹PREENCHER] | 7 | Peça de terceiros (nome, autor, link, licença) |
| `07-Project-Based-Maker-Lab/docs/MAKERWORLD_PUBLICACAO.md:22` | ‹PREENCHER: link do repositório] | 2 | URL do repositório público no GitHub |
| `07-Project-Based-Maker-Lab/docs/MAKERWORLD_PUBLICACAO.md:31` | ‹PREENCHER] | 7 | Peça de terceiros (nome, autor, link, licença) |
| `07-Project-Based-Maker-Lab/docs/MAKERWORLD_PUBLICACAO.md:31` | ‹PREENCHER] | 7 | Peça de terceiros (nome, autor, link, licença) |
| `07-Project-Based-Maker-Lab/docs/MAKERWORLD_PUBLICACAO.md:31` | ‹PREENCHER: link] | 7 | Peça de terceiros (nome, autor, link, licença) |
| `07-Project-Based-Maker-Lab/docs/MAKERWORLD_PUBLICACAO.md:31` | ‹PREENCHER] | 7 | Peça de terceiros (nome, autor, link, licença) |
| `07-Project-Based-Maker-Lab/docs/MAKERWORLD_PUBLICACAO.md:72` | ‹PREENCHER] | 7 | Peça de terceiros (nome, autor, link, licença) |
| `07-Project-Based-Maker-Lab/docs/MAKERWORLD_PUBLICACAO.md:73` | ‹PREENCHER] | 7 | Peça de terceiros (nome, autor, link, licença) |
| `07-Project-Based-Maker-Lab/docs/MAKERWORLD_PUBLICACAO.md:74` | ‹PREENCHER] | 7 | Peça de terceiros (nome, autor, link, licença) |
| `07-Project-Based-Maker-Lab/docs/MAKERWORLD_PUBLICACAO.md:75` | ‹PREENCHER] | 7 | Peça de terceiros (nome, autor, link, licença) |
| `07-Project-Based-Maker-Lab/docs/MAKERWORLD_PUBLICACAO.md:76` | ‹PREENCHER: ex.: abraçadeira/clip que prende o suporte ao tubo de 25 mm] | 7 | Diagnóstico, medidas, fabricação e testes no mundo físico |
| `07-Project-Based-Maker-Lab/docs/MAKERWORLD_PUBLICACAO.md:77` | ‹PREENCHER: nenhuma / escala / furos] | 7 | Diagnóstico, medidas, fabricação e testes no mundo físico |
| `07-Project-Based-Maker-Lab/docs/RELATORIO_ENTREGA_MAKER.md:4` | ‹PREENCHER] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `07-Project-Based-Maker-Lab/docs/RELATORIO_ENTREGA_MAKER.md:10` | ‹PREENCHER: nomes completos e RMs] | 1 | Integrantes: nome completo, RM, papel e turma |
| `07-Project-Based-Maker-Lab/docs/RELATORIO_ENTREGA_MAKER.md:11` | ‹PREENCHER] | 7 | Diagnóstico, medidas, fabricação e testes no mundo físico |
| `07-Project-Based-Maker-Lab/docs/RELATORIO_ENTREGA_MAKER.md:13` | ‹PREENCHER: link do MakerWorld] | 2 | Link da página do modelo no MakerWorld |
| `07-Project-Based-Maker-Lab/docs/RELATORIO_ENTREGA_MAKER.md:14` | ‹PREENCHER: link do repositório] | 2 | URL do repositório público no GitHub |
| `07-Project-Based-Maker-Lab/docs/RELATORIO_ENTREGA_MAKER.md:15` | ‹PREENCHER: link] | 2 | Link do documento Onshape |
| `07-Project-Based-Maker-Lab/docs/RELATORIO_ENTREGA_MAKER.md:16` | ‹PREENCHER: link] | 2 | Link do vídeo-pitch/demonstração (público ou não listado) |
| `07-Project-Based-Maker-Lab/docs/RELATORIO_ENTREGA_MAKER.md:17` | ‹PREENCHER: URL pública] | 5 | URL pública do MVP (saída app_url do Terraform / FQDN do ACI) |
| `07-Project-Based-Maker-Lab/docs/RELATORIO_ENTREGA_MAKER.md:23` | ‹PREENCHER: local público de referência] | 7 | Diagnóstico, medidas, fabricação e testes no mundo físico |
| `07-Project-Based-Maker-Lab/docs/RELATORIO_ENTREGA_MAKER.md:24` | ‹PREENCHER: data] | 8 | Data de envio/entrega/conferência |
| `07-Project-Based-Maker-Lab/docs/RELATORIO_ENTREGA_MAKER.md:26` | ‹PREENCHER: 2–4 fotos do local — `docs/fotos/local_01_contexto.jpg`, `local_02_frontal.jpg | 3 | Prints, fotos e imagens de evidência |
| `07-Project-Based-Maker-Lab/docs/RELATORIO_ENTREGA_MAKER.md:29` | ‹PREENCHER: confirmado?] | 7 | Diagnóstico, medidas, fabricação e testes no mundo físico |
| `07-Project-Based-Maker-Lab/docs/RELATORIO_ENTREGA_MAKER.md:30` | ‹PREENCHER: confirmado?] | 7 | Diagnóstico, medidas, fabricação e testes no mundo físico |
| `07-Project-Based-Maker-Lab/docs/RELATORIO_ENTREGA_MAKER.md:31` | ‹PREENCHER: confirmado?] | 7 | Diagnóstico, medidas, fabricação e testes no mundo físico |
| `07-Project-Based-Maker-Lab/docs/RELATORIO_ENTREGA_MAKER.md:32` | ‹PREENCHER: confirmado?] | 7 | Diagnóstico, medidas, fabricação e testes no mundo físico |
| `07-Project-Based-Maker-Lab/docs/RELATORIO_ENTREGA_MAKER.md:38` | ‹PREENCHER: foto do croqui preenchido — `docs/imagens/croqui_original_preenchido.jpg`] | 3 | Prints, fotos e imagens de evidência |
| `07-Project-Based-Maker-Lab/docs/RELATORIO_ENTREGA_MAKER.md:42` | ‹PREENCHER] | 7 | Diagnóstico, medidas, fabricação e testes no mundo físico |
| `07-Project-Based-Maker-Lab/docs/RELATORIO_ENTREGA_MAKER.md:43` | ‹PREENCHER] | 7 | Diagnóstico, medidas, fabricação e testes no mundo físico |
| `07-Project-Based-Maker-Lab/docs/RELATORIO_ENTREGA_MAKER.md:44` | ‹PREENCHER] | 7 | Diagnóstico, medidas, fabricação e testes no mundo físico |
| `07-Project-Based-Maker-Lab/docs/RELATORIO_ENTREGA_MAKER.md:45` | ‹PREENCHER] | 7 | Diagnóstico, medidas, fabricação e testes no mundo físico |
| `07-Project-Based-Maker-Lab/docs/RELATORIO_ENTREGA_MAKER.md:46` | ‹PREENCHER] | 7 | Diagnóstico, medidas, fabricação e testes no mundo físico |
| `07-Project-Based-Maker-Lab/docs/RELATORIO_ENTREGA_MAKER.md:47` | ‹PREENCHER: trena / paquímetro] | 7 | Diagnóstico, medidas, fabricação e testes no mundo físico |
| `07-Project-Based-Maker-Lab/docs/RELATORIO_ENTREGA_MAKER.md:56` | ‹PREENCHER: confirmar que as medidas reais substituíram as estimativas — `ORIGINAL_MEDIDO_ | 7 | Diagnóstico, medidas, fabricação e testes no mundo físico |
| `07-Project-Based-Maker-Lab/docs/RELATORIO_ENTREGA_MAKER.md:75` | ‹PREENCHER: fotos reais — laser cortando, placa cortada, peças impressas, protótipo montad | 3 | Prints, fotos e imagens de evidência |
| `07-Project-Based-Maker-Lab/docs/RELATORIO_ENTREGA_MAKER.md:79` | ‹PREENCHER] | 7 | Diagnóstico, medidas, fabricação e testes no mundo físico |
| `07-Project-Based-Maker-Lab/docs/RELATORIO_ENTREGA_MAKER.md:80` | ‹PREENCHER] | 7 | Diagnóstico, medidas, fabricação e testes no mundo físico |
| `07-Project-Based-Maker-Lab/docs/RELATORIO_ENTREGA_MAKER.md:81` | ‹PREENCHER] | 7 | Diagnóstico, medidas, fabricação e testes no mundo físico |
| `07-Project-Based-Maker-Lab/docs/RELATORIO_ENTREGA_MAKER.md:89` | ‹PREENCHER] | 7 | Diagnóstico, medidas, fabricação e testes no mundo físico |
| `07-Project-Based-Maker-Lab/docs/RELATORIO_ENTREGA_MAKER.md:89` | ‹PREENCHER] | 7 | Diagnóstico, medidas, fabricação e testes no mundo físico |
| `07-Project-Based-Maker-Lab/docs/RELATORIO_ENTREGA_MAKER.md:97` | ‹PREENCHER: resultados reais — ver `IMPACTO_E_ODS.md`] | 7 | Diagnóstico, medidas, fabricação e testes no mundo físico |
| `07-Project-Based-Maker-Lab/docs/RELATORIO_ENTREGA_MAKER.md:103` | ‹PREENCHER: link do MakerWorld] | 2 | Link da página do modelo no MakerWorld |
| `07-Project-Based-Maker-Lab/docs/RELATORIO_ENTREGA_MAKER.md:104` | ‹PREENCHER: print da página publicada] | 3 | Prints, fotos e imagens de evidência |
| `07-Project-Based-Maker-Lab/docs/RELATORIO_ENTREGA_MAKER.md:108` | ‹PREENCHER: nome] | 7 | Peça de terceiros (nome, autor, link, licença) |
| `07-Project-Based-Maker-Lab/docs/RELATORIO_ENTREGA_MAKER.md:108` | ‹PREENCHER: autor] | 7 | Diagnóstico, medidas, fabricação e testes no mundo físico |
| `07-Project-Based-Maker-Lab/docs/RELATORIO_ENTREGA_MAKER.md:108` | ‹PREENCHER: link] | 7 | Diagnóstico, medidas, fabricação e testes no mundo físico |
| `07-Project-Based-Maker-Lab/docs/RELATORIO_ENTREGA_MAKER.md:108` | ‹PREENCHER] | 7 | Diagnóstico, medidas, fabricação e testes no mundo físico |
| `07-Project-Based-Maker-Lab/docs/RELATORIO_ENTREGA_MAKER.md:109` | ‹PREENCHER] | 7 | Diagnóstico, medidas, fabricação e testes no mundo físico |
| `07-Project-Based-Maker-Lab/docs/RELATORIO_ENTREGA_MAKER.md:110` | ‹PREENCHER: link] | 2 | Link do vídeo-pitch/demonstração (público ou não listado) |
| `07-Project-Based-Maker-Lab/docs/RELATORIO_ENTREGA_MAKER.md:115` | ‹PREENCHER: URL pública] | 5 | URL pública do MVP (saída app_url do Terraform / FQDN do ACI) |
| `07-Project-Based-Maker-Lab/docs/RELATORIO_ENTREGA_MAKER.md:115` | ‹PREENCHER: data] | 8 | Data de envio/entrega/conferência |
| `07-Project-Based-Maker-Lab/docs/RELATORIO_ENTREGA_MAKER.md:116` | ‹PREENCHER: nº] | 7 | Diagnóstico, medidas, fabricação e testes no mundo físico |
| `07-Project-Based-Maker-Lab/docs/ROTEIRO_VIDEO_MAKER.md:6` | ‹PREENCHER: link do vídeo] | 2 | Link do vídeo-pitch/demonstração (público ou não listado) |
| `07-Project-Based-Maker-Lab/docs/ROTEIRO_VIDEO_MAKER.md:10` | ‹PREENCHER: bairro/cidade] | 7 | Diagnóstico, medidas, fabricação e testes no mundo físico |
| `07-Project-Based-Maker-Lab/docs/ROTEIRO_VIDEO_MAKER.md:11` | ‹PREENCHER] | 7 | Diagnóstico, medidas, fabricação e testes no mundo físico |
| `07-Project-Based-Maker-Lab/docs/TUTORIAL_ONSHAPE.md:74` | ‹PREENCHER: link do documento Onshape] | 2 | Link do documento Onshape |
| `07-Project-Based-Maker-Lab/tests/test_maker_parametros_laser.py:203` | ‹PREENCHER: URL] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `PASSO_A_PASSO_PARA_CONCLUIR_O_PROJETO.txt:15` | ‹PREENCHER: ...] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `PASSO_A_PASSO_PARA_CONCLUIR_O_PROJETO.txt:56` | ‹PREENCHER] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `PASSO_A_PASSO_PARA_CONCLUIR_O_PROJETO.txt:324` | ‹PREENCHER] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `PASSO_A_PASSO_PARA_CONCLUIR_O_PROJETO.txt:422` | ‹PREENCHER] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `PASSO_A_PASSO_PARA_CONCLUIR_O_PROJETO.txt:672` | ‹PREENCHER" \| Group-Object Path \| Select-Object Count, Name | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `PASSO_A_PASSO_PARA_CONCLUIR_O_PROJETO.txt:673` | ‹PREENCHER] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `PASSO_A_PASSO_PARA_CONCLUIR_O_PROJETO.txt:679` | ‹PREENCHER] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `PASSO_A_PASSO_PARA_CONCLUIR_O_PROJETO.txt:748` | ‹PREENCHER] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `README.md:21` | ‹PREENCHER: nome da equipe] | 1 | Nome da equipe/startup |
| `README.md:21` | ‹PREENCHER: nomes e RMs dos integrantes] | 1 | Integrantes: nome completo, RM, papel e turma |
| `README.md:23` | ‹PREENCHER: cidade/bairros onde a equipe observou o problema] | 4 | Território onde a equipe observou o problema (cidade/bairro/data) |
| `README.md:29` | ‹PREENCHER: URL pública do MVP] | 5 | URL pública do MVP (saída app_url do Terraform / FQDN do ACI) |
| `README.md:30` | ‹PREENCHER: URL do repositório público no GitHub] | 2 | URL do repositório público no GitHub |
| `README.md:31` | ‹PREENCHER: link do vídeo] | 2 | Link do vídeo-pitch/demonstração (público ou não listado) |
| `README.md:202` | ‹PREENCHER: URL do repositório] | 2 | URL do repositório público no GitHub |
| `README.md:209` | ‹PREENCHER] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `README.md:227` | ‹PREENCHER: licença escolhida pela equipe (ex.: MIT) e arquivo LICENSE] | 8 | Licença do repositório |
| `README.md:234` | ‹PREENCHER] | 1 | Integrantes: nome completo, RM, papel e turma |
| `README.md:234` | ‹PREENCHER] | 1 | Integrantes: nome completo, RM, papel e turma |
| `README.md:234` | ‹PREENCHER] | 1 | Integrantes: nome completo, RM, papel e turma |
| `README.md:235` | ‹PREENCHER] | 1 | Integrantes: nome completo, RM, papel e turma |
| `README.md:235` | ‹PREENCHER] | 1 | Integrantes: nome completo, RM, papel e turma |
| `README.md:235` | ‹PREENCHER] | 1 | Integrantes: nome completo, RM, papel e turma |
| `README.md:236` | ‹PREENCHER] | 1 | Integrantes: nome completo, RM, papel e turma |
| `README.md:236` | ‹PREENCHER] | 1 | Integrantes: nome completo, RM, papel e turma |
| `README.md:236` | ‹PREENCHER] | 1 | Integrantes: nome completo, RM, papel e turma |
| `app/frontend/js/views/sobre.js:76` | ‹PREENCHER: prazo de guarda das denúncias e das fotos e como ocorre a exclusão] | 8 | Política de retenção/exclusão e base legal LGPD |
| `app/frontend/js/views/sobre.js:130` | ‹PREENCHER: e-mail ou canal de contato da equipe] | 8 | Canal de contato da equipe (e-mail institucional) |
| `app/frontend/tests_e2e/e2e_acessacidade.py:576` | ‹PREENCHER] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `app/frontend/tests_e2e/e2e_acessacidade.py:579` | ‹PREENCHER" in texto: | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `app/frontend/tests_e2e/e2e_acessacidade.py:580` | ‹PREENCHER] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `docs/ARQUITETURA_GERAL.md:80` | ‹PREENCHER: URL pública do MVP — saída `app_url` do Terraform após o deploy real] | 5 | URL pública do MVP (saída app_url do Terraform / FQDN do ACI) |
| `docs/FICHA_TECNICA_MVP.md:5` | ‹PREENCHER] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `docs/FICHA_TECNICA_MVP.md:10` | ‹PREENCHER: nome da equipe] | 1 | Nome da equipe/startup |
| `docs/FICHA_TECNICA_MVP.md:10` | ‹PREENCHER: nomes e RMs dos integrantes] | 1 | Integrantes: nome completo, RM, papel e turma |
| `docs/FICHA_TECNICA_MVP.md:12` | ‹PREENCHER: cidade/bairros onde a equipe observou o problema] | 4 | Território onde a equipe observou o problema (cidade/bairro/data) |
| `docs/FICHA_TECNICA_MVP.md:15` | ‹PREENCHER: URL pública do MVP] | 5 | URL pública do MVP (saída app_url do Terraform / FQDN do ACI) |
| `docs/FICHA_TECNICA_MVP.md:16` | ‹PREENCHER: URL do repositório público no GitHub] | 2 | URL do repositório público no GitHub |
| `docs/FICHA_TECNICA_MVP.md:17` | ‹PREENCHER: link do vídeo] | 2 | Link do vídeo-pitch/demonstração (público ou não listado) |
| `docs/FICHA_TECNICA_MVP.md:60` | ‹PREENCHER: dado + fonte, conferidos antes do pitch] | 4 | Dados públicos de contexto (IBGE/Censo/DATASUS/legislação) com fonte |
| `docs/FICHA_TECNICA_MVP.md:74` | ‹PREENCHER: medido pela equipe] | 4 | Resultados de teste de usabilidade com usuários (n, tempos, SUS, concl |
| `docs/FICHA_TECNICA_MVP.md:75` | ‹PREENCHER] | 4 | Resultados de teste de usabilidade com usuários (n, tempos, SUS, concl |
| `docs/FICHA_TECNICA_MVP.md:76` | ‹PREENCHER] | 4 | Resultados de teste de usabilidade com usuários (n, tempos, SUS, concl |
| `docs/FICHA_TECNICA_MVP.md:80` | ‹PREENCHER: quando houver piloto] | 4 | Validação do Lean Canvas (entrevistas/CP1, canais, preço, ativos) |
| `evidencias/README.md:45` | ‹PREENCHER: URL pública do MVP] | 5 | URL pública do MVP (saída app_url do Terraform / FQDN do ACI) |
| `evidencias/mvp_local/LEIAME.md:16` | ‹PREENCHER: URL pública e prints/vídeo da aplicação implantada] | 5 | URL pública do MVP (saída app_url do Terraform / FQDN do ACI) |
| `tools/gerar_pdf_markdown.py:13` | ‹PREENCHER...] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `tools/gerar_pdf_markdown.py:41` | ‹PREENCHER[^\] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `tools/gerar_pdf_markdown.py:164` | ‹PREENCHER] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `tools/gerar_pdf_markdown.py:180` | ‹PREENCHER] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `tools/gerar_pdf_markdown.py:184` | ‹PREENCHER] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `tools/gerar_todos_pdfs.ps1:19` | ‹PREENCHER] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `tools/gerar_todos_pdfs.ps1:20` | ‹PREENCHER] | 9 | Menção ao marcador em instrução/código/teste/modelo |
| `tools/gerar_todos_pdfs.ps1:112` | ‹PREENCHER] | 9 | Menção ao marcador em instrução/código/teste/modelo |
