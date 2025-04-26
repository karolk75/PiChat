# Azure AD Application Registration
resource "azuread_application" "app" {
  display_name = var.application_name
  
  # Web platform configuration for single tenant auth
  web {
    redirect_uris = var.redirect_uris
    implicit_grant {
      access_token_issuance_enabled = true
      id_token_issuance_enabled     = true
    }
  }

  # API configuration
  api {
    requested_access_token_version = 2
    oauth2_permission_scope {
      admin_consent_description  = "Allow the application to access ${var.application_name} on behalf of the signed-in user"
      admin_consent_display_name = "Access ${var.application_name}"
      enabled                    = true
      id                         = "00000000-0000-0000-0000-000000000001" # This is a placeholder UUID
      type                       = "User"
      user_consent_description   = "Allow the application to access ${var.application_name} on your behalf"
      user_consent_display_name  = "Access ${var.application_name}"
      value                      = "user_impersonation"
    }
  }

  # Single tenant configuration
  sign_in_audience = "AzureADMyOrg"
}

# Service Principal for the application
resource "azuread_service_principal" "sp" {
  client_id = azuread_application.app.client_id
}

# App password/client secret
resource "azuread_application_password" "app_password" {
  application_id = azuread_application.app.object_id
  display_name   = "Terraform managed secret"
} 