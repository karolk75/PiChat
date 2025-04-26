variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
}

variable "location" {
  description = "Azure region to deploy resources"
  type        = string
}

variable "key_vault_name" {
  description = "Name of the Key Vault"
  type        = string
}

variable "tenant_id" {
  description = "Azure AD tenant ID"
  type        = string
}

variable "object_id" {
  description = "Object ID of the current user/service principal"
  type        = string
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}

variable "cosmos_endpoint" {
  description = "Cosmos DB endpoint URL"
  type        = string
}

variable "cosmos_key" {
  description = "Cosmos DB primary key"
  type        = string
  sensitive   = true
}

variable "app_client_id" {
  description = "Azure AD application client ID"
  type        = string
}

variable "app_client_secret" {
  description = "Azure AD application client secret"
  type        = string
  sensitive   = true
} 