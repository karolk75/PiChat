variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
}

variable "location" {
  description = "Azure region to deploy resources"
  type        = string
}

variable "cosmos_db_name" {
  description = "Name of the Cosmos DB account"
  type        = string
}

variable "database_name" {
  description = "Name of the Cosmos DB database"
  type        = string
}

variable "containers" {
  description = "Cosmos DB containers configuration"
  type = list(object({
    name                = string
    partition_key_paths = list(string)
  }))
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
} 