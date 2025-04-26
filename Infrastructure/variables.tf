variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "pichat"
}

variable "subscription_id" {
  description = "Azure subscription ID"
  type        = string
}

variable "environment" {
  description = "Environment (dev, test, prod)"
  type        = string
  default     = "dev"
}

variable "location" {
  description = "Azure region to deploy resources"
  type        = string
  default     = "uksouth"
}

variable "cosmos_database_name" {
  description = "Name of the Cosmos DB database"
  type        = string
  default     = "pichat"
}

variable "cosmos_containers" {
  description = "Cosmos DB containers configuration"
  type = list(object({
    name                = string
    partition_key_paths = list(string)
  }))
  default = [
    {
      name                = "chats"
      partition_key_paths = ["/id"]
    },
    {
      name                = "messages"
      partition_key_paths = ["/chat_id"]
    },
    {
      name                = "users"
      partition_key_paths = ["/id"]
    },
    {
      name                = "settings"
      partition_key_paths = ["/user_id"]
    }
  ]
}

variable "redirect_uris" {
  description = "Redirect URIs for the Azure AD application"
  type        = list(string)
  default     = ["http://localhost:3000/", "http://localhost:8080/docs/oauth2-redirect/"]
} 
