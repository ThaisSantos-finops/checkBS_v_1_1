import os
import yaml
from .log import setup_logger, log_info, log_error

# Specific path for the configuration file
CONFIG_FILE_PATH = os.path.join(os.getcwd(), 'configs', 'config.yaml')


def log_config():
    setup_logger()

# Loads settings from the config.yaml file.
def load_config():
    """
    Loads settings from the config.yaml file.
    If the file doesn't exist, raises an error.
    
    Returns:
        dict: Loaded settings
    """
    try:
        log_config()
        if os.path.exists(CONFIG_FILE_PATH):
            with open(CONFIG_FILE_PATH, 'r') as file:
                config = yaml.safe_load(file)
                log_info(f"Settings loaded from {CONFIG_FILE_PATH}")
                # No default value substitution - use exactly what's in the file
                return config
        else:
            log_error(f"Configuration file {CONFIG_FILE_PATH} not found.")
            raise FileNotFoundError(f"Configuration file {CONFIG_FILE_PATH} not found.")
    except Exception as e:
        log_error(f"Error loading settings: {e}")
        raise