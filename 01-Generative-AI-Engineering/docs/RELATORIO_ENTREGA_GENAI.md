# AcessaCidade Helper — Relatório de entrega

**FIAP · Global Solution 2026.2 · CitizenTech · Engenharia de Software 4º ano**
**Disciplina:** Generative AI for Engineering — Prof. Reinaldo Augusto de Oliveira Ramos
**Componente no MVP:** Inteligência (IA generativa) do AcessaCidade
**Equipe:** [PREENCHER: nome da equipe] — [PREENCHER: nomes e RMs dos integrantes]
**Data:** [PREENCHER: data de envio]

> **Requisitos a confirmar.** No PDF oficial da GS a atividade desta disciplina está como **TBD**
> (nome, papel no MVP, conceito, objetivo, entregáveis e avaliação), com a orientação de falar
> diretamente com o professor. Este relatório descreve o componente desenvolvido pelo escopo
> definido pela equipe. [PREENCHER: requisitos confirmados com o professor, data e canal da confirmação;
> ajustar este relatório ao formato pedido]

## Links da entrega

| Item | Link |
|---|---|
| Repositório (público) | [PREENCHER: URL_REPOSITORIO] |
| Código do helper | [PREENCHER: URL_REPOSITORIO]/tree/main/01-Generative-AI-Engineering |
| MVP publicado — tela do assistente | [PREENCHER: URL_MVP]/#/assistente |
| Vídeo de demonstração (se exigido) | [PREENCHER: URL_VIDEO] |

Os links acima são substituídos automaticamente a partir de `docs/links_entrega.yaml` pelo script
`docs/gerar_pdf_relatorio.py`. Confira cada link em uma aba anônima antes de enviar.

## 1. Problema e papel da IA generativa

O AcessaCidade é uma plataforma web em que pessoas com deficiência, cadeirantes, pessoas idosas e
pessoas com mobilidade reduzida registram, acompanham e consultam denúncias de problemas de
acessibilidade em calçadas e espaços públicos (ODS 11). A IA generativa resolve três dores reais
desse público:

1. **Escrever uma boa descrição** do problema (modo `descricao`): o helper organiza o texto da
   pessoa em *O quê / Onde / Tamanho aproximado / Impacto / Quem é afetado*, sugere tipo e impacto
   e pergunta o que faltar — sem inventar fatos.
2. **Entender a triagem automática da foto** (modo `explicar_resultado`): explica a classificação da
   visão computacional, que a pontuação vai de 0 a 1 e **não** é probabilidade, e a revisão humana.
3. **Tirar dúvidas e acompanhar a denúncia** (modo `geral`): como registrar, significado de cada
   status, consulta por protocolo, privacidade/LGPD e ODS 11.

## 2. Arquitetura

| Etapa | Módulo | O que faz |
|---|---|---|
| 1. Entrada | backend `POST /api/assistente` | Valida o pedido, busca a denúncia **pública** (sem nome) pelo protocolo e monta o `AssistantRequest` |
| 2. Guardrails de entrada | `guardrails.py` | Limites (mensagem ≤ 1000, histórico ≤ 6 × 1000), remove caracteres de controle e dados pessoais óbvios (e-mail, CPF, telefone), neutraliza marcadores de bloco |
| 3. Contexto seguro | `context.py` | Lista branca de campos da denúncia, indicadores, enumerações e status; tudo em blocos de **dados** delimitados |
| 4. Prompts | `prompts.py` + `prompts/*.md` | Prompt de sistema + instruções do modo + guia da plataforma, com marcadores `{{...}}` |
| 5. Modelo | `llm_client.py` | API compatível com OpenAI no OpenRouter (`/chat/completions`), `temperature=0.2`, `max_tokens=500`, timeout configurável; erros viram exceções tipadas |
| 6. Guardrails de saída | `guardrails.py` | Descarta resposta que cita protocolo não fornecido, afirma status/triagem sem base ou diz que um local é acessível |
| 7. Modo básico | `fallback.py` | Sem chave, com falha da API ou com resposta reprovada: respostas por regras e intenções em pt-BR, com aviso |
| 8. Saída | `service.py` | `AssistantResponse` com `resposta`, `fonte` (`llm`/`fallback`), `modelo`, `denuncia_referenciada`, `avisos` |

Modelo padrão: `openai/gpt-4o-mini` via OpenRouter, trocável pela variável `OPENROUTER_MODEL`. A
chave (`OPENROUTER_API_KEY`) fica só em variável de ambiente (`.env` local, secure environment
variable na nuvem). Diagrama completo (Mermaid) no [README.md](../README.md) da disciplina.

## 3. Engenharia de prompts (resumo)

- Papel e público definidos; linguagem simples (frases de até 20 palavras, sem jargão, "pessoa com deficiência").
- 11 regras numeradas contra invenção (protocolo, status, datas, prazos, resultados de triagem; nunca dizer que um local é acessível; triagem não é avaliação oficial; não é serviço do governo; emergência → 192/193).
- Contexto fechado: só vale o que está no prompt e nos blocos de dados.
- Defesa contra *prompt injection*: pergunta, histórico e descrição da denúncia vão em blocos
  `<mensagem_usuario>`, `<historico_conversa>`, `<dados_denuncia>`; o prompt manda tratá-los como dados.
- Instruções separadas por modo e formato de saída fixo no modo descrição.
- Texto puro, compatível com leitor de tela, até 120 palavras (180 no modo descrição).

Detalhes: [docs/ENGENHARIA_DE_PROMPTS.md](ENGENHARIA_DE_PROMPTS.md).

## 4. Testes e resultados (reais)

Execução local em 2026-11-15 (Windows 11, Python 3.11.9), sem rede, com a API simulada por
`httpx.MockTransport`:

```text
.\.venv\Scripts\python.exe -m pytest 01-Generative-AI-Engineering/tests
145 passed
```

| Grupo | Aprovados |
|---|---|
| CLI e exemplos | 7 |
| Modo básico (fallback) | 32 |
| Guardrails | 28 |
| Cliente LLM (sucesso, 400/401/402/403/404/429/500/502/503, timeout, conexão, JSON inválido, resposta vazia) | 28 |
| Prompt injection | 5 |
| Prompts | 11 |
| Serviço (ponta a ponta) | 34 |

Plano completo e casos: [docs/PLANO_DE_TESTES_E_EVIDENCIAS.md](PLANO_DE_TESTES_E_EVIDENCIAS.md).

## 5. Exemplo real (modo básico, gerado executando o código)

Arquivo `examples/fallback/exemplos_fallback.md`, caso `10_descricao_completa`:

Mensagem: *"tem um buraco de uns 40 cm na Rua Exemplo em frente ao mercado, cadeirantes não conseguem passar"*

```text
Organizei o que você contou. Não acrescentei nenhuma informação nova.

- O quê: Buraco na calçada
- Onde: Rua Exemplo em frente ao mercado
- Tamanho aproximado: 40 cm
- Impacto: Impede a passagem
- Quem é afetado: cadeirantes

Sugestão de descrição (com as suas palavras):
Tem um buraco de uns 40 cm na Rua Exemplo em frente ao mercado, cadeirantes não conseguem passar.

Tipo de obstáculo sugerido no formulário: Buraco na calçada
Impacto sugerido no formulário: Impede a passagem
```

Outros exemplos reais: 20 casos do modo básico ([examples/fallback/exemplos_fallback.md](../examples/fallback/exemplos_fallback.md)) e 10 cenários de erro tratados
([examples/erros/exemplos_erros.md](../examples/erros/exemplos_erros.md): sem chave, 401, 429, 500, timeout, resposta vazia, JSON inválido, protocolo
inexistente, protocolo inventado pelo modelo, "rota acessível").

**Exemplos com o LLM real:** [PREENCHER: gerar com `examples/gerar_exemplos_llm.py` usando a chave
da equipe e citar aqui o arquivo `examples/llm_real/respostas_llm_<data>.md`, o modelo e o custo
observado]. Nenhuma resposta de LLM foi escrita à mão.

## 6. Custos estimados (premissas declaradas)

Com ~3.900 tokens de entrada (1 token ≈ 3,5 caracteres; prompt medido de 11,4 mil a 13,6 mil
caracteres) e ~200 tokens de saída, ao preço de referência do `openai/gpt-4o-mini` (US$ 0,15 por
milhão de tokens de entrada e US$ 0,60 por milhão de saída — [PREENCHER: confirmar preço vigente no
OpenRouter]): cerca de **US$ 0,0007 por pergunta**, US$ 0,70–0,90 por 1.000 perguntas.
Estimativa, não faturamento real. [PREENCHER: custo real observado]

## 7. IA responsável: riscos e limites

| Risco | Mitigação |
|---|---|
| Alucinação | Regras no prompt, contexto fechado, `temperature` baixa, verificação pós-resposta, aviso "Resposta gerada por IA" |
| Prompt injection | Blocos de dados delimitados e neutralização de marcadores; o helper não tem ferramentas nem acesso ao banco |
| Privacidade (LGPD) | Nome do denunciante nunca enviado; lista branca de campos; remoção de e-mail/CPF/telefone; sem chave nenhum dado sai do servidor |
| Dependência de terceiro e custo | Modo básico automático; timeout; `max_tokens`; limite de gasto na chave; rate limit no backend |
| Excesso de confiança | Avisos: triagem é apoio inicial, revisão humana, AcessaCidade não é serviço oficial |

Detalhes: [docs/RISCOS_E_LIMITES.md](RISCOS_E_LIMITES.md).

## 8. Integração com o MVP

O backend chama `AssistantService.from_env()` uma vez e responde `POST /api/assistente` com
`resp.to_dict()`; `GET /health` informa `componentes.assistente = "llm" | "fallback"`; a métrica
`acessacidade_assistente_respostas_total{fonte}` aparece em `/metrics`. A tela `#/assistente` mostra a
resposta, a origem e os avisos. Detalhes e checklist: [docs/INTEGRACAO.md](INTEGRACAO.md).

## 9. Checklist antes do envio

- [ ] Requisitos confirmados com o professor Reinaldo Ramos e relatório ajustado.
- [ ] Links preenchidos em `docs/links_entrega.yaml` e conferidos em aba anônima.
- [ ] Exemplos reais com LLM gerados e citados na seção 5.
- [ ] Prints das evidências (tela `#/assistente` com `fonte = llm` e em modo básico; `/health`).
- [ ] PDF gerado com `docs/gerar_pdf_relatorio.py --estrito` (falha se restar algum [PREENCHER]).
