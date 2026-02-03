#!/usr/bin/env python3
"""
Azure Configuration Management Module

This script provides utilities for managing Azure configurations,
including environment variables, secrets, and connection strings.
"""

import os
import json
import logging
from typing import Dict, Optional, Any
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AzureConfigManager:
    """Manager for Azure deployment configurations."""
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize the configuration manager.
        
        Args:
            config_file: Path to configuration file (JSON)
        """
        self.config_file = config_file
        self.config: Dict[str, Any] = {}
        
        if config_file and os.path.exists(config_file):
            self.load_config(config_file)
    
    def load_config(self, config_file: str) -> Dict[str, Any]:
        """
        Load configuration from a JSON file.
        
        Args:
            config_file: Path to configuration file
            
        Returns:
            Configuration dictionary
        """
        logger.info(f"Loading configuration from '{config_file}'")
        with open(config_file, 'r') as f:
            self.config = json.load(f)
        return self.config
    
    def save_config(self, config_file: Optional[str] = None) -> None:
        """
        Save configuration to a JSON file.
        
        Args:
            config_file: Path to configuration file (uses default if not provided)
        """
        file_path = config_file or self.config_file
        if not file_path:
            raise ValueError("No configuration file specified")
        
        logger.info(f"Saving configuration to '{file_path}'")
        
        # Create directory if it doesn't exist
        # Skip if file_path has no directory component (i.e., file in current directory)
        dir_path = os.path.dirname(file_path)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)
        
        with open(file_path, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: Configuration key (supports dot notation, e.g., 'azure.storage.account')
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value.
        
        Args:
            key: Configuration key (supports dot notation)
            value: Configuration value
        """
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def get_azure_connection_string(self, storage_account: str, access_key: str) -> str:
        """
        Build Azure Storage connection string.
        
        Args:
            storage_account: Storage account name
            access_key: Storage account access key
            
        Returns:
            Connection string
        """
        return (
            f"DefaultEndpointsProtocol=https;"
            f"AccountName={storage_account};"
            f"AccountKey={access_key};"
            f"EndpointSuffix=core.windows.net"
        )
    
    def get_env_config(self) -> Dict[str, str]:
        """
        Get configuration from environment variables.
        
        Returns:
            Dictionary of environment-based configuration
        """
        env_config = {
            'subscription_id': os.getenv('AZURE_SUBSCRIPTION_ID'),
            'tenant_id': os.getenv('AZURE_TENANT_ID'),
            'client_id': os.getenv('AZURE_CLIENT_ID'),
            'client_secret': os.getenv('AZURE_CLIENT_SECRET'),
            'resource_group': os.getenv('AZURE_RESOURCE_GROUP'),
            'storage_account': os.getenv('AZURE_STORAGE_ACCOUNT_NAME'),
            'storage_connection_string': os.getenv('AZURE_STORAGE_CONNECTION_STRING'),
            'function_app_name': os.getenv('AZURE_FUNCTION_APP_NAME'),
            'location': os.getenv('AZURE_LOCATION', 'eastus'),
        }
        
        # Filter out None values
        return {k: v for k, v in env_config.items() if v is not None}
    
    def set_env_vars(self, env_vars: Dict[str, str]) -> None:
        """
        Set environment variables.
        
        Args:
            env_vars: Dictionary of environment variables to set
        """
        for key, value in env_vars.items():
            os.environ[key] = value
            logger.info(f"Set environment variable: {key}")
    
    def generate_app_settings(self) -> Dict[str, str]:
        """
        Generate application settings for Azure Function App.
        
        Returns:
            Dictionary of app settings
        """
        app_settings = {}
        
        # Add storage connection string
        storage_conn = self.get('azure.storage.connection_string') or os.getenv('AZURE_STORAGE_CONNECTION_STRING')
        if storage_conn:
            app_settings['AzureWebJobsStorage'] = storage_conn
        
        # Add custom settings from config
        custom_settings = self.get('azure.function_app.settings', {})
        app_settings.update(custom_settings)
        
        return app_settings
    
    def validate_config(self) -> bool:
        """
        Validate that required configuration is present.
        
        Returns:
            True if configuration is valid
        """
        required_keys = [
            'azure.resource_group',
            'azure.storage.account_name',
            'azure.function_app.name'
        ]
        
        missing = []
        for key in required_keys:
            if not self.get(key):
                missing.append(key)
        
        if missing:
            logger.error(f"Missing required configuration: {', '.join(missing)}")
            return False
        
        logger.info("Configuration validation passed")
        return True
    
    def export_to_env_file(self, file_path: str) -> None:
        """
        Export configuration to a .env file.
        
        Args:
            file_path: Path to .env file
        """
        logger.info(f"Exporting configuration to '{file_path}'")
        
        env_vars = []
        
        # Flatten configuration to environment variables
        def flatten(data: Dict, prefix: str = ''):
            for key, value in data.items():
                env_key = f"{prefix}{key}".upper().replace('.', '_')
                if isinstance(value, dict):
                    flatten(value, f"{prefix}{key}_")
                else:
                    env_vars.append(f"{env_key}={value}")
        
        flatten(self.config, 'AZURE_')
        
        with open(file_path, 'w') as f:
            f.write('\n'.join(env_vars))


def main():
    """Example usage of the configuration manager."""
    # Initialize config manager
    config_manager = AzureConfigManager()
    
    # Set configuration values
    config_manager.set('azure.resource_group', 'my-resource-group')
    config_manager.set('azure.storage.account_name', 'mystorageaccount')
    config_manager.set('azure.function_app.name', 'my-function-app')
    config_manager.set('azure.function_app.settings.CUSTOM_SETTING', 'custom_value')
    
    # Get configuration
    resource_group = config_manager.get('azure.resource_group')
    print(f"Resource Group: {resource_group}")
    
    # Generate app settings
    app_settings = config_manager.generate_app_settings()
    print(f"App Settings: {json.dumps(app_settings, indent=2)}")
    
    # Validate configuration
    is_valid = config_manager.validate_config()
    print(f"Configuration valid: {is_valid}")


if __name__ == "__main__":
    main()
