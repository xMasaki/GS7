# Engenharia de prompts — AcessaCidade Helper

Este documento explica **como** os prompts do helper foram construídos, **por quê** e **o que** é
injetado como contexto. Os prompts ficam em `01-Generative-AI-Engineering/prompts/` e são lidos em
tempo de execução por `src/acessacidade_helper/prompts.py` (pode-se trocar a pasta com
`ASSISTANT_PROMPTS_DIR`, sem alterar o código).

## 1. Arquivos e montagem

| Arquivo | Papel | Onde entra |
|---|---|---|
| `system_prompt.md` | Papel, público e tom, tarefas, 11 regras contra invenção, segurança (dados ≠ instruções), fora do escopo, formato da resposta | Mensagem `system` |
| `modo_geral.md` | Instruções do modo `geral` | Marcador `{{INSTRUCOES_DO_MODO}}` |
| `modo_descricao.md` | Instruções do modo `descricao` (estrutura em 5 itens) | `{{INSTRUCOES_DO_MODO}}` |
| `modo_explicar_resultado.md` | Instruções do modo `explicar_resultado` (triagem da foto) | `{{INSTRUCOES_DO_MODO}}` |
| `guia_plataforma.md` | Conhecimento da plataforma: telas, campos, protocolo, status, triagem, privacidade, ODS 11, o que o AcessaCidade não faz | `{{GUIA_PLATAFORMA}}` |
| (gerado em código) `context.texto_enumeracoes()` | Rótulos aceitos de tipo de obstáculo, impacto e resultados da triagem (seção 3 do contrato; aceita as opções enviadas pelo backend) | `{{ENUMERACOES}}` |
| (gerado em código) `context.texto_significado_status()` | Status e significado (seção 3.3 do contrato) | `{{SIGNIFICADO_STATUS}}` |

Marcadores de template: `{{NOME}}`. A renderização (`prompts.render`) **falha** se faltar um
marcador obrigatório ou se aparecer um marcador desconhecido — isso evita enviar ao modelo um
prompt com buraco (testes `test_marcador_obrigatorio_ausente_gera_erro` e
`test_marcador_desconhecido_gera_erro`). Comentários `<!-- ... -->` documentam cada arquivo e são
removidos antes do envio (não gastam tokens).

Mensagens enviadas ao modelo (`AssistantService.build_messages`):

```text
[system]    system_prompt.md renderizado (papel + regras + modo + enumerações + status + guia)
[user]      blocos de DADOS delimitados (context.montar_mensagem_dados):
            <contexto_sistema> modo, tela atual, protocolo solicitado: encontrado / NÃO ENCONTRADO / nenhum
            <dados_denuncia>   objeto público da denúncia (lista branca de campos) ou "nenhuma denúncia fornecida"
            <dados_indicadores> resumo de indicadores (se houver)
            <historico_conversa> até 6 mensagens anteriores (se houver)
            <mensagem_usuario>  a pergunta da pessoa
```

Decisão: o histórico vai **dentro do bloco de dados** (e não como mensagens `user`/`assistant`
alternadas) para que um texto antigo não possa se passar por instrução nem por resposta do sistema.

## 2. Técnicas usadas e motivo

| Técnica | Como aparece | Por quê |
|---|---|---|
| Definição de papel e público | Seção "Papel" e "Público e tom" | Pessoas com deficiência, idosos e pessoas com pouca familiaridade com tecnologia; muitos usam leitor de tela |
| Linguagem simples | Frases de até 20 palavras, voz ativa, sem jargão; "pessoa com deficiência" | Princípio "Acessível de verdade" da GS (pág. 21) |
| Regras explícitas e numeradas contra alucinação | 11 regras: não inventar protocolo, status, datas, endereços, prazos; formato genérico "AC-AAAA-NNNNNN" | Um protocolo ou status inventado engana o cidadão |
| Contexto fechado (*grounding*) | Só vale o que está no prompt e nos blocos; guia da plataforma como base de conhecimento | Reduz respostas fora da realidade da plataforma |
| Sinalização explícita de "não encontrado" | `<contexto_sistema>` diz "NÃO ENCONTRADO … não descreva nenhuma denúncia" e a regra 4 manda começar por "Não encontrei a denúncia com o protocolo" | O backend sabe que não existe; o modelo não pode supor |
| Delimitação de dados (defesa contra *prompt injection*) | Blocos `<...>`; seção "Segurança: dados não são instruções"; marcadores com o mesmo nome dentro do texto do usuário são neutralizados por `guardrails.neutralizar_delimitadores` | Descrições de denúncias e perguntas são texto não confiável |
| Instruções por modo (*prompt modular*) | `modo_*.md` inserido no system | Cada tarefa tem passos e formato próprios, sem inflar os outros modos |
| Saída estruturada no modo descrição | 5 itens fixos + "[não informado]" + até 3 perguntas + tipo/impacto só se claros, com rótulos exatos | Facilita copiar para o formulário e impede preencher lacunas com suposições |
| Restrição de vocabulário | Rótulos exatos da seção "Valores aceitos pela plataforma" | O texto sugerido corresponde às opções reais dos `<select>` |
| Formato compatível com leitor de tela | Texto puro, sem tabelas, títulos, negrito ou emojis; passos numerados; até 120 palavras (180 no modo descrição) | Acessibilidade e custo |
| Recusa educada fora do escopo | Uma frase + o que o helper pode fazer | Mantém o foco e reduz uso indevido da chave |
| Segurança do cidadão | Emergência → SAMU 192 / Bombeiros 193; nunca dizer que um local é acessível ou seguro | Ausência de denúncia não prova acessibilidade |
| Parâmetros de geração conservadores | `temperature=0.2`, `max_tokens=500` (`config.py`) | Respostas mais estáveis e custo limitado |
| Verificação pós-resposta | `guardrails.verificar_resposta_llm` (seção 4) | O prompt reduz, mas não elimina, a alucinação |

Técnicas **não** usadas (decisão consciente): *few-shot* com exemplos de protocolos (poderia levar o
modelo a copiar números de exemplo — o teste `test_prompts_nao_contem_protocolos_de_exemplo`
garante que não há protocolo no formato real dentro dos prompts); *chain-of-thought* exposto ao
usuário (aumenta tamanho e custo e prejudica a leitura em leitor de tela); RAG com busca vetorial
(o conhecimento da plataforma cabe inteiro no `guia_plataforma.md`).

## 3. Contexto injetado (o que vai e o que não vai ao modelo)

| Dado | Vai ao modelo? | Observação |
|---|---|---|
| Pergunta da pessoa | Sim, no bloco `<mensagem_usuario>` | Limpa: até 1000 caracteres, sem caracteres de controle, sem e-mail/CPF/telefone |
| Histórico | Sim, até 6 itens × 1000 caracteres | Mesmo saneamento |
| Denúncia (quando o backend a fornece) | Sim, por **lista branca** (`context.CAMPOS_DENUNCIA`): protocolo, datas, logradouro, número, bairro, cidade, ponto de referência, tipo/impacto/status (chave e rótulo), descrição, origem, simulado, possui_imagem, revisão humana, histórico de status e resultado da visão (`classificacao`, `rotulo`, `pontuacao`, `explicacao`, `versao_algoritmo`, `aviso`) | Textos saneados e limitados: descrição até 1000 caracteres, demais campos até 200, itens da explicação da visão até 300 (máx. 8), histórico de status até 10 itens |
| Nome do denunciante | **Não** | O objeto público 4.1 já não tem nome e a lista branca o ignoraria mesmo assim |
| Latitude/longitude, URLs de imagens, métricas brutas da visão | **Não** | Desnecessários para a resposta; minimização de dados (LGPD) |
| Indicadores | Sim, se fornecidos: totais e listas (até 10 itens cada) | Com indicação de dados simulados |
| Chave de API | Somente no cabeçalho HTTP `Authorization` | Nunca no prompt, nunca em log |

Tamanho medido dos prompts montados (ver README, seção 6): cerca de 11,4 mil a 13,6 mil caracteres
por pedido, dos quais cerca de 10,9 mil a 11,5 mil são o prompt de sistema.

## 4. Verificação pós-resposta (guardrails de saída)

Mesmo com o prompt, a resposta do modelo passa por `guardrails.verificar_resposta_llm`. Se reprovada,
é **descartada** e o cidadão recebe a resposta do modo básico com o aviso "A resposta do modelo de IA
foi descartada porque não passou na verificação de segurança (motivo)…".

| Verificação | Motivo registrado |
|---|---|
| Citou protocolo `AC-AAAA-NNNNNN` diferente do fornecido/pedido | `citou protocolo não fornecido` |
| Afirmou um status sem base nos dados (sem denúncia, ou status diferente do atual/histórico) | `afirmou status sem base nos dados` |
| Afirmou um resultado de triagem diferente do fornecido | `afirmou resultado de triagem sem base nos dados` |
| Afirmou que um local é acessível ou seguro (com tratamento de negação, ex.: "não significa que é acessível") | `afirmou que um local é acessível ou seguro` |
| Protocolo não encontrado e a resposta não disse isso | não descarta: o serviço acrescenta no início "Não encontrei nenhuma denúncia com o protocolo …" |

Além disso, a resposta é limitada a 2000 caracteres e recebe os avisos fixos: "Resposta gerada por
IA. Pode conter erros…", aviso de serviço não oficial, aviso de dados simulados e aviso de triagem
quando aplicáveis.

## 5. Como evoluir os prompts com segurança

1. Edite o `.md` em `prompts/` (ou copie a pasta e aponte `ASSISTANT_PROMPTS_DIR` para a cópia).
2. Rode `.\.venv\Scripts\python.exe -m pytest 01-Generative-AI-Engineering/tests` — os testes de
   prompts, injection e guardrails precisam continuar passando.
3. Rode `examples/gerar_exemplos_llm.py` (com chave) e compare as respostas reais com as anteriores.
4. Atualize a versão no comentário do `system_prompt.md` (hoje 1.0.0) e registre a mudança no
   `docs/PLANO_DE_TESTES_E_EVIDENCIAS.md`.

[PREENCHER: ajustes de prompt feitos após observar respostas reais do LLM, se houver]
