# infra/ — scripts Azure CLI e template do ACI

Esta pasta complementa a infraestrutura como código oficial do projeto, que está em
[`06-Secure-DevOps-Cloud/terraform/`](../06-Secure-DevOps-Cloud/terraform/).

| O quê | Onde | Quando usar |
|---|---|---|
| **IaC oficial** (RG, ACR, identidade gerenciada, ACI, Log Analytics opcional) | `06-Secure-DevOps-Cloud/terraform/` | Sempre. O GitHub Actions aplica esse Terraform no deploy automático. |
| Preparação da assinatura (login, providers) | `infra/azure/01_login_e_providers.*` | Uma vez, antes do primeiro `terraform apply`. |
| State remoto do Terraform (Storage Account) | `infra/azure/02_state_remoto.*` | Uma vez. O state **nunca** vai para o Git. |
| Identidade do GitHub Actions (OIDC, sem senha) | `infra/azure/03_oidc_github.*` | Uma vez, para habilitar o deploy automático. |
| Build/push da imagem (`az acr build` **sem Docker local** ou `docker push`) | `infra/azure/04_build_push_imagem.*` | Deploy manual entre a fase 1 e a fase 2 do Terraform. |
| Template YAML do ACI (`az container create --file`) | `infra/aci-deployment.template.yaml` + `infra/azure/05_deploy_aci_yaml.*` | **Alternativa** manual ao Terraform fase 2 (mesmo conceito do exercício Calango TI). Não use os dois para o mesmo container. |
| Renderizador do template | `infra/azure/render_aci_template.py` | Chamado pelo script 05; grava o YAML com segredos **fora** do repositório e apaga depois. |
| Status, eventos, logs e health check | `infra/azure/06_status_logs.*` | Diagnóstico a qualquer momento (somente leitura). |
| Limpeza | `infra/azure/99_limpeza.*` | **Somente depois do fim da correção.** |

## Classificação dos comandos

Cada script lista no cabeçalho a classificação de **todos** os comandos e repete a marcação
na linha anterior a cada comando:

- **[SOMENTE LEITURA]** — consulta, login ou geração de arquivo local; não cria nada na nuvem.
- **[CRIA RECURSOS/CUSTO]** — cria ou altera recursos/permissões na assinatura (pode gerar cobrança).
- **[REMOVE RECURSOS — NÃO EXECUTAR ANTES DO FIM DA CORREÇÃO]** — apaga recursos; a URL pública deixa de funcionar.

## Ordem de uso (resumo)

1. `01_login_e_providers` → 2. `02_state_remoto` → 3. `03_oidc_github` (se for usar deploy automático)
→ 4. `terraform apply` fase 1 (`deploy_container=false`) → 5. `04_build_push_imagem`
→ 6. `terraform apply` fase 2 (`deploy_container=true`, `image_tag=<tag>`) → 7. `06_status_logs`.

Passo a passo completo, com prints esperados: [`06-Secure-DevOps-Cloud/docs/PUBLICACAO_AZURE.md`](../06-Secure-DevOps-Cloud/docs/PUBLICACAO_AZURE.md).

## Segurança

- Nenhum script contém segredo. Tokens (`ADMIN_TOKEN`, `PIPELINE_TOKEN`) e a chave `OPENROUTER_API_KEY`
  entram por variável de ambiente da sessão (ou GitHub Secrets no CI) e chegam ao ACI como
  `secureValue` / `secure_environment_variables` (não aparecem no portal nem em `az container show`).
- A única porta pública é **8000/TCP** (aplicação). **Não existe porta administrativa** (SSH 22/RDP 3389):
  o ACI não expõe máquina virtual; diagnóstico é feito por `az container logs` / `az container exec`,
  que passam pela API autenticada da Azure.
- O ACR tem `admin_enabled = false`: o pull usa identidade gerenciada com a função `AcrPull`.
