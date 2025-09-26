#!/bin/bash

# Canvas Smith - Azure Container Apps Deployment Script
# This script builds and deploys the Canvas Smith application to Azure Container Apps

set -e

# Load environment variables
if [ -f .env.azure ]; then
    export $(cat .env.azure | grep -v '#' | xargs)
fi

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Canvas Smith - Azure Container Apps Deployment${NC}"
echo "=================================================="

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo -e "${RED}❌ Azure CLI is not installed. Please install it first.${NC}"
    exit 1
fi

# Login to Azure (if not already logged in)
echo -e "${YELLOW}📋 Checking Azure login status...${NC}"
if ! az account show &> /dev/null; then
    echo -e "${YELLOW}🔐 Please login to Azure...${NC}"
    az login
fi

# Set default subscription (optional)
# az account set --subscription "your-subscription-id"

# Create resource group
echo -e "${YELLOW}📦 Creating resource group: $AZURE_RESOURCE_GROUP${NC}"
az group create \
    --name $AZURE_RESOURCE_GROUP \
    --location $AZURE_LOCATION

# Create Azure Container Registry
echo -e "${YELLOW}🏗️  Creating Azure Container Registry: $AZURE_CONTAINER_REGISTRY${NC}"
az acr create \
    --resource-group $AZURE_RESOURCE_GROUP \
    --name $AZURE_CONTAINER_REGISTRY \
    --sku Basic \
    --admin-enabled true

# Get ACR login server
ACR_LOGIN_SERVER=$(az acr show --name $AZURE_CONTAINER_REGISTRY --resource-group $AZURE_RESOURCE_GROUP --query "loginServer" --output tsv)
echo -e "${GREEN}✅ ACR Login Server: $ACR_LOGIN_SERVER${NC}"

# Build and push Docker image
echo -e "${YELLOW}🔨 Building and pushing Docker image...${NC}"
az acr build \
    --registry $AZURE_CONTAINER_REGISTRY \
    --image canvas-smith:latest \
    .

# Create Container Apps Environment
echo -e "${YELLOW}🌍 Creating Container Apps Environment: $AZURE_ENVIRONMENT_NAME${NC}"
az containerapp env create \
    --name $AZURE_ENVIRONMENT_NAME \
    --resource-group $AZURE_RESOURCE_GROUP \
    --location $AZURE_LOCATION

# Get ACR credentials
ACR_USERNAME=$(az acr credential show --name $AZURE_CONTAINER_REGISTRY --query "username" --output tsv)
ACR_PASSWORD=$(az acr credential show --name $AZURE_CONTAINER_REGISTRY --query "passwords[0].value" --output tsv)

# Create Container App
echo -e "${YELLOW}🚀 Creating Container App: $AZURE_CONTAINER_APP_NAME${NC}"
az containerapp create \
    --name $AZURE_CONTAINER_APP_NAME \
    --resource-group $AZURE_RESOURCE_GROUP \
    --environment $AZURE_ENVIRONMENT_NAME \
    --image $ACR_LOGIN_SERVER/canvas-smith:latest \
    --target-port 8000 \
    --ingress 'external' \
    --registry-server $ACR_LOGIN_SERVER \
    --registry-username $ACR_USERNAME \
    --registry-password $ACR_PASSWORD \
    --env-vars PORT=8000 ENVIRONMENT=production \
    --cpu $CPU_REQUESTS \
    --memory $MEMORY_REQUESTS \
    --min-replicas $MIN_REPLICAS \
    --max-replicas $MAX_REPLICAS

# Get the application URL
APP_URL=$(az containerapp show --name $AZURE_CONTAINER_APP_NAME --resource-group $AZURE_RESOURCE_GROUP --query "properties.configuration.ingress.fqdn" --output tsv)

echo -e "${GREEN}✅ Deployment completed successfully!${NC}"
echo "=================================================="
echo -e "${GREEN}🌐 Application URL: https://$APP_URL${NC}"
echo -e "${GREEN}📖 API Documentation: https://$APP_URL/docs${NC}"
echo -e "${GREEN}❤️  Health Check: https://$APP_URL/health${NC}"
echo "=================================================="
echo -e "${YELLOW}💡 To update the application, run:${NC}"
echo "   az acr build --registry $AZURE_CONTAINER_REGISTRY --image canvas-smith:latest ."
echo "   az containerapp update --name $AZURE_CONTAINER_APP_NAME --resource-group $AZURE_RESOURCE_GROUP --image $ACR_LOGIN_SERVER/canvas-smith:latest"