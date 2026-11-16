# Roteiro do vídeo — Pitch Visão Computacional (até 5 min)

Entregável oficial: *"Vídeo (até 5 min) com demo do projeto desenvolvido — link público com a
participação de todos integrantes"*. Avaliação da disciplina: 3 pontos documentação, 3 pontos vídeo,
8 pontos automação — por isso a demo mostra o processamento **automático** na URL pública, não slides.

- Duração alvo: **4:40** (folga de 20 s para não passar de 5:00).
- Todos os integrantes aparecem falando (câmera ou voz identificada na tela). Equipe de até 5 pessoas:
  se forem menos, redistribua os blocos; se forem 5, ninguém fica sem fala.
- Ritmo de fala: ~130 palavras por minuto. Textos abaixo já cabem no tempo.
- Somente dados fictícios ou fotos reais **autorizadas**, sem rostos nem placas legíveis.

## Blocos

| Tempo | Bloco | Quem fala | Tela a gravar |
|---|---|---|---|
| 0:00–0:30 | 1. Problema e cidadão | [PREENCHER: Integrante 1] | Rosto + foto de calçada com buraco (real e autorizada, ou sintética identificada como tal) |
| 0:30–1:00 | 2. O que a visão faz no AcessaCidade | [PREENCHER: Integrante 2] | Diagrama do fluxo (`docs/DOCUMENTACAO_TECNICA_TRANSFORMACOES.md`, seção 1) |
| 1:00–2:20 | 3. Demo ponta a ponta na URL pública | [PREENCHER: Integrante 3] | Navegador em [PREENCHER: URL_MVP]: `#/analise` e `#/registrar` → `#/denuncia/{protocolo}` |
| 2:20–3:20 | 4. Transformações intermediárias | [PREENCHER: Integrante 4] | Painel `results/sintetica_buraco_01/painel_etapas.jpg` e etapas na tela de detalhe |
| 3:20–4:10 | 5. Dados extraídos e comparação manual | [PREENCHER: Integrante 5] | `results/dados_extraidos.csv` aberto no Excel + `results/RELATORIO_COMPARACAO.md` |
| 4:10–4:40 | 6. Limites, revisão humana e encerramento | [PREENCHER: Integrante 1 ou todos] | Painel de um falso positivo (`sintetica_tampa_bueiro_01`) + tela final com links |

## Falas sugeridas (ajuste com as palavras da equipe)

**1. Problema e cidadão (0:00–0:30) — [PREENCHER: Integrante 1]**
"Para quem usa cadeira de rodas, anda com bengala ou tem mais idade, um buraco na calçada é uma
barreira e um risco de queda. O AcessaCidade deixa o cidadão denunciar esses problemas com uma foto.
Mas alguém precisa olhar cada foto. É aí que entra a visão computacional."

**2. O que a visão faz (0:30–1:00) — [PREENCHER: Integrante 2]**
"Cada foto enviada passa automaticamente por um fluxo de OpenCV clássico, sem rede neural: primeiro
protegemos a privacidade, removendo a localização da foto e borrando rostos. Depois transformamos a
imagem em sete etapas e extraímos medidas. No fim, uma regra explicável diz se há possível buraco,
nenhum indício ou se a análise é inconclusiva — sempre com revisão humana."

**3. Demo ponta a ponta (1:00–2:20) — [PREENCHER: Integrante 3]**
Ações na tela (gravar sem cortes, na URL pública):
1. Abrir [PREENCHER: URL_MVP]/#/analise, enviar `sintetica_buraco_01.jpg` (ou foto real autorizada).
2. Mostrar o resultado: rótulo, pontuação (dizer "não é probabilidade"), explicações e as 7 etapas.
3. Ir em `#/registrar`, preencher com dados fictícios (Cidade Exemplo), anexar a foto, enviar.
4. Mostrar o protocolo gerado e abrir `#/denuncia/{protocolo}`: status "Aguardando revisão" e etapas salvas.
5. (Opcional, 10 s) Enviar uma foto escura (`sintetica_escura_01.jpg`) → "Análise inconclusiva".
Fala: "Tudo isso aconteceu sozinho, em segundos, assim que a foto chegou. A denúncia já entra na fila
de revisão humana com as imagens e as medidas."

**4. Transformações (2:20–3:20) — [PREENCHER: Integrante 4]**
"Na etapa cinza ficamos só com o brilho. A filtrada aplica uma convolução gaussiana cinco por cinco
para tirar ruído. O contraste usa CLAHE, que realça detalhes por regiões. Em bordas, o detector de
Canny marca transições fortes. A máscara separa regiões bem mais escuras que o piso, com limiar de
Otsu e um limiar robusto, e a morfologia limpa os pontos soltos. Por fim, os contornos recebem caixa,
rótulo e medidas."

**5. Dados e comparação (3:20–4:10) — [PREENCHER: Integrante 5]**
"De cada imagem extraímos brilho, contraste, nitidez, área, solidez, circularidade, contraste com o
entorno, densidade de bordas e a caixa delimitadora — tudo em CSV e JSON no repositório. Comparamos a
triagem com rótulos manuais em 25 imagens sintéticas: 20 concordaram. Atenção: é uma base sintética,
feita por nós; isso verifica o fluxo, mas não mede desempenho no mundo real."
[PREENCHER: se houver base real rotulada, trocar por: número de fotos reais e resultado da comparação]

**6. Limites e encerramento (4:10–4:40) — [PREENCHER: Integrante 1 ou todos]**
"A regra erra: aqui, uma tampa de bueiro virou possível buraco. Sombras, manchas e poças também
confundem. Por isso a triagem é só apoio: nenhuma denúncia é descartada pela máquina e toda foto passa
por uma pessoa. Os links do MVP, do repositório e da documentação estão na descrição. Obrigado!"
(Todos aparecem juntos ou em sequência rápida, dizendo o próprio nome.)

## Checklist de gravação

- [ ] Ensaiar com cronômetro; versão final ≤ 5:00 (meta 4:40).
- [ ] Gravar a demo na **URL pública** (não em localhost) — a URL deve aparecer na barra do navegador.
- [ ] Ampliar o zoom do navegador (125–150%) para as etapas ficarem legíveis.
- [ ] Nenhuma chave, token, e-mail pessoal ou aba privada visível.
- [ ] Legenda ou nome na tela de cada integrante quando falar.
- [ ] Publicar no YouTube como **público** ou **não listado**; conferir o link em aba anônima.
- [ ] Colar o link em `docs/links_entrega.yaml` (`url_video`) e gerar o PDF.

Ferramentas sugeridas: OBS Studio (gravação de tela + webcam) ou Xbox Game Bar (Win + G) para tela;
editor de vídeo à escolha (ex.: Clipchamp, que vem no Windows 11). Dicas gerais de áudio e gravação:
`03-Business-Intelligence-Startup/pitch/ROTEIRO_DE_GRAVACAO.md`.
