# Guia de campo — fotografar e medir o ponto de ônibus

Objetivo: produzir as **fotos no local** e as **medidas em croqui** exigidas no bloco Diagnóstico (2 pts).
Tempo estimado no local: 30 a 45 minutos, com 2 pessoas.

## 1. Levar

- Trena de 3 m ou 5 m (alturas, larguras); fita métrica de costura (perímetro do poste);
- Paquímetro (espessura da chapa, diâmetro de parafusos/abraçadeiras) — se não houver, use a trena e anote "±1 mm";
- Celular com câmera; **referência de escala**: régua de 30 cm, a própria trena aberta ou um cartão de 85,6 × 54 mm;
- Folha impressa `docs/imagens/croqui_original_A_PREENCHER.svg` (ou caderno) e caneta;
- Colete ou roupa clara se for perto de via; garrafa de água.

## 2. Segurança e ética

- Fique **na calçada**; nunca na faixa de rolamento. Não suba no abrigo, banco ou poste. Não use escada.
- Medidas altas (acima de ~2 m): encoste a trena no poste a partir do piso e leia com o celular em zoom, ou
  estime pela foto com referência de escala — anote "estimada por foto".
- **Não fotografe pessoas** (nem rostos, nem placas de veículos de forma identificável). Espere o ponto
  esvaziar ou enquadre só o objeto. Se alguém aparecer, desfoque antes de publicar.
- Não bloqueie a passagem de pedestres, principalmente cadeirantes. Não interfira no embarque.
- Não remova, cole nem altere nada no mobiliário público.
- Não registre endereço residencial; use referência pública (nome da via + ponto de referência).

## 3. Fotos (mínimo 8)

| # | Foto | Como | Por quê |
|---|---|---|---|
| 1 | Contexto | 5–8 m de distância, mostrando calçada, poste, placa e abrigo | Mostra o local |
| 2 | Frontal da placa | Perpendicular, celular na altura possível, **sem flash** | Contraste real |
| 3 | Frontal com escala | Mesma foto com trena/régua encostada na placa ou no poste | Permite medir pela foto |
| 4 | Altura de instalação | Trena do piso até a borda inferior da placa, foto de lado | Medida C |
| 5 | Fixação | Close das abraçadeiras/parafusos, de lado | Falha F5 e medida H |
| 6 | Superfície | Close inclinado (luz rasante) mostrando ausência de relevo/Braille | Falha F3 |
| 7 | Ponto de vista do usuário | Câmera a ~1,10 m (altura dos olhos de pessoa sentada em cadeira de rodas) | Falha F1 |
| 8 | Piso no entorno | Calçada, piso tátil (ou ausência), obstáculos | Falhas F6 e ligação com o app |
| 9 | (opcional) Noite | Mesmo enquadramento da foto 2 | Contraste com iluminação pública |

Nomeie os arquivos: `local_01_contexto.jpg`, `local_02_frontal.jpg` … e guarde em
`07-Project-Based-Maker-Lab/docs/fotos/` (criar a pasta) ou em uma pasta compartilhada [PREENCHER: link].
Antes de publicar, confira se nenhuma foto tem pessoas identificáveis.

## 4. Medidas (tabela para preencher)

Mesmas letras do croqui `docs/imagens/croqui_original_A_PREENCHER.svg`.

| Letra | Medida | Instrumento | Valor (mm) | Medido ou estimado por foto? |
|---|---|---|---|---|
| A | Largura da placa | trena | [PREENCHER] | |
| B | Altura da placa | trena | [PREENCHER] | |
| C | Piso → borda inferior da placa | trena | [PREENCHER] | |
| D | Piso → borda superior da placa | trena | [PREENCHER] | |
| E | Diâmetro do poste (perímetro ÷ π) | fita métrica | [PREENCHER] | |
| F | Altura das letras maiúsculas | trena/paquímetro | [PREENCHER] | |
| G | Espessura da chapa | paquímetro | [PREENCHER] | |
| H | Afastamento placa ↔ poste (projeção) | trena | [PREENCHER] | |
| I | Largura livre da calçada no ponto | trena | [PREENCHER] | |
| J | Distância poste ↔ meio-fio | trena | [PREENCHER] | |
| K | Altura do assento/abrigo (se houver) | trena | [PREENCHER] | |
| L | Distância até o piso tátil (se houver) | trena | [PREENCHER] | |

Dica: meça duas vezes cada item e anote a média. Diâmetro do poste: meça o perímetro com a fita métrica e
divida por 3,1416.

## 5. Depois da visita

1. Passe as medidas para `cad/parametros.py` (bloco "OBJETO ORIGINAL"):
   `ORIGINAL_PLACA_LARGURA` = A, `ORIGINAL_PLACA_ALTURA` = B, `ORIGINAL_ALTURA_BORDA_INFERIOR` = C,
   `ORIGINAL_POSTE_DIAMETRO` = E, `ORIGINAL_TEXTO_ALTURA` = F, `ORIGINAL_PLACA_ESPESSURA` = G,
   `ORIGINAL_AFASTAMENTO_PLACA_POSTE` = H, `ORIGINAL_TEXTO` = texto real; e mude
   `ORIGINAL_MEDIDO_EM_CAMPO = True`.
2. Rode `.\.venv\Scripts\python.exe 07-Project-Based-Maker-Lab\cad\gerar_todos.py` e os testes.
3. Atualize `DIAGNOSTICO_OBJETO_ORIGINAL.md` (coluna "Resultado observado") e `CROQUI_MEDIDAS.md`.
