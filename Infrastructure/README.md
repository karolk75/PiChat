# PiChat Azure Infrastructure

This directory contains Terraform code to set up the Azure infrastructure required for the PiChat application.

## Resources Created

- **Resource Group**: Container for all resources
- **Azure Cosmos DB**: NoSQL database with containers for:
  - Chats
  - Messages
  - Users
  - Settings
- **Azure AD Application**: For single-tenant authentication
- **Azure Key Vault**: For securely storing secrets and connection strings

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

3. **Create terraform.tfvars file (optional)**

    Create a `terraform.tfvars` file to customize variables:

    ```
    project_name = "pichat"
    environment = "dev"
    location = "eastus"
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

    ```
    COSMOS_ENDPOINT=<cosmos_db_endpoint>
    COSMOS_KEY=<cosmos_primary_master_key>
    ```

    You can get these values from the Azure Key Vault or from the Terraform outputs.

## Module Structure

```
Infrastructure/
├── main.tf             # Main Terraform configuration
├── variables.tf        # Input variables
├── environments/       # Environment-specific configurations
└── modules/
    ├── cosmos_db/      # Azure Cosmos DB configuration
    ├── auth/           # Azure AD authentication
    └── key_vault/      # Azure Key Vault for secrets
```

## Customization

You can customize the deployment by modifying the variables in:

- `terraform.tfvars` - For environment-specific values
- `variables.tf` - For default values and variable definitions

## Cleanup

To destroy all created resources:

```bash
terraform destroy
``` 