# GitHub Actions — onde estão os workflows

O GitHub só executa workflows que estão em **`.github/workflows/`** na raiz do repositório. Por isso
o pipeline da disciplina 06 fica lá, e esta pasta guarda apenas os arquivos de apoio.

| Arquivo | Função |
|---|---|
| [`.github/workflows/ci-devsecops.yml`](../../.github/workflows/ci-devsecops.yml) | Pipeline DevSecOps: testes, Gitleaks, Semgrep, Terraform validate/test + Trivy config, build + Trivy image + smoke test e deploy na Azure (ACR + ACI via Terraform) |
| [`requirements-ci.txt`](requirements-ci.txt) | Dependências do job `testes` (sem `cadquery` e `playwright`, que são pesados/precisam de navegador) |

Ferramentas e configurações usadas pelo pipeline:

| Ferramenta | Versão fixa | Configuração |
|---|---|---|
| Gitleaks | 8.21.2 (binário oficial + checksum) | [`.gitleaks.toml`](../../.gitleaks.toml) |
| Semgrep | 1.185.0 (pip) | [`.semgrep/acessacidade.yml`](../../.semgrep/acessacidade.yml) + pacotes `p/python`, `p/javascript`, `p/secrets`, `p/dockerfile` |
| Trivy | `aquasec/trivy:0.76.2` (container) | `.trivyignore` na raiz (opcional — não existe hoje; só criar com justificativa por CVE) |
| Terraform | 1.9.8 (`hashicorp/setup-terraform@v3`) | [`../terraform`](../terraform) |
| Actions | `actions/checkout@v4`, `actions/setup-python@v5`, `actions/upload-artifact@v4`, `actions/download-artifact@v4`, `azure/login@v2`, `hashicorp/setup-terraform@v3` | — |

Documentação completa (jobs, Secrets/Variables, OIDC): [`../docs/CI_CD_DEVSECOPS.md`](../docs/CI_CD_DEVSECOPS.md).

Testes de pipeline sem GitHub: `python -m pytest 06-Secure-DevOps-Cloud/tests` (valida YAML, jobs,
versões fixas e ausência de segredos) e `python 06-Secure-DevOps-Cloud/tools/testar_regras_semgrep.py`.
