# Validações locais — resultados reais

Executadas em **15/11/2026**, Windows 11, na raiz do repositório, **sem Docker, sem Azure CLI e sem
credenciais de nuvem** (nenhum `terraform plan/apply`, nenhum recurso criado). Ferramentas:
Terraform 1.9.8, Gitleaks 8.21.2, Trivy 0.76.2, Semgrep 1.185.0 (pip, Python 3.11), Python 3.11 (.venv).
As saídas abaixo foram resumidas (cortes indicados por "…").

## 1. Terraform (`06-Secure-DevOps-Cloud/terraform`)

```text
> terraform fmt -check -recursive
(sem saída)  exit=0

> terraform init -backend=false        (provider baixado: hashicorp/azurerm 4.81.0, hashicorp/random 3.9.1)
> terraform validate
Success! The configuration is valid.

> terraform test                        (mock_provider — nenhum recurso real)
tests\acessacidade.tftest.hcl... in progress
  run "fase1_cria_somente_rg_acr_identidade"... pass
  run "fase2_expoe_somente_porta_8000_e_segredos_protegidos"... pass
  run "porta_diferente_de_8000_e_rejeitada"... pass
Success! 3 passed, 0 failed.
```

## 2. Trivy config (má configuração)

```text
> trivy config 06-Secure-DevOps-Cloud/docker  (severidades CRITICAL..LOW)
│ Dockerfile │ dockerfile │ 0 │          → nenhuma má configuração

> trivy config --skip-dirs 06-Secure-DevOps-Cloud/terraform/.terraform 06-Secure-DevOps-Cloud/terraform
│ .          │ terraform  │ 0 │          → nenhuma má configuração

> trivy fs --scanners secret,misconfig --skip-dirs .venv --skip-dirs …/.terraform --severity CRITICAL,HIGH .
│ 06-Secure-DevOps-Cloud/docker/Dockerfile │ dockerfile │ - │ 0 │
│ 06-Secure-DevOps-Cloud/terraform         │ terraform  │ - │ 0 │
(nenhum segredo encontrado no repositório)
```

Observação: o Trivy não aponta a falta de HTTPS do ACI (não há regra para isso); a limitação está
documentada em `ARQUITETURA_CLOUD.md` com a evolução proposta (Container Apps / Front Door).

## 3. Trivy fs — dependências (`requirements.txt`)

```text
> trivy fs --scanners vuln --severity CRITICAL,HIGH,MEDIUM <cópia de requirements.txt>
requirements.txt (pip)  Total: 4 (MEDIUM: 1, HIGH: 3, CRITICAL: 0)
python-multipart 0.0.20  CVE-2026-24486 HIGH   fixed in 0.0.22  (path traversal / escrita de arquivo)
                         CVE-2026-42561 HIGH   fixed in 0.0.27  (DoS)
                         CVE-2026-53539 HIGH   fixed in 0.0.30  (DoS)
                         CVE-2026-40347 MEDIUM fixed in 0.0.26  (DoS)
```

Varredura das versões **efetivamente instaladas** no .venv (fastapi 0.115.12 → starlette 0.46.2):

```text
Total: 10 (MEDIUM: 4, HIGH: 6, CRITICAL: 0)
python-multipart 0.0.20 → 3 HIGH + 1 MEDIUM (acima)
starlette 0.46.2        → CVE-2025-62727 HIGH (fixed 0.49.1), CVE-2026-48818 HIGH (fixed 1.1.0),
                          CVE-2026-54283 HIGH (fixed 1.3.1), CVE-2025-54121 MEDIUM (fixed 0.47.2),
                          CVE-2026-48710 MEDIUM (fixed 1.0.1), CVE-2026-48817 MEDIUM (fixed 1.1.0)
```

**Impacto no pipeline:** o job `imagem` roda `trivy image --severity CRITICAL,HIGH --ignore-unfixed --exit-code 1`;
com essas versões ele **vai barrar** o build (é o comportamento correto — serve inclusive como
"execução barrada" real). Correção necessária em `requirements.txt` (área do backend, não alterada
pela disciplina 06): subir `python-multipart` para ≥ 0.0.30 e `fastapi`/`starlette` para versões com
`starlette` ≥ 1.3.1 (no PyPI em 15/11/2026: fastapi 0.163.0, starlette 1.10.0, python-multipart 0.0.33),
rodar os testes da API e repetir o Trivy. Não foi criado `.trivyignore` porque as correções existem.
A imagem base (pacotes Debian) **não pôde** ser varrida localmente (sem Docker) — será varrida no CI.

### 3.1 Correção aplicada e revalidação (15/11/2026)

`requirements.txt` atualizado para versões publicadas no PyPI há mais de duas semanas na data:
`fastapi==0.162.0`, `starlette==1.10.0`, `python-multipart==0.0.33`, `uvicorn==0.54.0`
(a fastapi 0.162.0 traz `opentelemetry-api` como dependência transitiva).

```text
> pytest app/backend/tests 01-.../tests 04-.../tests  (venv temporário só com as novas versões)  -> todos passaram
> .\.venv\Scripts\python.exe -m pytest   (repositório inteiro, venv atualizado)               -> 485 passed
> trivy fs --scanners vuln --severity HIGH,CRITICAL requirements.txt
  requirements.txt │ pip │ 0                                                                   -> limpo
```

A varredura da **imagem** (`trivy image`, inclui pacotes Debian da base) continua dependendo do job
`imagem` no GitHub Actions.

## 4. Gitleaks

```text
> gitleaks dir . --config .gitleaks.toml --redact      (1ª execução)
WRN leaks found: 40
  generic-api-key .semgrep\tests\acessacidade.py 42
  generic-api-key .venv\Lib\site-packages\… (39 achados em bibliotecas de terceiros)
```

Causas e correções aplicadas: (1) as exclusões de caminho usavam só `/` e o Windows reporta `\` —
regex trocada para `[\\/]`; (2) o valor fictício do arquivo de teste do Semgrep foi trocado por um de
baixa entropia (`"ficticio-nao-usar"`), sem precisar de allowlist.

```text
> gitleaks dir . --config .gitleaks.toml --redact      (após a correção; repetido no fim do trabalho)
INF scan completed in 3.46s
INF no leaks found          exit=0
```

Teste da regra da demonstração (arquivo com token gerado na hora, **fora do repositório**):

```text
> gitleaks dir <pasta temporária> --config .gitleaks.toml --redact -v
RuleID: acessacidade-demo-token
WRN leaks found: 1          exit=1
```

O histórico Git (`gitleaks git .`) não foi varrido localmente: a pasta ainda não é um repositório Git.

## 5. Semgrep

```text
> python 06-Secure-DevOps-Cloud/tools/testar_regras_semgrep.py --semgrep <semgrep.exe>
Achados esperados: 13 | encontrados: 13
RESULTADO: OK — todas as regras customizadas se comportaram como esperado
```

(`semgrep --test` falha no Windows com `IndexError` em `relatively_eq`; por isso o script acima.)

```text
> semgrep scan --config p/python --config p/javascript --config p/secrets --config p/dockerfile
    --config .semgrep/ --exclude .semgrep/tests --exclude .venv --error
    06-Secure-DevOps-Cloud scripts infra .github
1ª execução: 1 achado — dangerous-subprocess-use-tainted-env-args em
             06-Secure-DevOps-Cloud/tools/testar_regras_semgrep.py:57
Correção: exceção justificada com comentário nosemgrep (ferramenta de desenvolvimento,
          lista de argumentos fixa, shell=False).
2ª execução: 0 achados, exit=0
```

Varredura do repositório inteiro (mesma linha de comando, alvo `.`), no fim do trabalho:

```text
achados 1  erros 0  arquivos 337
  05-Robotic-Process-Automation\scripts\gerar_pdf_relatorio.py:86  dangerous-subprocess-use-tainted-env-args (ERROR)
  -> RESOLVIDO em 15/11/2026 com "# nosemgrep" justificado (lista de argumentos, sem shell, ferramenta local).
     Nova execução no repositório inteiro (mesmas configs do CI): 0 achados, exit 0.
```

**Impacto no pipeline:** o job `semgrep` usa `--error` e **vai barrar** enquanto esse achado existir
(área da disciplina 05 — não alterada aqui). Correção sugerida ao responsável: validar o caminho do
executável com `shutil.which`/lista fixa ou registrar exceção justificada com `# nosemgrep`.

## 6. Testes automatizados (pytest)

```text
> python -m pytest 06-Secure-DevOps-Cloud/tests
38 passed in 4.99s

> python -m pytest            (repositório inteiro, nesta máquina, com cadquery instalado)
485 passed in 54.30s
```

## 7. Configurações YAML/JSON

`yaml.safe_load` OK em: `docker-compose.yml`, `.github/workflows/ci-devsecops.yml`,
`infra/aci-deployment.template.yaml`, `monitoring/prometheus/{prometheus,prometheus.azure,alert_rules}.yml`,
`monitoring/alertmanager/alertmanager.yml`, `monitoring/grafana/provisioning/**.yml`.
`json.load` OK no dashboard (26 painéis). Alertas: `AcessaCidadeIndisponivel`, `AcessaCidadeTaxaErros5xxAlta`,
`AcessaCidadeLatenciaP95Alta`, `AcessaCidadeMuitas4xx`, `AcessaCidadeSaturacaoMemoria`.

## 8. Não executado (depende da equipe)

- `docker build` / `docker compose up` / Trivy image / smoke test — sem Docker nesta máquina (rodam no CI).
- `terraform plan/apply`, push no ACR, URL pública — sem credenciais Azure (por regra, nada criado).
- Pipeline no GitHub (verde, barrada, corrigida) — repositório ainda não publicado.
- Prometheus/Grafana em execução e alerta disparado — dependem do Docker Desktop.
