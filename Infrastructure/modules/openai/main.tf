resource "azurerm_cognitive_account" "openai" {
  name                = var.openai_service_name
  # location            = var.location
  location            = "eastus2"
  resource_group_name = var.resource_group_name
  kind                = "OpenAI"
  sku_name            = var.sku
  tags                = var.tags

  identity {
    type = "SystemAssigned"
  }
}

resource "azurerm_cognitive_deployment" "gpt_model" {
  name                 = var.model_deployment_name
  cognitive_account_id = azurerm_cognitive_account.openai.id
  model {
    format  = "OpenAI"
    name    = var.model_name
    version = var.model_version
  }

  scale {
    type     = "GlobalStandard"
    capacity = var.model_capacity
  }
}