variable "iot_hub_name" {
  description = "Name of the IoT Hub"
  type        = string
}

variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
}

variable "location" {
  description = "Azure region to deploy resources"
  type        = string
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}

variable "sku_name" {
  description = "The SKU name of the IoT Hub. Possible values are B1, B2, B3, F1, S1, S2, and S3."
  type        = string
  default     = "F1"
}

variable "sku_capacity" {
  description = "The number of IoT Hub units"
  type        = number
  default     = 1
} 