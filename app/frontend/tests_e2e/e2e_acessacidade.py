#!/usr/bin/env python
"""Teste ponta a ponta (E2E) do frontend AcessaCidade contra um backend REAL em execução.

Não é coletado pelo pytest (o nome do arquivo não começa com ``test_``). É um script executável:

    python app/frontend/tests_e2e/e2e_acessacidade.py --url http://127.0.0.1:8000

Opções úteis:
    --shots <pasta>     salva screenshots de cada etapa (ex.: evidencias/mvp_local)
    --fotos <pasta>     pasta com as fotos SINTÉTICAS (padrão: data/samples/fotos)
    --navegador msedge  canal do Chromium usado pelo Playwright (padrão: msedge; use "chromium"
                        se tiver rodado "playwright install chromium")

Token da equipe (opcional): o script NUNCA recebe token por argumento de linha de comando.
Para exercitar a mudança de status em #/revisao, defina a variável de ambiente
``ACESSACIDADE_E2E_ADMIN_TOKEN`` com o mesmo valor de ``ADMIN_TOKEN`` do servidor. Sem ela, o
script verifica apenas que um token inválido é recusado com mensagem clara (401/403).

Pré-requisitos: backend rodando com SEED_DEMO_DATA=true (dados SIMULADOS) e o assistente em modo
básico (sem OPENROUTER_API_KEY) ou com IA — o script aceita as duas fontes, mas registra qual foi.

O que é verificado (larguras 1280 px e 390 px):
  início com indicadores -> registrar denúncia com foto sintética e outra sem foto (?canal=rpa)
  -> protocolo em #protocolo-gerado -> detalhe com as 7 etapas (imagens carregadas)
  -> consultar/filtrar/paginar -> análise avulsa -> assistente responde e referencia o protocolo
  -> painel com gráficos e seção analítica -> revisão com token muda o status -> sobre -> 404.
  Também: sem erros de console/CSP, sem respostas HTTP 4xx/5xx inesperadas, sem rolagem
  horizontal, link "Pular para o conteúdo" e formulário alcançáveis por Tab, foco visível.

Código de saída: 0 se todas as verificações passarem; 1 caso contrário.
"""
from __future__ import annotations

import argparse
import os
import re
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

try:
    from playwright.sync_api import Page, sync_playwright
except ImportError:  # pragma: no cover
    print("Playwright não está instalado. Use: pip install playwright", file=sys.stderr)
    sys.exit(2)

REPO_ROOT = Path(__file__).resolve().parents[3]
ETAPAS = ["original", "cinza", "filtrada", "contraste", "bordas", "mascara", "contornos"]
PROTOCOLO_RE = re.compile(r"^AC-\d{4}-\d{6}$")
TIMEOUT_MS = 30_000


def esperar(page: Page, expressao: str, arg=None, timeout: int = TIMEOUT_MS):
    """Espera uma condição JS ficar verdadeira usando page.evaluate em laço.

    Não usa page.wait_for_function porque, sob a CSP "script-src 'self'" da aplicação, o polling
    do Playwright pode depender de eval e é bloqueado (EvalError)."""
    limite = time.time() + timeout / 1000
    while True:
        valor = page.evaluate(expressao, arg)
        if valor:
            return valor
        if time.time() > limite:
            raise TimeoutError(f"Condição não satisfeita em {timeout} ms: {expressao[:120]}")
        page.wait_for_timeout(150)


@dataclass
class Resultado:
    ok: list[str] = field(default_factory=list)
    falhas: list[str] = field(default_factory=list)

    def check(self, condicao: bool, descricao: str, detalhe: str = "") -> bool:
        if condicao:
            self.ok.append(descricao)
            print(f"  [OK]    {descricao}")
        else:
            msg = f"{descricao}" + (f" -- {detalhe}" if detalhe else "")
            self.falhas.append(msg)
            print(f"  [FALHA] {msg}")
        return condicao


@dataclass
class Monitor:
    """Coleta erros de console, de página e respostas HTTP >= 400 de uma página."""

    erros_console: list[str] = field(default_factory=list)
    erros_pagina: list[str] = field(default_factory=list)
    respostas_ruins: list[tuple[str, str, int]] = field(default_factory=list)
    falhas_rede: list[str] = field(default_factory=list)
    esperadas: list[tuple[str, str, int]] = field(default_factory=list)  # (método, regex url, status)

    def anexar(self, page: Page) -> None:
        def on_console(msg):
            if msg.type == "error" or "Content Security Policy" in msg.text:
                self.erros_console.append(f"{msg.type}: {msg.text}")

        def on_response(resp):
            if resp.status >= 400:
                self.respostas_ruins.append((resp.request.method, resp.url, resp.status))

        def on_failed(req):
            falha = req.failure or ""
            if "ERR_ABORTED" in falha or "NS_BINDING_ABORTED" in falha:
                return  # requisições canceladas de propósito (troca de rota / AbortController)
            self.falhas_rede.append(f"{req.method} {req.url}: {falha}")

        page.on("console", on_console)
        page.on("pageerror", lambda exc: self.erros_pagina.append(str(exc)))
        page.on("response", on_response)
        page.on("requestfailed", on_failed)

    def esperar(self, metodo: str, padrao_url: str, status: int) -> None:
        self.esperadas.append((metodo, padrao_url, status))

    def _esperada(self, metodo: str, url: str, status: int) -> bool:
        return any(m == metodo and re.search(p, url) and s == status for m, p, s in self.esperadas)

    def inesperadas(self) -> list[tuple[str, str, int]]:
        return [r for r in self.respostas_ruins if not self._esperada(*r)]

    def console_inesperado(self) -> list[str]:
        saida = []
        status_esperados = {str(s) for _, _, s in self.esperadas}
        for e in self.erros_console:
            m = re.search(r"status of (\d{3})", e)
            if m and m.group(1) in status_esperados and "Failed to load resource" in e:
                continue  # o navegador loga a resposta 4xx esperada (ex.: token inválido de propósito)
            saida.append(e)
        return saida


class E2E:
    def __init__(self, base_url: str, shots: Path | None, fotos: Path, admin_token: str):
        self.base = base_url.rstrip("/")
        self.shots = shots
        self.fotos = fotos
        self.admin_token = admin_token
        self.r = Resultado()
        self.protocolo_foto = ""
        self.protocolo_rpa = ""
        self.id_foto = 0
        self.monitor: Monitor | None = None

    # ------------------------------------------------------------- utilidades
    def ir(self, page: Page, rota: str) -> None:
        url = f"{self.base}/#{rota}"
        if page.url.startswith(self.base + "/") and "#" in page.url:
            page.evaluate("h => { window.location.hash = h; }", rota)
        else:
            page.goto(url, wait_until="domcontentloaded")
        esperar(page, 
            "() => { const h = document.querySelector('#conteudo h1'); return h && h.textContent.trim().length > 0; }",
            timeout=TIMEOUT_MS,
        )

    def foto(self, page: Page, nome: str) -> None:
        if not self.shots:
            return
        self.shots.mkdir(parents=True, exist_ok=True)
        page.wait_for_timeout(250)
        page.screenshot(path=str(self.shots / nome), full_page=True)
        print(f"  [print] {nome}")

    def sem_rolagem_horizontal(self, page: Page, tela: str) -> None:
        largura = page.viewport_size["width"]
        sw = page.evaluate("() => document.documentElement.scrollWidth")
        self.r.check(sw <= largura + 1, f"{tela}: sem rolagem horizontal em {largura}px", f"scrollWidth={sw}")

    def titulo_ok(self, page: Page, trecho: str, tela: str) -> None:
        t = page.title()
        self.r.check(trecho.lower() in t.lower(), f"{tela}: document.title contém '{trecho}'", f"title={t!r}")

    def aguardar_sem_carregando(self, page: Page, seletor: str) -> None:
        esperar(page, 
            "s => { const e = document.querySelector(s); return e && !e.closest('[aria-busy=\"true\"]') && !e.querySelector('[aria-busy=\"true\"], .carregando'); }",
            arg=seletor,
            timeout=TIMEOUT_MS,
        )

    def imagens_carregadas(self, page: Page, seletor_lista: str, tela: str) -> None:
        imgs = page.locator(f"{seletor_lista} img")
        n = imgs.count()
        self.r.check(n == 7, f"{tela}: 7 imagens de etapas", f"encontradas={n}")
        for i in range(n):
            imgs.nth(i).scroll_into_view_if_needed()
        esperar(page, 
            "s => Array.from(document.querySelectorAll(s + ' img')).every(i => i.complete && i.naturalWidth > 0)",
            arg=seletor_lista,
            timeout=TIMEOUT_MS,
        )
        larguras = page.eval_on_selector_all(f"{seletor_lista} img", "els => els.map(i => i.naturalWidth)")
        self.r.check(len(larguras) == 7 and all(w > 0 for w in larguras), f"{tela}: todas as etapas com naturalWidth>0", str(larguras))

    def verificar_etapas_em_ordem(self, page: Page, seletor_lista: str, tela: str, por_url: bool) -> None:
        legendas = page.eval_on_selector_all(f"{seletor_lista} figcaption", "els => els.map(e => e.textContent.trim())")
        self.r.check(
            len(legendas) == 7 and all(legendas[i].startswith(f"{i + 1}.") for i in range(len(legendas))),
            f"{tela}: 7 legendas numeradas em ordem",
            str([lg[:25] for lg in legendas]),
        )
        if por_url:
            srcs = page.eval_on_selector_all(f"{seletor_lista} img", "els => els.map(e => e.getAttribute('src'))")
            ordem = [s.rsplit("/", 1)[-1] for s in srcs]
            self.r.check(ordem == ETAPAS, f"{tela}: etapas na ordem do contrato", str(ordem))

    # --------------------------------------------------------------- fluxos
    def teclado(self, page: Page) -> None:
        print("\n== Navegação por teclado")
        page.goto(f"{self.base}/#/", wait_until="domcontentloaded")
        page.wait_for_selector("#titulo-inicio")
        page.keyboard.press("Tab")
        ativo = page.evaluate("() => document.activeElement && document.activeElement.id")
        self.r.check(ativo == "link-pular", "Primeiro Tab chega ao link 'Pular para o conteúdo'", f"ativo={ativo}")
        page.wait_for_timeout(100)
        caixa = page.evaluate(
            "() => { const r = document.activeElement.getBoundingClientRect(); return [r.top, r.width, r.height]; }"
        )
        self.r.check(caixa[1] > 0 and caixa[2] > 0 and caixa[0] >= 0, "Link de pular conteúdo fica visível ao receber foco", str(caixa))
        page.keyboard.press("Enter")
        page.wait_for_timeout(200)
        foco = page.evaluate("() => document.activeElement && document.activeElement.tagName")
        self.r.check(foco in ("H1", "MAIN"), "Enter no link de pular move o foco para o conteúdo principal", f"foco={foco}")

        self.ir(page, "/registrar")
        page.wait_for_selector("#campo-tipo option[value='BURACO_CALCADA']", state="attached")
        page.evaluate("() => document.activeElement && document.activeElement.blur()")
        alcancou = False
        for _ in range(60):
            page.keyboard.press("Tab")
            if page.evaluate("() => document.activeElement && document.activeElement.id") == "campo-nome":
                alcancou = True
                break
        self.r.check(alcancou, "Tab alcança o primeiro campo do formulário (#campo-nome)")
        if alcancou:
            estilo = page.evaluate(
                "() => { const s = getComputedStyle(document.activeElement); return [s.outlineStyle, s.outlineWidth, s.boxShadow]; }"
            )
            self.r.check(estilo[0] != "none" or estilo[2] != "none", "Campo focado tem indicador de foco visível", str(estilo))

    def inicio(self, page: Page, sufixo: str, n: str) -> None:
        print(f"\n== Início ({sufixo})")
        self.ir(page, "/")
        page.wait_for_selector("#conteudo .indicadores .indicador__valor", timeout=TIMEOUT_MS)
        valores = page.eval_on_selector_all(".indicador__valor", "els => els.map(e => e.textContent.trim())")
        self.r.check(len(valores) >= 4 and all(re.search(r"\d", v) for v in valores), "Início: indicadores numéricos carregados", str(valores))
        recentes = page.locator("section[aria-labelledby='titulo-recentes'] .lista-cartoes > li").count()
        self.r.check(1 <= recentes <= 5, "Início: até 5 ocorrências recentes", f"recentes={recentes}")
        texto = page.inner_text("#conteudo")
        self.r.check("ODS 11" in texto, "Início: bloco ODS 11 presente")
        self.r.check("não é um serviço oficial" in texto, "Início: aviso de que não é serviço oficial")
        self.r.check(page.locator("#conteudo a[href='#/registrar']").count() >= 1, "Início: botão 'Registrar denúncia'")
        self.titulo_ok(page, "Início", "Início")
        self.sem_rolagem_horizontal(page, "Início")
        self.foto(page, f"{n}_inicio_{sufixo}.png")

    def registrar_com_foto(self, page: Page, n: str) -> None:
        print("\n== Registrar denúncia com foto sintética")
        self.ir(page, "/registrar")
        page.wait_for_selector("#campo-tipo option[value='BURACO_CALCADA']", state="attached")
        # ids, names e data-rpa do contrato (seção 7)
        campos = {
            "campo-nome": "nome", "campo-logradouro": "logradouro", "campo-numero": "numero",
            "campo-bairro": "bairro", "campo-cidade": "cidade", "campo-referencia": "ponto_referencia",
            "campo-tipo": "tipo_obstaculo", "campo-descricao": "descricao", "campo-impacto": "impacto",
            "campo-latitude": "latitude", "campo-longitude": "longitude", "campo-foto": "foto",
            "campo-consentimento": "consentimento",
        }
        for id_, nome in campos.items():
            attrs = page.evaluate(
                "id => { const e = document.getElementById(id); return e ? [e.name, e.dataset.rpa, !!(e.labels && e.labels.length)] : null; }",
                id_,
            )
            self.r.check(attrs is not None and attrs[0] == nome and attrs[1] == nome and attrs[2],
                         f"#{id_}: name/data-rpa='{nome}' e <label>", str(attrs))
        for id_ in ["form-denuncia", "botao-enviar", "resultado-envio", "protocolo-gerado", "erro-envio", "botao-nova-denuncia"]:
            self.r.check(page.locator(f"#{id_}").count() == 1, f"Registrar: #{id_} existe")
        rotulo_tipo = page.eval_on_selector("#campo-tipo option[value='BURACO_CALCADA']", "o => o.textContent.trim()")
        self.r.check(rotulo_tipo == "Buraco na calçada", "Select tipo: texto visível = rótulo do contrato", rotulo_tipo)
        rotulo_imp = page.eval_on_selector("#campo-impacto option[value='RISCO_QUEDA']", "o => o.textContent.trim()")
        self.r.check(rotulo_imp == "Risco de queda ou acidente", "Select impacto: texto visível = rótulo do contrato", rotulo_imp)

        # validação no cliente: envio vazio não chama a API e mostra erros
        page.click("#botao-enviar")
        page.wait_for_selector("#erro-envio:not([hidden])")
        self.r.check(page.locator(".campo-erro:not([hidden])").count() >= 4, "Validação no cliente: erros junto aos campos obrigatórios")
        self.foto(page, f"{n}a_registrar_validacao_desktop.png")

        page.fill("#campo-nome", "Pessoa de teste (simulado)")
        page.fill("#campo-logradouro", "Rua Exemplo do Teste Automatizado")
        page.fill("#campo-numero", "120")
        page.fill("#campo-bairro", "Centro")
        page.fill("#campo-cidade", "Cidade Exemplo")
        page.fill("#campo-referencia", "Em frente ao ponto de ônibus (teste E2E)")
        page.select_option("#campo-tipo", label="Buraco na calçada")
        page.fill("#campo-descricao", "Teste automatizado E2E: buraco na calçada com foto sintética, dificulta a passagem de cadeira de rodas.")
        page.select_option("#campo-impacto", label="Impede a passagem")
        page.set_input_files("#campo-foto", str(self.fotos / "sintetica_buraco_02.jpg"))
        page.wait_for_selector("#previa-foto:not([hidden]) img", state="attached")
        self.r.check(page.locator("#previa-foto img").get_attribute("src").startswith("blob:"), "Prévia da foto via URL.createObjectURL")
        page.check("#campo-consentimento")
        self.foto(page, f"{n}b_registrar_preenchido_desktop.png")

        with page.expect_response(lambda r: r.url.endswith("/api/denuncias") and r.request.method == "POST", timeout=60_000) as info:
            page.click("#botao-enviar")
            estado_botao = page.evaluate(
                "() => { const b = document.getElementById('botao-enviar'); return [b.disabled, b.textContent.trim()]; }"
            )
            self.r.check(estado_botao[0] and "Enviando" in estado_botao[1],
                         "Botão de envio desabilitado com 'Enviando e analisando a foto...'", str(estado_botao))
        resp = info.value
        self.r.check(resp.status == 201, "POST /api/denuncias com foto -> 201", f"status={resp.status}")
        corpo = resp.json()
        page.wait_for_selector("#resultado-envio:not([hidden]) #protocolo-gerado")
        protocolo = page.inner_text("#protocolo-gerado").strip()
        self.r.check(bool(PROTOCOLO_RE.match(protocolo)), "#protocolo-gerado contém só o protocolo", repr(protocolo))
        self.r.check(protocolo == corpo.get("protocolo"), "#protocolo-gerado igual ao protocolo da API")
        self.r.check(page.locator("#form-denuncia").is_hidden(), "Formulário oculto após sucesso")
        link = page.locator(f"#resultado-envio a[href='#/denuncia/{protocolo}']").count()
        self.r.check(link >= 1, "Link para #/denuncia/{protocolo} no resultado")
        resumo = page.inner_text("#resumo-resultado")
        rot = (corpo.get("visao") or {}).get("rotulo", "")
        self.r.check(bool(rot) and rot in resumo, "Resumo da triagem exibido no resultado", resumo[:120])
        self.r.check("nome" not in corpo, "Resposta pública não contém o campo nome")
        self.protocolo_foto = protocolo
        self.id_foto = corpo.get("id", 0)
        self.foto(page, f"{n}c_registrar_protocolo_desktop.png")

        page.click("#botao-nova-denuncia")
        page.wait_for_selector("#form-denuncia:not([hidden])")
        self.r.check(page.input_value("#campo-logradouro") == "" and page.locator("#resultado-envio").is_hidden(),
                     "#botao-nova-denuncia reexibe o formulário limpo")

    def registrar_rpa(self, page: Page, n: str) -> None:
        print("\n== Registrar denúncia sem foto (?canal=rpa)")
        page.goto(f"{self.base}/#/registrar?canal=rpa", wait_until="domcontentloaded")
        page.wait_for_selector("#campo-tipo option[value='OBSTACULO_FIXO']", state="attached")
        page.fill("#campo-logradouro", "Avenida Exemplo (teste RPA)")
        page.fill("#campo-bairro", "Jardim Exemplo")
        page.select_option("#campo-tipo", label="Obstáculo fixo (poste, lixeira, placa)")
        page.fill("#campo-descricao", "Teste automatizado E2E pelo canal RPA: poste no meio da calçada, sem fotografia.")
        page.select_option("#campo-impacto", label="Dificulta a passagem")
        page.fill("#campo-latitude", "-23,5505")
        page.fill("#campo-longitude", "-46.6333")
        page.check("#campo-consentimento")
        with page.expect_response(lambda r: r.url.endswith("/api/denuncias") and r.request.method == "POST", timeout=60_000) as info:
            page.click("#botao-enviar")
        self.r.check(info.value.status == 201, "POST sem foto (RPA) -> 201", f"status={info.value.status}")
        page.wait_for_selector("#resultado-envio:not([hidden]) #protocolo-gerado")
        self.protocolo_rpa = page.inner_text("#protocolo-gerado").strip()
        det = page.request.get(f"{self.base}/api/denuncias/{self.protocolo_rpa}").json()
        self.r.check(det.get("origem") == "RPA", "Denúncia via ?canal=rpa gravada com origem=RPA", str(det.get("origem")))
        self.r.check(det.get("visao") is None and det.get("possui_imagem") is False, "Denúncia sem foto: visao=null")
        self.r.check(det.get("status") == "RECEBIDA", "Sem foto: status RECEBIDA", str(det.get("status")))
        self.foto(page, f"{n}_registrar_rpa_sem_foto_desktop.png")

    def detalhe(self, page: Page, sufixo: str, n: str) -> None:
        print(f"\n== Detalhe da denúncia ({sufixo})")
        self.ir(page, f"/denuncia/{self.protocolo_foto}")
        page.wait_for_selector("#titulo-analise", timeout=TIMEOUT_MS)
        page.wait_for_selector("ol.etapas li img", state="attached")
        texto = page.inner_text("#conteudo")
        self.r.check(self.protocolo_foto in texto, "Detalhe: protocolo exibido")
        atual = page.request.get(f"{self.base}/api/denuncias/{self.protocolo_foto}").json()
        self.r.check(atual["status_rotulo"] in texto, "Detalhe: status com rótulo", atual["status_rotulo"])
        self.r.check("Pessoa de teste" not in texto, "Detalhe: nome do denunciante nunca exibido")
        self.r.check(page.locator("#titulo-historico").count() == 1, "Detalhe: seção de histórico")
        hist = page.locator("section[aria-labelledby='titulo-historico'] li").count()
        self.r.check(hist >= 2, "Detalhe: histórico com RECEBIDA e AGUARDANDO_REVISAO", f"itens={hist}")
        self.verificar_etapas_em_ordem(page, "ol.etapas", "Detalhe", por_url=True)
        self.imagens_carregadas(page, "ol.etapas", "Detalhe")
        self.r.check("não é" in texto.lower() and "probabilidade" in texto.lower(), "Detalhe: explica que a pontuação não é probabilidade")
        self.r.check(page.locator(".analise-visao table").count() >= 1, "Detalhe: tabela de métricas")
        self.r.check("revisão humana" in texto.lower(), "Detalhe: aviso de revisão humana")
        self.r.check(page.locator("#botao-perguntar-assistente").count() == 1, "Detalhe: botão 'Perguntar ao assistente'")
        self.titulo_ok(page, self.protocolo_foto, "Detalhe")
        self.sem_rolagem_horizontal(page, "Detalhe")
        self.foto(page, f"{n}_detalhe_etapas_{sufixo}.png")

    def detalhe_simulado(self, page: Page, n: str) -> None:
        print("\n== Detalhe de denúncia SIMULADA do seed")
        lista = page.request.get(f"{self.base}/api/denuncias?limite=100").json()
        simulada = next((d for d in lista["itens"] if d.get("simulado") and d.get("possui_imagem")), None)
        if not self.r.check(simulada is not None, "Seed contém denúncia simulada com foto"):
            return
        self.ir(page, f"/denuncia/{simulada['protocolo']}")
        page.wait_for_selector("ol.etapas li img", state="attached")
        self.r.check("SIMULADO" in page.inner_text("#conteudo"), "Detalhe simulado: selo SIMULADO visível")
        self.imagens_carregadas(page, "ol.etapas", "Detalhe simulado")
        self.foto(page, f"{n}_detalhe_simulado_desktop.png")

    def consultar(self, page: Page, sufixo: str, n: str) -> None:
        print(f"\n== Consultar ({sufixo})")
        self.ir(page, "/consultar")
        page.wait_for_selector("#resultados-consulta .lista-cartoes > li", timeout=TIMEOUT_MS)
        self.r.check(page.locator("#filtro-status option").count() >= 6, "Consultar: filtro de status com opções")
        page.fill("#busca-protocolo", self.protocolo_foto.lower())
        page.press("#busca-protocolo", "Enter")
        # a busca por protocolo leva direto ao detalhe da denúncia
        esperar(page, "p => window.location.hash === '#/denuncia/' + p && document.querySelector('#titulo-historico')",
                arg=self.protocolo_foto)
        self.r.check(self.protocolo_foto in page.inner_text("#conteudo h1"),
                     "Consultar: busca por protocolo (digitado em minúsculas) abre o detalhe")
        if sufixo == "desktop":
            self.foto(page, f"{n}a_consultar_protocolo_desktop.png")
        self.ir(page, "/consultar")
        page.wait_for_selector("#resultados-consulta .lista-cartoes > li")
        atual = page.request.get(f"{self.base}/api/denuncias/{self.protocolo_foto}").json()
        page.select_option("#filtro-status", atual["status"])
        page.uncheck("#filtro-simulados")
        page.click("form[aria-labelledby='titulo-filtros'] button[type='submit']")
        esperar(page, 
            "p => { const a = document.querySelector('#resultados-consulta'); return a && a.textContent.includes(p) && !a.textContent.includes('SIMULADO'); }",
            arg=self.protocolo_foto, timeout=TIMEOUT_MS,
        )
        cartoes = page.locator("#resultados-consulta .lista-cartoes > li")
        textos = [cartoes.nth(i).inner_text() for i in range(cartoes.count())]
        self.r.check(len(textos) >= 1 and all(atual["status_rotulo"] in t for t in textos),
                     "Consultar: filtro status + sem simulados aplicado", f"{len(textos)} cartões")
        self.r.check(self.protocolo_rpa not in " ".join(textos), "Consultar: denúncia RECEBIDA fica fora do filtro")
        self.sem_rolagem_horizontal(page, "Consultar")
        self.foto(page, f"{n}_consultar_filtros_{sufixo}.png")
        # paginação (com simulados há mais de uma página)
        page.click("#filtro-limpar")
        page.wait_for_selector("#pagina-proxima:not([disabled])", timeout=TIMEOUT_MS)
        primeira = page.inner_text("#resultados-consulta .lista-cartoes > li:first-child")
        page.click("#pagina-proxima")
        esperar(page, 
            "t => { const e = document.querySelector('#resultados-consulta .lista-cartoes > li:first-child'); return e && e.innerText !== t; }",
            arg=primeira, timeout=TIMEOUT_MS,
        )
        self.r.check(page.locator("#pagina-anterior:not([disabled])").count() == 1, "Consultar: paginação próxima/anterior")

    def analise(self, page: Page, sufixo: str, n: str) -> None:
        print(f"\n== Análise avulsa ({sufixo})")
        antes = page.request.get(f"{self.base}/api/indicadores").json()["total"]
        self.ir(page, "/analise")
        page.set_input_files("#analise-foto", str(self.fotos / "sintetica_buraco_01.jpg"))
        with page.expect_response(lambda r: "/api/visao/analisar" in r.url, timeout=60_000) as info:
            page.click("#analise-enviar")
        self.r.check(info.value.status == 200, "POST /api/visao/analisar -> 200", f"status={info.value.status}")
        page.wait_for_selector("#analise-resultado ol.etapas li img", state="attached")
        srcs = page.eval_on_selector_all("#analise-resultado ol.etapas img", "els => els.map(e => e.getAttribute('src').slice(0, 15))")
        self.r.check(len(srcs) == 7 and all(s.startswith("data:image/") for s in srcs), "Análise: 7 etapas em data URI")
        self.verificar_etapas_em_ordem(page, "#analise-resultado ol.etapas", "Análise", por_url=False)
        self.imagens_carregadas(page, "#analise-resultado ol.etapas", "Análise")
        depois = page.request.get(f"{self.base}/api/indicadores").json()["total"]
        self.r.check(antes == depois, "Análise avulsa não grava denúncia", f"{antes} -> {depois}")
        self.sem_rolagem_horizontal(page, "Análise")
        self.foto(page, f"{n}_analise_avulsa_{sufixo}.png")

    def assistente(self, page: Page, sufixo: str, n: str) -> None:
        print(f"\n== Assistente ({sufixo})")
        # entra pelo botão do detalhe (protocolo pré-preenchido)
        self.ir(page, f"/denuncia/{self.protocolo_foto}")
        page.click("#botao-perguntar-assistente")
        page.wait_for_selector("#assistente-mensagem")
        self.r.check(page.input_value("#assistente-protocolo") == self.protocolo_foto, "Assistente: protocolo pré-preenchido a partir do detalhe")
        self.r.check(page.get_attribute("#assistente-log", "role") == "log", "Assistente: área de conversa com role=log")
        self.r.check(page.locator("ul.sugestoes button").count() >= 1, "Assistente: sugestões de perguntas clicáveis")
        page.select_option("#assistente-modo", "explicar_resultado")
        page.fill("#assistente-mensagem", "O que significa o resultado da análise da minha denúncia?")
        with page.expect_response(lambda r: "/api/assistente" in r.url, timeout=60_000) as info:
            page.click("#assistente-enviar")
        resp = info.value
        self.r.check(resp.status == 200, "POST /api/assistente -> 200", f"status={resp.status}")
        corpo = resp.json()
        page.wait_for_selector("#assistente-log .msg--assistente", timeout=TIMEOUT_MS)
        msg = page.inner_text("#assistente-log .msg--assistente >> nth=-1")
        print(f"  [info]  fonte do assistente: {corpo.get('fonte')}")
        self.r.check(corpo.get("denuncia_referenciada") == self.protocolo_foto, "Assistente referencia o protocolo", str(corpo.get("denuncia_referenciada")))
        self.r.check(self.protocolo_foto in msg, "Resposta exibida mostra a denúncia consultada")
        self.r.check(("básico" in msg.lower()) if corpo.get("fonte") == "fallback" else True, "Assistente mostra a fonte (modo básico no fallback)", msg[-200:])
        # segunda pergunta por sugestão (usa histórico)
        page.locator("ul.sugestoes button").first.click()
        esperar(page, "() => document.querySelectorAll('#assistente-log .msg--assistente').length >= 2", timeout=TIMEOUT_MS)
        self.r.check(True, "Assistente: sugestão clicável gera nova resposta")
        self.sem_rolagem_horizontal(page, "Assistente")
        self.foto(page, f"{n}_assistente_{sufixo}.png")

    def painel(self, page: Page, sufixo: str, n: str) -> None:
        print(f"\n== Painel ({sufixo})")
        self.ir(page, "/painel")
        page.wait_for_selector("#painel-operacional figure.grafico svg", timeout=TIMEOUT_MS)
        graficos = page.locator("#painel-operacional figure.grafico").count()
        self.r.check(graficos >= 6, "Painel: gráficos operacionais (categoria, bairro, status, visão, origem, dia)", f"{graficos}")
        acess = page.eval_on_selector_all(
            "#painel-operacional figure.grafico svg",
            "els => els.every(s => s.querySelector('title') && s.querySelector('desc'))",
        )
        self.r.check(acess, "Painel: SVGs com <title> e <desc>")
        self.r.check(page.locator("#painel-operacional figure.grafico table").count() >= graficos,
                     "Painel: tabela de dados equivalente para cada gráfico")
        self.r.check(page.locator("#painel-operacional .indicador").count() >= 5, "Painel: cartões de indicadores")
        esperar(page, 
            "() => { const s = document.querySelector('#painel-analitico'); return s && !s.querySelector('.carregando') && s.innerText.length > 80; }",
            timeout=TIMEOUT_MS,
        )
        analitico = page.inner_text("#painel-analitico")
        dados = page.request.get(f"{self.base}/api/indicadores/analiticos").json()
        if dados.get("disponivel"):
            self.r.check(page.locator("#painel-analitico figure.grafico").count() >= 3, "Painel analítico: gráficos da camada Gold")
            self.r.check("camada Gold" in page.inner_text("#titulo-analitico"), "Painel analítico: título camada Gold")
            self.r.check(str(dados.get("execucao_id", "")) in analitico, "Painel analítico: identificação da execução do pipeline")
            self.r.check(any(str(f.get("nome")) in analitico for f in dados.get("fontes", [])), "Painel analítico: fontes listadas")
        else:
            self.r.check("pipeline" in analitico.lower(), "Painel analítico: explica como rodar o pipeline (disponivel=false)")
        self.sem_rolagem_horizontal(page, "Painel")
        self.foto(page, f"{n}_painel_{sufixo}.png")
        if sufixo == "desktop":
            page.uncheck("#painel-simulados")
            esperar(page, 
                "() => document.querySelector('#painel-operacional .indicador__valor') && !document.querySelector('#painel-operacional .carregando')",
                timeout=TIMEOUT_MS,
            )
            total = page.request.get(f"{self.base}/api/indicadores?incluir_simulados=false").json()["total"]
            primeiro = page.inner_text("#painel-operacional .indicador__valor >> nth=0").strip()
            self.r.check(primeiro == str(total), "Painel: filtro 'incluir simulados' recarrega os indicadores", f"{primeiro} vs {total}")
            page.locator("#painel-analitico").scroll_into_view_if_needed()
            if self.shots:
                page.locator("section[aria-labelledby='titulo-analitico']").screenshot(path=str(self.shots / f"{n}b_painel_analitico_desktop.png"))
                print(f"  [print] {n}b_painel_analitico_desktop.png")

    def revisao(self, page: Page, mon: Monitor, n: str) -> None:
        print("\n== Revisão (área da equipe)")
        self.ir(page, "/revisao")
        page.wait_for_selector("#revisao-lista .lista-cartoes > li", timeout=TIMEOUT_MS)
        mon.esperar("PATCH", r"/api/denuncias/\d+/status$", 401)
        page.fill("#revisao-token", "token-invalido-de-teste")
        page.click("#form-token button[type='submit']")
        self.r.check(page.input_value("#revisao-token") == "", "Token não fica visível no campo após salvar")
        cartao = page.locator("#revisao-lista .lista-cartoes > li", has_text=self.protocolo_foto)
        self.r.check(cartao.count() == 1, "Revisão: denúncia nova aparece em 'Aguardando revisão'")
        cartao.locator("button", has_text="Revisar").click()
        page.wait_for_selector("#painel-revisao:not([hidden]) #revisao-status")
        page.select_option("#revisao-status", "ENCAMINHADA")
        page.click("#revisao-salvar")
        self.r.check(page.locator("#revisao-observacao-erro:not([hidden])").count() == 1,
                     "Revisão: observação obrigatória para ENCAMINHADA (validação no cliente)")
        page.select_option("#revisao-status", "EM_ANALISE")
        page.fill("#revisao-observacao", "Revisão de teste automatizado E2E (dados de teste).")
        page.check("#revisao-humana-confirmado")
        with page.expect_response(lambda r: "/status" in r.url and r.request.method == "PATCH") as info:
            page.click("#revisao-salvar")
        self.r.check(info.value.status == 401, "PATCH com token inválido -> 401", f"status={info.value.status}")
        esperar(page, "() => /token/i.test(document.querySelector('#revisao-resultado').innerText)", timeout=TIMEOUT_MS)
        self.r.check(True, "Revisão: mensagem clara de token inválido")
        if not self.admin_token:
            print("  [info]  ACESSACIDADE_E2E_ADMIN_TOKEN não definido: mudança de status com token válido não testada")
            self.foto(page, f"{n}_revisao_token_invalido_desktop.png")
            return
        page.fill("#revisao-token", self.admin_token)
        page.click("#form-token button[type='submit']")
        with page.expect_response(lambda r: "/status" in r.url and r.request.method == "PATCH") as info:
            page.click("#revisao-salvar")
        self.r.check(info.value.status == 200, "PATCH com token válido -> 200", f"status={info.value.status}")
        esperar(page, "() => /sucesso|salva|atualizad/i.test(document.querySelector('#revisao-resultado').innerText)", timeout=TIMEOUT_MS)
        det = page.request.get(f"{self.base}/api/denuncias/{self.protocolo_foto}").json()
        self.r.check(det.get("status") == "EM_ANALISE" and det.get("revisao_humana") == "CONFIRMADO",
                     "Status mudou para EM_ANALISE com revisão CONFIRMADO", f"{det.get('status')} / {det.get('revisao_humana')}")
        self.r.check(len(det.get("historico", [])) >= 3, "Histórico ganhou a nova entrada")
        self.foto(page, f"{n}_revisao_status_alterado_desktop.png")
        page.click("#revisao-esquecer-token")
        ok = page.evaluate("() => !sessionStorage.getItem('acessacidade.tokenEquipe')")
        self.r.check(ok, "Revisão: 'Esquecer token' limpa o sessionStorage")
        self.ir(page, f"/denuncia/{self.protocolo_foto}")
        page.wait_for_selector("#titulo-historico")
        self.r.check("Em análise" in page.inner_text("#conteudo"), "Detalhe reflete o novo status")

    def sobre(self, page: Page, sufixo: str, n: str) -> None:
        print(f"\n== Sobre ({sufixo})")
        self.ir(page, "/sobre")
        texto = page.inner_text("#conteudo")
        # "retenção" e "Contato" continuam presentes depois que a equipe trocar os [PREENCHER] (D14 da pasta 06).
        for termo in ["LGPD", "ODS 11", "ODS 10", "EXIF", "retenção", "Contato", "não é"]:
            self.r.check(termo in texto, f"Sobre: menciona '{termo}'")
        if "[PREENCHER" in texto:
            print("  [aviso] Sobre ainda tem [PREENCHER] (retenção/contato) — preencher antes da entrega (06 D14).")
        self.sem_rolagem_horizontal(page, "Sobre")
        self.foto(page, f"{n}_sobre_{sufixo}.png")

    def nao_encontrada(self, page: Page, sufixo: str, n: str) -> None:
        print(f"\n== 404 ({sufixo})")
        self.ir(page, "/rota-que-nao-existe")
        self.r.check(page.locator("#titulo-404").count() == 1, "Rota inexistente mostra página 404 amigável")
        self.r.check(page.locator("#conteudo a[href='#/']").count() >= 1, "404: link para voltar ao início")
        self.titulo_ok(page, "não encontrada", "404")
        self.foto(page, f"{n}_404_{sufixo}.png")
        if self.monitor:
            self.monitor.esperar("GET", r"/api/denuncias/AC-2099-999999$", 404)
        self.ir(page, "/denuncia/AC-2099-999999")
        esperar(page, "() => /não (foi )?encontrad/i.test(document.querySelector('#conteudo').innerText)", timeout=TIMEOUT_MS)
        self.r.check(True, "Protocolo inexistente: mensagem de não encontrada")

    def ajuda_flutuante(self, page: Page) -> None:
        print("\n== Botão flutuante de ajuda")
        self.ir(page, "/consultar")
        href = page.get_attribute("#botao-ajuda", "href") or ""
        self.r.check("contexto=" in href, "Botão 'Ajuda' leva ao assistente com contexto_tela", href)
        page.click("#botao-ajuda")
        page.wait_for_selector("#assistente-mensagem")
        self.r.check(page.locator("#botao-ajuda").is_hidden(), "Botão 'Ajuda' oculto dentro do assistente")

    # ------------------------------------------------------------- execução
    def executar(self, canal: str) -> int:
        with sync_playwright() as p:
            try:
                navegador = p.chromium.launch(channel=canal, headless=True) if canal != "chromium" else p.chromium.launch(headless=True)
            except Exception as exc:  # noqa: BLE001
                print(f"Não foi possível abrir o navegador ({canal}): {exc}", file=sys.stderr)
                return 2
            monitores: list[tuple[str, Monitor]] = []

            def nova_pagina(largura: int, altura: int, nome: str):
                ctx = navegador.new_context(viewport={"width": largura, "height": altura}, locale="pt-BR",
                                            reduced_motion="reduce")
                pg = ctx.new_page()
                pg.set_default_timeout(TIMEOUT_MS)
                mon = Monitor()
                self.monitor = mon
                mon.anexar(pg)
                monitores.append((nome, mon))
                return ctx, pg, mon

            # cabeçalhos de segurança do contrato (seção 11)
            resp = navegador.new_context().request.get(self.base + "/")
            csp = resp.headers.get("content-security-policy", "")
            self.r.check("script-src 'self'" in csp and "style-src 'self'" in csp, "Página servida com a CSP do contrato", csp)
            self.r.check(resp.headers.get("x-frame-options", "").upper() == "DENY", "X-Frame-Options: DENY")

            ctx, page, mon = nova_pagina(1280, 900, "desktop")
            try:
                self.teclado(page)
                self.inicio(page, "desktop", "01")
                self.registrar_com_foto(page, "02")
                self.registrar_rpa(page, "03")
                self.detalhe(page, "desktop", "04")
                self.detalhe_simulado(page, "05")
                self.consultar(page, "desktop", "06")
                self.analise(page, "desktop", "07")
                self.assistente(page, "desktop", "08")
                self.ajuda_flutuante(page)
                self.painel(page, "desktop", "09")
                self.revisao(page, mon, "10")
                self.sobre(page, "desktop", "11")
                self.nao_encontrada(page, "desktop", "12")
            except Exception as exc:  # noqa: BLE001
                self.r.check(False, "Fluxo desktop executado sem exceção", f"{type(exc).__name__}: {exc}"[:500])
                self.foto(page, "99_erro_desktop.png")
            ctx.close()

            ctx, page, mon = nova_pagina(390, 844, "mobile")
            try:
                self.inicio(page, "mobile", "21")
                if self.protocolo_foto:
                    self.detalhe(page, "mobile", "22")
                    self.consultar(page, "mobile", "23")
                self.analise(page, "mobile", "24")
                if self.protocolo_foto:
                    self.assistente(page, "mobile", "25")
                self.painel(page, "mobile", "26")
                self.sobre(page, "mobile", "27")
                self.nao_encontrada(page, "mobile", "28")
                print("\n== Menu móvel")
                self.ir(page, "/")
                page.click("#botao-menu")
                self.r.check(page.get_attribute("#botao-menu", "aria-expanded") == "true", "Menu móvel abre (aria-expanded=true)")
                page.click("#menu-principal a[href='#/registrar']")
                page.wait_for_selector("#form-denuncia")
                self.r.check(page.locator("#form-denuncia").is_visible(), "Menu móvel navega para Registrar")
                self.sem_rolagem_horizontal(page, "Registrar")
                self.foto(page, "29_registrar_mobile.png")
            except Exception as exc:  # noqa: BLE001
                self.r.check(False, "Fluxo mobile executado sem exceção", f"{type(exc).__name__}: {exc}"[:500])
                self.foto(page, "99_erro_mobile.png")
            ctx.close()
            navegador.close()

        print("\n== Console, CSP e rede")
        for nome, mon in monitores:
            self.r.check(not mon.console_inesperado(), f"{nome}: sem erros de console/CSP", "; ".join(mon.console_inesperado())[:800])
            self.r.check(not mon.erros_pagina, f"{nome}: sem exceções JavaScript", "; ".join(mon.erros_pagina)[:800])
            self.r.check(not mon.inesperadas(), f"{nome}: sem respostas HTTP 4xx/5xx inesperadas", str(mon.inesperadas())[:800])
            self.r.check(not mon.falhas_rede, f"{nome}: sem falhas de rede", "; ".join(mon.falhas_rede)[:800])

        total = len(self.r.ok) + len(self.r.falhas)
        print(f"\nRESULTADO: {len(self.r.ok)}/{total} verificações OK; {len(self.r.falhas)} falha(s).")
        print(f"Protocolos criados nesta execução: {self.protocolo_foto or '-'} (com foto), {self.protocolo_rpa or '-'} (RPA, sem foto)")
        for f in self.r.falhas:
            print(f"  - {f}")
        return 0 if not self.r.falhas else 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Teste E2E do frontend AcessaCidade contra um backend real.")
    ap.add_argument("--url", default="http://127.0.0.1:8000", help="URL base do backend (serve também o frontend).")
    ap.add_argument("--shots", type=Path, default=None, help="Pasta onde salvar screenshots (opcional).")
    ap.add_argument("--fotos", type=Path, default=REPO_ROOT / "data" / "samples" / "fotos", help="Pasta com as fotos sintéticas.")
    ap.add_argument("--navegador", default="msedge", help="Canal do navegador: msedge (padrão), chrome ou chromium.")
    args = ap.parse_args(argv)
    for fluxo in (sys.stdout, sys.stderr):
        try:
            fluxo.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    if not (args.fotos / "sintetica_buraco_02.jpg").is_file():
        print(f"Fotos sintéticas não encontradas em {args.fotos}", file=sys.stderr)
        return 2
    token = os.environ.get("ACESSACIDADE_E2E_ADMIN_TOKEN", "").strip()
    inicio = time.time()
    print(f"AcessaCidade E2E — {args.url} — navegador {args.navegador}")
    codigo = E2E(args.url, args.shots, args.fotos, token).executar(args.navegador)
    print(f"Duração: {time.time() - inicio:.1f}s")
    return codigo


if __name__ == "__main__":
    sys.exit(main())
