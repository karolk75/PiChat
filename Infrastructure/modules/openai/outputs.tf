output "openai_id" {
  value = azurerm_cognitive_account.openai.id
}

output "openai_endpoint" {
  value = azurerm_cognitive_account.openai.endpoint
}

output "openai_key" {
  value     = azurerm_cognitive_account.openai.primary_access_key
  sensitive = true
}

output "openai_model_deployment_id" {
  value = azurerm_cognitive_deployment.gpt_model.id
} 