# =====================================================================
# Testes do Terraform SEM nuvem e SEM credenciais (terraform test + mock_provider,
# Terraform >= 1.7). Nenhum recurso real é criado: o provider azurerm é simulado.
#
#   cd 06-Secure-DevOps-Cloud/terraform
#   terraform init -backend=false
#   terraform test
# =====================================================================

mock_provider "azurerm" {
  mock_resource "azurerm_container_registry" {
    defaults = {
      id           = "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rg-teste/providers/Microsoft.ContainerRegistry/registries/acessacidadeacrteste"
      login_server = "acessacidadeacrteste.azurecr.io"
    }
  }
  mock_resource "azurerm_user_assigned_identity" {
    defaults = {
      id           = "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rg-teste/providers/Microsoft.ManagedIdentity/userAssignedIdentities/id-teste"
      principal_id = "11111111-1111-1111-1111-111111111111"
      client_id    = "22222222-2222-2222-2222-222222222222"
    }
  }
  mock_resource "azurerm_container_group" {
    defaults = {
      fqdn       = "acessacidade-teste.brazilsouth.azurecontainer.io"
      ip_address = "198.51.100.10"
    }
  }
}

variables {
  name_suffix = "teste1"
}

run "fase1_cria_somente_rg_acr_identidade" {
  command = apply

  variables {
    deploy_container = false
  }

  assert {
    condition     = length(azurerm_container_group.app) == 0
    error_message = "Na fase 1 (deploy_container=false) o ACI não pode ser criado."
  }

  assert {
    condition     = azurerm_container_registry.acr.admin_enabled == false
    error_message = "O usuário administrativo do ACR deve ficar desabilitado."
  }

  assert {
    condition     = azurerm_role_assignment.acr_pull.role_definition_name == "AcrPull"
    error_message = "A identidade do ACI deve ter somente AcrPull."
  }

  assert {
    condition     = output.app_url == null
    error_message = "Sem container, app_url deve ser null."
  }

  assert {
    condition     = azurerm_container_registry.acr.name == "acessacidadeacrteste1"
    error_message = "Nome do ACR fora do padrão esperado."
  }
}

run "fase2_expoe_somente_porta_8000_e_segredos_protegidos" {
  command = apply

  variables {
    deploy_container = true
    image_tag        = "0123456789abcdef"
    admin_token      = "valor-ficticio-somente-para-teste"
  }

  assert {
    condition     = length(azurerm_container_group.app) == 1
    error_message = "Na fase 2 o ACI deve ser criado."
  }

  assert {
    condition     = length(azurerm_container_group.app[0].exposed_port) == 1 && alltrue([for p in azurerm_container_group.app[0].exposed_port : p.port == 8000 && p.protocol == "TCP"])
    error_message = "Somente a porta 8000/TCP pode ser exposta (nenhuma porta administrativa)."
  }

  assert {
    condition     = alltrue([for p in azurerm_container_group.app[0].container[0].ports : p.port == 8000])
    error_message = "O container deve abrir somente a porta 8000."
  }

  assert {
    condition     = azurerm_container_group.app[0].container[0].image == "acessacidadeacrteste.azurecr.io/acessacidade:0123456789abcdef"
    error_message = "A imagem deve vir do ACR do projeto com a tag informada."
  }

  assert {
    condition     = contains(keys(azurerm_container_group.app[0].container[0].secure_environment_variables), "ADMIN_TOKEN")
    error_message = "ADMIN_TOKEN deve ir em secure_environment_variables."
  }

  assert {
    condition     = !contains(keys(azurerm_container_group.app[0].container[0].environment_variables), "ADMIN_TOKEN")
    error_message = "Segredos não podem ir em environment_variables comuns."
  }

  assert {
    condition     = !contains(keys(azurerm_container_group.app[0].container[0].secure_environment_variables), "OPENROUTER_API_KEY")
    error_message = "Segredo vazio deve ser omitido (assistente em modo alternativo)."
  }

  assert {
    condition     = azurerm_container_group.app[0].ip_address_type == "Public" && azurerm_container_group.app[0].os_type == "Linux"
    error_message = "ACI deve ser Linux com IP público."
  }

  assert {
    condition     = output.app_url == "http://acessacidade-teste.brazilsouth.azurecontainer.io:8000"
    error_message = "app_url fora do formato http://<fqdn>:8000."
  }

  assert {
    condition     = output.health_url == "http://acessacidade-teste.brazilsouth.azurecontainer.io:8000/health"
    error_message = "health_url fora do formato esperado."
  }
}

run "porta_diferente_de_8000_e_rejeitada" {
  command = plan

  variables {
    app_port = 22
  }

  expect_failures = [var.app_port]
}
