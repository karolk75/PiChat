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

variable "openai_key" {
  description = "OpenAI key"
  type        = string
  sensitive   = true
}

variable "openai_endpoint" {
  description = "OpenAI endpoint"
  type        = string
  sensitive   = true
}

variable "openai_model_deployment_id" {
  description = "OpenAI model deployment id"
  type        = string
}

variable "speech_service_key" {
  description = "Speech service key"
  type        = string
  sensitive   = true
}

variable "speech_service_endpoint" {
  description = "Speech service endpoint"
  type        = string
  sensitive   = true
}

variable "additional_user_email" {
  description = "Email of additional user to grant access to Key Vault"
  type        = string
  default     = ""
}

variable "iot_hub_connection_string" {
  description = "IoT Hub connection string"
  type        = string
  sensitive   = true
  default     = ""
}

variable "iot_hub_event_hub_endpoint" {
  description = "IoT Hub Event Hub-compatible endpoint"
  type        = string
  sensitive   = true
  default     = ""
}

variable "iot_hub_event_hub_path" {
  description = "IoT Hub Event Hub-compatible path"
  type        = string
  default     = ""
}

variable "checkpoint_storage_connection_string" {
  description = "Storage account connection string for IoT Hub checkpoints"
  type        = string
  sensitive   = true
  default     = ""
}







