# Demonstração: execução barrada e execução corrigida

A GS pede para **mostrar uma execução do pipeline barrada e a corrigida**. O roteiro abaixo é seguro:
usa um token **fictício** da equipe (formato `acd_demo_` + 32 caracteres `[a-z0-9]`), que não é
credencial de nenhum provedor, e uma regra customizada do Gitleaks (`acessacidade-demo-token` em
`.gitleaks.toml`) que o reconhece.

> Este documento descreve o **formato** do token, mas não contém nenhum token completo.
> **Nunca** use uma chave real para a demonstração e **nunca** faça a demonstração na `main`.

## Roteiro principal — Gitleaks (segredo vazado)

Pré-requisito: repositório publicado no GitHub com o workflow `CI DevSecOps` já verde na `main`.

1. Crie uma branch de demonstração a partir da `main`:
   ```powershell
   git switch main; git pull
   git switch -c demo/execucao-barrada
   ```
2. Gere um token fictício **na hora** e grave num arquivo de demonstração:
   ```powershell
   .\.venv\Scripts\python.exe -c "import secrets,string; a=string.ascii_lowercase+string.digits; open('demo_segredo_vazado.py','w').write('DEMO_TOKEN = ' + repr('acd_demo_' + ''.join(secrets.choice(a) for _ in range(32))) + chr(10))"
   Get-Content demo_segredo_vazado.py
   ```
   (Comando testado no PowerShell 5.1; no Git Bash funciona igual com `python` no lugar do caminho do venv.)
3. Commit e push:
   ```powershell
   git add demo_segredo_vazado.py
   git commit -m "demo: simula segredo vazado (token ficticio)"
   git push -u origin demo/execucao-barrada
   ```
4. GitHub → **Actions** → execução da branch `demo/execucao-barrada`:
   - job **Segredos (Gitleaks)** fica **vermelho** com `RuleID: acessacidade-demo-token`,
     arquivo `demo_segredo_vazado.py` e o valor **mascarado** (`--redact`);
   - o job `deploy` não roda (não é `main` e depende de todos os jobs).
   - **Print 1**: lista de jobs com o Gitleaks falhando. **Print 2**: log do passo "Varredura do histórico Git".
5. Correção. Como o Gitleaks varre **todo o histórico**, apagar o arquivo num commit novo **não basta**
   (o segredo continua no histórico — exatamente o comportamento correto). Escolha uma opção:
   - **Opção A (recomendada) — branch limpa:**
     ```powershell
     git switch main
     git branch -D demo/execucao-barrada
     git push origin --delete demo/execucao-barrada
     git switch -c demo/execucao-corrigida
     git commit --allow-empty -m "demo: execucao corrigida (sem segredo)"
     git push -u origin demo/execucao-corrigida
     ```
   - **Opção B — reescrever o histórico da branch de demonstração:**
     ```powershell
     git reset --hard HEAD~1        # remove o commit com o token (somente nesta branch!)
     git commit --allow-empty -m "demo: execucao corrigida (sem segredo)"
     git push --force-with-lease origin demo/execucao-barrada
     ```
6. GitHub → Actions → nova execução: **todos os jobs verdes**. **Print 3**.
7. Confirme que o arquivo não existe mais: `Test-Path demo_segredo_vazado.py` → `False`.
   Se o token fictício tivesse sido uma credencial real, o passo obrigatório seria **revogar/rotacionar** a credencial no provedor.

## Alternativa 1 — Semgrep (código inseguro)

1. `git switch -c demo/semgrep-barrado`
2. Crie `demo_inseguro.py` com:
   ```python
   import sys
   print(eval(sys.argv[1]))  # entrada do usuário executada como código
   ```
3. Commit + push → job **SAST (Semgrep)** vermelho com `acessacidade-python-eval-exec` (e regras do `p/python`). **Print.**
4. Correção: troque por `print(int(sys.argv[1]))` (ou apague o arquivo), commit + push → verde. **Print.**
   (Aqui um commit novo resolve, porque o Semgrep analisa o código atual, não o histórico.)

## Alternativa 2 — Trivy (imagem base vulnerável)

1. `git switch -c demo/trivy-barrado`
2. No `06-Secure-DevOps-Cloud/docker/Dockerfile`, troque **somente nesta branch** o `ARG PYTHON_IMAGE`
   por uma imagem antiga e sem atualizações, por exemplo `python:3.11.0-slim-bullseye`.
3. Commit + push → job **Build da imagem + Trivy image** vermelho listando CVEs CRITICAL/HIGH com correção disponível. **Print.**
4. Correção: volte para `python:3.11-slim-bookworm`, commit + push → verde. **Print.**
5. Apague a branch depois: `git push origin --delete demo/trivy-barrado`.

## Validação local feita pela equipe de desenvolvimento

A regra foi testada sem GitHub: um arquivo com token gerado na hora, **fora do repositório**
(pasta temporária), foi varrido com `gitleaks dir <pasta> --config .gitleaks.toml --redact` → `leaks found: 1`,
`RuleID: acessacidade-demo-token`, código de saída 1. Ver `evidencias/validacoes_locais.md`.

## Checklist

- [ ] Print da execução barrada (Gitleaks ou alternativa) com o motivo visível
- [ ] Print da execução corrigida (todos os jobs verdes)
- [ ] Links das duas execuções no PDF: [PREENCHER: URL da execução barrada] / [PREENCHER: URL da execução corrigida]
- [ ] Branch de demonstração removida; nenhum arquivo `demo_*` no repositório
