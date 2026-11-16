# Impacto e ODS

## 1. O que falhava → o que mudou → ganho para o cidadão

| O que falhava (hipótese a verificar no local) | O que mudou no redesign | Ganho esperado (hipótese a validar) |
|---|---|---|
| Informação só visual, alta e de baixo contraste | Branco sobre preto, letras maiores, placa mais baixa, módulo amarelo | Pessoa com baixa visão ou idosa lê a curta distância |
| Nenhuma informação tátil | Letras em relevo, seta em relevo e Braille "PONTO" a altura de alcance | Pessoa cega confirma que chegou ao ponto e o sentido de embarque |
| Nenhum canal para reportar problemas do entorno | QR Code → tela de registro do AcessaCidade | Qualquer cidadão registra calçada quebrada, obstáculo ou falta de piso tátil **no local exato**, com foto |
| Quinas vivas e fixação improvisada | Cantos arredondados, chanfros, suporte dedicado | Menos risco para quem se orienta pelo tato |
| Objeto difícil de replicar | Arquivos abertos (DXF/SVG/STL/3MF/STEP + código) | Prefeitura, escola ou Fab Lab fabrica com laser + impressora 3D |

**Nada disso foi medido ainda.** Sugestão de validação com o protótipo (registrar resultados reais):

| Teste | Como | Resultado |
|---|---|---|
| Leitura do QR | 3 celulares diferentes, a 30 cm e a 60 cm, luz natural e artificial | [PREENCHER] |
| Legibilidade | Integrantes leem o título a 1 m e 3 m (protótipo) — comparar com foto do original | [PREENCHER] |
| Identificação tátil | Integrante de olhos vendados identifica o sentido da seta e conta as celas Braille | [PREENCHER] |
| Fixação | Empurrão lateral leve: a placa gira no tubo? | [PREENCHER] |
| Opinião de usuários (opcional, com consentimento, anonimizado) | Conversa com pessoa com deficiência visual | [PREENCHER] |

## 2. ODS conectados

| ODS | Meta | Como o projeto contribui |
|---|---|---|
| **ODS 11 — Cidades e comunidades sustentáveis** | **11.2** — sistemas de transporte acessíveis, com atenção a pessoas com deficiência e idosos | Torna a informação do ponto de ônibus perceptível pelo tato e por quem tem baixa visão |
| ODS 11 | **11.7** — acesso universal a espaços públicos seguros, inclusivos e acessíveis | O QR conecta o ponto ao AcessaCidade: problemas de calçada/obstáculos no entorno viram denúncias rastreáveis |
| **ODS 10 — Redução das desigualdades** | **10.2** — inclusão social independentemente de deficiência ou idade | Mesma informação disponível para quem enxerga, quem tem baixa visão e quem é cego |
| ODS 9 (complementar) | 9.1 — infraestrutura de qualidade e acessível | Projeto aberto e fabricável localmente (Fab Labs, escolas técnicas) |

## 3. Conexão com o produto AcessaCidade

- O QR aponta para `<URL_PUBLICA>/#/registrar` — a tela de denúncia definida no contrato de integração
  (seção 7). O cidadão preenche tipo de obstáculo, local, impacto e foto; a triagem por visão computacional e o
  acompanhamento por protocolo acontecem no sistema web.
- **Dependência:** a URL pública só existe depois do deploy (disciplina 06). Até lá a placa tem apenas a área
  reservada — não gravamos QR apontando para endereço inventado. [PREENCHER: URL pública].
- Sugestão de evolução (não implementada): incluir no QR um identificador do ponto para preencher a referência
  automaticamente — exigiria mudar o contrato de integração primeiro.

## 4. Escala

Uma placa custa materiais de baixo custo (MDF/acrílico + ~70 g de filamento + parafusos) [PREENCHER: custo
real levantado]. Os arquivos são paramétricos: trocar texto, sentido da seta ou diâmetro do poste é editar
`cad/parametros.py` e rodar um script.

Este projeto **não é serviço oficial** de nenhuma prefeitura e **não declara conformidade** com a ABNT NBR 9050 ou
NBR 16537; uma instalação real exigiria validação técnica e autorização do órgão responsável.
