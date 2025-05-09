output "speech_service_id" {
  value = azurerm_cognitive_account.speech.id
}

output "speech_service_endpoint" {
  value = azurerm_cognitive_account.speech.endpoint
}

output "speech_service_key" {
  value     = azurerm_cognitive_account.speech.primary_access_key
  sensitive = true
} 