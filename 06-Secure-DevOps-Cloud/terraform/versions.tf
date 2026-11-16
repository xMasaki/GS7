# Versões do Terraform e dos providers.
# Validado localmente com Terraform 1.9.8 (terraform init -backend=false + validate).
# O arquivo .terraform.lock.hcl gerado pelo "terraform init" DEVE ser versionado
# (fixa os hashes dos providers para o CI usar exatamente as mesmas versões).
terraform {
  required_version = ">= 1.6.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }
}
