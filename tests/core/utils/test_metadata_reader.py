"""Tests for metadata_reader utility."""

import unittest
from unittest.mock import patch, mock_open
from pathlib import Path

from sec_interp.core.utils.metadata_reader import (
    read_plugin_metadata,
    clear_metadata_cache,
)


class TestMetadataReader(unittest.TestCase):
    """Test suite for metadata reader utility."""

    def setUp(self):
        """Set up test environment."""
        clear_metadata_cache()

    def tearDown(self):
        """Clean up after tests."""
        clear_metadata_cache()

    @patch("sec_interp.core.utils.metadata_reader.Path")
    @patch("sec_interp.core.utils.metadata_reader.ConfigParser")
    def test_read_plugin_metadata_success(self, mock_parser_cls, mock_path_cls):
        """Test successful reading of metadata."""
        # Setup mocks
        mock_path_obj = mock_path_cls.return_value
        # Mock __file__ parent chain
        mock_path_obj.parent.parent.parent.__truediv__.return_value.exists.return_value = (
            True
        )

        # Mock parser
        mock_parser = mock_parser_cls.return_value
        mock_parser.get.side_effect = lambda section, option: {
            "name": "Test Plugin",
            "version": "1.0.0",
            "author": "Test Author",
            "email": "test@example.com",
            "description": "Test Description",
            "homepage": "http://example.com",
        }.get(option)

        # Execute
        metadata = read_plugin_metadata()

        # Assert
        self.assertEqual(metadata["name"], "Test Plugin")
        self.assertEqual(metadata["version"], "1.0.0")
        self.assertEqual(metadata["author"], "Test Author")
        self.assertEqual(metadata["email"], "test@example.com")
        self.assertEqual(metadata["homepage"], "http://example.com")

    @patch("sec_interp.core.utils.metadata_reader.Path")
    def test_read_plugin_metadata_file_not_found(self, mock_path_cls):
        """Test error when metadata.txt is missing."""
        # Setup mocks
        mock_path_obj = mock_path_cls.return_value
        # Mock exists() to return False
        mock_path_obj.parent.parent.parent.__truediv__.return_value.exists.return_value = (
            False
        )

        # Execute & Assert
        with self.assertRaises(FileNotFoundError):
            read_plugin_metadata()

    @patch("sec_interp.core.utils.metadata_reader.Path")
    @patch("sec_interp.core.utils.metadata_reader.ConfigParser")
    def test_read_plugin_metadata_missing_fields(self, mock_parser_cls, mock_path_cls):
        """Test error when required fields are missing."""
        # Setup mocks
        mock_path_obj = mock_path_cls.return_value
        mock_path_obj.parent.parent.parent.__truediv__.return_value.exists.return_value = (
            True
        )

        # Mock parser to fail on 'version'
        mock_parser = mock_parser_cls.return_value

        def side_effect(section, option):
            if option == "version":
                raise Exception("Missing field")
            return "Test Value"

        mock_parser.get.side_effect = side_effect

        # Execute & Assert
        with self.assertRaises(ValueError):
            read_plugin_metadata()

    def test_integration_real_metadata(self):
        """Integration test with the real metadata.txt file."""
        # This test reads the actual file on disk
        # It serves as a sanity check that our location logic is correct
        try:
            metadata = read_plugin_metadata()
            self.assertEqual(metadata["name"], "Sec Interp")
            self.assertIn(".", metadata["version"])  # Version should have dots
            self.assertTrue(len(metadata["author"]) > 0)
        except FileNotFoundError:
            self.fail("Could not find real metadata.txt - path logic might be wrong")
