# PiChat Azure Infrastructure

This directory contains Terraform code to set up the Azure infrastructure required for the PiChat application.

## Resources Created

- **Resource Group**: Container for all resources
- **Azure Cosmos DB**: NoSQL database with containers for:
  - Chats
  - Messages
  - Users
  - Settings
  - Processed messages
- **Azure Key Vault**: For securely storing secrets and connection strings
- **Azure Cognitive Services Speech**: For voice recognition and speech synthesis
- **Azure OpenAI Service**: For ChatGPT API integration
- **Azure IoT Hub**: For Raspberry Pi device communication

## Prerequisites

- [Terraform](https://www.terraform.io/downloads.html) (v1.0.0 or higher)
- [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli) (latest version)
- Azure subscription

## Getting Started

1. **Login to Azure**

    ```bash
    az login
    ```

2. **Initialize Terraform**

    ```bash
    terraform init
    ```

3. **Create terraform.tfvars file (required)**

    Create a `dev.tfvars` file to customize variables:

    ```
    project_name = "pichat"
    environment = "dev"
    location = "uksouth"
    subscription_id = "your-subscription-id"
    additional_user_email = "your-email@example.com" # Optional
    ```

4. **Plan the deployment**

    ```bash
    terraform plan -var-file="environments/{env}.tfvars" -out=tfplan
    ```

5. **Apply the plan**

    ```bash
    terraform apply tfplan
    ```

6. **Update Backend Environment Variables**

    After deployment, update your Backend `.env` file with the generated outputs:

    You can get these values from the Azure Key Vault or from the Terraform outputs.

## Module Structure

```
Infrastructure/
├── main.tf             # Main Terraform configuration
├── variables.tf        # Input variables
├── environments/       # Environment-specific configurations
└── modules/
    ├── cosmos_db/      # Azure Cosmos DB configuration
    ├── key_vault/      # Azure Key Vault for secrets
    ├── speech_services/# Azure Cognitive Services Speech
    ├── openai/         # Azure OpenAI Service
    ├── iot_hub/        # Azure IoT Hub for device communication
    ├── auth/           # Azure AD authentication (currently disabled)
    └── storage/        # Azure Storage Account (currently disabled)
```

## Customization

You can customize the deployment by modifying the variables in:

- `{environment name}.tfvars` - For environment-specific values
- `variables.tf` - For default values and variable definitions

## Cleanup

To destroy all created resources:

```bash
terraform destroy
``` 