# 07 — Project-Based Maker Lab · "CitizenTech: Cidade remodelada"

**Componente físico do AcessaCidade:** placa de sinalização acessível para ponto de ônibus, com texto em
alto contraste, módulo tátil (seta e letras em relevo + Braille "PONTO") e **área reservada para o QR Code**
que leva o cidadão à tela de registro do AcessaCidade (`#/registrar`) para reportar problemas de
acessibilidade naquele ponto.

> **Situação honesta deste material:** tudo aqui foi **modelado e gerado por script**. Nada foi fabricado,
> medido em campo ou publicado ainda. As dimensões do **objeto original** são **ESTIMADAS** ("a substituir
> após medição em campo"). As ações que dependem da equipe estão em
> [`PENDENCIAS_E_ACOES_MANUAIS.txt`](PENDENCIAS_E_ACOES_MANUAIS.txt).

## Peças

| Peça | Processo | Material sugerido | Dimensões (mm) | Escala |
|---|---|---|---|---|
| Placa principal | Corte + gravação a laser | MDF 3 mm pintado de preto fosco **ou** acrílico/laminado bicolor 3 mm | 200 × 150 × 3, cantos R10, 8 furos | 1:3 (real sugerido 600 × 450) |
| Módulo tátil | Impressão 3D (FDM) | PLA/PETG amarelo | 76 × 70 × 5,5 (base 4 + relevo 1,5) | **1:1** (o tato não lê em escala) |
| Suporte/abraçadeira para tubo | Impressão 3D (FDM) | PETG (ou PLA no protótipo) | 36 × 88 × 24,9, berço para tubo Ø25 | 1:3 (tubo de PVC 25 mm faz o papel do poste) |
| Peça de terceiros (bônus, opcional) | Download MakerWorld | — | [PREENCHER] | — |

Detalhes do Braille: ponto Ø1,5 mm × 0,7 mm de altura, 2,5 mm entre pontos, 6 mm entre celas;
"PONTO" = P(1234) O(135) N(1345) T(2345) O(135). Seta em relevo de 1,5 mm (requisito ≥ 1 mm). Letras
"PONTO" em relevo de 1 mm. **Valores usuais de referência — verificar na ABNT NBR 9050; o projeto não declara
conformidade com norma.**

## Arquivos

| Caminho | O que é |
|---|---|
| `cad/parametros.py` | **Todas** as dimensões (mm), comentadas; bloco "OBJETO ORIGINAL" com valores ESTIMADOS; `verificar_coerencia()` |
| `cad/geometria_2d.py` | Layout 2D da placa (textos convertidos em contornos com fonte DejaVu Sans Bold), escritores DXF/SVG |
| `cad/modelo_original.py` | CAD do original simplificado (placa genérica, alta, sem relevo/Braille/QR) |
| `cad/modelo_redesign.py` | CAD do redesign: placa, módulo tátil, suporte e montagem |
| `cad/cq_util.py`, `cad/imagens.py` | Utilitários CadQuery e geração das imagens/croquis |
| `cad/gerar_todos.py` | Gera tudo abaixo (≈ 2–4 min) e `cad/relatorio_geracao.txt` |
| `cad/*.step` | STEP do original (placa e montagem, ESTIMADOS) e do redesign (3 peças + montagem) |
| `laser-cut/placa_principal_laser.dxf` / `.svg` | Arquivo do laser (camadas CORTE, GRAVACAO_VETORIAL, GRAVACAO_RASTER, AREA_QR, TEXTO_REFERENCIA) |
| `laser-cut/gerar_qrcode.py` | Gera o QR **somente** com a URL pública real (`--url`) e a placa já com o QR |
| `3d-print/modulo_tatil.stl` / `.3mf` | Módulo tátil já orientado (verso na mesa, relevo para cima) |
| `3d-print/suporte_tubo.stl` / `.3mf` | Suporte já orientado (face da flange na mesa) |
| `docs/imagens/` | Comparação lado a lado (3D e vistas), elevação em escala real, prévia do laser, Braille, croquis SVG |
| `docs/*.md` | Diagnóstico, guia de fotos/medição, croqui, Onshape, comparação, fabricação, impacto/ODS, MakerWorld, bônus, vídeo, fotos, relatório |
| `tests/test_maker_*.py` | Testes automatizados (pytest) |

## Como regenerar

```powershell
cd c:\Users\masak\Desktop\GS7-4ESPR
.\.venv\Scripts\python.exe 07-Project-Based-Maker-Lab\cad\gerar_todos.py           # tudo (~2-4 min)
.\.venv\Scripts\python.exe 07-Project-Based-Maker-Lab\cad\gerar_todos.py --so-laser # só DXF/SVG
.\.venv\Scripts\python.exe 07-Project-Based-Maker-Lab\laser-cut\gerar_qrcode.py --url https://<URL_PUBLICA_REAL>
.\.venv\Scripts\python.exe -m pytest 07-Project-Based-Maker-Lab\tests
```

## Convenção de cores do laser

| Camada (DXF) / grupo (SVG) | Cor | Operação |
|---|---|---|
| `GRAVACAO_RASTER` | preto `#000000` (ACI 7) | Gravação de preenchimento — textos, pictograma, QR. **1º** |
| `GRAVACAO_VETORIAL` | azul `#0000FF` (ACI 5) | Gravação de linha — moldura e marca de posição do módulo. **2º** |
| `CORTE` | vermelho `#FF0000` (ACI 1) | Corte passante — contorno e furos. **Por último** |
| `AREA_QR` | cinza tracejado | Guia da área do QR — **não enviar ao laser** |
| `TEXTO_REFERENCIA` | verde | Textos editáveis/notas — **não enviar ao laser** |

Os textos já estão **convertidos em curvas** (polilinhas fechadas) na camada `GRAVACAO_RASTER`; a cópia
`TEXT` editável fica só em `TEXTO_REFERENCIA`. Ver [`docs/FABRICACAO.md`](docs/FABRICACAO.md).

## Integração com o restante do AcessaCidade

O QR leva a `<URL_PUBLICA>/#/registrar` (rota definida em `docs/CONTRATOS_DE_INTEGRACAO.md`, seção 7). A URL
pública depende do deploy da disciplina 06 (Secure DevOps & Cloud) — **[PREENCHER: URL pública do AcessaCidade]**.
