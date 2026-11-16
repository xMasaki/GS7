"""Parâmetros do projeto Maker Lab — Placa de sinalização acessível para ponto de ônibus.

AcessaCidade · FIAP Global Solution 2026.2 · Disciplina 07 (Project-Based Maker Lab).

TODAS as dimensões estão em MILÍMETROS (mm), salvo indicação contrária.
Sistema de coordenadas dos modelos:
  * X = largura da placa (esquerda → direita, vista de frente)
  * Y = altura da placa (baixo → cima)
  * Z = espessura (face frontal da placa em Z = PLACA_ESPESSURA; face traseira em Z = 0)
  * Origem no CENTRO da placa. Os arquivos 2D (DXF/SVG) são transladados para que o canto
    inferior esquerdo da placa fique em (0, 0), convenção usual dos softwares de laser.

Como usar:
  1. Depois de ir ao ponto de ônibus e medir (docs/GUIA_FOTOGRAFAR_E_MEDIR.md), substitua os
     valores do bloco "OBJETO ORIGINAL" (todos marcados como ESTIMADOS).
  2. Ajuste o redesign se necessário (ex.: diâmetro do tubo de demonstração).
  3. Rode:  .venv\\Scripts\\python.exe 07-Project-Based-Maker-Lab\\cad\\gerar_todos.py
  4. Rode os testes: .venv\\Scripts\\python.exe -m pytest 07-Project-Based-Maker-Lab\\tests
     (a função verificar_coerencia() abaixo também é chamada pelo gerar_todos.py).

Normas de REFERÊNCIA a verificar (este projeto NÃO declara conformidade com nenhuma norma):
  * ABNT NBR 9050 (acessibilidade a edificações, mobiliário, espaços e equipamentos urbanos):
    contraste, alturas de instalação, dimensões do Braille, textos e pictogramas em relevo.
  * ABNT NBR 16537 (sinalização tátil no piso): integração com piso tátil de alerta/direcional
    que conduz ao ponto de ônibus.
"""

from __future__ import annotations

import math

# =====================================================================================
# 0. ESCALA
# =====================================================================================
# O protótipo da placa e do suporte é fabricado em escala reduzida (1:3) para caber na
# mesa do laser e da impressora de um laboratório típico. O MÓDULO TÁTIL (Braille, seta e
# letras em relevo) é SEMPRE em escala 1:1, porque o tato não "lê" em escala: o mesmo STL
# serve para o protótipo e para a versão em tamanho real.
ESCALA_PROTOTIPO = 1.0 / 3.0          # 1:3 (placa e suporte)
ESCALA_TEXTO = "1:3 (placa e suporte) · 1:1 (módulo tátil)"

# Limites de fabricação do laboratório (ajuste para as máquinas do seu Fab Lab)
MESA_LASER_X = 600.0                  # mm — área útil típica de laser CO2 de bancada (a confirmar no lab)
MESA_LASER_Y = 400.0
MESA_IMPRESSORA_X = 200.0             # mm — volume útil considerado para a impressora 3D (a confirmar)
MESA_IMPRESSORA_Y = 200.0
MESA_IMPRESSORA_Z = 200.0
BICO_FDM = 0.4                        # mm — diâmetro do bico da impressora FDM
ALTURA_CAMADA_FDM = 0.12              # mm — camada recomendada para o módulo tátil (pontos Braille)
ESPESSURA_MINIMA_PAREDE_FDM = 1.2     # mm — 3 perímetros de 0,4 mm
KERF_LASER_ESTIMADO = 0.15            # mm — largura de corte típica em acrílico/MDF 3 mm (CALIBRAR no lab)

# =====================================================================================
# 1. OBJETO ORIGINAL (placa genérica de ponto de ônibus) — VALORES ESTIMADOS
# =====================================================================================
# ATENÇÃO: todos os valores deste bloco são ESTIMATIVAS para modelagem inicial.
# "A SUBSTITUIR APÓS MEDIÇÃO EM CAMPO" (trena/paquímetro — ver docs/GUIA_FOTOGRAFAR_E_MEDIR.md).
# Escala: 1:1 (tamanho real estimado).
ORIGINAL_MEDIDO_EM_CAMPO = False      # mude para True SOMENTE depois de medir de verdade
ORIGINAL_PLACA_LARGURA = 450.0        # ESTIMADO — a substituir após medição em campo
ORIGINAL_PLACA_ALTURA = 300.0         # ESTIMADO — a substituir após medição em campo
ORIGINAL_PLACA_ESPESSURA = 2.0        # ESTIMADO (chapa metálica) — a substituir após medição
ORIGINAL_PLACA_RAIO_CANTO = 5.0       # ESTIMADO — a substituir após medição em campo
ORIGINAL_TEXTO = "ÔNIBUS"             # ESTIMADO — registrar o texto real visto no local
ORIGINAL_TEXTO_ALTURA = 40.0          # ESTIMADO — altura das letras maiúsculas
ORIGINAL_POSTE_DIAMETRO = 76.2        # ESTIMADO (tubo ~3") — a substituir após medição em campo
ORIGINAL_POSTE_ALTURA_MODELADA = 3000.0   # trecho de poste representado no modelo
ORIGINAL_ALTURA_BORDA_INFERIOR = 2200.0   # ESTIMADO — piso até a borda inferior da placa
ORIGINAL_FURO_DIAMETRO = 8.0          # ESTIMADO — furos da placa para as abraçadeiras
ORIGINAL_ABRACADEIRA_LARGURA = 25.0   # ESTIMADO — fita/abraçadeira metálica
ORIGINAL_ABRACADEIRA_ESPESSURA = 3.0  # ESTIMADO
ORIGINAL_AFASTAMENTO_PLACA_POSTE = 10.0   # ESTIMADO — folga entre o tubo e a placa
# Características qualitativas (HIPÓTESES a confirmar no local)
ORIGINAL_TEM_BRAILLE = False
ORIGINAL_TEM_RELEVO = False
ORIGINAL_TEM_QR = False
ORIGINAL_CONTRASTE = "baixo (hipótese: letras cinza-claro sobre fundo azul/cinza, desbotadas)"

# =====================================================================================
# 2. REDESIGN — PLACA PRINCIPAL (CORTE A LASER, escala 1:3)
# =====================================================================================
PLACA_LARGURA = 200.0                 # mm (real sugerido: 600 mm)
PLACA_ALTURA = 150.0                  # mm (real sugerido: 450 mm)
PLACA_ESPESSURA = 3.0                 # mm — acrílico ou MDF de 3 mm
PLACA_RAIO_CANTO = 10.0               # mm — cantos arredondados (sem quinas vivas)
PLACA_MATERIAL = "MDF 3 mm pintado de preto fosco OU acrílico/laminado bicolor 3 mm"
PLACA_BORDA_GRAVADA_MARGEM = 5.0      # mm — moldura gravada (vetorial) a 5 mm da borda
PLACA_BORDA_GRAVADA_RAIO = 6.0        # mm
PROFUNDIDADE_GRAVACAO_MODELO = 0.3    # mm — profundidade representada no CAD (visual)

# Furos de canto (fixação alternativa em parede/abrigo) — Ø5 mm para parafuso 4,5 mm / M4
FURO_CANTO_DIAMETRO = 5.0
FURO_CANTO_DIST_BORDA = 12.0          # do centro do furo até as bordas laterais e superior/inferior

# Furos do suporte (abraçadeira impressa em 3D, no verso) — parafuso M4 com folga
FURO_SUPORTE_DIAMETRO = 4.4
FURO_SUPORTE_DIST_Y = 34.0            # furos em (0, +34) e (0, -34) — eixo vertical central
PARAFUSO_SUPORTE = "M4 x 16 mm cabeça panela + porca M4 (embutida no suporte)"
CABECA_PARAFUSO_M4_DIAMETRO = 8.0     # mm — usado para checar folga em relação ao texto

# Furos do módulo tátil (parafusos M3 entram pelo verso da placa no furo-guia do módulo)
FURO_MODULO_DIAMETRO = 3.4
PARAFUSO_MODULO = "M3 x 6 mm (ou parafuso autoatarraxante 2,9 x 6,5 mm)"
CABECA_PARAFUSO_M3_DIAMETRO = 5.5

# Textos gravados (convertidos em contornos no DXF/SVG; fonte DejaVu Sans Bold, embutida no matplotlib)
TEXTO_TITULO = "PONTO DE ÔNIBUS"
TEXTO_TITULO_ALTURA_MAIUSCULA = 10.0  # mm (real 1:1 ≈ 30 mm)
TEXTO_TITULO_BASE_Y = 50.0            # linha de base, relativa ao centro da placa
PICTOGRAMA_ONIBUS_ALTURA = 14.0       # pictograma simplificado de ônibus à esquerda do título
PICTOGRAMA_ONIBUS_LARGURA = 12.0
PICTOGRAMA_ESPACO_TEXTO = 4.0
TEXTO_RODAPE_LINHAS = (
    "PROBLEMA DE ACESSIBILIDADE AQUI?",
    "APONTE A CÂMERA E REPORTE NO ACESSACIDADE",
)
TEXTO_RODAPE_ALTURA_MAIUSCULA = 3.6   # mm (real 1:1 ≈ 11 mm)
TEXTO_RODAPE_BASES_Y = (-45.0, -54.0)
TEXTO_QR_LEGENDA = "QR CODE"          # pequena legenda gravada sob a área do QR
TEXTO_QR_LEGENDA_ALTURA = 3.0

# Área reservada para o QR Code (gravação raster). O QR SÓ é gerado com a URL pública real,
# pelo script laser-cut/gerar_qrcode.py. Até lá a placa tem apenas a ÁREA reservada.
AREA_QR_LADO = 46.0                   # mm — inclui a zona de silêncio de 4 módulos (real 1:1 ≈ 138 mm)
AREA_QR_CENTRO = (-52.0, 0.0)         # mm, relativo ao centro da placa
QR_ZONA_SILENCIO_MODULOS = 4
QR_MODULO_MINIMO = 0.8                # mm — tamanho mínimo de módulo aceitável para gravação a laser
ROTA_REGISTRAR_APP = "#/registrar"    # rota da SPA AcessaCidade (contrato, seção 7)

# Posição do módulo tátil sobre a placa (centro do módulo, relativo ao centro da placa)
MODULO_CENTRO_NA_PLACA = (55.0, -2.0)

# =====================================================================================
# 3. REDESIGN — MÓDULO TÁTIL (IMPRESSÃO 3D, escala 1:1)
# =====================================================================================
MODULO_LARGURA = 76.0
MODULO_ALTURA = 70.0
MODULO_ESPESSURA_BASE = 4.0
MODULO_RAIO_CANTO = 6.0
MODULO_CHANFRO_SUPERIOR = 0.8         # quebra de quinas para não machucar a mão
MODULO_MATERIAL = "PLA ou PETG amarelo (alto contraste com o fundo escuro da placa)"

# Furos-guia cegos no verso do módulo (para os parafusos M3 que vêm pelo verso da placa)
MODULO_FURO_GUIA_DIAMETRO = 2.5       # mm — rosca formada pelo próprio parafuso no plástico
MODULO_FURO_GUIA_PROFUNDIDADE = 3.0   # mm — deixa 1 mm de "pele" na frente
MODULO_FURO_GUIA_POSICOES = ((-28.0, -24.0), (28.0, -24.0))   # relativo ao centro do módulo

# Letras em relevo "PONTO" (para quem não lê Braille: pessoas que perderam a visão tarde etc.)
MODULO_TEXTO_RELEVO = "PONTO"
MODULO_TEXTO_ALTURA_MAIUSCULA = 9.0   # mm
MODULO_TEXTO_BASE_Y = 19.0            # linha de base, relativa ao centro do módulo
MODULO_TEXTO_RELEVO_ALTURA = 1.0      # mm acima da base (VERIFICAR valor de referência na NBR 9050)

# Seta direcional em relevo (aponta para a área de embarque; sentido definido em campo)
SETA_SENTIDO = "direita"              # "direita" ou "esquerda" — definir no local
SETA_COMPRIMENTO = 50.0
SETA_LARGURA_HASTE = 7.0
SETA_LARGURA_PONTA = 22.0
SETA_COMPRIMENTO_PONTA = 16.0
SETA_CENTRO_Y = 3.0                   # relativo ao centro do módulo
SETA_RELEVO_ALTURA = 1.5              # mm (requisito do projeto: ≥ 1 mm)
SETA_CHANFRO = 0.4

# Braille — padrão dimensional usual (VERIFICAR a tabela de Braille da ABNT NBR 9050 vigente)
BRAILLE_TEXTO = "PONTO"
BRAILLE_DIAMETRO_PONTO = 1.5          # mm — diâmetro da base do ponto
BRAILLE_ALTURA_PONTO = 0.7            # mm — faixa usual 0,6–0,8 mm
BRAILLE_APARO_TOPO = 0.02             # mm — topo aparado (evita polo degenerado na malha STL)
BRAILLE_DIST_PONTOS = 2.5             # mm — entre centros de pontos da mesma cela (horizontal e vertical)
BRAILLE_DIST_CELAS = 6.0              # mm — entre centros de celas consecutivas (mesma posição de ponto)
BRAILLE_CENTRO_Y = -20.0              # centro da linha Braille, relativo ao centro do módulo
# Alfabeto Braille (apenas as letras necessárias; pontos numerados 1-2-3 na coluna esquerda,
# de cima para baixo, e 4-5-6 na coluna direita)
BRAILLE_ALFABETO = {
    "P": (1, 2, 3, 4),
    "O": (1, 3, 5),
    "N": (1, 3, 4, 5),
    "T": (2, 3, 4, 5),
}

# =====================================================================================
# 4. REDESIGN — SUPORTE / ABRAÇADEIRA PARA TUBO (IMPRESSÃO 3D, escala 1:3)
# =====================================================================================
# No protótipo o "poste" é um tubo de PVC soldável de 25 mm (≈ 1:3 de um tubo de ~76 mm).
TUBO_DIAMETRO = 25.0                  # mm — diâmetro EXTERNO do tubo de demonstração (MEDIR o tubo comprado)
TUBO_FOLGA = 0.4                      # mm — folga radial do berço
TUBO_COMPRIMENTO_MODELO = 300.0       # trecho de tubo representado na montagem
SUPORTE_FLANGE_LARGURA = 36.0         # X
SUPORTE_FLANGE_ALTURA = 88.0          # Y
SUPORTE_FLANGE_ESPESSURA = 5.0        # Z
SUPORTE_FLANGE_RAIO = 4.0
SUPORTE_PAREDE_BERCO = 4.0            # parede lateral do berço (≥ ESPESSURA_MINIMA_PAREDE_FDM)
SUPORTE_AFASTAMENTO = 7.0             # material entre a flange e o fundo do berço
SUPORTE_BERCO_COMPRIMENTO = 44.0      # Y — comprimento do berço (bloco central)
SUPORTE_PORCA_M4_ENTRE_FACES = 7.0    # mm — porca M4 (DIN 934)
SUPORTE_PORCA_FOLGA = 0.3
SUPORTE_PORCA_PROFUNDIDADE = 3.4
# Túneis para abraçadeiras de nylon (enforca-gato) 4,8 mm × 1,3 mm (ou a peça de terceiros do bônus)
SUPORTE_TUNEL_LARGURA = 5.5           # Y
SUPORTE_TUNEL_ALTURA = 2.2            # Z
SUPORTE_TUNEIS_Y = (-12.0, 12.0)
SUPORTE_MATERIAL = "PETG (preferível em área externa) ou PLA para o protótipo"

# =====================================================================================
# 5. INSTALAÇÃO EM ESCALA REAL (proposta — VALORES A VERIFICAR NA NBR 9050)
# =====================================================================================
REAL_PLACA_LARGURA = PLACA_LARGURA / ESCALA_PROTOTIPO    # 600 mm
REAL_PLACA_ALTURA = PLACA_ALTURA / ESCALA_PROTOTIPO      # 450 mm
# Proposta: placa visual (com QR) e módulo tátil em alturas diferentes no mesmo poste.
REAL_ALTURA_CENTRO_MODULO_TATIL = 1100.0  # mm do piso — VERIFICAR faixa de referência na NBR 9050
REAL_ALTURA_BORDA_INFERIOR_PLACA = 1300.0  # mm do piso — VERIFICAR (leitura do QR por pessoa sentada/em pé)
REAL_PROJECAO_MAXIMA_ALVO = 100.0     # mm — projeção lateral alvo a partir do poste (VERIFICAR NBR 9050)


# =====================================================================================
# Funções auxiliares e verificação de coerência
# =====================================================================================
def furos_canto() -> list[tuple[float, float]]:
    """Centros dos 4 furos de canto (relativos ao centro da placa)."""
    dx = PLACA_LARGURA / 2 - FURO_CANTO_DIST_BORDA
    dy = PLACA_ALTURA / 2 - FURO_CANTO_DIST_BORDA
    return [(-dx, -dy), (dx, -dy), (dx, dy), (-dx, dy)]


def furos_suporte() -> list[tuple[float, float]]:
    return [(0.0, FURO_SUPORTE_DIST_Y), (0.0, -FURO_SUPORTE_DIST_Y)]


def furos_modulo_na_placa() -> list[tuple[float, float]]:
    cx, cy = MODULO_CENTRO_NA_PLACA
    return [(cx + x, cy + y) for x, y in MODULO_FURO_GUIA_POSICOES]


def todos_furos_placa() -> list[tuple[float, float, float, str]]:
    """(x, y, diâmetro, função) de todos os furos passantes da placa."""
    furos = [(x, y, FURO_CANTO_DIAMETRO, "canto") for x, y in furos_canto()]
    furos += [(x, y, FURO_SUPORTE_DIAMETRO, "suporte") for x, y in furos_suporte()]
    furos += [(x, y, FURO_MODULO_DIAMETRO, "modulo") for x, y in furos_modulo_na_placa()]
    return furos


def raio_berco() -> float:
    return TUBO_DIAMETRO / 2 + TUBO_FOLGA


def suporte_largura_berco() -> float:
    return 2 * (raio_berco() + SUPORTE_PAREDE_BERCO)


def suporte_profundidade_total() -> float:
    """Distância (Z) da face de contato com a placa até o eixo do tubo."""
    return SUPORTE_FLANGE_ESPESSURA + SUPORTE_AFASTAMENTO + raio_berco()


def braille_celas(texto: str = BRAILLE_TEXTO) -> list[tuple[str, tuple[int, ...]]]:
    return [(letra, BRAILLE_ALFABETO[letra]) for letra in texto]


def braille_pontos(texto: str = BRAILLE_TEXTO, centro=(0.0, BRAILLE_CENTRO_Y)) -> list[tuple[float, float]]:
    """Centros (x, y) dos pontos Braille, centralizados em `centro` (coordenadas do módulo)."""
    celas = braille_celas(texto)
    largura_total = (len(celas) - 1) * BRAILLE_DIST_CELAS + BRAILLE_DIST_PONTOS
    x0 = centro[0] - largura_total / 2
    pontos = []
    for i, (_, numeros) in enumerate(celas):
        xc = x0 + i * BRAILLE_DIST_CELAS
        for n in numeros:
            coluna = 0 if n <= 3 else 1
            linha = (n - 1) % 3                       # 0 = topo
            x = xc + coluna * BRAILLE_DIST_PONTOS
            y = centro[1] + BRAILLE_DIST_PONTOS - linha * BRAILLE_DIST_PONTOS
            pontos.append((x, y))
    return pontos


def braille_raio_esfera() -> float:
    """Raio da esfera cuja calota tem base BRAILLE_DIAMETRO_PONTO e altura BRAILLE_ALTURA_PONTO."""
    a = BRAILLE_DIAMETRO_PONTO / 2
    h = BRAILLE_ALTURA_PONTO
    return (a * a + h * h) / (2 * h)


def resumo_dimensoes() -> dict[str, str]:
    """Resumo usado no README e nos relatórios."""
    return {
        "Placa principal (laser)": f"{PLACA_LARGURA:g} × {PLACA_ALTURA:g} × {PLACA_ESPESSURA:g} mm, R{PLACA_RAIO_CANTO:g}",
        "Placa em escala real (sugerida)": f"{REAL_PLACA_LARGURA:g} × {REAL_PLACA_ALTURA:g} mm",
        "Área do QR Code": f"{AREA_QR_LADO:g} × {AREA_QR_LADO:g} mm (com zona de silêncio)",
        "Módulo tátil (3D, 1:1)": f"{MODULO_LARGURA:g} × {MODULO_ALTURA:g} × {MODULO_ESPESSURA_BASE + SETA_RELEVO_ALTURA:g} mm",
        "Braille": (f"ponto Ø{BRAILLE_DIAMETRO_PONTO:g} × {BRAILLE_ALTURA_PONTO:g} mm; {BRAILLE_DIST_PONTOS:g} mm entre pontos; "
                    f"{BRAILLE_DIST_CELAS:g} mm entre celas"),
        "Seta em relevo": f"{SETA_COMPRIMENTO:g} mm, relevo {SETA_RELEVO_ALTURA:g} mm",
        "Suporte para tubo (3D)": (f"{SUPORTE_FLANGE_LARGURA:g} × {SUPORTE_FLANGE_ALTURA:g} × "
                                   f"{suporte_profundidade_total():.1f} mm, tubo Ø{TUBO_DIAMETRO:g} mm"),
    }


def _dentro_retangulo_arredondado(x: float, y: float, margem: float) -> bool:
    """True se o ponto está dentro da placa (cantos arredondados) com folga `margem`."""
    hx, hy, r = PLACA_LARGURA / 2, PLACA_ALTURA / 2, PLACA_RAIO_CANTO
    ax, ay = abs(x), abs(y)
    if ax > hx - margem or ay > hy - margem:
        return False
    cx, cy = hx - r, hy - r
    if ax > cx and ay > cy:
        return math.hypot(ax - cx, ay - cy) <= r - margem
    return True


def verificar_coerencia() -> list[str]:
    """Retorna a lista de problemas encontrados (lista vazia = parâmetros coerentes)."""
    problemas: list[str] = []

    # Furos dentro da placa com material suficiente até a borda (≥ 1 × espessura)
    for x, y, d, funcao in todos_furos_placa():
        if not _dentro_retangulo_arredondado(x, y, d / 2 + PLACA_ESPESSURA):
            problemas.append(f"Furo de {funcao} em ({x:g}, {y:g}) muito perto da borda da placa")
    # Furos não se sobrepõem
    furos = todos_furos_placa()
    for i in range(len(furos)):
        for j in range(i + 1, len(furos)):
            (x1, y1, d1, _), (x2, y2, d2, _) = furos[i], furos[j]
            if math.hypot(x1 - x2, y1 - y2) < (d1 + d2) / 2 + 2 * PLACA_ESPESSURA:
                problemas.append(f"Furos muito próximos: ({x1:g},{y1:g}) e ({x2:g},{y2:g})")

    # Área do QR dentro da placa e sem furos
    qx, qy = AREA_QR_CENTRO
    h = AREA_QR_LADO / 2
    for cx, cy in ((qx - h, qy - h), (qx + h, qy - h), (qx + h, qy + h), (qx - h, qy + h)):
        if not _dentro_retangulo_arredondado(cx, cy, PLACA_BORDA_GRAVADA_MARGEM + 1):
            problemas.append("Área do QR fora da moldura da placa")
    for x, y, d, funcao in todos_furos_placa():
        if abs(x - qx) < h + d / 2 + 1 and abs(y - qy) < h + d / 2 + 1:
            problemas.append(f"Furo de {funcao} invade a área do QR")

    # Módulo tátil dentro da placa e sem cobrir furos que não sejam os dele
    mx, my = MODULO_CENTRO_NA_PLACA
    mw, mh = MODULO_LARGURA / 2, MODULO_ALTURA / 2
    for cx, cy in ((mx - mw, my - mh), (mx + mw, my - mh), (mx + mw, my + mh), (mx - mw, my + mh)):
        if not _dentro_retangulo_arredondado(cx, cy, 2.0):
            problemas.append("Módulo tátil ultrapassa a placa")
    for x, y, d, funcao in todos_furos_placa():
        if funcao != "modulo" and abs(x - mx) < mw + d / 2 and abs(y - my) < mh + d / 2:
            problemas.append(f"Módulo tátil cobre o furo de {funcao} em ({x:g},{y:g})")
    if abs(qx - mx) < h + mw + 2 and abs(qy - my) < h + mh + 2:
        problemas.append("Módulo tátil sobrepõe a área do QR")

    # Parafusos do módulo (pelo verso) não podem colidir com a flange do suporte
    for x, y in furos_modulo_na_placa():
        if abs(x) < SUPORTE_FLANGE_LARGURA / 2 + CABECA_PARAFUSO_M3_DIAMETRO / 2 and \
                abs(y) < SUPORTE_FLANGE_ALTURA / 2 + CABECA_PARAFUSO_M3_DIAMETRO / 2:
            problemas.append(f"Cabeça do parafuso do módulo em ({x:g},{y:g}) colide com a flange do suporte")

    # Furos do suporte dentro da flange e fora do berço
    for _, y in furos_suporte():
        if abs(y) + SUPORTE_PORCA_M4_ENTRE_FACES / 2 > SUPORTE_FLANGE_ALTURA / 2 - 1.5:
            problemas.append("Furo/porca do suporte fora da flange")
        if abs(y) - (SUPORTE_PORCA_M4_ENTRE_FACES + SUPORTE_PORCA_FOLGA) / math.sqrt(3) < SUPORTE_BERCO_COMPRIMENTO / 2:
            problemas.append("Porca do suporte colide com o bloco do berço")
    if suporte_largura_berco() > SUPORTE_FLANGE_LARGURA + 1e-6:
        problemas.append("Berço do suporte mais largo que a flange")
    for ty in SUPORTE_TUNEIS_Y:
        if abs(ty) + SUPORTE_TUNEL_LARGURA / 2 > SUPORTE_BERCO_COMPRIMENTO / 2 - ESPESSURA_MINIMA_PAREDE_FDM:
            problemas.append("Túnel da abraçadeira fora do berço")
    if SUPORTE_AFASTAMENTO - SUPORTE_TUNEL_ALTURA < 2 * ESPESSURA_MINIMA_PAREDE_FDM - 1e-9:
        problemas.append("Pouco material ao redor do túnel da abraçadeira")
    if SUPORTE_PAREDE_BERCO < ESPESSURA_MINIMA_PAREDE_FDM:
        problemas.append("Parede do berço abaixo do mínimo FDM")

    # Módulo tátil: Braille, seta e furos-guia
    if not 0.6 <= BRAILLE_ALTURA_PONTO <= 0.8:
        problemas.append("Altura do ponto Braille fora da faixa usual 0,6–0,8 mm")
    if BRAILLE_DIAMETRO_PONTO < 3 * BICO_FDM:
        problemas.append("Ponto Braille menor que 3 larguras de extrusão")
    if BRAILLE_DIST_PONTOS - BRAILLE_DIAMETRO_PONTO < 2 * BICO_FDM:
        problemas.append("Espaço entre pontos Braille menor que 2 larguras de extrusão")
    if SETA_RELEVO_ALTURA < 1.0:
        problemas.append("Seta com relevo menor que 1 mm")
    if SETA_LARGURA_HASTE < 3 * BICO_FDM:
        problemas.append("Haste da seta fina demais para FDM")
    pts = braille_pontos()
    r = BRAILLE_DIAMETRO_PONTO / 2
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    if min(xs) - r < -MODULO_LARGURA / 2 + 4 or max(xs) + r > MODULO_LARGURA / 2 - 4:
        problemas.append("Braille fora do módulo")
    if max(ys) + r > SETA_CENTRO_Y - SETA_LARGURA_PONTA / 2 - 3:
        problemas.append("Braille muito próximo da seta (≥ 3 mm de separação)")
    if SETA_CENTRO_Y + SETA_LARGURA_PONTA / 2 > MODULO_TEXTO_BASE_Y - 3:
        problemas.append("Seta muito próxima do texto em relevo")
    if SETA_COMPRIMENTO > MODULO_LARGURA - 2 * 6:
        problemas.append("Seta mais longa que o módulo")
    if MODULO_FURO_GUIA_PROFUNDIDADE > MODULO_ESPESSURA_BASE - 0.8:
        problemas.append("Furo-guia deixa menos de 0,8 mm de material na face frontal")
    for fx, fy in MODULO_FURO_GUIA_POSICOES:
        if abs(fx) + MODULO_FURO_GUIA_DIAMETRO / 2 + ESPESSURA_MINIMA_PAREDE_FDM > MODULO_LARGURA / 2 or \
                abs(fy) + MODULO_FURO_GUIA_DIAMETRO / 2 + ESPESSURA_MINIMA_PAREDE_FDM > MODULO_ALTURA / 2:
            problemas.append("Furo-guia do módulo fora do módulo")

    # Peças cabem nas máquinas
    if PLACA_LARGURA > MESA_LASER_X or PLACA_ALTURA > MESA_LASER_Y:
        problemas.append("Placa maior que a mesa do laser")
    if MODULO_LARGURA > MESA_IMPRESSORA_X or MODULO_ALTURA > MESA_IMPRESSORA_Y:
        problemas.append("Módulo tátil maior que a mesa da impressora")
    if SUPORTE_FLANGE_LARGURA > MESA_IMPRESSORA_X or SUPORTE_FLANGE_ALTURA > MESA_IMPRESSORA_Y:
        problemas.append("Suporte maior que a mesa da impressora")
    return problemas


if __name__ == "__main__":
    for k, v in resumo_dimensoes().items():
        print(f"{k}: {v}")
    probs = verificar_coerencia()
    print("Coerência:", "OK" if not probs else probs)
