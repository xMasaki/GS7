#!/usr/bin/env python3
"""Gera tráfego de demonstração para o AcessaCidade (observabilidade — Disciplina 06).

Uso (na raiz do repositório, com o venv ativado):

    # tráfego normal (somente leitura) por 2 minutos, 3 req/s
    python scripts/gerar_trafego_demo.py --url http://localhost:8000 --duracao 120 --modo normal

    # dispara o alerta AcessaCidadeMuitas4xx de forma SEGURA (consultas a protocolos
    # inexistentes -> 404) por 3 minutos
    python scripts/gerar_trafego_demo.py --url http://localhost:8000 --duracao 180 --modo erros404

    # contra o MVP publicado na Azure
    python scripts/gerar_trafego_demo.py --url http://SEU-DNS-LABEL.brazilsouth.azurecontainer.io:8000 --modo erros404

Segurança da demonstração:
  * Apenas requisições GET de leitura (nenhuma denúncia é criada, nada é alterado).
  * Os 404 vêm de consultas a protocolos que não existem (ano 2099), que a API
    responde com 404 — não exploram falhas nem sobrecarregam o serviço.
  * A taxa é limitada (padrão 3 req/s, máximo 20 req/s) e a duração máxima é de 15 min.
  * Opcional --com-visao envia, no máximo a cada 6 s, uma foto SINTÉTICA de
    data/samples/fotos para POST /api/visao/analisar (que não persiste nada),
    respeitando o rate limit padrão de 30 req/min da API.
"""
from __future__ import annotations

import argparse
import collections
import itertools
import random
import sys
import time
from pathlib import Path
from typing import Callable

import httpx

MAX_RPS = 20.0
MAX_DURACAO = 15 * 60
INTERVALO_MIN_VISAO = 6.0  # segundos -> no máximo 10 análises/min

ROTAS_NORMAIS = (
    "/health",
    "/api/meta/opcoes",
    "/api/denuncias?pagina=1&limite=10",
    "/api/denuncias?pagina=1&limite=5&incluir_simulados=true",
    "/api/indicadores",
    "/api/indicadores/analiticos",
    "/",
)

RAIZ = Path(__file__).resolve().parents[1]
PASTA_FOTOS = RAIZ / "data" / "samples" / "fotos"


def rota_404(seq: int) -> str:
    """Protocolo válido no formato do contrato (AC-AAAA-NNNNNN), porém inexistente."""
    return f"/api/denuncias/AC-2099-{(seq % 999999) + 1:06d}"


def listar_fotos(pasta: Path = PASTA_FOTOS) -> list[Path]:
    if not pasta.is_dir():
        return []
    return sorted(p for p in pasta.iterdir() if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"})


def proxima_rota(modo: str, seq: int, rng: random.Random) -> str:
    if modo == "erros404":
        # 80% de 404 + 20% de tráfego normal para o painel de tráfego continuar vivo
        return rota_404(seq) if rng.random() < 0.8 else rng.choice(ROTAS_NORMAIS)
    return rng.choice(ROTAS_NORMAIS)


def executar(
    url: str,
    duracao: float,
    modo: str,
    rps: float = 3.0,
    timeout: float = 10.0,
    com_visao: bool = False,
    transport: httpx.BaseTransport | None = None,
    relogio: Callable[[], float] = time.monotonic,
    dormir: Callable[[float], None] = time.sleep,
    saida=sys.stdout,
    semente: int = 42,
) -> dict:
    """Executa a geração de tráfego e devolve um resumo {status: quantidade}."""
    if modo not in ("normal", "erros404"):
        raise ValueError("modo deve ser 'normal' ou 'erros404'")
    if not 0 < rps <= MAX_RPS:
        raise ValueError(f"--rps deve estar entre 0 e {MAX_RPS:g}")
    if not 0 < duracao <= MAX_DURACAO:
        raise ValueError(f"--duracao deve estar entre 1 e {MAX_DURACAO} segundos")

    rng = random.Random(semente)
    fotos = listar_fotos() if com_visao else []
    if com_visao and not fotos:
        print(f"Aviso: nenhuma foto sintética encontrada em {PASTA_FOTOS}; --com-visao ignorado.", file=saida)
    ciclo_fotos = itertools.cycle(fotos) if fotos else None

    contagem: collections.Counter[str] = collections.Counter()
    intervalo = 1.0 / rps
    inicio = relogio()
    ultimo_visao = -INTERVALO_MIN_VISAO
    ultimo_log = inicio

    with httpx.Client(base_url=url.rstrip("/"), timeout=timeout, transport=transport,
                      headers={"User-Agent": "AcessaCidade-demo-trafego/1.0"}) as cliente:
        for seq in itertools.count():
            agora = relogio()
            decorrido = agora - inicio
            if decorrido >= duracao:
                break
            try:
                if ciclo_fotos is not None and decorrido - ultimo_visao >= INTERVALO_MIN_VISAO:
                    ultimo_visao = decorrido
                    foto = next(ciclo_fotos)
                    with foto.open("rb") as fh:
                        resp = cliente.post("/api/visao/analisar", files={"foto": (foto.name, fh.read())})
                else:
                    resp = cliente.get(proxima_rota(modo, seq, rng))
                contagem[str(resp.status_code)] += 1
            except httpx.HTTPError as exc:
                contagem[f"falha:{type(exc).__name__}"] += 1
            if agora - ultimo_log >= 15:
                ultimo_log = agora
                print(f"[{decorrido:5.0f}s] {sum(contagem.values())} requisições: {dict(contagem)}", file=saida)
            dormir(intervalo)

    total = sum(contagem.values())
    print(f"Concluído: {total} requisições em {relogio() - inicio:.0f}s (modo={modo}). Por status: {dict(contagem)}",
          file=saida)
    return dict(contagem)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Gera tráfego de demonstração (somente leitura) para o AcessaCidade.")
    parser.add_argument("--url", default="http://localhost:8000", help="URL base da aplicação (padrão: %(default)s)")
    parser.add_argument("--duracao", type=float, default=180, help="duração em segundos (padrão: %(default)s; máx. 900)")
    parser.add_argument("--modo", choices=("normal", "erros404"), default="normal",
                        help="normal = leituras; erros404 = maioria de consultas a protocolos inexistentes")
    parser.add_argument("--rps", type=float, default=3.0, help="requisições por segundo (padrão: %(default)s; máx. 20)")
    parser.add_argument("--timeout", type=float, default=10.0, help="timeout por requisição em segundos")
    parser.add_argument("--com-visao", action="store_true",
                        help="envia periodicamente uma foto SINTÉTICA para /api/visao/analisar (não persiste nada)")
    args = parser.parse_args(argv)
    try:
        executar(args.url, args.duracao, args.modo, rps=args.rps, timeout=args.timeout, com_visao=args.com_visao)
    except ValueError as exc:
        parser.error(str(exc))
    except KeyboardInterrupt:
        print("Interrompido pelo usuário.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
