variable "openai_service_name" {
  description = "Name of the OpenAI service resource"
  type        = string
}

variable "location" {
  description = "Azure region to deploy resources"
  type        = string
}

variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
}

variable "sku" {
  description = "The SKU of the OpenAI service"
  type        = string
  default     = "S0"
}

variable "tags" {
  description = "Tags to apply to the resources"
  type        = map(string)
  default     = {}
}

variable "model_deployment_name" {
  description = "Name of the model deployment"
  type        = string
}

variable "model_name" {
  description = "Name of the model to deploy"
  type        = string
  default     = "gpt-4o-mini"
}

variable "model_version" {
  description = "Version of the model to deploy"
  type        = string
  default     = "2024-07-18"
}

variable "model_capacity" {
  description = "Capacity of the model deployment"
  type        = number
  default     = 1
}