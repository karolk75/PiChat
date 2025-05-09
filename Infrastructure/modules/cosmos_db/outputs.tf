output "cosmos_endpoint" {
  description = "The endpoint of the Cosmos DB account"
  value       = azurerm_cosmosdb_account.cosmos_db.endpoint
}

output "primary_master_key" {
  description = "The primary master key for the Cosmos DB account"
  value       = azurerm_cosmosdb_account.cosmos_db.primary_key
  sensitive   = true
}

# output "connection_strings" {
#   description = "Connection strings for the Cosmos DB account"
#   value       = azurerm_cosmosdb_account.db.connection_strings
#   sensitive   = true
# }

output "cosmos_db_id" {
  description = "The ID of the Cosmos DB account"
  value       = azurerm_cosmosdb_account.cosmos_db.id
} 