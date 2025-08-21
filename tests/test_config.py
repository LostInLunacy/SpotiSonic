# tests/test_config.py


# Standard library
import unittest
import tempfile
import json
from pathlib import Path

# Actual file to test
from spotisonic.config import *


class TestConfig(unittest.TestCase):
    """Test cases for the config module."""

    def setUp(self):
        """Set up a temporary config file for each test."""
        # Create a temporary directory
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_config_path = Path(self.temp_dir.name) / "test_config.json"
        
        # Store the original path to restore later
        self.original_config_path = CONFIG_PATH
        
        # Point the config module to our temporary file
        set_config_path(self.temp_config_path)

    def tearDown(self):
        """Clean up after each test."""
        self.temp_dir.cleanup()
        # Reset to the original path
        set_config_path(self.original_config_path)

    def test_load_config_creates_file(self):
        """Test that load_config creates a file with defaults if none exists."""
        # Ensure the file doesn't exist initially - CRITICAL: Don't call reset_to_defaults!
        self.assertFalse(self.temp_config_path.exists())
        
        # Loading config should create the file
        config = load_config()
        
        # File should now exist
        self.assertTrue(self.temp_config_path.exists())
        # Should return default config
        self.assertEqual(config, DEFAULT_CONFIG)

    def test_load_config_reads_existing_file(self):
        """Test that load_config reads values from an existing file."""
        # Create a custom config file (manually, not using reset_to_defaults)
        custom_config = {'default_preview_length': 45, 'custom_setting': 'test'}
        with open(self.temp_config_path, 'w') as f:
            json.dump(custom_config, f)
        
        # Load should merge defaults with custom values
        config = load_config()
        
        # Custom values should be preserved
        self.assertEqual(config['default_preview_length'], 45)
        self.assertEqual(config['custom_setting'], 'test')
        # Default values should still be present for other keys
        self.assertEqual(config['min_liked_for_artist'], 1)

    def test_save_config(self):
        """Test that save_config writes to the file correctly."""
        test_config = {'test_key': 'test_value', 'number_setting': 42}
        
        save_config(test_config)
        
        # Verify file was created and contains correct data
        self.assertTrue(self.temp_config_path.exists())
        with open(self.temp_config_path, 'r') as f:
            saved_data = json.load(f)
        self.assertEqual(saved_data, test_config)

    def test_get_config_value(self):
        """Test get_config_value with various scenarios."""
        # Test existing key
        value = get_config_value('min_liked_for_artist')
        self.assertEqual(value, 1)  # Your default is 1
        
        # Test non-existent key with default
        value = get_config_value('non_existent_key', 'default_value')
        self.assertEqual(value, 'default_value')
        
        # Test non-existent key without default
        value = get_config_value('non_existent_key')
        self.assertIsNone(value)

    def test_set_config_value(self):
        """Test set_config_value updates config correctly."""
        # Set a new value
        set_config_value('min_liked_for_artist', 5)
        
        # Verify it was saved
        config = load_config()
        self.assertEqual(config['min_liked_for_artist'], 5)
        
        # Verify the file was updated
        with open(self.temp_config_path, 'r') as f:
            file_data = json.load(f)
        self.assertEqual(file_data['min_liked_for_artist'], 5)

    def test_set_config_value_preserves_other_settings(self):
        """Test that set_config_value doesn't affect other settings."""
        # Set multiple values
        set_config_value('setting_one', 'value_one')
        set_config_value('setting_two', 'value_two')
        
        # Update one setting
        set_config_value('setting_one', 'updated_value')
        
        # Verify both settings are preserved correctly
        config = load_config()
        self.assertEqual(config['setting_one'], 'updated_value')
        self.assertEqual(config['setting_two'], 'value_two')

    def test_reset_to_defaults(self):
        """Test that reset_to_defaults works correctly."""
        # First, manually create a file with custom settings
        custom_config = {'custom_setting': 'should_be_removed', 'min_liked_for_artist': 999}
        with open(self.temp_config_path, 'w') as f:
            json.dump(custom_config, f)
        
        # Now reset to defaults
        reset_to_defaults()
        
        # Verify custom setting is gone and defaults are restored
        config = load_config()
        self.assertNotIn('custom_setting', config)
        self.assertEqual(config['min_liked_for_artist'], 1)
        self.assertEqual(config, DEFAULT_CONFIG)

    def test_corrupt_config_file(self):
        """Test behavior when config file contains invalid JSON."""
        # Write invalid JSON to the config file
        with open(self.temp_config_path, 'w') as f:
            f.write('{invalid json')
        
        # Loading should handle the error and return defaults
        config = load_config()
        self.assertEqual(config, DEFAULT_CONFIG)
        
        # File should have been recreated with valid JSON
        self.assertTrue(self.temp_config_path.exists())
        with open(self.temp_config_path, 'r') as f:
            # Should be able to parse it now
            json.load(f)


if __name__ == '__main__':
    unittest.main()