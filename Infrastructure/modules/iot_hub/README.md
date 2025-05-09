# Azure IoT Hub Module for PiChat Local Development

This Terraform module creates an Azure IoT Hub for the PiChat project, specifically configured for local development where:

- Raspberry Pi runs locally and connects to IoT Hub
- Backend application runs on localhost:8080
- Backend handles data storage and response generation
- IoT Hub serves only as a message broker between Pi and backend

## Architecture for Local Development

1. **Raspberry Pi**:
   - Runs locally with wake word detection & audio capture
   - Sends speech-to-text results to IoT Hub
   - Receives responses from IoT Hub and plays them via text-to-speech

2. **Azure IoT Hub**:
   - Provides cloud connectivity for the Pi
   - Routes messages between Pi and backend
   - Handles device identity and authentication
   - Provides stable endpoints even during local development

3. **Local Backend (localhost:8080)**:
   - Receives messages from IoT Hub
   - Stores conversations in database
   - Generates responses via OpenAI
   - Sends responses back to Pi via IoT Hub

## Local Development Data Flow

1. User speaks → Pi recognizes wake word
2. Pi converts speech to text
3. Pi sends text as device-to-cloud message to IoT Hub
4. Backend receives message from IoT Hub
5. Backend processes message, stores in database, generates response
6. Backend sends response as cloud-to-device message to IoT Hub
7. IoT Hub delivers response to Pi
8. Pi converts response to speech

## Setup for Local Development

### Backend (localhost:8080)

1. Register your app with Azure IoT Hub using the backend service connection string:

```js
// Example in Node.js
require('dotenv').config(); // Load .env file
const { EventHubConsumerClient } = require('@azure/event-hubs');
const { ServiceClient } = require('azure-iothub');

// Connection string from Terraform output
const connectionString = process.env.IOTHUB_CONNECTION_STRING;
const consumerGroup = 'backend'; // Created by Terraform

// Listen for device-to-cloud messages
const consumerClient = new EventHubConsumerClient(consumerGroup, connectionString);
consumerClient.subscribe({
  processEvents: async (events) => {
    for (const event of events) {
      console.log(`Message from device: ${event.body.message}`);
      // Process message, generate response...
    }
  },
  processError: async (err) => {
    console.error(err);
  }
});

// Send cloud-to-device message
const serviceClient = ServiceClient.fromConnectionString(connectionString);
const message = {
  deviceId: 'raspberry-pi-1',
  message: { 
    body: 'This is the response from the backend'
  }
};
serviceClient.send(message.deviceId, JSON.stringify(message.message));
```

### Raspberry Pi

1. Register your Raspberry Pi with Azure IoT Hub and get the device connection string
2. Use the device connection string in your Pi code:

```python
# Example in Python
from azure.iot.device import IoTHubDeviceClient, Message
import json

# Connection string from Azure CLI command
connection_string = "DEVICE_CONNECTION_STRING"
client = IoTHubDeviceClient.create_from_connection_string(connection_string)

# Send message to backend
message = Message(json.dumps({"message": "Hello from Pi!"}))
client.send_message(message)

# Receive message from backend
client.on_message_received = lambda message: print(f"Message received: {message.data.decode()}")
```

## Usage

```hcl
module "iot_hub" {
  source              = "./modules/iot_hub"
  iot_hub_name        = "iot-pichat-dev"
  resource_group_name = azurerm_resource_group.rg.name
  location            = var.location
  tags                = var.tags
  sku_name            = "S1"  # Standard tier
  sku_capacity        = 1     # Units
}
```

## Note on Security

For local development, the IoT Hub is configured with public network access enabled. In production, consider:

1. Using private endpoints or IP restrictions
2. Implementing more granular access policies
3. Setting up monitoring and alerts 