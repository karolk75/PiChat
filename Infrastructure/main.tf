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

# Speech Services for voice recognition and synthesis
module "speech_services" {
  source              = "./modules/speech_services"
  speech_service_name = "speech-${var.project_name}-${var.environment}"
  resource_group_name = azurerm_resource_group.rg.name
  location            = var.location
  sku                 = var.speech_services_sku
  tags                = local.tags
  depends_on          = [azurerm_resource_group.rg]
}

# Azure OpenAI Service for ChatGPT API
module "openai" {
  source                = "./modules/openai"
  openai_service_name   = "openai-${var.project_name}-${var.environment}"
  resource_group_name   = azurerm_resource_group.rg.name
  location              = var.location
  sku                   = var.openai_sku
  model_deployment_name = var.openai_model_deployment_name
  model_name            = var.openai_model_name
  model_version         = var.openai_model_version
  model_capacity        = var.openai_model_capacity
  tags                  = local.tags
  depends_on            = [azurerm_resource_group.rg]
}

# Azure IoT Hub for Raspberry Pi communication
module "iot_hub" {
  source              = "./modules/iot_hub"
  iot_hub_name        = "iot-${var.project_name}-${var.environment}"
  resource_group_name = azurerm_resource_group.rg.name
  location            = var.location
  tags                = local.tags
  sku_name            = var.iot_hub_sku_name
  sku_capacity        = var.iot_hub_sku_capacity
  depends_on          = [azurerm_resource_group.rg]
}

# Storage Account
# module "checkpoint_storage" {
#   source                  = "./modules/storage"
#   storage_account_name    = "st${var.project_name}${var.environment}"
#   resource_group_name     = azurerm_resource_group.rg.name
#   location                = var.location
#   tags                    = local.tags
#   depends_on              = [azurerm_resource_group.rg]
# }

# Key Vault for storing secrets
module "key_vault" {
  source                     = "./modules/key_vault"
  resource_group_name        = azurerm_resource_group.rg.name
  location                   = var.location
  key_vault_name             = "kv-${var.project_name}-${var.environment}"
  tenant_id                  = data.azurerm_client_config.current.tenant_id
  object_id                  = data.azurerm_client_config.current.object_id
  tags                       = local.tags
  cosmos_endpoint            = module.cosmos_db.cosmos_endpoint
  cosmos_key                 = module.cosmos_db.primary_master_key
  app_client_id              = "dummy-id"     # Dummy value since auth module is commented out
  app_client_secret          = "dummy-secret" # Dummy value since auth module is commented out
  additional_user_email      = var.additional_user_email
  depends_on                 = [azurerm_resource_group.rg]
  openai_key                 = module.openai.openai_key
  openai_endpoint            = module.openai.openai_endpoint
  openai_model_deployment_id = module.openai.openai_model_deployment_id
  speech_service_key         = module.speech_services.speech_service_key
  speech_service_endpoint    = module.speech_services.speech_service_endpoint
  iot_hub_connection_string  = module.iot_hub.backend_service_connection_string
  iot_hub_event_hub_endpoint = module.iot_hub.event_hub_endpoint
  iot_hub_event_hub_path     = module.iot_hub.event_hub_path
  # checkpoint_storage_connection_string = module.checkpoint_storage.primary_connection_string
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

output "speech_service_endpoint" {
  value = module.speech_services.speech_service_endpoint
}

output "openai_endpoint" {
  value = module.openai.openai_endpoint
}

output "iot_hub_hostname" {
  value = module.iot_hub.iot_hub_hostname
}

output "iot_hub_event_hub_endpoint" {
  value     = module.iot_hub.event_hub_endpoint
  sensitive = true
}

output "iot_hub_name" {
  value = module.iot_hub.iot_hub_name
}

# output "checkpoint_storage_account_name" {
#   value = module.checkpoint_storage.storage_account_name
# }
