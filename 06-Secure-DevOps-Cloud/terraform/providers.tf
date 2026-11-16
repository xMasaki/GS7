# Provider Azure.
# Autenticação (nenhuma credencial neste repositório):
#   - Local: "az login" (Azure CLI) + subscription_id via variável
#     (TF_VAR_subscription_id) ou variável de ambiente ARM_SUBSCRIPTION_ID.
#   - GitHub Actions: OIDC (ARM_USE_OIDC=true, ARM_CLIENT_ID, ARM_TENANT_ID,
#     ARM_SUBSCRIPTION_ID vindos de GitHub Secrets). Ver docs/CI_CD_DEVSECOPS.md.
provider "azurerm" {
  features {
    resource_group {
      # Evita apagar por engano um grupo que contenha recursos criados fora do Terraform
      prevent_deletion_if_contains_resources = true
    }
  }

  # null => o provider usa ARM_SUBSCRIPTION_ID do ambiente
  subscription_id = var.subscription_id

  # Registro de Resource Providers feito explicitamente (infra/azure/01_*),
  # evitando que o Terraform tente registrar dezenas de providers sem permissão.
  resource_provider_registrations = "none"
}
