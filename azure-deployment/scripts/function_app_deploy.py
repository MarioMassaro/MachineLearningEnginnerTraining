#!/usr/bin/env python3
"""
Azure Function App Deployment Module

This script provides utilities for deploying and managing Azure Function Apps.
It handles configuration, deployment, and monitoring of function apps.
"""

import os
import json
import logging
import subprocess
from typing import Dict, Optional, List
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AzureFunctionDeployment:
    """Client for deploying and managing Azure Function Apps."""
    
    def __init__(self, 
                 resource_group: str,
                 function_app_name: str,
                 subscription_id: Optional[str] = None):
        """
        Initialize the Azure Function deployment client.
        
        Args:
            resource_group: Azure resource group name
            function_app_name: Name of the function app
            subscription_id: Azure subscription ID
        """
        self.resource_group = resource_group
        self.function_app_name = function_app_name
        self.subscription_id = subscription_id or os.getenv("AZURE_SUBSCRIPTION_ID")
        
        logger.info(f"Initialized deployment for function app: {function_app_name}")
    
    def run_az_command(self, command: List[str]) -> str:
        """
        Run an Azure CLI command.
        
        Args:
            command: Command to run as list of arguments
            
        Returns:
            Command output as string
        """
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            logger.error(f"Command failed: {e.stderr}")
            raise
    
    def create_function_app(self,
                           storage_account: str,
                           location: str = "eastus",
                           runtime: str = "python",
                           runtime_version: str = "3.9",
                           os_type: str = "Linux") -> Dict:
        """
        Create a new Azure Function App.
        
        Args:
            storage_account: Name of the storage account
            location: Azure region
            runtime: Runtime stack (python, node, dotnet, java)
            runtime_version: Runtime version
            os_type: Operating system (Linux or Windows)
            
        Returns:
            Function app details as dictionary
        """
        logger.info(f"Creating function app '{self.function_app_name}'...")
        
        command = [
            "az", "functionapp", "create",
            "--resource-group", self.resource_group,
            "--name", self.function_app_name,
            "--storage-account", storage_account,
            "--consumption-plan-location", location,
            "--runtime", runtime,
            "--runtime-version", runtime_version,
            "--os-type", os_type,
            "--functions-version", "4",
            "--output", "json"
        ]
        
        if self.subscription_id:
            command.extend(["--subscription", self.subscription_id])
        
        output = self.run_az_command(command)
        result = json.loads(output)
        logger.info(f"Function app created successfully: {result['defaultHostName']}")
        return result
    
    def deploy_function_app(self, source_path: str) -> None:
        """
        Deploy function app from local source.
        
        Args:
            source_path: Path to the function app source code
        """
        logger.info(f"Deploying function app from '{source_path}'...")
        
        # Change to source directory
        original_dir = os.getcwd()
        os.chdir(source_path)
        
        try:
            command = [
                "func", "azure", "functionapp", "publish",
                self.function_app_name,
                "--python"
            ]
            
            self.run_az_command(command)
            logger.info("Function app deployed successfully")
        finally:
            os.chdir(original_dir)
    
    def set_app_settings(self, settings: Dict[str, str]) -> None:
        """
        Configure application settings for the function app.
        
        Args:
            settings: Dictionary of setting key-value pairs
        """
        logger.info("Configuring application settings...")
        
        settings_args = []
        for key, value in settings.items():
            settings_args.append(f"{key}={value}")
        
        command = [
            "az", "functionapp", "config", "appsettings", "set",
            "--resource-group", self.resource_group,
            "--name", self.function_app_name,
            "--settings"
        ] + settings_args
        
        if self.subscription_id:
            command.extend(["--subscription", self.subscription_id])
        
        self.run_az_command(command)
        logger.info(f"Configured {len(settings)} application settings")
    
    def get_app_settings(self) -> Dict[str, str]:
        """
        Get current application settings.
        
        Returns:
            Dictionary of current settings
        """
        command = [
            "az", "functionapp", "config", "appsettings", "list",
            "--resource-group", self.resource_group,
            "--name", self.function_app_name,
            "--output", "json"
        ]
        
        if self.subscription_id:
            command.extend(["--subscription", self.subscription_id])
        
        output = self.run_az_command(command)
        settings_list = json.loads(output)
        
        # Convert list to dictionary
        settings = {item['name']: item['value'] for item in settings_list}
        return settings
    
    def enable_managed_identity(self) -> Dict:
        """
        Enable system-assigned managed identity for the function app.
        
        Returns:
            Identity details
        """
        logger.info("Enabling managed identity...")
        
        command = [
            "az", "functionapp", "identity", "assign",
            "--resource-group", self.resource_group,
            "--name", self.function_app_name,
            "--output", "json"
        ]
        
        if self.subscription_id:
            command.extend(["--subscription", self.subscription_id])
        
        output = self.run_az_command(command)
        identity = json.loads(output)
        logger.info(f"Managed identity enabled: {identity['principalId']}")
        return identity
    
    def get_function_app_details(self) -> Dict:
        """
        Get function app details.
        
        Returns:
            Function app details as dictionary
        """
        command = [
            "az", "functionapp", "show",
            "--resource-group", self.resource_group,
            "--name", self.function_app_name,
            "--output", "json"
        ]
        
        if self.subscription_id:
            command.extend(["--subscription", self.subscription_id])
        
        output = self.run_az_command(command)
        return json.loads(output)
    
    def start_function_app(self) -> None:
        """Start the function app."""
        logger.info(f"Starting function app '{self.function_app_name}'...")
        
        command = [
            "az", "functionapp", "start",
            "--resource-group", self.resource_group,
            "--name", self.function_app_name
        ]
        
        if self.subscription_id:
            command.extend(["--subscription", self.subscription_id])
        
        self.run_az_command(command)
        logger.info("Function app started")
    
    def stop_function_app(self) -> None:
        """Stop the function app."""
        logger.info(f"Stopping function app '{self.function_app_name}'...")
        
        command = [
            "az", "functionapp", "stop",
            "--resource-group", self.resource_group,
            "--name", self.function_app_name
        ]
        
        if self.subscription_id:
            command.extend(["--subscription", self.subscription_id])
        
        self.run_az_command(command)
        logger.info("Function app stopped")
    
    def restart_function_app(self) -> None:
        """Restart the function app."""
        logger.info(f"Restarting function app '{self.function_app_name}'...")
        
        command = [
            "az", "functionapp", "restart",
            "--resource-group", self.resource_group,
            "--name", self.function_app_name
        ]
        
        if self.subscription_id:
            command.extend(["--subscription", self.subscription_id])
        
        self.run_az_command(command)
        logger.info("Function app restarted")


def main():
    """Example usage of the Azure Function deployment client."""
    resource_group = os.getenv("AZURE_RESOURCE_GROUP", "my-resource-group")
    function_app_name = os.getenv("AZURE_FUNCTION_APP_NAME", "my-function-app")
    storage_account = os.getenv("AZURE_STORAGE_ACCOUNT_NAME", "mystorageaccount")
    
    # Initialize deployment client
    deployment = AzureFunctionDeployment(
        resource_group=resource_group,
        function_app_name=function_app_name
    )
    
    # Example: Get function app details
    try:
        details = deployment.get_function_app_details()
        print(f"Function App URL: {details['defaultHostName']}")
        print(f"State: {details['state']}")
    except Exception as e:
        logger.error(f"Error getting function app details: {e}")


if __name__ == "__main__":
    main()
