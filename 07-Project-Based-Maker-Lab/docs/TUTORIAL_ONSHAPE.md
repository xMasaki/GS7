# Tutorial — usar os modelos no Onshape

O CAD oficial deste projeto é **paramétrico em código** (CadQuery, `cad/*.py`). O Onshape serve para:
(1) apresentar os modelos lado a lado no navegador, (2) gerar desenhos (Drawings) e (3) recriar
nativamente as peças caso a professora exija modelagem em software de CAD. Conta gratuita: onshape.com
(plano Free/Education — documentos do plano Free são públicos).

## 1. Criar o documento e importar os STEP

1. Entre em https://cad.onshape.com → **Create → Document** → nome "AcessaCidade — Placa acessível".
2. Clique no **+** (canto inferior esquerdo) → **Import…** → selecione, de `07-Project-Based-Maker-Lab/cad/`:
   `original_montagem_ESTIMADO.step`, `redesign_montagem.step` e as peças `redesign_*.step`.
3. Na janela de importação marque **"Import as a single part studio"** para as peças individuais; para as
   montagens mantenha o padrão (cria Assembly + Part Studio).
4. Unidades: os arquivos estão em **milímetros**. Se o Onshape perguntar, escolha *Millimeter*.
5. Resultado esperado: abas "original_montagem_ESTIMADO", "redesign_montagem" e uma aba por peça.
6. Como saber se deu certo: selecione a placa redesign e use **Measure** (régua no canto inferior direito):
   200 × 150 × 3 mm.

## 2. Importar o DXF da placa (sketch)

1. Abra um **Part Studio** novo → **Sketch** no plano *Front*.
2. Na barra do sketch: **Insert DXF or DWG** → enviar `laser-cut/placa_principal_laser.dxf` → unidade **mm**.
3. As camadas viram geometria de sketch. Para modelar só o corte, apague as entidades das camadas
   `TEXTO_REFERENCIA` e `AREA_QR` (ou importe e use apenas o contorno).

## 3. Variáveis (para ajustar como no `parametros.py`)

1. No Part Studio: **Variable** (ícone `#x`) → crie `#placa_l = 200 mm`, `#placa_a = 150 mm`,
   `#placa_e = 3 mm`, `#raio = 10 mm`, `#furo_canto = 5 mm`, `#dist_borda = 12 mm`.
2. Use `#placa_l` etc. nas cotas do sketch (digite `#placa_l` no campo da cota).
3. Alterar a variável atualiza a peça — equivalente a editar `parametros.py` e rodar `gerar_todos.py`.

## 4. Recriar nativamente (se a modelagem no Onshape for exigida)

**Placa principal (laser)**
1. Sketch no plano *Front*: **Center point rectangle** `#placa_l × #placa_a`; **Fillet** de sketch `#raio` nos 4 cantos.
2. Círculos: 4 × Ø5 a 12 mm das bordas; 2 × Ø4,4 em (0, +34) e (0, −34); 2 × Ø3,4 em (27, −26) e (83, −26)
   (centro do módulo em (55, −2) + furos-guia em (±28, −24)).
3. **Extrude** 3 mm. Gravações: sketch na face frontal com o texto (**Text** do sketch, fonte sans bold)
   e **Extrude → Remove** 0,3 mm (só para visualização; no laser é gravação).

**Módulo tátil (3D)**
1. Sketch retângulo 76 × 70, fillet 6 → Extrude 4 mm → **Chamfer** 0,8 nas arestas de cima.
2. Sketch na face superior: seta (polígono — haste 7 mm, ponta 22 × 16 mm, comprimento 50 mm) →
   Extrude **Add** 1,5 mm. Texto "PONTO" 9 mm → Extrude Add 1 mm.
3. Braille: sketch de 18 pontos Ø1,5 (ver `docs/imagens/detalhe_braille_seta.png` para posições:
   2,5 mm entre pontos, 6 mm entre celas, linha em y = −20 mm) → Extrude Add 0,7 mm → **Fillet** 0,5 no topo
   (aproxima a calota esférica do CadQuery).
4. Furos-guia Ø2,5 × 3 mm de profundidade pelo verso em (±28, −24).

**Suporte para tubo (3D)**
1. Flange 36 × 88 × 5 (fillet 4) → bloco central 2×(12,9+4) × 44 com profundidade até o eixo do tubo
   (5 + 7 + 12,9 = 24,9 mm) → **Extrude Remove** de um cilindro Ø25,8 (berço) → túneis 5,5 × 2,2 mm para
   abraçadeira de nylon em y = ±12 → furos M4 em (0, ±34) com alojamento hexagonal para porca M4 (7 mm entre faces + 0,3 mm de folga, 3,4 mm de profundidade).

## 5. Exportar

- **DXF/SVG de face ou sketch:** clique com o botão direito na face frontal da placa (ou no sketch) →
  **Export as DXF/DWG** → versão 2013, unidade mm. (No Drawing: botão direito na aba → **Export** → DXF/SVG.)
- **STL/3MF:** botão direito na peça (lista de peças) → **Export** → formato **STL** (Binary, mm, resolução
  *Fine*) ou **3MF**.
- **STEP:** botão direito na aba → **Export** → STEP.

## 6. Drawing para croqui

1. Botão direito na aba da peça → **Create drawing** → template ISO A4 Landscape, unidade mm.
2. Inserir vista frontal e lateral; **Dimension** para cotar largura, altura, furos, área do QR.
3. Exportar PDF (botão direito na aba do Drawing → Export → PDF) e anexar ao relatório.

## 7. Compartilhar o link

**Share** → *Make public* (ou "Anyone with the link can view") → copiar o link para
`RELATORIO_ENTREGA_MAKER.md`: [PREENCHER: link do documento Onshape].
