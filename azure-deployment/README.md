# Azure Deployment

This directory contains all the necessary files and scripts for deploying Azure resources, including blob storage connections and Azure Function Apps for the Machine Learning Engineer Training project.

## 📁 Directory Structure

```
azure-deployment/
├── pipelines/                  # Azure DevOps pipelines
│   ├── azure-function-ci-cd.yml
│   └── infrastructure-deployment.yml
├── scripts/                    # Modular Python scripts
│   ├── blob_storage.py
│   ├── function_app_deploy.py
│   └── config_manager.py
├── infrastructure/             # Infrastructure as Code (Bicep)
│   ├── main.bicep
│   └── parameters.json
├── config/                     # Configuration files
│   ├── config.json
│   └── .env.template
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## 🚀 Quick Start

### Prerequisites

1. **Azure CLI** - [Install Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)
2. **Azure Functions Core Tools** - [Install Functions Core Tools](https://docs.microsoft.com/en-us/azure/azure-functions/functions-run-local)
3. **Python 3.9+** - [Download Python](https://www.python.org/downloads/)
4. **Azure Subscription** - Active Azure subscription

### Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Configure your Azure credentials:
```bash
# Login to Azure
az login

# Set your subscription
az account set --subscription <your-subscription-id>
```

3. Create your environment configuration:
```bash
# Copy the template
cp config/.env.template config/.env

# Edit the .env file with your values
nano config/.env
```

## 📝 Configuration

### Environment Variables

Configure the following environment variables in `config/.env`:

- `AZURE_SUBSCRIPTION_ID` - Your Azure subscription ID
- `AZURE_TENANT_ID` - Your Azure AD tenant ID
- `AZURE_RESOURCE_GROUP` - Resource group name
- `AZURE_LOCATION` - Azure region (e.g., eastus)
- `AZURE_STORAGE_ACCOUNT_NAME` - Storage account name
- `AZURE_FUNCTION_APP_NAME` - Function app name

### Configuration File

Alternatively, use `config/config.json` for structured configuration management.

## 🔧 Usage

### 1. Blob Storage Operations

Use the `blob_storage.py` script to interact with Azure Blob Storage:

```python
from scripts.blob_storage import AzureBlobStorageClient

# Initialize client
client = AzureBlobStorageClient()

# Create a container
client.create_container("my-container")

# Upload a file
client.upload_file("my-container", "/path/to/file.txt")

# Download a file
client.download_file("my-container", "file.txt", "/path/to/save/file.txt")

# List blobs
blobs = client.list_blobs("my-container")
```

### 2. Function App Deployment

Use the `function_app_deploy.py` script to deploy and manage Azure Functions:

```python
from scripts.function_app_deploy import AzureFunctionDeployment

# Initialize deployment
deployment = AzureFunctionDeployment(
    resource_group="my-resource-group",
    function_app_name="my-function-app"
)

# Create function app
deployment.create_function_app(
    storage_account="mystorageaccount",
    location="eastus"
)

# Deploy from source
deployment.deploy_function_app("/path/to/function-app")

# Configure app settings
deployment.set_app_settings({
    "CUSTOM_SETTING": "value"
})
```

### 3. Configuration Management

Use the `config_manager.py` script to manage configurations:

```python
from scripts.config_manager import AzureConfigManager

# Initialize config manager
config = AzureConfigManager("config/config.json")

# Get configuration values
resource_group = config.get("azure.resource_group")

# Set configuration values
config.set("azure.storage.account_name", "newaccount")

# Generate app settings
app_settings = config.generate_app_settings()
```

## 🏗️ Infrastructure Deployment

### Using Azure CLI

Deploy infrastructure using Bicep templates:

```bash
# Create resource group
az group create --name ml-training-rg --location eastus

# Deploy infrastructure
az deployment group create \
  --resource-group ml-training-rg \
  --template-file infrastructure/main.bicep \
  --parameters infrastructure/parameters.json
```

### Using Azure DevOps Pipelines

1. **Infrastructure Pipeline** (`pipelines/infrastructure-deployment.yml`):
   - Validates and deploys Azure infrastructure
   - Creates storage account, function app, and related resources

2. **Function App CI/CD Pipeline** (`pipelines/azure-function-ci-cd.yml`):
   - Builds and tests the function app
   - Deploys to Azure Function App

To use these pipelines:
1. Import the YAML files into Azure DevOps
2. Configure the required service connections
3. Set the pipeline variables
4. Run the pipeline

## 📦 Infrastructure Components

### Storage Account
- **Purpose**: Store ML models, training data, and results
- **Containers**:
  - `ml-models` - Machine learning model files
  - `training-data` - Training datasets
  - `results` - Processing results

### Function App
- **Runtime**: Python 3.9
- **Hosting**: Consumption Plan (pay-per-execution)
- **Features**:
  - System-assigned managed identity
  - Application Insights integration
  - HTTPS only

### Application Insights
- Monitor function app performance
- Track exceptions and logs
- Custom metrics and telemetry

## 🔐 Security Best Practices

1. **Managed Identity**: The function app uses system-assigned managed identity for Azure resource access
2. **HTTPS Only**: All resources enforce HTTPS traffic
3. **Minimum TLS Version**: TLS 1.2 is enforced
4. **No Public Access**: Blob containers have no public access
5. **Connection Strings**: Store connection strings in Key Vault (not in code)

## 🧪 Testing

### Local Testing

Test scripts locally before deployment:

```bash
# Test blob storage connection
python scripts/blob_storage.py

# Test configuration management
python scripts/config_manager.py
```

### Function App Local Testing

```bash
# Start function app locally
cd /path/to/function-app
func start
```

## 🐛 Troubleshooting

### Common Issues

1. **Authentication Errors**
   - Ensure you're logged in: `az login`
   - Verify subscription: `az account show`

2. **Storage Account Name Conflicts**
   - Storage account names must be globally unique
   - Use lowercase letters and numbers only (3-24 characters)

3. **Permission Issues**
   - Ensure you have Contributor access to the resource group
   - Check role assignments: `az role assignment list`

4. **Function App Deployment Failures**
   - Check function app logs in Azure Portal
   - Verify app settings are correct
   - Ensure dependencies are in requirements.txt

## 📚 Additional Resources

- [Azure Functions Python Developer Guide](https://docs.microsoft.com/en-us/azure/azure-functions/functions-reference-python)
- [Azure Storage Blob Python SDK](https://docs.microsoft.com/en-us/python/api/overview/azure/storage-blob-readme)
- [Bicep Documentation](https://docs.microsoft.com/en-us/azure/azure-resource-manager/bicep/)
- [Azure DevOps Pipelines](https://docs.microsoft.com/en-us/azure/devops/pipelines/)

## 🤝 Contributing

When adding new deployment scripts or infrastructure:

1. Follow the existing module structure
2. Add appropriate logging
3. Update this README
4. Test locally before committing
5. Update pipeline configurations if needed

## 📄 License

This project is part of the Machine Learning Engineer Training repository.
