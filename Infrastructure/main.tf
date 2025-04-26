terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
    azuread = {
      source  = "hashicorp/azuread"
      version = "~> 2.0"
    }
  }
  backend "local" {
    path = "terraform.tfstate"
  }
}

provider "azurerm" {
  features {
    key_vault {
      purge_soft_delete_on_destroy = true
    }
  }
  subscription_id = var.subscription_id
}

provider "azuread" {}

# Local variables
locals {
  tags = {
    Environment = var.environment
    Project     = "PiChat"
    Terraform   = "true"
  }
}

# Resource Group
resource "azurerm_resource_group" "rg" {
  name     = "rg-${var.project_name}-${var.environment}"
  location = var.location
  tags     = local.tags
}

# Cosmos DB Account
module "cosmos_db" {
  source              = "./modules/cosmos_db"
  resource_group_name = azurerm_resource_group.rg.name
  location            = var.location
  cosmos_db_name      = "cosmos-${var.project_name}-${var.environment}"
  database_name       = var.cosmos_database_name
  containers          = var.cosmos_containers
  tags                = local.tags
  depends_on          = [azurerm_resource_group.rg]
}

# Azure AD Application for Authentication
# module "auth" {
#   source            = "./modules/auth"
#   resource_group_name = azurerm_resource_group.rg.name
#   application_name  = "${var.project_name}-app-${var.environment}"
#   api_scopes        = ["user_impersonation"]
#   redirect_uris     = var.redirect_uris
#   depends_on        = [azurerm_resource_group.rg]
# }

# Key Vault for storing secrets
module "key_vault" {
  source              = "./modules/key_vault"
  resource_group_name = azurerm_resource_group.rg.name
  location            = var.location
  key_vault_name      = "kv-${var.project_name}-${var.environment}"
  tenant_id           = data.azurerm_client_config.current.tenant_id
  object_id           = data.azurerm_client_config.current.object_id
  tags                = local.tags
  cosmos_endpoint     = module.cosmos_db.cosmos_endpoint
  cosmos_key          = module.cosmos_db.primary_master_key
  app_client_id       = "dummy-id"      # Dummy value since auth module is commented out
  app_client_secret   = "dummy-secret"  # Dummy value since auth module is commented out
  depends_on          = [azurerm_resource_group.rg]
}

# Current client configuration
data "azurerm_client_config" "current" {}

# Outputs
output "resource_group_name" {
  value = azurerm_resource_group.rg.name
}

output "cosmos_db_endpoint" {
  value = module.cosmos_db.cosmos_endpoint
}

# output "cosmos_db_connection_strings" {
#   value     = module.cosmos_db.connection_strings
#   sensitive = true
# }

# output "application_id" {
#   value = module.auth.application_id
# }

output "tenant_id" {
  value = data.azurerm_client_config.current.tenant_id
}

output "key_vault_uri" {
  value = module.key_vault.key_vault_uri
} 