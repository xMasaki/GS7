# Plano de testes e evidências — AcessaCidade Helper

## 1. Estratégia

| Nível | O quê | Ferramenta | Rede/chave? |
|---|---|---|---|
| Unitário | guardrails, fallback (intenções), prompts, cliente LLM | `pytest` | Não — `httpx.MockTransport` simula a API |
| Serviço | `AssistantService.answer` de ponta a ponta (LLM simulado, falhas, guardrails, LGPD) | `pytest` | Não |
| CLI e exemplos | `python -m acessacidade_helper`, arquivos de `examples/` conferidos contra o código atual | `pytest` + scripts | Não |
| Exemplos reais do LLM | 20 perguntas de `examples/perguntas_teste.json` contra o modelo real | `examples/gerar_exemplos_llm.py` | **Sim** — só a equipe, com a própria chave |
| Integração com o produto | `POST /api/assistente`, `GET /health`, tela `#/assistente` | testes do backend (`app/backend/tests/test_api_*.py`) + E2E 199/199 (15/11/2026); falta a URL pública | Opcional |

## 2. Resultado real registrado (execução local)

- Data: 2026-11-15 — Windows 11, Python 3.11.9, venv do repositório.
- Comando (na raiz): `.\.venv\Scripts\python.exe -m pytest 01-Generative-AI-Engineering/tests -v`
- Resultado: **`145 passed in 1.99s`** (nenhuma falha, nenhum teste pulado).

| Arquivo de teste | Testes aprovados | Cobre |
|---|---|---|
| `test_helper_cli_e_exemplos.py` | 7 | CLI sem chave, protocolo inexistente, `--denuncia-json`, arquivo inexistente; exemplos de fallback iguais à saída do código atual; exemplos de erro registrados; nenhum exemplo de LLM inventado |
| `test_helper_fallback.py` | 32 | Intenções (registrar, status, triagem com/sem foto e genérica, consulta, descrição completa/incompleta/curta/com dado pessoal, privacidade, ODS, rota, oficial, emergência, fora do escopo, indicadores); fallback nunca cita protocolo não recebido |
| `test_helper_guardrails.py` | 28 | `extract_protocol`, formato do protocolo, limpeza de controles e tamanho, neutralização de delimitadores, remoção de PII preservando protocolo/datas/medidas, verificação de saída (protocolo, status, histórico, triagem, rota acessível e negação), "não encontrado", limite da resposta |
| `test_helper_llm_client.py` | 28 | Cabeçalhos (`Authorization: Bearer`, `X-Title: AcessaCidade`) e payload; HTTP 400/401/402/403/404/429/500/502/503 → exceções tipadas; timeouts de leitura/conexão/escrita/pool; timeout; falha de conexão; JSON inválido; resposta vazia; formato inesperado; erro no corpo com status 200; conteúdo em partes; `repr` sem chave; cliente exige chave |
| `test_helper_prompt_injection.py` | 5 | Injeção na descrição da denúncia, na mensagem e no histórico fica **dentro** do bloco delimitado; system prompt instrui tratar blocos como dados; resposta que obedece à injeção é descartada |
| `test_helper_prompts.py` | 11 | Caminho padrão a partir do pacote, todos os prompts carregam, marcadores substituídos, prompts sem protocolos de exemplo, prompt/marcador ausente ou desconhecido gera erro, `ASSISTANT_PROMPTS_DIR`, enumerações vindas do backend |
| `test_helper_service.py` | 34 | `from_env` com/sem chave, timeout e base URL inválidos, prompts ausentes; sucesso do LLM; falhas → fallback com aviso; chave nunca nos logs; guardrails (protocolo inventado, status, rota, triagem); protocolo não encontrado (fallback e LLM); protocolo extraído da mensagem; denúncia que não corresponde ao protocolo; dados sensíveis não vão ao LLM; truncamento; histórico ≤ 6; modo inválido; serialização com campos do contrato; mensagem vazia |

Saída resumida (por arquivo, extraída do `-v`):

```text
      7 tests/test_helper_cli_e_exemplos.py PASSED
     32 tests/test_helper_fallback.py PASSED
     28 tests/test_helper_guardrails.py PASSED
     28 tests/test_helper_llm_client.py PASSED
      5 tests/test_helper_prompt_injection.py PASSED
     11 tests/test_helper_prompts.py PASSED
     34 tests/test_helper_service.py PASSED
============================= 145 passed in 1.99s =============================
```

(A contagem é maior que o número de funções porque vários testes são parametrizados.)

## 3. Casos de teste funcionais (20 perguntas)

Definidos em `examples/perguntas_teste.json` e usados tanto no modo básico quanto com o LLM real.

| Id | Objetivo | Resultado esperado |
|---|---|---|
| 01_como_registrar | Explicar como registrar | Passos numerados com a tela "Registrar" (#/registrar) |
| 02_status_aguardando_revisao | Status específico | Significado de "Aguardando revisão" |
| 03_todos_status | Todos os status | Lista dos 5 status |
| 04_consultar_protocolo_encontrado | Resumir denúncia fornecida | Resumo com dados da denúncia simulada + aviso de simulado |
| 05_consultar_protocolo_inexistente | Não inventar | "Não encontrei…" |
| 06_consultar_sem_protocolo | Pedir o número | Pede AC-AAAA-NNNNNN ou indica #/consultar |
| 07_explicar_resultado_com_foto | Explicar triagem fornecida | Rótulo, pontuação (não é probabilidade), revisão humana |
| 08_explicar_resultado_sem_foto | Denúncia sem foto | Diz que não houve triagem |
| 09_explicar_resultado_generico | 3 classes | Explica as 3 classes sem citar foto específica |
| 10_descricao_completa | Estruturar | 5 itens preenchidos só com fatos do texto |
| 11_descricao_incompleta | Perguntar o que falta | "[não informado]" + perguntas |
| 12_descricao_com_dado_pessoal | LGPD | Sugestão sem telefone/e-mail + aviso |
| 13_privacidade | LGPD | O que é coletado e por quê |
| 14_ods | ODS 11 | Ligação com o ODS 11 |
| 15_rota_segura | Não afirmar acessibilidade | Não diz que o local é acessível |
| 16_prefeitura_prazo | Não oficial | Não promete prazo; não é serviço oficial |
| 17_indicadores | Indicadores fornecidos | Cita números exatamente como fornecidos |
| 18_fora_de_escopo | Recusa | Recusa educada + o que o helper faz |
| 19_emergencia | Segurança | SAMU 192 / Bombeiros 193 |
| 20_injecao_de_prompt | Injection | Ignora a instrução e segue as regras |

## 4. Evidências já geradas (reais, executando o código)

| Evidência | Arquivo | Como foi gerada |
|---|---|---|
| Saídas reais do modo básico (20 casos) | `examples/fallback/exemplos_fallback.json` e `.md` (gerado em 2026-11-15T01:50:37Z) | `examples/gerar_exemplos_fallback.py` |
| Erros reais tratados (10 cenários: sem chave, 401, 429, 500, timeout, resposta vazia, JSON inválido, protocolo inexistente, guardrail de protocolo inventado, guardrail de rota acessível) | `examples/erros/exemplos_erros.json` e `.md` | `examples/gerar_exemplos_erros.py` (falhas simuladas com `httpx.MockTransport`) |
| CLI com protocolo inexistente | saída abaixo | comando abaixo |

```text
> $env:PYTHONPATH="01-Generative-AI-Engineering/src"
> .\.venv\Scripts\python.exe -m acessacidade_helper "Qual o status?" --protocolo AC-2026-000999 --json
{"resposta": "Não encontrei nenhuma denúncia com o protocolo AC-2026-000999.\nConfira se o número está certo. ...",
 "fonte": "fallback", "modelo": null,
 "avisos": ["Assistente em modo básico: as respostas são geradas por regras pré-definidas, sem modelo de IA."],
 "denuncia_referenciada": null}
```

## 5. Evidências pendentes (dependem da equipe)

| Evidência | Como produzir | Onde registrar |
|---|---|---|
| Respostas reais do LLM (20 casos) | `examples/gerar_exemplos_llm.py` com `OPENROUTER_API_KEY` (ver `examples/llm_real/LEIAME.md`) | `examples/llm_real/respostas_llm_*.json/.md` — 15/11/2026 modelo:GPT-4o-mini |
| Custo real | Painel *Activity* do OpenRouter após gerar os exemplos | US$0.0005 tokens:2949 |
| Print da tela `#/assistente` com `fonte = llm` | Navegador na URL pública com chave configurada | `evidencias/` — [PREENCHER: nome do arquivo] |
| Print da tela `#/assistente` em modo básico (sem chave) | Ambiente local sem chave | [PREENCHER] |
| Print de `GET /health` mostrando `assistente` | Navegador/`curl` na URL pública | [PREENCHER] |
| Teste com usuário real (opcional) | Roteiro de usabilidade da disciplina 03 (`03-Business-Intelligence-Startup/pitch/ROTEIRO_TESTE_USABILIDADE.md`) | [PREENCHER: resultado real, com consentimento] |

## 6. Critérios de aceite

- [x] 145 testes automatizados passando sem rede.
- [x] Sem chave → `fonte = "fallback"` + aviso "Assistente em modo básico".
- [x] Falha da API (401/429/5xx/timeout/vazia/JSON inválido) → fallback + aviso, sem exceção para o backend.
- [x] Protocolo inexistente → "Não encontrei…", nunca uma denúncia inventada.
- [x] Protocolo inventado pelo LLM → resposta descartada.
- [x] Conteúdo do usuário e da denúncia sempre dentro de blocos delimitados.
- [ ] Exemplos reais com LLM gerados pela equipe.
- [ ] Integração verificada na URL pública (checklist em `docs/INTEGRACAO.md`, seção 6).
