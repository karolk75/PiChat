output "iot_hub_name" {
  description = "The name of the IoT Hub"
  value       = azurerm_iothub.iothub.name
}

output "iot_hub_hostname" {
  description = "The hostname of the IoT Hub"
  value       = azurerm_iothub.iothub.hostname
}

output "backend_service_connection_string" {
  description = "The connection string for the backend service"
  value       = azurerm_iothub_shared_access_policy.backend_service.primary_connection_string
  sensitive   = true
}

output "event_hub_endpoint" {
  description = "The Event Hub-compatible endpoint for receiving device-to-cloud messages"
  value       = azurerm_iothub.iothub.event_hub_events_endpoint
  sensitive   = true
}

output "event_hub_path" {
  description = "The Event Hub-compatible path"
  value       = azurerm_iothub.iothub.event_hub_events_path
}

# Local development helper outputs
output "backend_service_connection_string_example" {
  description = "Example code for using the connection string in the backend"
  value       = "// Set in your local .env file or environment variables:\n// IOTHUB_CONNECTION_STRING=<backend_service_connection_string>"
}

output "raspberry_pi_connection_info" {
  description = "Information on how to set up Raspberry Pi with IoT Hub"
  value       = "# Register your Pi and get its connection string:\naz iot hub device-identity create --hub-name ${azurerm_iothub.iothub.name} --device-id raspberry-pi-1\naz iot hub device-identity connection-string show --hub-name ${azurerm_iothub.iothub.name} --device-id raspberry-pi-1\n\n# Then set in your Pi's environment:\n# IOTHUB_DEVICE_CONNECTION_STRING=<device_connection_string>"
} 