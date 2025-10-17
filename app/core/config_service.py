import json
import os

CONFIG_FILE = "config.json"

def save_config(config):
    """Saves the configuration dictionary to a JSON file."""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

def load_config():
    """Loads the configuration dictionary from a JSON file."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {}

def get_setting(key, default=None):
    """Gets a specific setting from the config file."""
    config = load_config()
    return config.get(key, default)

def set_setting(key, value):
    """Sets a specific setting in the config file."""
    config = load_config()
    config[key] = value
    save_config(config)