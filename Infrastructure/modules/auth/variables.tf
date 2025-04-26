variable "application_name" {
  description = "Name of the Azure AD application"
  type        = string
}

variable "redirect_uris" {
  description = "Redirect URIs for the Azure AD application"
  type        = list(string)
  default     = []
}

variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
}

variable "api_scopes" {
  description = "List of API scopes to create"
  type        = list(string)
  default     = ["user_impersonation"]
} 