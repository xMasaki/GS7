"""Gerador da fonte SIMULADA `data/samples/denuncias_simuladas.csv`.

Por que simular? O AcessaCidade é um MVP novo: ainda não existe histórico real de
denúncias. Para exercitar o pipeline (e mostrar o que cada camada resolve), geramos
uma exportação "bagunçada" de um sistema legado FICTÍCIO da prefeitura FICTÍCIA da
"Cidade Exemplo", com os problemas típicos de dados reais de cadastro:

- grafias diferentes para o mesmo bairro / logradouro / categoria / status;
- datas em vários formatos (ISO, dd/mm/aaaa, dd-mm-aaaa hh:mm, "14 de outubro de 2026")
  e algumas inválidas;
- coordenadas como texto (vírgula ou ponto), algumas inválidas, fora do Brasil ou vazias;
- campos obrigatórios ausentes;
- duplicatas exatas (~4%) e quase-duplicatas (mesma ocorrência registrada 2x no mesmo dia);
- coluna `nome_denunciante` ("Pessoa Simulada 017") para demonstrar a minimização LGPD;
- coluna `origem_dado` = "SIMULADO" em TODAS as linhas.

Semente fixa (SEMENTE) -> o arquivo gerado é sempre idêntico.
Uso:  python -m acessacidade_pipeline.simulate [--saida caminho.csv]
"""
from __future__ import annotations

import argparse
import csv
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

from .config import PipelineConfig
from .dominio import COLUNAS_FONTE_SIMULADA
from .parsing import FUSO_LOCAL

SEMENTE = 20261114
LINHAS_BASE = 250
QUASE_DUPLICATAS = 10
DUPLICATAS_EXATAS = 11

INICIO = datetime(2026, 8, 1, 0, 0)
FIM = datetime(2026, 11, 13, 23, 59)

MESES_PT = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto",
            "setembro", "outubro", "novembro", "dezembro"]

# bairro oficial -> (peso, variações de grafia, centro aproximado (lat, lon) SINTÉTICO)
# Coordenadas sorteadas em torno de um ponto arbitrário; não correspondem a endereços reais.
BAIRROS = {
    "Centro": (20, ["Centro", "centro", "CENTRO", " Centro ", "Centro "], (-10.180, -48.330)),
    "Jardim das Flores": (15, ["Jardim das Flores", "Jd. das Flores", "Jd das Flores", "jardim das flores",
                               "JARDIM DAS FLORES", "Jardim das  Flores"], (-10.165, -48.345)),
    "Vila Nova": (14, ["Vila Nova", "V. Nova", "vila nova", "VILA NOVA", "Vl. Nova"], (-10.195, -48.315)),
    "São José": (12, ["São José", "Sao Jose", "S. José", "são josé", "SAO JOSE"], (-10.170, -48.310)),
    "Bela Vista": (10, ["Bela Vista", "bela vista", "BELA VISTA", "Bela  Vista"], (-10.200, -48.350)),
    "Parque das Árvores": (10, ["Parque das Árvores", "Pq. das Arvores", "Parque das Arvores",
                                "pq das árvores"], (-10.155, -48.325)),
    "Santa Luzia": (9, ["Santa Luzia", "Sta. Luzia", "Sta Luzia", "santa luzia"], (-10.210, -48.335)),
    "Nova Esperança": (8, ["Nova Esperança", "Nova Esperanca", "NOVA ESPERANÇA", "nova esperança"],
                       (-10.185, -48.360)),
    # Bairro fora do dicionário oficial: demonstra que a Silver não inventa correspondência.
    "Recanto Verde": (2, ["Recanto Verde", "recanto verde", "RECANTO VERDE"], (-10.150, -48.300)),
}

# logradouro oficial -> variações de grafia (nomes genéricos inventados)
LOGRADOUROS = {
    "Rua das Acácias": ["Rua das Acácias", "R. das Acácias", "rua das acacias", "RUA DAS ACACIAS"],
    "Avenida Central": ["Avenida Central", "Av. Central", "AV CENTRAL", "avenida central"],
    "Rua dos Girassóis": ["Rua dos Girassóis", "R. dos Girassois", "rua dos girassóis"],
    "Travessa dos Ipês": ["Travessa dos Ipês", "Tv. dos Ipês", "travessa dos ipes"],
    "Rua do Mercado": ["Rua do Mercado", "R. do Mercado", "RUA DO MERCADO"],
    "Avenida das Palmeiras": ["Avenida das Palmeiras", "Av. das Palmeiras", "av das palmeiras"],
    "Rua da Estação": ["Rua da Estação", "R. da Estacao", "rua da estação"],
    "Alameda dos Sabiás": ["Alameda dos Sabiás", "Al. dos Sabiás", "alameda dos sabias"],
    "Rua Exemplo": ["Rua Exemplo", "R. Exemplo", "rua exemplo"],
    "Praça da Matriz": ["Praça da Matriz", "Pça da Matriz", "praca da matriz"],
    "Rua Projetada Um": ["Rua Projetada Um", "R. Projetada Um", "RUA PROJETADA UM"],
    "Avenida do Contorno": ["Avenida do Contorno", "Av. do Contorno", "avenida do contorno"],
}

# chave do contrato -> (peso, variações de texto)
TIPOS = {
    "BURACO_CALCADA": (25, ["buraco", "Buraco na calçada", "BURACO_CALCADA", "buraco calcada",
                            "Buraco na calcada", "buraco_calcada"]),
    "BURACO_VIA": (10, ["Buraco na via ou travessia", "BURACO_VIA", "buraco na rua", "Buraco na travessia"]),
    "CALCADA_DANIFICADA": (20, ["Calçada quebrada ou desnivelada", "CALCADA_DANIFICADA", "calçada quebrada",
                                "Calcada desnivelada", "piso solto na calçada"]),
    "RAMPA_IRREGULAR": (12, ["Rampa ausente ou irregular", "RAMPA_IRREGULAR", "sem rampa",
                             "rampa irregular", "Rampa quebrada"]),
    "PISO_TATIL": (8, ["Piso tátil ausente ou danificado", "PISO_TATIL", "piso tatil", "Piso tátil danificado"]),
    "OBSTACULO_FIXO": (10, ["Obstáculo fixo (poste, lixeira, placa)", "OBSTACULO_FIXO",
                            "poste no meio da calçada", "lixeira", "placa"]),
    "OBSTACULO_TEMPORARIO": (10, ["Obstáculo temporário (entulho, veículo, obra)", "OBSTACULO_TEMPORARIO",
                                  "entulho", "carro estacionado na calçada", "obra sem sinalização"]),
    "OUTRO": (5, ["Outro", "OUTRO", "outros", "falta de iluminação na travessia"]),
}

DESCRICOES = {
    "BURACO_CALCADA": "Buraco de aproximadamente {n} cm na calçada; cadeira de rodas não consegue passar.",
    "BURACO_VIA": "Buraco na faixa de travessia com cerca de {n} cm, perigoso para quem atravessa com bengala.",
    "CALCADA_DANIFICADA": "Calçada quebrada e desnivelada em um trecho de {n} metros, com placas soltas.",
    "RAMPA_IRREGULAR": "Rampa de acesso com degrau de {n} cm no final; cadeirantes não conseguem subir.",
    "PISO_TATIL": "Piso tátil interrompido em {n} metros, sem continuidade até a faixa de pedestres.",
    "OBSTACULO_FIXO": "Poste instalado no meio da calçada, deixando apenas {n} cm livres para passagem.",
    "OBSTACULO_TEMPORARIO": "Entulho de obra ocupando a calçada há vários dias, cerca de {n} metros bloqueados.",
    "OUTRO": "Trecho com problema de acessibilidade não listado; observado em {n} visitas ao local.",
}

IMPACTOS = {
    "IMPEDE_PASSAGEM": (30, ["IMPEDE_PASSAGEM", "Impede a passagem", "impede passagem", "impede"]),
    "DIFICULTA_PASSAGEM": (35, ["DIFICULTA_PASSAGEM", "Dificulta a passagem", "dificulta"]),
    "RISCO_QUEDA": (25, ["RISCO_QUEDA", "Risco de queda ou acidente", "risco de queda", "risco acidente"]),
    "BAIXO_IMPACTO": (10, ["BAIXO_IMPACTO", "Baixo impacto", "baixo"]),
}

STATUS_VARIACOES = {
    "RECEBIDA": ["RECEBIDA", "Recebida", "recebida", " RECEBIDA"],
    "EM_ANALISE": ["EM_ANALISE", "Em análise", "em analise", "Em Analise"],
    "AGUARDANDO_REVISAO": ["AGUARDANDO_REVISAO", "Aguardando revisão", "aguardando revisao"],
}

VISAO_VARIACOES = {
    "POSSIBLE_POTHOLE": ["POSSIBLE_POTHOLE", "possible_pothole", "Possível buraco identificado"],
    "NOT_IDENTIFIED": ["NOT_IDENTIFIED", "not_identified", "Nenhum indício suficiente de buraco"],
    "INCONCLUSIVE": ["INCONCLUSIVE", "inconclusive", "Análise inconclusiva"],
}

REFERENCIAS = ["Em frente ao ponto de ônibus", "Próximo à escola municipal", "Ao lado da farmácia",
               "Perto da praça", "Esquina com a padaria", "Em frente à unidade de saúde", ""]


def _escolher_ponderado(rng: random.Random, opcoes: dict) -> str:
    chaves = list(opcoes)
    pesos = [opcoes[k][0] for k in chaves]
    return rng.choices(chaves, weights=pesos, k=1)[0]


def _formatar_data(rng: random.Random, local: datetime) -> str:
    """Escreve a data/hora LOCAL (UTC-3) em um dos formatos 'bagunçados'."""
    sorteio = rng.random()
    if sorteio < 0.33:
        utc = local.replace(tzinfo=FUSO_LOCAL).astimezone(timezone.utc)
        return utc.strftime("%Y-%m-%dT%H:%M:%SZ")
    if sorteio < 0.48:
        return local.strftime("%Y-%m-%d %H:%M:%S")
    if sorteio < 0.62:
        return local.strftime("%d/%m/%Y")
    if sorteio < 0.72:
        return local.strftime("%d/%m/%Y %H:%M")
    if sorteio < 0.85:
        return local.strftime("%d-%m-%Y %H:%M")
    if sorteio < 0.95:
        return f"{local.day} de {MESES_PT[local.month - 1]} de {local.year}"
    # Datas inválidas / impossíveis (≈5%)
    return rng.choice(["", "31/09/2026", "2026-13-05", "ontem", "15/10/26", "sem data"])


def _formatar_coordenada(rng: random.Random, valor: float) -> str:
    texto = f"{valor:.6f}"
    sorteio = rng.random()
    if sorteio < 0.45:
        return texto.replace(".", ",")
    if sorteio < 0.55:
        return f" {texto} "
    return texto


def _coordenadas(rng: random.Random, centro: tuple[float, float]) -> tuple[str, str]:
    sorteio = rng.random()
    if sorteio < 0.42:
        return "", ""  # sem coordenadas (comum: cidadão não compartilhou localização)
    if sorteio < 0.44:
        return rng.choice([
            ("abc", "-48.33"),           # texto não numérico
            ("-10.18.2", "-48,33"),      # formato quebrado
            ("-123.400000", "-48.330000"),  # latitude fora da faixa -90..90
            ("-10.180000", ""),          # só um dos dois
            ("0", "0"),                  # "ilha nula": formato válido, fora do Brasil
            ("40.712800", "-74.006000"),  # fora do Brasil
            ("38,722300", "-9,139300"),  # fora do Brasil
        ])
    lat = centro[0] + rng.uniform(-0.008, 0.008)
    lon = centro[1] + rng.uniform(-0.008, 0.008)
    return _formatar_coordenada(rng, lat), _formatar_coordenada(rng, lon)


def _linha_base(rng: random.Random, ident: int) -> tuple[dict, dict]:
    """Gera uma linha bagunçada + metadados 'verdadeiros' usados para criar quase-duplicatas."""
    bairro = _escolher_ponderado(rng, BAIRROS)
    _, variacoes_bairro, centro = BAIRROS[bairro]
    logradouro = rng.choice(list(LOGRADOUROS))
    tipo = _escolher_ponderado(rng, TIPOS)
    impacto = _escolher_ponderado(rng, IMPACTOS)
    segundos = rng.randint(0, int((FIM - INICIO).total_seconds()))
    criado_local = INICIO + timedelta(seconds=segundos)

    possui_imagem = rng.random() < 0.6
    visao, pontuacao = "", ""
    if possui_imagem:
        if tipo in ("BURACO_CALCADA", "BURACO_VIA"):
            classe = rng.choices(list(VISAO_VARIACOES), weights=[60, 15, 25])[0]
        else:
            classe = rng.choices(list(VISAO_VARIACOES), weights=[15, 55, 30])[0]
        faixa = {"POSSIBLE_POTHOLE": (0.60, 0.95), "INCONCLUSIVE": (0.35, 0.59), "NOT_IDENTIFIED": (0.05, 0.34)}
        valor = rng.uniform(*faixa[classe])
        pontuacao = f"{valor:.2f}"
        if rng.random() < 0.35:
            pontuacao = pontuacao.replace(".", ",")
        if rng.random() < 0.01:
            pontuacao = "1,70"  # pontuação fora da faixa 0..1
        visao = "" if rng.random() < 0.04 else rng.choice(VISAO_VARIACOES[classe])
        status = rng.choices(["AGUARDANDO_REVISAO", "EM_ANALISE"], weights=[60, 40])[0]
    else:
        status = rng.choices(["RECEBIDA", "EM_ANALISE"], weights=[70, 30])[0]

    revisao = ""
    if possui_imagem and status == "EM_ANALISE" and rng.random() < 0.5:
        revisao = rng.choice(["CONFIRMADO", "confirmado", "DESCARTADO", "Confirmado"])

    lat, lon = _coordenadas(rng, centro)
    atualizado = ""
    if rng.random() < 0.7:
        atualizado_local = min(criado_local + timedelta(minutes=rng.randint(1, 60 * 24 * 5)), FIM)
        atualizado = (atualizado_local.replace(tzinfo=FUSO_LOCAL).astimezone(timezone.utc)
                      .strftime("%Y-%m-%dT%H:%M:%SZ"))

    descricao = DESCRICOES[tipo].format(n=rng.randint(5, 80))
    numero = str(rng.randint(1, 1500))
    if rng.random() < 0.08:
        numero = rng.choice(["S/N", "s/n", "SN", ""])

    linha = {
        "id": str(ident),
        "protocolo": f"SIM-2026-{ident:06d}",
        "criado_em": _formatar_data(rng, criado_local),
        "atualizado_em": atualizado,
        "logradouro": rng.choice(LOGRADOUROS[logradouro]),
        "numero": numero,
        "bairro": rng.choice(variacoes_bairro),
        "cidade": rng.choices(["Cidade Exemplo", "cidade exemplo", "CIDADE EXEMPLO", "Cid. Exemplo",
                               "Cidade Exemplo ", ""], weights=[70, 8, 6, 6, 5, 5])[0],
        "ponto_referencia": rng.choice(REFERENCIAS),
        "tipo_obstaculo": rng.choice(TIPOS[tipo][1]),
        "descricao": descricao,
        "impacto": rng.choice(IMPACTOS[impacto][1]),
        "latitude": lat,
        "longitude": lon,
        "status": "" if rng.random() < 0.05 else rng.choice(STATUS_VARIACOES[status]),
        "origem": rng.choice(["SIMULADO", "SIMULADO", "simulado", "Simulado"]),
        "simulado": rng.choice(["true", "true", "TRUE", "1", "sim"]),
        "possui_imagem": rng.choice(["true", "TRUE", "1", "sim"]) if possui_imagem
        else rng.choice(["false", "FALSE", "0", "não"]),
        "visao_classificacao": visao,
        "visao_pontuacao": pontuacao,
        "revisao_humana": revisao,
        "nome_denunciante": f"Pessoa Simulada {rng.randint(1, 120):03d}" if rng.random() < 0.6 else "",
        "origem_dado": "SIMULADO",
    }

    # Campos obrigatórios ausentes / insuficientes (cada um ≈2–3%)
    if rng.random() < 0.02:
        linha["logradouro"] = ""
    if rng.random() < 0.02:
        linha["bairro"] = ""
    if rng.random() < 0.02:
        linha["tipo_obstaculo"] = ""
    if rng.random() < 0.03:
        linha["descricao"] = rng.choice(["", "ruim", "buraco"])
    if rng.random() < 0.03:
        linha["impacto"] = ""

    meta = {"criado_local": criado_local, "logradouro": logradouro, "tipo": tipo, "bairro": bairro}
    return linha, meta


# Casos de borda aplicados de forma determinística (garantem que TODA flag/regra do pipeline
# seja exercitada pelo arquivo, independentemente do sorteio).
CASOS_DE_BORDA = (
    {"latitude": "abc", "longitude": "-48.33"},
    {"latitude": "-10.18.2", "longitude": "-48,33"},
    {"latitude": "-123.400000", "longitude": "-48.330000"},
    {"latitude": "-10.180000", "longitude": ""},
    {"latitude": "0", "longitude": "0"},
    {"latitude": "40.712800", "longitude": "-74.006000"},
    {"latitude": "38,722300", "longitude": "-9,139300"},
    {"criado_em": ""},
    {"criado_em": "31/09/2026"},
    {"tipo_obstaculo": "falta de iluminação na travessia"},
    {"bairro": "   "},
    {"possui_imagem": "false", "visao_classificacao": "INCONCLUSIVE", "visao_pontuacao": "0.41"},
    {"possui_imagem": "talvez", "visao_classificacao": "POSSIBLE_POTHOLE", "visao_pontuacao": "0,77"},
    {"status": "pendente"},
    {"impacto": "muito ruim"},
)


def gerar_linhas(semente: int = SEMENTE) -> list[dict]:
    rng = random.Random(semente)
    base: list[tuple[dict, dict]] = [_linha_base(rng, i) for i in range(1, LINHAS_BASE + 1)]
    ids_borda = set()
    for (linha, _), caso in zip(rng.sample(base, len(CASOS_DE_BORDA)), CASOS_DE_BORDA):
        linha.update(caso)
        ids_borda.add(linha["id"])
    linhas = [l for l, _ in base]
    proximo_id = LINHAS_BASE + 1

    # Quase-duplicatas: mesma ocorrência registrada de novo no MESMO dia, com outra grafia.
    candidatos = [
        (l, m) for l, m in base
        if l["id"] not in ids_borda and l["logradouro"] and l["bairro"] and l["tipo_obstaculo"]
        and l["criado_em"] not in ("", "31/09/2026", "2026-13-05", "ontem", "15/10/26", "sem data")
    ]
    for original, meta in rng.sample(candidatos, QUASE_DUPLICATAS):
        copia = dict(original)
        local = meta["criado_local"]
        fim_do_dia = local.replace(hour=23, minute=59, second=0)
        novo_local = min(local + timedelta(minutes=rng.randint(5, 180)), fim_do_dia)
        copia.update({
            "id": str(proximo_id),
            "protocolo": f"SIM-2026-{proximo_id:06d}",
            "criado_em": rng.choice([novo_local.strftime("%d/%m/%Y %H:%M"),
                                     novo_local.strftime("%Y-%m-%d %H:%M:%S")]),
            "logradouro": rng.choice(LOGRADOUROS[meta["logradouro"]]),
            "bairro": rng.choice(BAIRROS[meta["bairro"]][1]),
            "tipo_obstaculo": rng.choice(TIPOS[meta["tipo"]][1]),
            "nome_denunciante": f"Pessoa Simulada {rng.randint(1, 120):03d}" if rng.random() < 0.5 else "",
            "descricao": "Mesmo problema já relatado por outra pessoa: " + DESCRICOES[meta["tipo"]].format(
                n=rng.randint(5, 80)),
        })
        linhas.append(copia)
        proximo_id += 1

    # Duplicatas exatas (≈4%): a mesma linha exportada duas vezes pelo sistema legado.
    for original in rng.sample(linhas, DUPLICATAS_EXATAS):
        linhas.append(dict(original))

    rng.shuffle(linhas)
    return linhas


def gerar_csv(destino: Path | str | None = None, semente: int = SEMENTE) -> Path:
    destino = Path(destino) if destino else PipelineConfig.from_env().samples_csv
    destino.parent.mkdir(parents=True, exist_ok=True)
    linhas = gerar_linhas(semente)
    with open(destino, "w", encoding="utf-8", newline="") as arq:
        escritor = csv.DictWriter(arq, fieldnames=list(COLUNAS_FONTE_SIMULADA), lineterminator="\n")
        escritor.writeheader()
        escritor.writerows(linhas)
    return destino


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Gera a fonte simulada de denúncias (semente fixa).")
    parser.add_argument("--saida", help="Caminho do CSV (padrão: <PIPELINE_DATA_DIR>/samples/denuncias_simuladas.csv)")
    parser.add_argument("--semente", type=int, default=SEMENTE)
    args = parser.parse_args(argv)
    caminho = gerar_csv(args.saida, args.semente)
    print(f"Fonte simulada gerada: {caminho} ({LINHAS_BASE + QUASE_DUPLICATAS + DUPLICATAS_EXATAS} linhas, "
          f"semente {args.semente})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
