"""Processa todas as imagens de uma pasta com o mesmo fluxo usado pelo backend.

Para cada imagem: valida → sanitiza (remove EXIF/GPS, reduz, borra rostos) → analisa.
Saídas (na pasta de resultados):
    <nome_da_imagem>/<etapa>.jpg       — uma imagem por etapa (STAGE_ORDER)
    <nome_da_imagem>/painel_etapas.jpg — painel com todas as etapas lado a lado
    <nome_da_imagem>/resultado.json    — resultado completo (to_dict) da imagem
    dados_extraidos.csv                — uma linha por imagem com as principais medidas
    dados_extraidos.json               — resultado completo de todas as imagens

Uso (na raiz do repositório):
    .venv\\Scripts\\python.exe 04-Applied-Computer-Vision\\scripts\\analisar_pasta.py
    .venv\\Scripts\\python.exe 04-Applied-Computer-Vision\\scripts\\analisar_pasta.py --entrada <pasta> --saida <pasta>
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import cv2

COMPONENT = Path(__file__).resolve().parents[1]
ROOT = COMPONENT.parent
sys.path.insert(0, str(COMPONENT / "src"))

from acessacidade_vision import (  # noqa: E402
    ALGORITHM_VERSION,
    STAGE_ORDER,
    VisionError,
    analyze_image,
    sanitize_image_with_report,
    validate_image_bytes,
)
from acessacidade_vision.visualize import montage  # noqa: E402

EXTENSOES = {".jpg", ".jpeg", ".png", ".webp"}
MAX_BYTES = 10 * 1024 * 1024

CSV_COLUNAS = [
    "arquivo", "classificacao", "rotulo", "pontuacao", "decisao", "num_deteccoes",
    "brilho_medio", "contraste_rms", "nitidez_laplaciano", "qualidade_adequada",
    "limiar_otsu", "limiar_robusto", "limiar_aplicado", "percentual_mascara", "num_candidatas",
    "area_relativa", "circularidade", "solidez", "razao_aspecto", "alongamento",
    "contraste_int_ext", "textura_relativa", "razao_bordas", "nitidez_borda",
    "gradiente_profundidade", "fracao_toca_borda_imagem",
    "bbox_x", "bbox_y", "bbox_largura", "bbox_altura",
    "rostos_borrados", "metadados_removidos", "versao_algoritmo", "explicacao",
]


def linha_csv(nome: str, res: dict, san: dict) -> dict:
    m = res["metricas"]
    cand = m["candidatas"][0] if m["candidatas"] else {}
    # quando há detecção, as medidas são da detecção principal; senão, da maior candidata
    if res["deteccoes"]:
        d = res["deteccoes"][0]
        cand = next((c for c in m["candidatas"] if c["x"] == d["x"] and c["y"] == d["y"]), cand)
    row = {
        "arquivo": nome,
        "classificacao": res["classificacao"],
        "rotulo": res["rotulo"],
        "pontuacao": res["pontuacao"],
        "decisao": m["decisao"],
        "num_deteccoes": len(res["deteccoes"]),
        "qualidade_adequada": m["qualidade_adequada"],
        "rostos_borrados": san.get("rostos_borrados", 0),
        "metadados_removidos": san.get("metadados_removidos", True),
        "versao_algoritmo": res["versao_algoritmo"],
        "explicacao": " | ".join(res["explicacao"]),
    }
    for k in ("brilho_medio", "contraste_rms", "nitidez_laplaciano", "limiar_otsu", "limiar_robusto",
              "limiar_aplicado", "percentual_mascara", "num_candidatas"):
        row[k] = m.get(k)
    for k in ("area_relativa", "circularidade", "solidez", "razao_aspecto", "alongamento", "contraste_int_ext",
              "textura_relativa", "razao_bordas", "nitidez_borda", "gradiente_profundidade",
              "fracao_toca_borda_imagem"):
        row[k] = cand.get(k, "")
    row["bbox_x"], row["bbox_y"] = cand.get("x", ""), cand.get("y", "")
    row["bbox_largura"], row["bbox_altura"] = cand.get("largura", ""), cand.get("altura", "")
    return row


def processar(entrada: Path, saida: Path, sanitizar: bool = True) -> list[dict]:
    saida.mkdir(parents=True, exist_ok=True)
    arquivos = sorted(p for p in entrada.iterdir() if p.is_file() and p.suffix.lower() in EXTENSOES)
    if not arquivos:
        print(f"Nenhuma imagem encontrada em {entrada}")
        return []
    linhas, completos = [], []
    for p in arquivos:
        data = p.read_bytes()
        try:
            validate_image_bytes(data, MAX_BYTES)
            san = {"metadados_removidos": False, "rostos_borrados": 0}
            if sanitizar:
                data, san = sanitize_image_with_report(data, max_side=1600, blur_faces=True)
            result = analyze_image(data)
        except VisionError as exc:
            print(f"[ERRO] {p.name}: {exc.code} — {exc.message}")
            linhas.append({"arquivo": p.name, "classificacao": "ERRO", "rotulo": exc.message, "decisao": exc.code})
            continue
        res = result.to_dict()
        pasta = saida / p.stem
        pasta.mkdir(parents=True, exist_ok=True)
        for etapa, conteudo in result.encode_stages(".jpg", 85).items():
            (pasta / f"{etapa}.jpg").write_bytes(conteudo)
        painel = montage(result.stages, STAGE_ORDER, cols=4, cell_w=360)
        cv2.imwrite(str(pasta / "painel_etapas.jpg"), painel, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
        completo = {"arquivo": p.name, "sanitizacao": san, **res}
        (pasta / "resultado.json").write_text(json.dumps(completo, ensure_ascii=False, indent=2), encoding="utf-8")
        completos.append(completo)
        linhas.append(linha_csv(p.name, res, san))
        print(f"{p.name:40s} {res['classificacao']:17s} pontuação={res['pontuacao']:.2f}")

    with open(saida / "dados_extraidos.csv", "w", newline="", encoding="utf-8") as fh:
        wr = csv.DictWriter(fh, fieldnames=CSV_COLUNAS, extrasaction="ignore")
        wr.writeheader()
        for row in linhas:
            wr.writerow(row)
    meta = {
        "gerado_em": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "pasta_entrada": str(entrada.relative_to(ROOT)) if entrada.is_relative_to(ROOT) else str(entrada),
        "versao_algoritmo": ALGORITHM_VERSION,
        "sanitizado_antes_da_analise": sanitizar,
        "aviso": "Pontuação heurística (não é probabilidade). Triagem requer revisão humana.",
        "imagens": completos,
    }
    (saida / "dados_extraidos.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n{len(completos)} imagem(ns) processada(s). Resultados em {saida}")
    return linhas


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Analisa todas as imagens de uma pasta (AcessaCidade).")
    ap.add_argument("--entrada", type=Path, default=ROOT / "data" / "samples" / "fotos")
    ap.add_argument("--saida", type=Path, default=COMPONENT / "results")
    ap.add_argument("--sem-sanitizar", action="store_true", help="analisa o arquivo bruto (não recomendado)")
    args = ap.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    processar(args.entrada.resolve(), args.saida.resolve(), sanitizar=not args.sem_sanitizar)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
