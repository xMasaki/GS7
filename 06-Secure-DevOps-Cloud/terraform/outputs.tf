output "resource_group_name" {
  description = "Nome do Resource Group criado."
  value       = azurerm_resource_group.main.name
}

output "acr_name" {
  description = "Nome do Azure Container Registry (usado em az acr login / az acr build)."
  value       = azurerm_container_registry.acr.name
}

output "acr_login_server" {
  description = "Servidor de login do ACR (prefixo da imagem)."
  value       = azurerm_container_registry.acr.login_server
}

output "aci_identity_client_id" {
  description = "Client ID da identidade gerenciada usada pelo ACI para baixar a imagem."
  value       = azurerm_user_assigned_identity.aci.client_id
}

output "image" {
  description = "Referência completa da imagem implantada (ou a implantar)."
  value       = local.image_ref
}

output "container_group_name" {
  description = "Nome do Container Group (null na fase 1)."
  value       = var.deploy_container ? azurerm_container_group.app[0].name : null
}

output "container_fqdn" {
  description = "FQDN público do container (null na fase 1)."
  value       = var.deploy_container ? azurerm_container_group.app[0].fqdn : null
}

output "container_ip" {
  description = "IP público do container (null na fase 1)."
  value       = var.deploy_container ? azurerm_container_group.app[0].ip_address : null
}

output "app_url" {
  description = "URL pública do MVP (HTTP na porta 8000 — o ACI não oferece HTTPS nativo)."
  value       = var.deploy_container ? "http://${azurerm_container_group.app[0].fqdn}:${var.app_port}" : null
}

output "health_url" {
  description = "URL do health check."
  value       = var.deploy_container ? "http://${azurerm_container_group.app[0].fqdn}:${var.app_port}/health" : null
}

output "metrics_url" {
  description = "URL das métricas Prometheus (alvo do prometheus.azure.yml)."
  value       = var.deploy_container ? "http://${azurerm_container_group.app[0].fqdn}:${var.app_port}/metrics" : null
}
