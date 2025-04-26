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