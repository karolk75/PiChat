output "application_id" {
  description = "The Application ID"
  value       = azuread_application.app.client_id
}

output "client_id" {
  description = "The Client ID"
  value       = azuread_application.app.client_id
}

output "client_secret" {
  description = "The Client Secret"
  value       = azuread_application_password.app_password.value
  sensitive   = true
}

output "object_id" {
  description = "The Object ID of the application"
  value       = azuread_application.app.object_id
} 