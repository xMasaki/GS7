// Arquivo de TESTE das regras Semgrep da equipe (não é código da aplicação).
// Excluído das varreduras do CI (--exclude .semgrep/tests).

function renderizar(el, denuncia) {
  // ruleid: acessacidade-js-innerhtml
  el.innerHTML = "<p>" + denuncia.descricao + "</p>";
  // ruleid: acessacidade-js-innerhtml
  el.insertAdjacentHTML("beforeend", denuncia.descricao);
  // ok: acessacidade-js-innerhtml
  el.innerHTML = "";
  // ok: acessacidade-js-innerhtml
  el.textContent = denuncia.descricao;
}

function executar(codigo) {
  // ruleid: acessacidade-js-eval
  eval(codigo);
  // ruleid: acessacidade-js-eval
  const f = new Function(codigo);
  // ok: acessacidade-js-eval
  setTimeout(() => f(), 10);
}
