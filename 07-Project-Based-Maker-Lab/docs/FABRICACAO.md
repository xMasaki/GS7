# Fabricação — corte a laser + impressão 3D + montagem

> **Status:** arquivos prontos para fabricação; **nada foi fabricado ainda**. Os parâmetros abaixo são
> **pontos de partida** e precisam ser calibrados na máquina do laboratório com uma peça de teste.
> Registre os valores realmente usados na tabela da seção 6.

## 1. Lista de materiais (protótipo)

| Qtd | Item | Uso |
|---|---|---|
| 1 | Chapa de MDF 3 mm (≥ 220 × 170 mm) **ou** acrílico 3 mm preto / laminado bicolor (preto com núcleo branco) | Placa principal |
| — | Tinta spray preto fosco (só se for MDF cru) | Fundo de alto contraste |
| ~25 g | Filamento PLA ou PETG **amarelo** | Módulo tátil |
| ~45 g | Filamento PETG (ou PLA) | Suporte para tubo |
| 2 | Parafuso M4 × 16 cabeça panela + 2 porcas M4 + 2 arruelas | Placa ↔ suporte |
| 2 | Parafuso M3 × 6 (ou autoatarraxante 2,9 × 6,5) | Placa ↔ módulo tátil (pelo verso) |
| 2 | Abraçadeira de nylon 4,8 mm (comprimento ≥ 150 mm) — ou a peça de terceiros do bônus | Suporte ↔ tubo |
| 1 | Tubo de PVC soldável 25 mm, ~300–400 mm | "Poste" em escala 1:3 para demonstração |

Massas de filamento são estimativas a partir do volume das malhas (módulo 21,9 cm³ e suporte 32,7 cm³ de
volume sólido; com preenchimento parcial o consumo real será menor) — confira no fatiador.

## 2. Corte a laser — placa principal

Arquivos: `laser-cut/placa_principal_laser.svg` (LightBurn/Inkscape) ou `.dxf` (RDWorks/LaserCAD/LightBurn).
Com o QR: `placa_principal_laser_com_qr.svg/.dxf` (gerado por `gerar_qrcode.py --url <URL real>`).

**Camadas e ordem de execução**

| Ordem | Camada / cor | Modo | Partida — MDF 3 mm (laser CO2 ~40–60 W) | Partida — acrílico 3 mm |
|---|---|---|---|---|
| 1 | `GRAVACAO_RASTER` (preto) | Fill/Scan, intervalo 0,1 mm | velocidade alta, potência baixa (ex.: 300 mm/s, 15–20%) | 300 mm/s, 12–18% |
| 2 | `GRAVACAO_VETORIAL` (azul) | Line | 100 mm/s, 10–15% | 100 mm/s, 8–12% |
| 3 | `CORTE` (vermelho) | Line | 10–15 mm/s, 60–70%, 1 passada | 8–12 mm/s, 60–70% |
| — | `AREA_QR` (cinza) e `TEXTO_REFERENCIA` (verde) | **desligar saída** | — | — |

Os percentuais variam muito entre máquinas — **são só ponto de partida**. Faça antes um quadrado de teste
20 × 20 mm com gravação e corte no mesmo material.

**Kerf:** estimado em 0,15 mm (`KERF_LASER_ESTIMADO`). Para os furos de fixação não é preciso compensar
(têm folga). Meça o kerf real cortando um quadrado de 20 mm e medindo com paquímetro: kerf = 20 − medida.

**Textos:** já estão convertidos em curvas (polilinhas fechadas) na camada `GRAVACAO_RASTER`; a fonte
não precisa estar instalada. A camada `TEXTO_REFERENCIA` traz os mesmos textos como `TEXT` editável —
não grave essa camada. Se quiser trocar um texto: edite em `cad/parametros.py` e rode `gerar_todos.py`;
ou no LightBurn/Inkscape digite o texto novo e use **Converter em curvas** (LightBurn: *Arrange → Convert to Path*;
Inkscape: *Caminho → Objeto em caminho*; RDWorks: importe já convertido).

**Importação:**
- LightBurn: *File → Import* → SVG (unidades mm são lidas do arquivo) → confira largura 200 mm na barra de
  dimensões → cada cor vira uma camada → configure conforme a tabela.
- Inkscape: abra o SVG; documento em mm 200 × 150; as camadas aparecem em *Camada → Camadas e objetos*.
- RDWorks: *File → Import* → DXF → confirme a escala 1:1 em mm.

**Contraste:** com MDF pintado de preto, a gravação expõe a madeira clara (contraste moderado; passar verniz
fosco depois). Para contraste máximo use laminado bicolor preto/branco para laser ou acrílico preto
(gravação fica branca-fosca). **Verificar** o contraste real com foto lado a lado do original.

## 3. Impressão 3D

Arquivos: `3d-print/modulo_tatil.stl/.3mf` e `3d-print/suporte_tubo.stl/.3mf` — **já orientados** (não gire).

| Parâmetro | Módulo tátil | Suporte para tubo |
|---|---|---|
| Material | PLA ou PETG amarelo | PETG (externo) ou PLA (protótipo) |
| Bico | 0,4 mm | 0,4 mm |
| Altura de camada | **0,12 mm** (pontos Braille de 0,7 mm ≈ 6 camadas) | 0,2 mm |
| Perímetros | 3 | 4 |
| Topo/fundo | 5 / 4 camadas | 5 / 5 |
| Preenchimento | 20% (giroide) | 40% (giroide) |
| Orientação | verso liso na mesa, relevo para cima | face da flange na mesa, berço para cima |
| Suporte | **não precisa** | em princípio não precisa (berço aberto para cima); confira na pré-visualização do fatiador as pontes dos túneis das abraçadeiras (vão de ~5,5 mm) e o teto dos alojamentos das porcas |
| Adesão | saia (skirt) | brim de 3 mm se houver empenamento (PETG) |

Verificações de projeto (testadas automaticamente em `tests/`): STL estanque, peça cabe em 200 × 200 × 200 mm,
paredes ≥ 1,2 mm (3 linhas do bico de 0,4), relevo da seta ≥ 1 mm. O Braille impresso em FDM é uma
**aproximação de protótipo**: verifique se os pontos ficaram nítidos e não "colados"; se necessário
imprima com camada 0,08 mm ou em resina.

## 4. Montagem

1. Lixe levemente as bordas da placa e do módulo (lixa 400) — nada de rebarba onde a mão passa.
2. Encaixe as porcas M4 nos alojamentos hexagonais do suporte (se apertado, aqueça a porca com o ferro de solda
   por 2 s e empurre).
3. Posicione o módulo tátil sobre a marca gravada (azul) da placa e fixe pelo verso com 2 parafusos M3 × 6 nos
   furos-guia (o parafuso forma a rosca no plástico — não aperte demais).
4. Encoste o suporte no verso da placa, alinhando os furos Ø4,4, e aparafuse os 2 M4 × 16 com arruelas.
5. Encaixe o tubo de PVC 25 mm no berço e passe 2 abraçadeiras de nylon pelos túneis, apertando ao redor do tubo
   (ou use a peça de terceiros do bônus).
6. Teste: a placa não pode girar no tubo com um empurrão leve; nenhuma ponta de parafuso exposta na frente.

## 5. Segurança no laboratório

- Use o laser **somente** com autorização/treinamento do laboratório; nunca deixe o laser cortando sem
  supervisão; exaustão ligada; tampa fechada; extintor acessível.
- **Nunca** corte PVC, vinil ou policarbonato no laser (gases tóxicos/corrosivos). Acrílico (PMMA) e MDF são
  permitidos na maioria dos labs — confirme com o responsável.
- MDF gera fumaça e fuligem: espere a exaustão limpar antes de abrir a tampa.
- Impressora 3D: bico (~200–250 °C) e mesa quente; remova peças só com a mesa fria; espátula com a mão atrás.
- Use óculos de proteção ao cortar abraçadeiras/lixar; ferro de solda em suporte próprio.

## 6. Registro da fabricação (preencher com valores REAIS)

| Item | Valor usado |
|---|---|
| Laboratório / máquina laser | [PREENCHER] |
| Material e espessura medida | [PREENCHER] |
| Raster: velocidade / potência / intervalo | [PREENCHER] |
| Vetorial: velocidade / potência | [PREENCHER] |
| Corte: velocidade / potência / passadas | [PREENCHER] |
| Kerf medido | [PREENCHER] |
| Impressora 3D / fatiador | [PREENCHER] |
| Filamento (material/cor/marca) | [PREENCHER] |
| Tempo e massa — módulo tátil (fatiador) | [PREENCHER] |
| Tempo e massa — suporte (fatiador) | [PREENCHER] |
| Problemas e ajustes | [PREENCHER] |
| Fotos (link) | [PREENCHER] |
