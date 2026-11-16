# =====================================================================
# State remoto (Azure Storage) — configuração PARCIAL.
#
# O state NUNCA fica no repositório (.gitignore bloqueia *.tfstate e *.tfvars).
# Os valores do backend são passados na hora do init:
#
#   CI (GitHub Actions) — valores vindos de GitHub Secrets:
#     terraform init \
#       -backend-config="resource_group_name=$TFSTATE_RESOURCE_GROUP" \
#       -backend-config="storage_account_name=$TFSTATE_STORAGE_ACCOUNT" \
#       -backend-config="container_name=$TFSTATE_CONTAINER" \
#       -backend-config="key=$TFSTATE_KEY" \
#       -backend-config="use_oidc=true" \
#       -backend-config="use_azuread_auth=true"
#
#   Local, com o MESMO state remoto (recomendado — evita divergência com o CI):
#     terraform init -backend-config=backend.hcl
#     (backend.hcl fica FORA do Git — modelo em backend.hcl.example)
#
#   Local, só para validar a sintaxe (sem nuvem, sem state):
#     terraform init -backend=false
#     terraform validate
#
#   Local, com state LOCAL fora do repositório (somente para estudo):
#     copie backend_override.tf.example para backend_override.tf
#     (*_override.tf está no .gitignore) e rode terraform init.
# =====================================================================
terraform {
  backend "azurerm" {}
}
