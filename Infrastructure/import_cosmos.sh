#!/bin/bash

# This script helps import the existing CosmosDB account into Terraform state
# Run this script with your subscription ID and resource group name

# Get the provider prefix from your terraform state
PROVIDER_PREFIX=$(terraform state list | grep module.cosmos_db | head -n 1 | sed 's/\..*$//')

# Import the existing CosmosDB account
terraform import ${PROVIDER_PREFIX}.azurerm_cosmosdb_account.db \
  /subscriptions/$SUBSCRIPTION_ID/resourceGroups/rg-pichat-dev/providers/Microsoft.DocumentDB/databaseAccounts/cosmos-pichat-dev

echo "CosmosDB account imported successfully!"
echo "Now you can run 'terraform plan' and 'terraform apply' again." 