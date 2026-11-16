"""Remove metadados (EXIF/GPS), reduz e borra rostos de todas as fotos de uma pasta.

Use ANTES de versionar ou compartilhar fotos reais. As fotos originais não são alteradas;
as versões limpas são gravadas (sempre em JPEG) na pasta de saída.

Uso (na raiz do repositório):
    .venv\\Scripts\\python.exe 04-Applied-Computer-Vision\\scripts\\sanitizar_fotos.py ^
        --entrada C:\\caminho\\fotos_brutas --saida 04-Applied-Computer-Vision\\samples\\real\\fotos
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

COMPONENT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(COMPONENT / "src"))

from acessacidade_vision import VisionError, sanitize_image_with_report  # noqa: E402

EXTENSOES = {".jpg", ".jpeg", ".png", ".webp"}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Sanitiza fotos (remove EXIF/GPS, reduz, borra rostos).")
    ap.add_argument("--entrada", type=Path, required=True)
    ap.add_argument("--saida", type=Path, required=True)
    ap.add_argument("--max-lado", type=int, default=1600)
    args = ap.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    if args.entrada.resolve() == args.saida.resolve():
        print("Use uma pasta de saída diferente da pasta de entrada.")
        return 2
    args.saida.mkdir(parents=True, exist_ok=True)
    n = 0
    for p in sorted(args.entrada.iterdir()):
        if not (p.is_file() and p.suffix.lower() in EXTENSOES):
            continue
        try:
            data, rep = sanitize_image_with_report(p.read_bytes(), max_side=args.max_lado, blur_faces=True,
                                                   max_bytes=30 * 1024 * 1024)
        except VisionError as exc:
            print(f"[IGNORADA] {p.name}: {exc.message}")
            continue
        destino = args.saida / (p.stem + ".jpg")
        destino.write_bytes(data)
        n += 1
        aviso = "" if rep["detector_rostos_disponivel"] else " (detector de rostos indisponível — confira manualmente)"
        print(f"{p.name} -> {destino.name}: {rep['largura_final']}x{rep['altura_final']}, "
              f"rostos borrados: {rep['rostos_borrados']}{aviso}")
    print(f"{n} foto(s) sanitizada(s) em {args.saida}. Confira visualmente se não restou pessoa ou placa identificável.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
