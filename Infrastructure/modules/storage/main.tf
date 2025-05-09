resource "azurerm_storage_account" "storage" {
  name                     = var.storage_account_name
  resource_group_name      = var.resource_group_name
  location                 = var.location
  account_tier             = var.account_tier
  account_replication_type = var.account_replication_type
  tags                     = var.tags

  # Features specific for blob storage used for checkpointing
  min_tls_version          = "TLS1_2"
  https_traffic_only_enabled = true
  
  # Cost optimization settings
  blob_properties {
    delete_retention_policy {
      days = 7
    }
  }
}

# Create a container for checkpoint storage
resource "azurerm_storage_container" "checkpoint_container" {
  name                  = "checkpoints"
  storage_account_name  = azurerm_storage_account.storage.name
  container_access_type = "private"
} 