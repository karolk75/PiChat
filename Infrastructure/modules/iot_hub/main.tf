resource "azurerm_iothub" "iothub" {
  name                = var.iot_hub_name
  resource_group_name = var.resource_group_name
  location            = var.location
  tags                = var.tags

  sku {
    name     = var.sku_name
    capacity = var.sku_capacity
  }

  # Set the partition count explicitly for the events endpoint
  event_hub_partition_count = 2
  event_hub_retention_in_days = 1

  # Default fallback route - enable all device messages to go to the events endpoint
  fallback_route {
    source         = "DeviceMessages"
    endpoint_names = ["events"]
    enabled        = true
  }


  # Cloud to Device messaging settings - crucial for sending responses back to Pi
  cloud_to_device {
    max_delivery_count = 1
    default_ttl        = "PT15M"
    feedback {
      time_to_live       = "PT15M"
      max_delivery_count = 1
      lock_duration      = "PT30S"
    }
  }

  # Public network access is enabled for local development
  public_network_access_enabled = true
}

# Consumer group for the built-in endpoint - backend service will connect to this
resource "azurerm_iothub_consumer_group" "backend" {
  name                   = "backend"
  iothub_name            = azurerm_iothub.iothub.name
  eventhub_endpoint_name = "events"
  resource_group_name    = var.resource_group_name
}

# IoT Hub shared access policy for backend service
resource "azurerm_iothub_shared_access_policy" "backend_service" {
  name                = "backend-service"
  resource_group_name = var.resource_group_name
  iothub_name         = azurerm_iothub.iothub.name
  
  # Allow backend to register devices and send/receive messages
  registry_read   = true
  registry_write  = true
  service_connect = true
}
