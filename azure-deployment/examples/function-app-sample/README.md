# Sample Azure Function App

This is a sample Azure Function App that demonstrates how to interact with Azure Blob Storage.

## Function: BlobStorageFunction

HTTP-triggered function that uploads data to Azure Blob Storage.

### Usage

**Endpoint**: `POST /api/BlobStorageFunction`

**Request Body**:
```json
{
  "container": "my-container",
  "blob_name": "data.json",
  "data": {
    "key": "value",
    "timestamp": "2024-01-01T00:00:00Z"
  }
}
```

**Response**:
```json
{
  "status": "success",
  "message": "Data uploaded to my-container/data.json",
  "blob_name": "data.json",
  "container": "my-container"
}
```

## Local Testing

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up local.settings.json:
```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "AZURE_STORAGE_CONNECTION_STRING": "your-connection-string"
  }
}
```

3. Run locally:
```bash
func start
```

4. Test with curl:
```bash
curl -X POST http://localhost:7071/api/BlobStorageFunction \
  -H "Content-Type: application/json" \
  -d '{
    "container": "test-container",
    "blob_name": "test.json",
    "data": {"test": "data"}
  }'
```

## Deployment

Deploy using the function_app_deploy.py script from the parent directory:

```bash
python ../scripts/function_app_deploy.py
```

Or use the Azure CLI:

```bash
func azure functionapp publish <function-app-name>
```
