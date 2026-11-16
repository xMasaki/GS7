# Roteiro do pitch — AcessaCidade (até 5:00)

> Estrutura oficial da disciplina (PDF da GS, pág. 34): seis blocos em cinco minutos —
> **0:45 · 0:45 · 1:30 · 1:00 · 0:30 · 0:30**. Todos os integrantes falam.
> Ritmo de referência: ~130 palavras por minuto (fala calma e clara; a demo tem fala mais lenta porque a tela "fala junto").
>
> Antes de gravar: substitua cada `[PREENCHER: ...]`. **Não diga números que a equipe não mediu.** Se o teste com
> usuários ainda não aconteceu, use a frase alternativa indicada no bloco 5.

## Distribuição de falas

| Bloco | Tempo | Duração | Quem fala | Palavras (fala abaixo) | Máximo a 130 ppm |
|---|---|---|---|---|---|
| 1. Problema e cidadão | 0:00–0:45 | 0:45 | [PREENCHER: Integrante 1] | 97 | 97 |
| 2. Solução e proposta de valor | 0:45–1:30 | 0:45 | [PREENCHER: Integrante 2] | 94 | 97 |
| 3. Demo do MVP | 1:30–3:00 | 1:30 | [PREENCHER: Integrante 3] (narra) · [PREENCHER: Integrante 4] (opera a tela, fala a parte do painel) | 118 | 195 |
| 4. Modelo de negócio | 3:00–4:00 | 1:00 | [PREENCHER: Integrante 4] | 117 + frase do CP1 (~12) | 130 |
| 5. Impacto e ODS | 4:00–4:30 | 0:30 | [PREENCHER: Integrante 5] | 52 + resultado (~13) | 65 |
| 6. Time e próximos passos | 4:30–5:00 | 0:30 | Todos (uma frase cada) + [PREENCHER: Integrante 1] fecha | 48 + nomes e papéis (~17) | 65 |
| **Total** | | **5:00** | | **526 + ~42 dos [PREENCHER]** | **649** |

> As contagens de palavras foram feitas por script sobre o texto abaixo, **sem** contar os `[PREENCHER]`.
> Se a equipe tiver menos de 5 pessoas, junte os blocos 4 e 5 ou 1 e 2 para o mesmo integrante, mantendo os tempos.
> Ao completar os `[PREENCHER]`, recronometre: cada frase nova de ~10 palavras consome ~5 segundos.

---

## Bloco 1 — Problema e cidadão (0:00–0:45) · [PREENCHER: Integrante 1]

**Na tela:** foto real de calçada com buraco feita pela equipe no território (`[PREENCHER: foto própria — bairro/cidade]`), depois o título "Quem sofre, onde e quanto custa".

<!-- FALA -->
> Imagine sair de casa de cadeira de rodas e, duas quadras depois, encontrar um buraco que ocupa a calçada
> inteira. A saída é descer para a rua, no meio dos carros. Para pessoas com deficiência, idosos e quem tem
> mobilidade reduzida, isso é rotina. A PNAD Contínua 2022, do IBGE, estima dezoito vírgula seis milhões de
> brasileiros com deficiência. Avisar quem pode consertar costuma ser demorado, e quase nunca há retorno. E quem
> precisa consertar recebe relatos soltos, sem foto organizada e sem prioridade. O custo é perder autonomia,
> correr risco de queda e desistir de sair.
> [PREENCHER: uma frase real ouvida em entrevista, com autorização — ou o local observado pela equipe]
<!-- /FALA -->

Observação: conferir o dado da PNAD Contínua 2022 (IBGE) na fonte antes de gravar.

## Bloco 2 — Solução e proposta de valor (0:45–1:30) · [PREENCHER: Integrante 2]

**Na tela:** logotipo/nome AcessaCidade e um diagrama simples: cidadão → denúncia com foto → triagem + revisão humana → protocolo → painel.

<!-- FALA -->
> Por isso criamos o AcessaCidade. Pelo celular, sem instalar nada e sem criar conta, a pessoa registra a barreira
> em poucos passos: endereço, tipo de obstáculo, impacto e, se quiser, uma foto. Na hora, recebe um protocolo para
> acompanhar. A foto passa por uma triagem automática com visão computacional, que mostra cada etapa e explica o
> resultado, mas quem decide é sempre uma pessoa. Um assistente tira dúvidas em linguagem simples. O que muda
> para o cidadão: ele é ouvido, sabe em que pé está a denúncia, e a cidade ganha dados para priorizar.
<!-- /FALA -->

## Bloco 3 — Demo do MVP (1:30–3:00) · [PREENCHER: Integrante 3] narra · [PREENCHER: Integrante 4] opera

**Na tela:** gravação REAL da URL pública `[PREENCHER: URL pública do MVP]` (ver `ROTEIRO_DE_GRAVACAO.md`).
Fluxo: página inicial → Registrar → foto → protocolo → triagem com etapas → consulta por protocolo → assistente → painel.

<!-- FALA -->
> Vamos ver funcionando, na URL pública. Esta é a página inicial. Clico em Registrar denúncia. Preencho a rua e o
> bairro, escolho buraco na calçada, descrevo o problema e marco que impede a passagem. Anexo a foto, aceito o
> termo e envio. Pronto: protocolo gerado. Abrindo o acompanhamento, vemos a triagem da foto: original, tons de
> cinza, filtro, contraste, bordas, máscara e contornos, com a explicação do resultado. O status mudou sozinho
> para aguardando revisão, porque uma pessoa sempre confere. Agora consulto pelo protocolo e pergunto ao
> assistente o que significa aguardando revisão. Ele responde com base nessa denúncia.
> No painel, a nova denúncia já entra nos indicadores, ao lado dos dados analíticos do pipeline, identificados
> como simulados.
<!-- /FALA -->

Regras da demo: nada de tela falsa nem montagem de resultado. Cortes de edição são permitidos para pular
esperas (ex.: upload), mas a sequência deve ser a real. Se o assistente estiver em modo por regras (sem chave
de API), diga "no modo por regras" em vez de esconder.

## Bloco 4 — Modelo de negócio (3:00–4:00) · [PREENCHER: Integrante 4]

**Na tela:** Lean Canvas (`business-model/LEAN_CANVAS.html`) com destaque nos blocos Segmentos, Receitas e Canais;
depois a tabela de planos (marcada "valores hipotéticos") e o cálculo do ponto de equilíbrio.

<!-- FALA -->
> Quem usa não paga. Quem paga é quem precisa resolver: prefeituras, concessionárias que abrem valas nas calçadas e
> administradoras de grandes áreas, como shoppings e campi. O modelo é assinatura anual, com preço por faixa de
> população: de mil e duzentos a seis mil e quinhentos reais por mês nos planos municipais, valores que ainda são
> hipóteses a validar. Somam-se módulo de painel, implantação e uma API para concessionárias. Entramos por pilotos
> de noventa dias e programas de inovação aberta e, como caminho possível, pelo contrato público de solução
> inovadora do Marco Legal das Startups. Com custo fixo estimado em cinquenta e cinco mil reais por mês, o ponto de
> equilíbrio é de vinte e quatro municípios.
> [PREENCHER: o que o Lean Canvas mudou desde o CP1, em uma frase]
<!-- /FALA -->

## Bloco 5 — Impacto e ODS (4:00–4:30) · [PREENCHER: Integrante 5]

**Na tela:** indicadores de impacto (tempo para registrar antes × depois — **somente se medido**) e ícones dos ODS 11, 10 e 9.

<!-- FALA -->
> Medimos impacto no tempo que o cidadão leva para registrar um problema, no canal de hoje e no AcessaCidade,
> e na taxa de conclusão sem ajuda; nos pilotos, no tempo até o encaminhamento.
> [PREENCHER: resultado real do teste com usuários — ex.: "com N participantes, o tempo caiu de X para Y"]
> Contribuímos com o ODS onze, meta onze ponto sete, espaços públicos acessíveis, e com os ODS dez e nove.
<!-- /FALA -->

Frase alternativa se **não** houve teste real até a gravação: "Nosso protocolo de teste com usuários está pronto
e será aplicado em [PREENCHER: data]; ainda não temos resultado medido." (Nunca invente número.)

## Bloco 6 — Time e próximos passos (4:30–5:00) · Todos

**Na tela:** cada integrante aparece (câmera ou foto) com nome e papel em legenda.

<!-- FALA -->
> [PREENCHER: Integrante 1 — nome], [PREENCHER: papel em poucas palavras].
> [PREENCHER: Integrante 2 — nome], [PREENCHER: papel].
> [PREENCHER: Integrante 3 — nome], [PREENCHER: papel].
> [PREENCHER: Integrante 4 — nome], [PREENCHER: papel].
> [PREENCHER: Integrante 5 — nome], [PREENCHER: papel].
> Próximos passos: testar com mais pessoas com deficiência, um piloto com um município e integração com o cento e
> cinquenta e seis. Pedimos a indicação de um município para piloto e mentoria em vendas ao setor público.
> AcessaCidade: calçada acessível começa com uma denúncia que não se perde.
<!-- /FALA -->

---

## Checklist antes de gravar

- [ ] Todos os `[PREENCHER]` substituídos; nenhum número que a equipe não tenha medido ou conferido na fonte.
- [ ] Dado da PNAD Contínua 2022 conferido no site do IBGE.
- [ ] URL pública do MVP funcionando no momento da gravação (abrir em aba anônima).
- [ ] Ensaio cronometrado completo ≤ 5:00 (ideal 4:45 para margem).
- [ ] Todos os integrantes aparecem e falam.
- [ ] Valores de preço ditos como "hipóteses a validar".
- [ ] Nenhuma menção a parceria, contrato ou cliente que não exista.
