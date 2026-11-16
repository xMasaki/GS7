"""Testes da documentação e dos scripts de entrega da disciplina 05 (RPA)."""
from __future__ import annotations

import importlib.util
import re
from pathlib import Path

import pytest

BASE = Path(__file__).resolve().parents[1]
DOCS = BASE / "docs"

DOCS_ESPERADOS = [
    "ANALISE_RPA_VS_API.md", "BUSINESS_CASE.md", "CONFIGURACAO_SELETORES.md", "INSTRUCOES_UIPATH_STUDIO.md",
    "ROTEIRO_VIDEO_RPA.md", "EVIDENCIAS_NECESSARIAS.md", "RELATORIO_RPA.md", "INSTRUCOES_ZIP_ENTREGA.md",
]


@pytest.mark.parametrize("nome", DOCS_ESPERADOS)
def test_documento_existe_e_nao_esta_vazio(nome):
    p = DOCS / nome
    assert p.is_file(), nome
    assert len(p.read_text(encoding="utf-8")) > 800


def test_arquivos_raiz_da_disciplina():
    for nome in ("README.md", "PENDENCIAS_E_ACOES_MANUAIS.txt", "process-mapping/MAPEAMENTO_PROCESSOS.md"):
        assert (BASE / nome).is_file(), nome
    pend = (BASE / "PENDENCIAS_E_ACOES_MANUAIS.txt").read_text(encoding="utf-8")
    for secao in ("A.", "B.", "C.", "D.", "E.", "F."):
        assert re.search(rf"^{re.escape(secao)} ", pend, re.M), f"seção {secao} ausente nas pendências"


def test_relatorio_nao_inventa_link_do_video():
    """O relatório só pode ter um link de vídeo se a equipe o informou em dados_entrega.yaml (links.videos."05")."""
    import yaml

    texto = (DOCS / "RELATORIO_RPA.md").read_text(encoding="utf-8")
    dados = yaml.safe_load((BASE.parent / "dados_entrega.yaml").read_text(encoding="utf-8")) or {}
    informado = str(((dados.get("links") or {}).get("videos") or {}).get("05") or "").strip().rstrip("/")
    links_de_video = set(re.findall(r"https?://(?:www\.)?(?:youtu|drive\.google|onedrive)[^\s)>\]`]*", texto))
    if informado:
        assert links_de_video <= {informado}, "link de vídeo diferente do informado em dados_entrega.yaml"
    else:
        assert "[PREENCHER: link do vídeo]" in texto
        assert not links_de_video
    assert "79,4" in texto  # valor calculado do assessment


def test_mapeamento_tem_mermaid_as_is_e_to_be():
    texto = (BASE / "process-mapping" / "MAPEAMENTO_PROCESSOS.md").read_text(encoding="utf-8")
    assert texto.count("```mermaid") >= 2


def test_script_zip_nao_contem_link_e_exclui_pastas_locais():
    texto = (BASE / "scripts" / "gerar_zip_entrega.ps1").read_text(encoding="utf-8")
    assert "link_video.txt" in texto and "RELATORIO_RPA_AcessaCidade.pdf" in texto
    for pasta in (".local", ".objects"):
        assert f'"{pasta}"' in texto
    assert not re.search(r"https?://", texto)


def test_gerar_pdf_converte_markdown_em_html():
    spec = importlib.util.spec_from_file_location("gerar_pdf_rpa", BASE / "scripts" / "gerar_pdf_relatorio.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    html = mod.gerar_html((DOCS / "RELATORIO_RPA.md").read_text(encoding="utf-8"))
    assert "<table>" in html and "<h1>" in html and "charset='utf-8'" in html
