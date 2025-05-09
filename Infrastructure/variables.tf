variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "pichat"
}

variable "subscription_id" {
  description = "Azure subscription ID"
  type        = string
}

variable "additional_user_email" {
  description = "Email of additional user to grant access to Key Vault"
  type        = string
  default     = ""
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

# Speech Services variables
variable "speech_services_sku" {
  description = "The SKU of the speech service"
  type        = string
  default     = "S0"
}

# OpenAI Service variables
variable "openai_sku" {
  description = "The SKU of the OpenAI service"
  type        = string
  default     = "S0"
}

variable "openai_model_deployment_name" {
  description = "Name of the OpenAI model deployment"
  type        = string
  default     = "gpt35turbo"
}

variable "openai_model_name" {
  description = "Name of the OpenAI model to deploy"
  type        = string
  default     = "gpt-35-turbo-16k"
}

variable "openai_model_version" {
  description = "Version of the OpenAI model to deploy"
  type        = string
  default     = "0301"
}

variable "openai_model_capacity" {
  description = "Capacity of the OpenAI model deployment"
  type        = number
  default     = 1
}

# IoT Hub variables
variable "iot_hub_sku_name" {
  description = "The SKU name of the IoT Hub"
  type        = string
  default     = "F1"
}

variable "iot_hub_sku_capacity" {
  description = "The number of IoT Hub units"
  type        = number
  default     = 1
} 
