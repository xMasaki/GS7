# =====================================================================
# Variáveis — AcessaCidade (Azure Container Registry + Container Instances)
# Valores reais ficam em terraform.tfvars (FORA do Git) ou em TF_VAR_* no CI.
# Modelo: terraform.tfvars.example
# =====================================================================

# --- Assinatura e localização --------------------------------------------------

variable "subscription_id" {
  description = "ID da assinatura Azure. Deixe null para usar ARM_SUBSCRIPTION_ID do ambiente (recomendado no CI)."
  type        = string
  default     = null
}

variable "project_prefix" {
  description = "Prefixo dos nomes dos recursos (minúsculas, números e hífen)."
  type        = string
  default     = "acessacidade"

  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{2,20}$", var.project_prefix))
    error_message = "project_prefix deve ter de 3 a 21 caracteres: letras minúsculas, números e hífen, começando por letra."
  }
}

variable "environment" {
  description = "Nome do ambiente (ex.: prod, demo)."
  type        = string
  default     = "prod"

  validation {
    condition     = can(regex("^[a-z0-9]{2,8}$", var.environment))
    error_message = "environment deve ter de 2 a 8 caracteres minúsculos/números."
  }
}

variable "location" {
  description = <<-EOT
    Região Azure. Padrão brazilsouth (menor latência para o cidadão brasileiro e dados no país).
    Observação: preços em brazilsouth costumam ser maiores que em eastus, e algumas assinaturas
    Azure for Students restringem regiões/cotas de ACI. Se a criação falhar por cota/política,
    use "eastus" (documentado em docs/ESTIMATIVA_DE_CUSTOS.md e docs/PUBLICACAO_AZURE.md).
  EOT
  type        = string
  default     = "brazilsouth"
}

variable "name_suffix" {
  description = "Sufixo para nomes globalmente únicos (ACR, DNS). Vazio = gerado aleatoriamente (random_string, guardado no state)."
  type        = string
  default     = ""

  validation {
    condition     = var.name_suffix == "" || can(regex("^[a-z0-9]{3,8}$", var.name_suffix))
    error_message = "name_suffix deve ter de 3 a 8 caracteres minúsculos/números (ou ficar vazio)."
  }
}

variable "tags" {
  description = "Tags extras aplicadas a todos os recursos."
  type        = map(string)
  default     = {}
}

# --- Registro de imagens --------------------------------------------------------

variable "acr_sku" {
  description = "SKU do Azure Container Registry. Basic é o mais barato e suficiente para o MVP."
  type        = string
  default     = "Basic"

  validation {
    condition     = contains(["Basic", "Standard", "Premium"], var.acr_sku)
    error_message = "acr_sku deve ser Basic, Standard ou Premium."
  }
}

variable "image_name" {
  description = "Nome (repositório) da imagem no ACR."
  type        = string
  default     = "acessacidade"
}

variable "image_tag" {
  description = "Tag da imagem a publicar. No CI é o SHA do commit (github.sha) — imutável e rastreável."
  type        = string
  default     = "latest"
}

# --- Container (ACI) -------------------------------------------------------------

variable "deploy_container" {
  description = <<-EOT
    Implantação em 2 fases:
      false (fase 1) = cria apenas Resource Group, ACR e identidade gerenciada (+ AcrPull);
      true  (fase 2) = depois do push da imagem para o ACR, cria o Container Instance.
  EOT
  type        = bool
  default     = false
}

variable "container_cpu" {
  description = "vCPUs do container (ACI cobra por vCPU-segundo)."
  type        = number
  default     = 1
}

variable "container_memory" {
  description = "Memória do container em GB (ACI cobra por GB-segundo)."
  type        = number
  default     = 1.5
}

variable "dns_name_label" {
  description = "Rótulo DNS público do ACI (<label>.<region>.azurecontainer.io). Vazio = <project_prefix>-<sufixo>."
  type        = string
  default     = ""

  validation {
    condition     = var.dns_name_label == "" || can(regex("^[a-z][a-z0-9-]{1,61}[a-z0-9]$", var.dns_name_label))
    error_message = "dns_name_label deve conter apenas minúsculas, números e hífen (3 a 63 caracteres)."
  }
}

variable "app_port" {
  description = "Porta HTTP da aplicação. Única porta exposta publicamente (não há porta administrativa)."
  type        = number
  default     = 8000

  validation {
    condition     = var.app_port == 8000
    error_message = "O contrato de integração fixa APP_PORT=8000 (Dockerfile, probes e Prometheus)."
  }
}

# --- Configuração NÃO sensível da aplicação -------------------------------------

variable "app_env" {
  description = "APP_ENV da aplicação."
  type        = string
  default     = "production"
}

variable "log_level" {
  description = "LOG_LEVEL da aplicação."
  type        = string
  default     = "INFO"
}

variable "seed_demo_data" {
  description = "Carregar denúncias de demonstração (todas SIMULADAS) na primeira inicialização."
  type        = bool
  default     = true
}

variable "cidade_padrao" {
  description = "Cidade usada quando o cidadão não informa uma."
  type        = string
  default     = ""
}

variable "openrouter_model" {
  description = "Modelo usado pelo assistente via OpenRouter."
  type        = string
  default     = "openai/gpt-4o-mini"
}

variable "extra_environment_variables" {
  description = "Variáveis de ambiente NÃO sensíveis adicionais (ex.: RATE_LIMIT_PER_MINUTE, MAX_UPLOAD_MB)."
  type        = map(string)
  default     = {}
}

# --- Segredos (sensitive) — NUNCA em arquivos versionados ------------------------
# Forneça via TF_VAR_openrouter_api_key, TF_VAR_admin_token, TF_VAR_pipeline_token
# (no CI vêm de GitHub Secrets). Vazio = funcionalidade desativada / modo alternativo.

variable "openrouter_api_key" {
  description = "Chave da API OpenRouter (vazio = assistente em modo alternativo por regras)."
  type        = string
  default     = ""
  sensitive   = true
}

variable "admin_token" {
  description = "Token da equipe para revisar/alterar status (vazio = rota desativada, 403)."
  type        = string
  default     = ""
  sensitive   = true
}

variable "pipeline_token" {
  description = "Token do pipeline de dados (vazio = exportação/publicação Gold desativadas, 403)."
  type        = string
  default     = ""
  sensitive   = true
}

# --- Observabilidade na nuvem (opcional) ---------------------------------------

variable "enable_log_analytics" {
  description = <<-EOT
    Cria um Log Analytics Workspace e envia os logs do container para ele.
    Padrão false: o Log Analytics cobra por GB ingerido (ver docs/ESTIMATIVA_DE_CUSTOS.md);
    sem ele, os logs continuam disponíveis via "az container logs".
  EOT
  type        = bool
  default     = false
}

variable "log_analytics_retention_days" {
  description = "Retenção dos logs no Log Analytics (30 dias é o mínimo incluído no preço)."
  type        = number
  default     = 30
}
