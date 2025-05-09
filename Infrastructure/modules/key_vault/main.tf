# Data source to get the user object ID from email
data "azuread_user" "additional_user" {
  count               = var.additional_user_email != "" ? 1 : 0
  user_principal_name = var.additional_user_email
}

# Key Vault Resource
resource "azurerm_key_vault" "kv" {
  name                = var.key_vault_name
  location            = var.location
  resource_group_name = var.resource_group_name
  tenant_id           = var.tenant_id
  sku_name            = "standard"

  # Enable access to the current user deploying this
  access_policy {
    tenant_id = var.tenant_id
    object_id = var.object_id

    secret_permissions = [
      "Get", "List", "Set", "Delete", "Purge", "Recover", "Backup", "Restore"
    ]
  }
  
  # Access policy for additional user (if provided)
  dynamic "access_policy" {
    for_each = var.additional_user_email != "" ? [1] : []
    content {
      tenant_id = var.tenant_id
      object_id = data.azuread_user.additional_user[0].id

      secret_permissions = [
        "Get", "List"
      ]
    }
  }

  tags = var.tags
}

# Store Cosmos DB Connection Strings in Key Vault
resource "azurerm_key_vault_secret" "cosmos_endpoint" {
  name         = "cosmos-endpoint"
  value        = var.cosmos_endpoint
  key_vault_id = azurerm_key_vault.kv.id
}

resource "azurerm_key_vault_secret" "cosmos_key" {
  name         = "cosmos-key"
  value        = var.cosmos_key
  key_vault_id = azurerm_key_vault.kv.id
}

# Store Azure AD App Registration credentials in Key Vault
# resource "azurerm_key_vault_secret" "app_client_id" {
#   name         = "app-client-id"
#   value        = var.app_client_id
#   key_vault_id = azurerm_key_vault.kv.id
# }

# resource "azurerm_key_vault_secret" "app_client_secret" {
#   name         = "app-client-secret"
#   value        = var.app_client_secret
#   key_vault_id = azurerm_key_vault.kv.id
# } 

# Store OpenAI credentials in Key Vault
resource "azurerm_key_vault_secret" "openai_key" {
  name         = "openai-key"
  value        = var.openai_key
  key_vault_id = azurerm_key_vault.kv.id
}

resource "azurerm_key_vault_secret" "openai_endpoint" {
  name         = "openai-endpoint"
  value        = var.openai_endpoint
  key_vault_id = azurerm_key_vault.kv.id
}

# Store Speech Services credentials in Key Vault
resource "azurerm_key_vault_secret" "speech_key" {
  name         = "speech-service-key"
  value        = var.speech_service_key
  key_vault_id = azurerm_key_vault.kv.id
}

resource "azurerm_key_vault_secret" "speech_endpoint" {
  name         = "speech-service-endpoint"
  value        = var.speech_service_endpoint
  key_vault_id = azurerm_key_vault.kv.id
}

# Store IoT Hub credentials in Key Vault
resource "azurerm_key_vault_secret" "iot_hub_connection_string" {
  name         = "iot-hub-connection-string"
  value        = var.iot_hub_connection_string
  key_vault_id = azurerm_key_vault.kv.id
}

resource "azurerm_key_vault_secret" "iot_hub_event_hub_endpoint" {
  name         = "iot-hub-event-hub-endpoint"
  value        = var.iot_hub_event_hub_endpoint
  key_vault_id = azurerm_key_vault.kv.id
}

resource "azurerm_key_vault_secret" "iot_hub_event_hub_path" {
  name         = "iot-hub-event-hub-path"
  value        = var.iot_hub_event_hub_path
  key_vault_id = azurerm_key_vault.kv.id
}

# Store Storage Account connection string for IoT Hub checkpoints
resource "azurerm_key_vault_secret" "checkpoint_storage_connection_string" {
  name         = "checkpoint-storage-connection-string"
  value        = var.checkpoint_storage_connection_string
  key_vault_id = azurerm_key_vault.kv.id
}
