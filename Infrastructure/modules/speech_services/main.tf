resource "azurerm_cognitive_account" "speech" {
  name                = var.speech_service_name
  location            = var.location
  resource_group_name = var.resource_group_name
  kind                = "SpeechServices"
  sku_name            = var.sku
  tags                = var.tags

  identity {
    type = "SystemAssigned"
  }
}