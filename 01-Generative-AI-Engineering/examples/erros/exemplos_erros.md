# Exemplos reais de tratamento de erros — AcessaCidade Helper

Gerado por `examples/gerar_exemplos_erros.py`. As falhas da API são **simuladas** com
`httpx.MockTransport` (sem rede, sem chave real). As respostas abaixo foram produzidas
executando o código do helper.

- Gerado em (UTC): `2026-11-15T01:50:37Z`
- Versão do helper: `1.0.0` — Python `3.11.9`

## E01_sem_chave

- **Cenário:** OPENROUTER_API_KEY vazia: o helper nem tenta chamar a API.
- **Simulação:** nenhuma (configuração sem chave)
- **LLM habilitado:** `False`
- **Mensagem:** O que significa aguardando revisão?
- **Fonte da resposta:** `fallback`

```text
"Aguardando revisão" quer dizer: A triagem automática da foto terminou e uma pessoa precisa revisar o resultado.
Os outros status são: Recebida, Em análise, Encaminhada, Resolvida.
Para ver o status de uma denúncia, informe o protocolo ou use a tela "Consultar" (#/consultar).
```

**Avisos:**
- O AcessaCidade não é um serviço oficial do governo. O status mostra o registro da equipe do AcessaCidade, não uma confirmação de órgão público.
- Assistente em modo básico: as respostas são geradas por regras pré-definidas, sem modelo de IA.

## E02_chave_invalida_401

- **Cenário:** Chave inválida: a API responde HTTP 401.
- **Simulação:** MockTransport devolve 401 {"error": {"message": "No auth credentials found", "code": 401}}
- **LLM habilitado:** `True`
- **Mensagem:** O que significa aguardando revisão?
- **Exceção do cliente LLM:** `{"excecao": "LLMAuthError", "codigo": "autenticacao", "status_http": 401, "mensagem": "chave de API inválida ou sem permissão", "chave_aparece_na_mensagem": false}`
- **Fonte da resposta:** `fallback`

```text
"Aguardando revisão" quer dizer: A triagem automática da foto terminou e uma pessoa precisa revisar o resultado.
Os outros status são: Recebida, Em análise, Encaminhada, Resolvida.
Para ver o status de uma denúncia, informe o protocolo ou use a tela "Consultar" (#/consultar).
```

**Avisos:**
- O AcessaCidade não é um serviço oficial do governo. O status mostra o registro da equipe do AcessaCidade, não uma confirmação de órgão público.
- Não foi possível consultar o modelo de IA agora (chave de API inválida ou sem permissão). Assistente em modo básico: resposta gerada por regras pré-definidas.

## E03_limite_429

- **Cenário:** Limite de requisições atingido: HTTP 429.
- **Simulação:** MockTransport devolve 429
- **LLM habilitado:** `True`
- **Mensagem:** O que significa aguardando revisão?
- **Exceção do cliente LLM:** `{"excecao": "LLMRateLimitError", "codigo": "limite_requisicoes", "status_http": 429, "mensagem": "limite de requisições ou de créditos atingido", "chave_aparece_na_mensagem": false}`
- **Fonte da resposta:** `fallback`

```text
"Aguardando revisão" quer dizer: A triagem automática da foto terminou e uma pessoa precisa revisar o resultado.
Os outros status são: Recebida, Em análise, Encaminhada, Resolvida.
Para ver o status de uma denúncia, informe o protocolo ou use a tela "Consultar" (#/consultar).
```

**Avisos:**
- O AcessaCidade não é um serviço oficial do governo. O status mostra o registro da equipe do AcessaCidade, não uma confirmação de órgão público.
- Não foi possível consultar o modelo de IA agora (limite de requisições ou de créditos atingido). Assistente em modo básico: resposta gerada por regras pré-definidas.

## E04_erro_servidor_500

- **Cenário:** Instabilidade do provedor: HTTP 500.
- **Simulação:** MockTransport devolve 500
- **LLM habilitado:** `True`
- **Mensagem:** O que significa aguardando revisão?
- **Exceção do cliente LLM:** `{"excecao": "LLMServerError", "codigo": "erro_servidor", "status_http": 500, "mensagem": "o serviço de IA está com instabilidade", "chave_aparece_na_mensagem": false}`
- **Fonte da resposta:** `fallback`

```text
"Aguardando revisão" quer dizer: A triagem automática da foto terminou e uma pessoa precisa revisar o resultado.
Os outros status são: Recebida, Em análise, Encaminhada, Resolvida.
Para ver o status de uma denúncia, informe o protocolo ou use a tela "Consultar" (#/consultar).
```

**Avisos:**
- O AcessaCidade não é um serviço oficial do governo. O status mostra o registro da equipe do AcessaCidade, não uma confirmação de órgão público.
- Não foi possível consultar o modelo de IA agora (o serviço de IA está com instabilidade). Assistente em modo básico: resposta gerada por regras pré-definidas.

## E05_timeout

- **Cenário:** O provedor não responde dentro de ASSISTANT_TIMEOUT_SECONDS.
- **Simulação:** MockTransport levanta httpx.ReadTimeout
- **LLM habilitado:** `True`
- **Mensagem:** O que significa aguardando revisão?
- **Exceção do cliente LLM:** `{"excecao": "LLMTimeoutError", "codigo": "tempo_esgotado", "status_http": null, "mensagem": "o serviço de IA demorou demais para responder", "chave_aparece_na_mensagem": false}`
- **Fonte da resposta:** `fallback`

```text
"Aguardando revisão" quer dizer: A triagem automática da foto terminou e uma pessoa precisa revisar o resultado.
Os outros status são: Recebida, Em análise, Encaminhada, Resolvida.
Para ver o status de uma denúncia, informe o protocolo ou use a tela "Consultar" (#/consultar).
```

**Avisos:**
- O AcessaCidade não é um serviço oficial do governo. O status mostra o registro da equipe do AcessaCidade, não uma confirmação de órgão público.
- Não foi possível consultar o modelo de IA agora (o serviço de IA demorou demais para responder). Assistente em modo básico: resposta gerada por regras pré-definidas.

## E06_resposta_vazia

- **Cenário:** O provedor devolve 200 com conteúdo vazio.
- **Simulação:** MockTransport devolve 200 com message.content = ""
- **LLM habilitado:** `True`
- **Mensagem:** O que significa aguardando revisão?
- **Exceção do cliente LLM:** `{"excecao": "LLMEmptyResponseError", "codigo": "resposta_vazia", "status_http": 200, "mensagem": "o serviço de IA devolveu uma resposta vazia", "chave_aparece_na_mensagem": false}`
- **Fonte da resposta:** `fallback`

```text
"Aguardando revisão" quer dizer: A triagem automática da foto terminou e uma pessoa precisa revisar o resultado.
Os outros status são: Recebida, Em análise, Encaminhada, Resolvida.
Para ver o status de uma denúncia, informe o protocolo ou use a tela "Consultar" (#/consultar).
```

**Avisos:**
- O AcessaCidade não é um serviço oficial do governo. O status mostra o registro da equipe do AcessaCidade, não uma confirmação de órgão público.
- Não foi possível consultar o modelo de IA agora (o serviço de IA devolveu uma resposta vazia). Assistente em modo básico: resposta gerada por regras pré-definidas.

## E07_json_invalido

- **Cenário:** O provedor devolve 200 com corpo que não é JSON.
- **Simulação:** MockTransport devolve 200 com texto '<html>erro</html>'
- **LLM habilitado:** `True`
- **Mensagem:** O que significa aguardando revisão?
- **Exceção do cliente LLM:** `{"excecao": "LLMInvalidResponseError", "codigo": "resposta_invalida", "status_http": 200, "mensagem": "o serviço de IA devolveu uma resposta em formato inesperado", "chave_aparece_na_mensagem": false}`
- **Fonte da resposta:** `fallback`

```text
"Aguardando revisão" quer dizer: A triagem automática da foto terminou e uma pessoa precisa revisar o resultado.
Os outros status são: Recebida, Em análise, Encaminhada, Resolvida.
Para ver o status de uma denúncia, informe o protocolo ou use a tela "Consultar" (#/consultar).
```

**Avisos:**
- O AcessaCidade não é um serviço oficial do governo. O status mostra o registro da equipe do AcessaCidade, não uma confirmação de órgão público.
- Não foi possível consultar o modelo de IA agora (o serviço de IA devolveu uma resposta em formato inesperado). Assistente em modo básico: resposta gerada por regras pré-definidas.

## E08_protocolo_inexistente

- **Cenário:** Protocolo pedido não existe: o backend envia protocolo_solicitado sem denúncia.
- **Simulação:** nenhuma (configuração sem chave); denuncia=None
- **LLM habilitado:** `False`
- **Mensagem:** Qual o status do protocolo AC-2026-000999?
- **Fonte da resposta:** `fallback`

```text
Não encontrei nenhuma denúncia com o protocolo AC-2026-000999.
Confira se o número está certo. O formato é AC-AAAA-NNNNNN, com letras maiúsculas e hífens.
Você também pode procurar na tela "Consultar" (#/consultar). Eu não invento informações sobre denúncias.
```

**Avisos:**
- Assistente em modo básico: as respostas são geradas por regras pré-definidas, sem modelo de IA.

## E09_guardrail_protocolo_inventado

- **Cenário:** O modelo cita um protocolo que não foi fornecido: a resposta é descartada.
- **Simulação:** MockTransport devolve 200 com texto que cita AC-2026-000777 (não fornecido)
- **LLM habilitado:** `True`
- **Mensagem:** Como está minha denúncia?
- **Exceção do cliente LLM:** `{"excecao": null, "observacao": "o cliente não levantou exceção (resposta HTTP aceita)"}`
- **Fonte da resposta:** `fallback`

```text
Para consultar uma denúncia, me diga o número do protocolo. O formato é AC-AAAA-NNNNNN: as letras AC, o ano com 4 números e mais 6 números, separados por hífen.
Você recebe esse número quando termina o registro. Também dá para procurar pelo bairro ou pelo tipo de problema na tela "Consultar" (#/consultar).
```

**Avisos:**
- A resposta do modelo de IA foi descartada porque não passou na verificação de segurança (citou protocolo não fornecido). Assistente em modo básico: resposta gerada por regras pré-definidas.

## E10_guardrail_rota_acessivel

- **Cenário:** O modelo afirma que uma rota é acessível: a resposta é descartada.
- **Simulação:** MockTransport devolve 200 com 'Sim, a rota pela Rua Exemplo é acessível.'
- **LLM habilitado:** `True`
- **Mensagem:** A rota pela Rua Exemplo é acessível para cadeirante?
- **Exceção do cliente LLM:** `{"excecao": null, "observacao": "o cliente não levantou exceção (resposta HTTP aceita)"}`
- **Fonte da resposta:** `fallback`

```text
Não consigo dizer se um caminho é acessível ou seguro. O AcessaCidade mostra só os problemas que as pessoas registraram. Se um lugar não tem denúncia, isso não quer dizer que ele é acessível.
Você pode ver as denúncias de um bairro na tela "Consultar" (#/consultar). Se encontrar um problema no caminho, registre em "Registrar" (#/registrar).
```

**Avisos:**
- A resposta do modelo de IA foi descartada porque não passou na verificação de segurança (afirmou que um local é acessível ou seguro). Assistente em modo básico: resposta gerada por regras pré-definidas.
