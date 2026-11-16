"""Testes de tools/preencher_marcadores.py — o script só pode trocar marcadores com correspondência exata e
com valor informado; nunca inventa dado, nunca mexe em marcador sem correspondência."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

import pytest
import yaml

RAIZ = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("preencher_marcadores", RAIZ / "tools" / "preencher_marcadores.py")
pm = importlib.util.module_from_spec(_spec)
sys.modules["preencher_marcadores"] = pm
_spec.loader.exec_module(pm)


def M(texto: str) -> str:
    """Marcador completo, montado em pedaços para este teste não contar como ocorrência no inventário."""
    return "[" + "PREENCHER" + ": " + texto + "]"


BARE = "[" + "PREENCHER" + "]"
EM = "—"
PASTA03 = "03-Business-Intelligence-Startup"


def dados_yaml(tmp_path: Path, **extra) -> Path:
    base = {"equipe": {"nome": "", "integrantes": []},
            "links": {"mvp": "", "repositorio": "", "video_pitch": "", "videos": {}}}
    for chave, valor in extra.items():
        grupo, campo = chave.split("__")
        base[grupo][campo] = valor
    caminho = tmp_path / "dados_entrega.yaml"
    caminho.write_text(yaml.safe_dump(base, allow_unicode=True), encoding="utf-8")
    return caminho


def escrever(raiz: Path, rel: str, texto: str, bom: bool = False) -> Path:
    p = raiz / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes((("﻿" if bom else "") + texto).encode("utf-8"))
    return p


def rodar(raiz: Path, dados: Path, *args: str) -> int:
    return pm.main(["--raiz", str(raiz), "--dados", str(dados), "--sem-regenerar", *args])


def snapshot(raiz: Path) -> dict[str, str]:
    return {p.relative_to(raiz).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in raiz.rglob("*") if p.is_file() and pm.BACKUP_DIR not in p.parts}


def test_yaml_vazio_nao_altera_nada(tmp_path, capsys):
    escrever(tmp_path, "README.md", f"MVP: {M('URL_MVP')}\r\n")
    antes = snapshot(tmp_path / ".")
    assert rodar(tmp_path, dados_yaml(tmp_path), "--sim") == 0
    assert "Nada a fazer" in capsys.readouterr().out
    assert {k: v for k, v in snapshot(tmp_path).items() if k != "dados_entrega.yaml"} == \
        {k: v for k, v in antes.items() if k != "dados_entrega.yaml"}
    assert not (tmp_path / pm.BACKUP_DIR).exists()
    assert not (tmp_path / "docs" / "RELATORIO_PREENCHIMENTO.md").exists()


def test_troca_so_o_mapeado_e_preserva_bom_e_crlf(tmp_path):
    original = (f"| Equipe | {M('nome da equipe')} |\r\n"
                f"- MVP: {M('URL pública do MVP')}/#/assistente\r\n"
                f"- Repo: {M('URL_REPOSITORIO')}/tree/main/01\r\n"
                f"- Sem correspondência: {BARE} | {M('papel')} | {M('URL pública')} | {M('nome do integrante N')}\r\n")
    p = escrever(tmp_path, "README.md", original, bom=True)
    dados = dados_yaml(tmp_path, equipe__nome="Equipe Alfa", links__mvp="https://mvp.example.org/",
                       links__repositorio="https://github.com/alfa/app.git")
    assert rodar(tmp_path, dados, "--sim") == 0
    bruto = p.read_bytes()
    assert bruto.startswith(b"\xef\xbb\xbf")
    texto = bruto.decode("utf-8-sig")
    assert "| Equipe | Equipe Alfa |\r\n" in texto
    assert "- MVP: https://mvp.example.org/#/assistente\r\n" in texto      # sem barra dupla antes do sufixo
    assert "- Repo: https://github.com/alfa/app/tree/main/01\r\n" in texto  # .git removido
    assert f"{BARE} | {M('papel')} | {M('URL pública')} | {M('nome do integrante N')}" in texto
    assert texto.count("\r\n") == original.count("\r\n") and "\n" not in texto.replace("\r\n", "")


def test_dry_run_e_recusa_nao_gravam(tmp_path, monkeypatch):
    p = escrever(tmp_path, "README.md", f"{M('URL_MVP')}\n")
    antes = p.read_bytes()
    dados = dados_yaml(tmp_path, links__mvp="https://mvp.example.org")
    assert rodar(tmp_path, dados, "--dry-run") == 0 and p.read_bytes() == antes
    monkeypatch.setattr("builtins.input", lambda *_: "n")
    assert rodar(tmp_path, dados) == 1 and p.read_bytes() == antes

    def sem_entrada(*_):
        raise EOFError
    monkeypatch.setattr("builtins.input", sem_entrada)
    assert rodar(tmp_path, dados) == 1 and p.read_bytes() == antes
    monkeypatch.setattr("builtins.input", lambda *_: "s")
    assert rodar(tmp_path, dados) == 0 and b"mvp.example.org" in p.read_bytes()
    assert (tmp_path / pm.BACKUP_DIR).exists()


@pytest.mark.parametrize("extra", [
    {"links__video_pitch": "http://inseguro.example.org/v"},
    {"links__repositorio": "github.com/sem/esquema"},
    {"equipe__nome": "Equipe | com barra"},
    {"equipe__nome": "Equipe " + M("nome da equipe")},
    {"links__mvp": "https://x.example.org/<id>"},
])
def test_valor_invalido_aborta_sem_alterar(tmp_path, capsys, extra):
    p = escrever(tmp_path, "README.md", f"{M('URL_MVP')} {M('nome da equipe')}\n")
    antes = p.read_bytes()
    assert rodar(tmp_path, dados_yaml(tmp_path, **extra), "--sim") == 2
    assert "ERRO" in capsys.readouterr().err and p.read_bytes() == antes


def test_arquivo_de_dados_ausente_ou_invalido(tmp_path):
    assert rodar(tmp_path, tmp_path / "nao_existe.yaml") == 2
    ruim = tmp_path / "ruim.yaml"
    ruim.write_text("equipe: [1, 2\n", encoding="utf-8")
    assert rodar(tmp_path, ruim) == 2


def test_integrante_parcial_nao_gera_composicoes_incompletas(tmp_path):
    p = escrever(tmp_path, "README.md",
                 f"A {M('Integrante 1')} B {M('nomes e RMs dos integrantes')} C {M('integrante 1 ' + EM + ' RM')}\n")
    integrantes = [{"nome": "Ana Teste", "rm": "", "papel": ""}]
    assert rodar(tmp_path, dados_yaml(tmp_path, equipe__integrantes=integrantes), "--sim") == 0
    assert p.read_text(encoding="utf-8") == (
        f"A Ana Teste B {M('nomes e RMs dos integrantes')} C {M('integrante 1 ' + EM + ' RM')}\n")
    # com RM, as composições passam a ser preenchidas
    integrantes[0]["rm"] = "RM123"
    assert rodar(tmp_path, dados_yaml(tmp_path, equipe__integrantes=integrantes), "--sim") == 0
    assert p.read_text(encoding="utf-8") == f"A Ana Teste B Ana Teste (RM123) C Ana Teste {EM} RM123\n"


def test_tabela_de_integrantes_e_linhas_do_pitch(tmp_path):
    tabela = (f"| {M('Integrante 1')} | {BARE} | {BARE} |\n| {M('Integrante 2')} | {BARE} | {BARE} |\n"
              f"| {M('Integrante 3')} | {BARE} | {BARE} |\n")
    pitch = (f"> {M('Integrante 1 ' + EM + ' nome')}, {M('papel em poucas palavras')}.\n"
             f"> {M('Integrante 2 ' + EM + ' nome')}, {M('papel')}.\n")
    escrever(tmp_path, f"{PASTA03}/docs/DOCUMENTO_DE_ENTREGA_BI.md", tabela)
    escrever(tmp_path, f"{PASTA03}/pitch/ROTEIRO_PITCH.md", pitch)
    integrantes = [{"nome": "Ana", "rm": "RM1", "papel": "Backend"}, {"nome": "Bia", "rm": "RM2", "papel": ""}]
    assert rodar(tmp_path, dados_yaml(tmp_path, equipe__integrantes=integrantes), "--sim") == 0
    assert (tmp_path / PASTA03 / "docs" / "DOCUMENTO_DE_ENTREGA_BI.md").read_text(encoding="utf-8") == (
        f"| Ana | RM1 | Backend |\n| Bia | RM2 | {BARE} |\n| {M('Integrante 3')} | {BARE} | {BARE} |\n")
    assert (tmp_path / PASTA03 / "pitch" / "ROTEIRO_PITCH.md").read_text(encoding="utf-8") == (
        f"> Ana, Backend.\n> Bia, {M('papel')}.\n")


def test_video_e_resolvido_por_disciplina(tmp_path):
    corpo = f"V: {M('link do vídeo')}\n"
    for rel in ("README.md", f"{PASTA03}/README.md", "02-Big-Data-Architecture/docs/R.md",
                "05-Robotic-Process-Automation/docs/R.md"):
        escrever(tmp_path, rel, corpo)
    dados = dados_yaml(tmp_path, links__video_pitch="https://youtu.be/pitch", links__videos={"02": "https://youtu.be/dois"})
    assert rodar(tmp_path, dados, "--sim") == 0
    lido = lambda rel: (tmp_path / rel).read_text(encoding="utf-8")  # noqa: E731
    assert lido("README.md") == "V: https://youtu.be/pitch\n"
    assert lido(f"{PASTA03}/README.md") == "V: https://youtu.be/pitch\n"
    assert lido("02-Big-Data-Architecture/docs/R.md") == "V: https://youtu.be/dois\n"
    assert lido("05-Robotic-Process-Automation/docs/R.md") == corpo  # sem vídeo da 05 no YAML: intacto


def test_idempotente_com_backup_e_relatorio_sem_dado_pessoal(tmp_path):
    escrever(tmp_path, "README.md", f"{M('nome da equipe')} {M('Integrante 1')} {M('URL_MVP')} {BARE}\n")
    integrantes = [{"nome": "Fulana Privada", "rm": "RM987", "papel": ""}]
    dados = dados_yaml(tmp_path, equipe__nome="Equipe Zeta", equipe__integrantes=integrantes,
                       links__mvp="https://mvp.example.org")
    assert rodar(tmp_path, dados, "--sim") == 0
    backups = list((tmp_path / pm.BACKUP_DIR).iterdir())
    assert len(backups) == 1
    assert M("URL_MVP") in (backups[0] / "README.md").read_text(encoding="utf-8")   # backup = original
    relatorio = (tmp_path / "docs" / "RELATORIO_PREENCHIMENTO.md").read_text(encoding="utf-8")
    assert "Substituições gravadas: **3**" in relatorio
    assert "Fulana" not in relatorio and "RM987" not in relatorio and "example.org" not in relatorio
    assert "[" + "PREENCHER" not in relatorio       # o relatório não conta como pendência no inventário
    depois = snapshot(tmp_path)
    assert rodar(tmp_path, dados, "--sim") == 0      # segunda execução: nada a trocar
    assert snapshot(tmp_path) == depois
    assert len(list((tmp_path / pm.BACKUP_DIR).iterdir())) == 1


def test_links_entrega_yaml_preserva_comentarios_e_nao_sobrescreve(tmp_path):
    corpo = ('# cabeçalho\nurl_video: ""        # comentário do vídeo\nurl_mvp: ""  # comentário mvp\n'
             'url_repositorio: "https://github.com/ja/existe"  # já preenchido\n')
    p = escrever(tmp_path, f"{PASTA03}/docs/links_entrega.yaml", corpo)
    dados = dados_yaml(tmp_path, links__video_pitch="https://youtu.be/pitch", links__mvp="http://fqdn.example.org:8000",
                       links__repositorio="https://github.com/novo/repo")
    assert rodar(tmp_path, dados, "--sim") == 0
    assert p.read_text(encoding="utf-8") == (
        '# cabeçalho\nurl_video: "https://youtu.be/pitch"        # comentário do vídeo\n'
        'url_mvp: ""  # comentário mvp\n'                                  # http:// não vai para o yaml (exige https)
        'url_repositorio: "https://github.com/ja/existe"  # já preenchido\n')  # valor existente não é sobrescrito


def test_escopo_nao_toca_pendencias_testes_scripts_e_gerados(tmp_path):
    corpo = f"{M('URL_MVP')}\n"
    intactos = ["PENDENCIAS_E_ACOES_MANUAIS.txt", f"{PASTA03}/PENDENCIAS_E_ACOES_MANUAIS.txt", "script.py",
                "docs/INVENTARIO_PREENCHER.md", f"{PASTA03}/tests/doc.md", "data/leia.md",
                f"{PASTA03}/business-model/LEAN_CANVAS.md", "app/frontend/sobre.js", "infra/x.tfvars.example"]
    for rel in intactos:
        escrever(tmp_path, rel, corpo)
    escrever(tmp_path, "docs/FICHA.md", corpo)
    assert rodar(tmp_path, dados_yaml(tmp_path, links__mvp="https://mvp.example.org"), "--sim") == 0
    for rel in intactos:
        assert (tmp_path / rel).read_text(encoding="utf-8") == corpo, rel
    assert (tmp_path / "docs" / "FICHA.md").read_text(encoding="utf-8") == "https://mvp.example.org\n"


def test_lean_canvas_json_continua_json_valido_e_o_gerado_nao_e_editado(tmp_path):
    fonte = json.dumps({"equipe": M("nome da equipe / startup"), "x": 1}, ensure_ascii=False, indent=2) + "\n"
    escrever(tmp_path, f"{PASTA03}/business-model/lean_canvas.json", fonte)
    gerado = escrever(tmp_path, f"{PASTA03}/business-model/LEAN_CANVAS.md", f"Equipe: {M('nome da equipe / startup')}\n")
    assert rodar(tmp_path, dados_yaml(tmp_path, equipe__nome='Equipe "Aspas" \\ Ltda'), "--sim") == 0
    dados = json.loads((tmp_path / PASTA03 / "business-model" / "lean_canvas.json").read_text(encoding="utf-8"))
    assert dados == {"equipe": 'Equipe "Aspas" \\ Ltda', "x": 1}
    assert M("nome da equipe / startup") in gerado.read_text(encoding="utf-8")  # só o gerador atualiza este


def test_dry_run_no_repositorio_real_nao_grava_nada(tmp_path, capsys):
    antes = snapshot(RAIZ)
    dados = dados_yaml(tmp_path, equipe__nome="Equipe Fictícia de Teste", links__mvp="https://mvp.example.invalid",
                       links__repositorio="https://github.com/teste/teste", links__video_pitch="https://youtu.be/teste")
    assert pm.main(["--dados", str(dados), "--dry-run", "--sem-diff"]) == 0
    saida = capsys.readouterr().out
    assert "nada foi gravado" in saida and "TOTAL" in saida
    assert snapshot(RAIZ) == antes


def test_dados_entrega_do_repositorio_e_valido():
    d = pm.carregar_dados(RAIZ / "dados_entrega.yaml")   # vazio ou preenchido: nunca pode estar inválido
    assert isinstance(d, pm.Dados)


def test_todas_as_chaves_da_tabela_de_correspondencia_resolvem():
    d = pm.Dados()
    for marcador, chave in pm.ALIASES.items():
        assert marcador.startswith("[" + "PREENCHER: ") and marcador.endswith("]")
        campo, valor = pm.resolver(chave, d, "README.md")
        assert campo and valor == ""      # sem dados informados, nenhum valor aparece do nada
