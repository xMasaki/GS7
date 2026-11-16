"""Permite `python -m acessacidade_pipeline [--sem-api]`."""
from .run_pipeline import main

if __name__ == "__main__":
    raise SystemExit(main())
