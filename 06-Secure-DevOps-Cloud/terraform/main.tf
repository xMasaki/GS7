# =====================================================================
# AcessaCidade — infraestrutura Azure (conceito do exercício Calango TI:
# Azure Container Registry + Azure Container Instances)
#
#   Resource Group
#    ├── Azure Container Registry (Basic, admin desabilitado)
#    ├── User Assigned Managed Identity  ──(AcrPull)──> ACR
#    ├── [fase 2] Container Group (ACI, Linux, IP público, SOMENTE porta 8000/TCP)
#    └── [opcional] Log Analytics Workspace (enable_log_analytics)
#
# NÃO existe porta administrativa (SSH 22 / RDP 3389): o ACI não tem VM para
# administrar. Diagnóstico via "az container logs" / "az container exec".
# =====================================================================

resource "random_string" "suffix" {
  length  = 6
  lower   = true
  upper   = false
  numeric = true
  special = false
}

locals {
  suffix         = var.name_suffix != "" ? var.name_suffix : random_string.suffix.result
  base_name      = "${var.project_prefix}-${var.environment}"
  acr_name       = substr("${replace(var.project_prefix, "-", "")}acr${local.suffix}", 0, 50)
  dns_name_label = var.dns_name_label != "" ? var.dns_name_label : "${var.project_prefix}-${local.suffix}"
  image_ref      = "${azurerm_container_registry.acr.login_server}/${var.image_name}:${var.image_tag}"

  common_tags = merge({
    projeto    = "AcessaCidade"
    disciplina = "06-Secure-DevOps-Cloud"
    ambiente   = var.environment
    gerenciado = "terraform"
    ods        = "11"
  }, var.tags)

  # Variáveis NÃO sensíveis (valores vazios são omitidos)
  app_environment = {
    for k, v in merge({
      APP_ENV          = var.app_env
      APP_PORT         = tostring(var.app_port)
      LOG_LEVEL        = var.log_level
      DATA_DIR         = "/app/data/runtime"
      SEED_DEMO_DATA   = var.seed_demo_data ? "true" : "false"
      CIDADE_PADRAO    = var.cidade_padrao
      OPENROUTER_MODEL = var.openrouter_model
    }, var.extra_environment_variables) : k => v if v != ""
  }

  # Segredos: vão em secure_environment_variables (não aparecem no portal nem
  # em "az container show"). Valores vazios são omitidos => funcionalidade desativada.
  app_secrets = {
    for k, v in {
      OPENROUTER_API_KEY = var.openrouter_api_key
      ADMIN_TOKEN        = var.admin_token
      PIPELINE_TOKEN     = var.pipeline_token
    } : k => v if v != ""
  }
}

# --- Grupo de recursos ---------------------------------------------------------

resource "azurerm_resource_group" "main" {
  name     = "rg-${local.base_name}"
  location = var.location
  tags     = local.common_tags
}

# --- Registro de imagens -------------------------------------------------------

resource "azurerm_container_registry" "acr" {
  name                = local.acr_name
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  sku                 = var.acr_sku

  # Sem usuário/senha administrativos: o pull é feito pela identidade gerenciada
  # (AcrPull) e o push pelo CI via Entra ID (OIDC) com "az acr login".
  admin_enabled = false

  tags = local.common_tags
}

# --- Identidade gerenciada para o ACI baixar a imagem ---------------------------

resource "azurerm_user_assigned_identity" "aci" {
  name                = "id-${local.base_name}-aci"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  tags                = local.common_tags
}

# Menor privilégio: somente leitura de imagens no ACR deste projeto
resource "azurerm_role_assignment" "acr_pull" {
  scope                = azurerm_container_registry.acr.id
  role_definition_name = "AcrPull"
  principal_id         = azurerm_user_assigned_identity.aci.principal_id
  principal_type       = "ServicePrincipal"
}

# --- Logs na nuvem (opcional, tem custo) ----------------------------------------

resource "azurerm_log_analytics_workspace" "logs" {
  count = var.enable_log_analytics ? 1 : 0

  name                = "log-${local.base_name}-${local.suffix}"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  sku                 = "PerGB2018"
  retention_in_days   = var.log_analytics_retention_days
  daily_quota_gb      = 1
  tags                = local.common_tags
}

# --- Aplicação (fase 2: somente depois do push da imagem) -----------------------

resource "azurerm_container_group" "app" {
  count = var.deploy_container ? 1 : 0

  name                = "aci-${local.base_name}"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  os_type             = "Linux"
  restart_policy      = "Always"

  ip_address_type = "Public"
  dns_name_label  = local.dns_name_label

  # Única porta pública: a da aplicação (HTTP 8000). Nenhuma porta de administração.
  exposed_port {
    port     = var.app_port
    protocol = "TCP"
  }

  identity {
    type         = "UserAssigned"
    identity_ids = [azurerm_user_assigned_identity.aci.id]
  }

  image_registry_credential {
    server                    = azurerm_container_registry.acr.login_server
    user_assigned_identity_id = azurerm_user_assigned_identity.aci.id
  }

  container {
    name   = "acessacidade"
    image  = local.image_ref
    cpu    = var.container_cpu
    memory = var.container_memory

    ports {
      port     = var.app_port
      protocol = "TCP"
    }

    environment_variables        = local.app_environment
    secure_environment_variables = local.app_secrets

    liveness_probe {
      http_get {
        path   = "/health"
        port   = var.app_port
        scheme = "http"
      }
      initial_delay_seconds = 40
      period_seconds        = 30
      timeout_seconds       = 5
      failure_threshold     = 3
    }

    readiness_probe {
      http_get {
        path   = "/health"
        port   = var.app_port
        scheme = "http"
      }
      initial_delay_seconds = 15
      period_seconds        = 10
      timeout_seconds       = 5
      failure_threshold     = 3
    }
  }

  dynamic "diagnostics" {
    for_each = var.enable_log_analytics ? [1] : []
    content {
      log_analytics {
        workspace_id  = azurerm_log_analytics_workspace.logs[0].workspace_id
        workspace_key = azurerm_log_analytics_workspace.logs[0].primary_shared_key
      }
    }
  }

  tags = local.common_tags

  # A permissão AcrPull precisa existir antes do primeiro pull da imagem
  depends_on = [azurerm_role_assignment.acr_pull]
}
