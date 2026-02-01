#!/usr/bin/env python3
"""
Azure Blob Storage Connection Module

This script provides utilities for connecting to and interacting with Azure Blob Storage.
It handles authentication, container operations, and blob upload/download operations.
"""

import os
import logging
from typing import Optional, List
from azure.storage.blob import BlobServiceClient, ContainerClient, BlobClient
from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
from azure.identity import DefaultAzureCredential

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AzureBlobStorageClient:
    """Client for interacting with Azure Blob Storage."""
    
    def __init__(self, account_name: Optional[str] = None, connection_string: Optional[str] = None):
        """
        Initialize the Azure Blob Storage client.
        
        Args:
            account_name: Azure Storage account name (uses DefaultAzureCredential)
            connection_string: Azure Storage connection string
        """
        self.account_name = account_name or os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
        self.connection_string = connection_string or os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        
        if self.connection_string:
            self.blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
            logger.info("Connected to Azure Blob Storage using connection string")
        elif self.account_name:
            account_url = f"https://{self.account_name}.blob.core.windows.net"
            credential = DefaultAzureCredential()
            self.blob_service_client = BlobServiceClient(account_url=account_url, credential=credential)
            logger.info(f"Connected to Azure Blob Storage account: {self.account_name}")
        else:
            raise ValueError("Either account_name or connection_string must be provided")
    
    def create_container(self, container_name: str) -> ContainerClient:
        """
        Create a new container in the storage account.
        
        Args:
            container_name: Name of the container to create
            
        Returns:
            ContainerClient instance
        """
        try:
            container_client = self.blob_service_client.create_container(container_name)
            logger.info(f"Container '{container_name}' created successfully")
            return container_client
        except ResourceExistsError:
            logger.info(f"Container '{container_name}' already exists")
            return self.blob_service_client.get_container_client(container_name)
    
    def list_containers(self) -> List[str]:
        """
        List all containers in the storage account.
        
        Returns:
            List of container names
        """
        containers = []
        for container in self.blob_service_client.list_containers():
            containers.append(container['name'])
        logger.info(f"Found {len(containers)} containers")
        return containers
    
    def upload_blob(self, container_name: str, blob_name: str, data: bytes, overwrite: bool = True) -> BlobClient:
        """
        Upload data to a blob.
        
        Args:
            container_name: Name of the container
            blob_name: Name of the blob
            data: Data to upload
            overwrite: Whether to overwrite if blob exists
            
        Returns:
            BlobClient instance
        """
        blob_client = self.blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        blob_client.upload_blob(data, overwrite=overwrite)
        logger.info(f"Uploaded blob '{blob_name}' to container '{container_name}'")
        return blob_client
    
    def upload_file(self, container_name: str, file_path: str, blob_name: Optional[str] = None, overwrite: bool = True) -> BlobClient:
        """
        Upload a file to blob storage.
        
        Args:
            container_name: Name of the container
            file_path: Path to the local file
            blob_name: Name for the blob (defaults to filename)
            overwrite: Whether to overwrite if blob exists
            
        Returns:
            BlobClient instance
        """
        if blob_name is None:
            blob_name = os.path.basename(file_path)
        
        with open(file_path, "rb") as file:
            data = file.read()
        
        return self.upload_blob(container_name, blob_name, data, overwrite)
    
    def download_blob(self, container_name: str, blob_name: str) -> bytes:
        """
        Download a blob.
        
        Args:
            container_name: Name of the container
            blob_name: Name of the blob
            
        Returns:
            Blob data as bytes
        """
        blob_client = self.blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        data = blob_client.download_blob().readall()
        logger.info(f"Downloaded blob '{blob_name}' from container '{container_name}'")
        return data
    
    def download_file(self, container_name: str, blob_name: str, file_path: str) -> None:
        """
        Download a blob to a local file.
        
        Args:
            container_name: Name of the container
            blob_name: Name of the blob
            file_path: Path where to save the file
        """
        data = self.download_blob(container_name, blob_name)
        
        # Create directory if it doesn't exist
        # Skip if file_path has no directory component (i.e., file in current directory)
        dir_path = os.path.dirname(file_path)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)
        
        with open(file_path, "wb") as file:
            file.write(data)
        
        logger.info(f"Saved blob to '{file_path}'")
    
    def list_blobs(self, container_name: str, name_starts_with: Optional[str] = None) -> List[str]:
        """
        List all blobs in a container.
        
        Args:
            container_name: Name of the container
            name_starts_with: Filter by blob name prefix
            
        Returns:
            List of blob names
        """
        container_client = self.blob_service_client.get_container_client(container_name)
        blobs = []
        for blob in container_client.list_blobs(name_starts_with=name_starts_with):
            blobs.append(blob.name)
        logger.info(f"Found {len(blobs)} blobs in container '{container_name}'")
        return blobs
    
    def delete_blob(self, container_name: str, blob_name: str) -> None:
        """
        Delete a blob.
        
        Args:
            container_name: Name of the container
            blob_name: Name of the blob to delete
        """
        blob_client = self.blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        blob_client.delete_blob()
        logger.info(f"Deleted blob '{blob_name}' from container '{container_name}'")
    
    def delete_container(self, container_name: str) -> None:
        """
        Delete a container.
        
        Args:
            container_name: Name of the container to delete
        """
        container_client = self.blob_service_client.get_container_client(container_name)
        container_client.delete_container()
        logger.info(f"Deleted container '{container_name}'")


def main():
    """Example usage of the Azure Blob Storage client."""
    # Initialize client
    client = AzureBlobStorageClient()
    
    # Example operations
    container_name = "example-container"
    
    # Create container
    client.create_container(container_name)
    
    # List containers
    containers = client.list_containers()
    print(f"Containers: {containers}")
    
    # Upload a blob
    data = b"Hello, Azure Blob Storage!"
    client.upload_blob(container_name, "example.txt", data)
    
    # List blobs
    blobs = client.list_blobs(container_name)
    print(f"Blobs in {container_name}: {blobs}")
    
    # Download blob
    downloaded_data = client.download_blob(container_name, "example.txt")
    print(f"Downloaded data: {downloaded_data.decode('utf-8')}")


if __name__ == "__main__":
    main()
