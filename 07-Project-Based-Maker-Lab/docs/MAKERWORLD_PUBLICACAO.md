# Publicação no MakerWorld (obrigatória — 1,5 pt)

> **Status:** NÃO publicado. Este arquivo é o rascunho pronto para copiar. Link final:
> [PREENCHER: link do modelo no MakerWorld].

## 1. Título

- PT: **Placa acessível para ponto de ônibus — relevo, Braille e QR para reportar problemas (AcessaCidade)**
- EN (se o site pedir em inglês): **Accessible bus stop sign — tactile arrow, Braille and QR to report accessibility issues**

## 2. Descrição (PT)

> Protótipo de placa de ponto de ônibus pensada para pessoas cegas, com baixa visão, idosos e cadeirantes.
> - Placa principal em **corte a laser** (MDF/acrílico 3 mm, 200 × 150 mm — escala 1:3 de uma placa de 600 × 450 mm), texto em alto contraste e área para QR Code.
> - **Módulo tátil impresso em 3D (escala 1:1)**: letras "PONTO" em relevo, seta direcional em relevo de 1,5 mm e "PONTO" em Braille.
> - **Suporte impresso** que prende a placa a um tubo de 25 mm com abraçadeiras de nylon.
> - O QR leva à tela de registro do AcessaCidade, um projeto acadêmico (FIAP Global Solution 2026) para reportar problemas de acessibilidade em calçadas e espaços públicos.
>
> Impressão: módulo tátil com camada 0,12 mm, sem suporte; suporte em PETG, camada 0,2 mm. Arquivos de laser em SVG/DXF com camadas por cor (vermelho = corte, azul = vetor, preto = raster).
> Dimensões de Braille e relevo seguem valores usuais de referência — **verifique a ABNT NBR 9050 antes de qualquer instalação real**. Projeto acadêmico, não oficial.
> Peça de terceiros utilizada: [PREENCHER: nome da peça] por [PREENCHER: autor] — [PREENCHER: link], licença [PREENCHER].
> Código paramétrico (CadQuery) e documentação: [PREENCHER: link do repositório].

## 3. Description (EN)

> Accessible bus stop sign prototype for blind and low-vision people, elderly and wheelchair users. Laser-cut main
> plate (3 mm, 200 × 150 mm, 1:3 scale) with high-contrast text and a reserved QR area; 3D-printed tactile module
> (1:1 scale) with raised letters, a 1.5 mm raised arrow and Braille "PONTO" (Portuguese for "stop"); 3D-printed bracket
> for a 25 mm tube. Braille/relief dimensions follow common reference values — check local accessibility standards
> before any real installation. Academic project (FIAP Global Solution 2026), not an official sign.
> Third-party part: [PREENCHER] by [PREENCHER] — [PREENCHER: link], license [PREENCHER].

## 4. Tags

`acessibilidade` `accessibility` `braille` `tactile` `sinalização` `bus stop` `ponto de ônibus` `laser cut`
`QR code` `ODS 11` `SDG 11` `inclusão` `citizentech` `fablab`

Categoria sugerida: *Household / Other* ou *Education* (escolha a mais próxima disponível no site).

## 5. Arquivos a subir

| Arquivo | Observação |
|---|---|
| `3d-print/modulo_tatil.3mf` (e `.stl`) | Configurar perfil de impressão (camada 0,12) se o site pedir "print profile" |
| `3d-print/suporte_tubo.3mf` (e `.stl`) | |
| `laser-cut/placa_principal_laser.svg` e `.dxf` | MakerWorld aceita anexos; se não aceitar SVG/DXF, coloque em um .zip ou link para o repositório |
| `laser-cut/placa_principal_laser_com_qr.svg` | **somente** depois de gerado com a URL pública real |
| `cad/redesign_montagem.step` | Opcional (para quem quer editar) |

## 6. Fotos necessárias (mínimo 4; a 1ª é a capa)

1. Protótipo montado no tubo, de frente, fundo neutro (capa).
2. Close do módulo tátil com luz rasante (relevo e Braille visíveis).
3. Mão tocando o Braille/seta.
4. Celular lendo o QR gravado e abrindo a tela de registro (sem dados pessoais na tela).
5. Peças soltas: placa cortada + módulo + suporte + parafusos (vista "explodida").
6. Antes × depois: foto do ponto real (sem pessoas) ao lado do protótipo.
Use **apenas fotos reais** do protótipo. As renderizações de `docs/imagens/` podem entrar como imagens
adicionais, identificadas como "renderização do modelo".

## 7. Licença sugerida

**CC BY-SA 4.0** (Creative Commons — Atribuição-CompartilhaIgual) — permite que prefeituras e Fab Labs
reproduzam e adaptem, mantendo o crédito e a mesma licença. Atenção: se a peça de terceiros tiver licença
"NonCommercial" ou "NoDerivatives", respeite-a (ver `BONUS_PECA_TERCEIROS.md`) — a licença do conjunto não pode
contrariar a da peça integrada.

## 8. Crédito da peça de terceiros (bônus)

| Campo | Valor |
|---|---|
| Nome da peça | [PREENCHER] |
| Autor(a) | [PREENCHER] |
| Link original | [PREENCHER] |
| Licença | [PREENCHER] |
| Função no projeto | [PREENCHER: ex.: abraçadeira/clip que prende o suporte ao tubo de 25 mm] |
| Modificações feitas | [PREENCHER: nenhuma / escala / furos] |

No MakerWorld use também o recurso de **Remix/"Based on"** (se disponível) apontando para a peça original.

## 9. Passo a passo de publicação

1. Acesse https://makerworld.com e entre (conta Bambu Lab).
2. **Upload** (botão no topo) → *Upload Model*.
3. Arraste os arquivos da seção 5; aguarde o processamento.
4. Preencha título, descrição, tags, categoria e licença (seções 1–4 e 7).
5. Envie as fotos (seção 6) — a primeira vira capa.
6. Em "Remix/Original" informe a peça de terceiros (se usada) e cole o crédito também na descrição.
7. **Publish**. Abra o link em uma janela anônima para conferir se está público.
8. Copie o link para `RELATORIO_ENTREGA_MAKER.md` e para o README.
