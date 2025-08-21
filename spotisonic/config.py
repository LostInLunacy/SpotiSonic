# spotisonic/config.py
import json
import os
from pathlib import Path

# Path.home() is user's home dir (e.g.  C:\Users\Alice)
# Other apps save config files like this such as Joplin:
CONFIG_PATH = Path.home() / ".config" / "spotisonic" / "config.json"

DEFAULT_CONFIG = {
    "default_preview_length": 30,
    "default_shuffle": True,
    "default_scrobble": True,
    "min_liked_for_artist": 1,
    "min_bookmarked_for_artist": 1,
    "max_plays_for_new_artist": 0
}

def set_config_path(path):
    """Set the config file path (for testing)."""
    global CONFIG_PATH
    CONFIG_PATH = Path(path)

def load_config():
    """Loads the config from file, creating it with defaults if it doesn't exist."""
    try:
        with open(CONFIG_PATH, 'r') as f:
            loaded_config = json.load(f)
            # Ensure all default keys are present
            return {**DEFAULT_CONFIG, **loaded_config}
    except FileNotFoundError:
        # Ensure parent folder exists. Create it it doesn't; don't throw error if it does.
        os.makedirs(CONFIG_PATH.parent, exist_ok=True)
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()
    except json.JSONDecodeError:
        # Handle corrupt config file
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()

def save_config(config_dict):
    """Saves the config dictionary to file."""
    os.makedirs(CONFIG_PATH.parent, exist_ok=True)
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config_dict, f, indent=4)

def get_config_value(key, default=None):
    """Gets a single config value. Safe if key doesn't exist."""
    config = load_config()
    return config.get(key, default)

def set_config_value(key, value):
    """Sets a single config value and saves the file."""
    config = load_config()
    config[key] = value
    save_config(config)

def reset_to_defaults():
    """Reset config to default values."""
    save_config(DEFAULT_CONFIG)
    return DEFAULT_CONFIG.copy()