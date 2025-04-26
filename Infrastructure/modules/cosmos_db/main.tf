resource "azurerm_cosmosdb_account" "db" {
  name                = var.cosmos_db_name
  location            = var.location
  resource_group_name = var.resource_group_name
  offer_type          = "Standard"
  kind                = "GlobalDocumentDB"

  consistency_policy {
    consistency_level       = "Session"
    max_interval_in_seconds = 5
    max_staleness_prefix    = 100
  }

  geo_location {
    location          = var.location
    failover_priority = 0
  }

  capabilities {
    name = "EnableServerless"
  }

  tags = var.tags
}

# Create Cosmos DB Database
resource "azurerm_cosmosdb_sql_database" "database" {
  name                = var.database_name
  resource_group_name = var.resource_group_name
  account_name        = azurerm_cosmosdb_account.db.name
}

# Create Cosmos DB Containers
resource "azurerm_cosmosdb_sql_container" "containers" {
  count               = length(var.containers)
  name                = var.containers[count.index].name
  resource_group_name = var.resource_group_name
  account_name        = azurerm_cosmosdb_account.db.name
  database_name       = azurerm_cosmosdb_sql_database.database.name
  partition_key_paths = var.containers[count.index].partition_key_paths
  
  # Default indexing policy
  indexing_policy {
    indexing_mode = "consistent"
    
    included_path {
      path = "/*"
    }
    
    excluded_path {
      path = "/\"_etag\"/?"
    }
  }
} 