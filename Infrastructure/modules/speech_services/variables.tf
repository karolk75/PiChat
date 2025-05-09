variable "speech_service_name" {
  description = "Name of the speech service resource"
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
  description = "The SKU of the speech service"
  type        = string
  default     = "S0"
}

variable "tags" {
  description = "Tags to apply to the resources"
  type        = map(string)
  default     = {}
}