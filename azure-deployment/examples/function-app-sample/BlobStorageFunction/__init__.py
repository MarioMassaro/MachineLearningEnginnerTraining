"""
Sample Azure Function that interacts with Blob Storage

This function demonstrates:
- Reading from blob storage
- Writing to blob storage
- Processing data
"""

import logging
import json
import os
import azure.functions as func
from azure.storage.blob import BlobServiceClient


def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Azure Function that uploads data to blob storage.
    
    Expected request body:
    {
        "container": "my-container",
        "blob_name": "data.json",
        "data": {"key": "value"}
    }
    """
    logging.info('Python HTTP trigger function processed a request.')

    try:
        # Parse request body
        req_body = req.get_json()
        container_name = req_body.get('container')
        blob_name = req_body.get('blob_name')
        data = req_body.get('data')

        if not all([container_name, blob_name, data]):
            return func.HttpResponse(
                "Please provide container, blob_name, and data in the request body",
                status_code=400
            )

        # Get connection string from environment
        connection_string = os.environ.get('AZURE_STORAGE_CONNECTION_STRING')
        
        if not connection_string:
            return func.HttpResponse(
                "Storage connection string not configured",
                status_code=500
            )

        # Create blob service client
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        
        # Get blob client
        blob_client = blob_service_client.get_blob_client(
            container=container_name,
            blob=blob_name
        )

        # Upload data
        blob_data = json.dumps(data).encode('utf-8')
        blob_client.upload_blob(blob_data, overwrite=True)

        logging.info(f'Successfully uploaded blob: {blob_name} to container: {container_name}')

        return func.HttpResponse(
            json.dumps({
                "status": "success",
                "message": f"Data uploaded to {container_name}/{blob_name}",
                "blob_name": blob_name,
                "container": container_name
            }),
            mimetype="application/json",
            status_code=200
        )

    except ValueError as e:
        logging.error(f'Invalid request body: {e}')
        return func.HttpResponse(
            "Invalid JSON in request body",
            status_code=400
        )
    except Exception as e:
        logging.error(f'Error processing request: {e}')
        return func.HttpResponse(
            f"Error: {str(e)}",
            status_code=500
        )
