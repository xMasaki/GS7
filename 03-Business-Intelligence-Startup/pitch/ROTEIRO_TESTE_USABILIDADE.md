# Roteiro de teste de usabilidade — AcessaCidade

Objetivo: verificar, com pessoas do público-alvo, se o fluxo central do MVP entrega valor (registrar uma barreira e
acompanhar o que acontece) e medir o **tempo para registrar** um problema **antes** (canal atual) e **depois**
(AcessaCidade). Resultado registrado em `registro_testes_usuarios_TEMPLATE.xlsx` (copiar e preencher).

## 1. Participantes

- **Perfil:** pessoas com deficiência (física, visual, auditiva), pessoas idosas, pessoas com mobilidade reduzida, cuidadores.
- **Quantidade:** 3 a 5 (suficiente para encontrar a maior parte dos problemas graves de usabilidade em um MVP; declarar que a amostra não é representativa).
- **Recrutamento:** contatos pessoais da equipe, associações locais (com autorização da associação). Não oferecer pagamento.
- **Inclusão de quem usa leitor de tela:** se possível, ao menos 1 participante que use TalkBack/VoiceOver/NVDA.
- Menores de 18 anos: **não** incluir sem autorização do responsável legal (recomendação: não incluir).

## 2. Papéis da equipe

| Papel | Quem | O que faz |
|---|---|---|
| Moderador | [PREENCHER: Integrante] | Lê as tarefas, não ajuda, faz as perguntas finais |
| Anotador/cronometrista | [PREENCHER: Integrante] | Cronometra (celular), anota erros e pedidos de ajuda na planilha |

## 3. Preparação (antes de cada sessão)

1. URL pública do MVP aberta no dispositivo do participante (preferível) ou da equipe: `[PREENCHER: URL]`.
2. Termo de consentimento (`TERMO_CONSENTIMENTO_MODELO.md`) impresso ou em formulário eletrônico.
3. Uma foto de calçada para anexar (do participante, de um problema real que ele conheça; ou a foto de teste da equipe).
4. Planilha aberta na aba **Tarefas**; código do participante definido (P01, P02...).
5. Cronômetro.

## 4. Roteiro da sessão (≈ 25 minutos)

### 4.1 Abertura (2 min) — ler em voz alta

> "Obrigado por participar. Estamos testando o site, não você: não existe resposta errada. Pense em voz alta enquanto
> usa — diga o que está procurando e o que acha estranho. Se travar, pode desistir da tarefa a qualquer momento.
> Vamos cronometrar o tempo das tarefas e anotar o que você disser, sem o seu nome. Você leu e concorda com o termo?"

Confirmar o termo **antes** de começar. Sem termo, não há teste.

### 4.2 Perguntas iniciais (3 min)

1. Quando você encontra um buraco ou obstáculo na calçada, o que costuma fazer?
2. Você já avisou a prefeitura ou outro responsável? Por qual canal? Como foi?
3. Você ficou sabendo o que aconteceu depois?

(Anotar na aba Participantes / Observações. Não sugerir respostas.)

### 4.3 Medição "ANTES" — canal atual (5 min)

> "Mostre como você avisaria hoje sobre um buraco na calçada, usando o canal que você usaria normalmente."

- Cronometrar do início até **a etapa imediatamente anterior ao envio** (ex.: tela de confirmação do site/app, ou
  momento em que a ligação seria atendida). **Não enviar denúncia falsa a canais oficiais.**
- Se o problema for real e o participante quiser registrá-lo de verdade, ele decide — a equipe não envia por ele.
- Anotar: canal, tempo (s), nº de etapas, como foi medido (aba **Antes_x_Depois**).

### 4.4 Tarefas no AcessaCidade (12 min)

Ler cada tarefa exatamente como está escrita. Iniciar o cronômetro ao terminar de ler; parar quando o critério de sucesso for atingido ou o participante desistir.

| Tarefa | Enunciado | Critério de sucesso |
|---|---|---|
| T1 | "Registre uma denúncia sobre um buraco na calçada, com foto, a partir da página inicial, até receber o número de protocolo." | Protocolo AC-AAAA-NNNNNN visível |
| T2 | "Abra a página de acompanhamento da denúncia que você acabou de registrar." | Página do protocolo aberta |
| T3 | "Com suas palavras, o que a análise da foto indicou? E o que significa o status atual?" | Entende que é triagem inicial revisada por uma pessoa |
| T4 | "Procure essa denúncia pelo número de protocolo na tela Consultar." | Detalhe aberto pela busca |
| T5 | "Pergunte ao assistente o que significa 'Aguardando revisão'." | Recebe resposta e diz se entendeu |
| T6 | "No painel, qual bairro tem mais denúncias?" | Nomeia o bairro corretamente |

Registrar por tarefa: Concluiu (Sim / Com ajuda / Não), tempo (s), nº de erros, pedidos de ajuda, comentário.
O tempo da T1 também vai para a coluna "Tempo AcessaCidade (s)" da aba **Antes_x_Depois**.

### 4.5 Questionário SUS (2 min)

Aplicar os 10 itens da aba **SUS_Itens** (1 = discordo totalmente, 5 = concordo totalmente). A planilha calcula a pontuação.

### 4.6 Perguntas finais (1 min)

1. O que foi mais fácil? O que foi mais difícil?
2. Você usaria isso de novo? Indicaria para alguém?
3. Posso usar alguma frase sua no vídeo, sem o seu nome? (marcar no termo)

## 5. Depois da sessão

1. Conferir se a planilha está completa e **sem dados pessoais**.
2. Anotar os 3 principais problemas encontrados e, se corrigidos no MVP, registrar o que mudou (é evidência de iteração).
3. Guardar o termo assinado **fora do repositório**.
4. Ao fim de todas as sessões, copiar os números da aba **Resumo** para `LISTA_DE_EVIDENCIAS.md` e para o bloco 5 do pitch.

## 6. Acessibilidade da própria sessão

- Local com acesso sem degraus, ou sessão remota por videochamada.
- Para pessoa cega/baixa visão: ler o termo em voz alta e registrar o aceite em áudio ou por escrito com testemunha.
- Respeitar o ritmo do participante; o tempo é medida, não pressão.
