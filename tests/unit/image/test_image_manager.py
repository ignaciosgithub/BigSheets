"""
Unit tests for the Image Manager module.
"""

import unittest
from unittest.mock import MagicMock, patch
import os
import tempfile
from PIL import Image as PILImage
from src.bigsheets.image.image_manager import ImageManager


class TestImageManager(unittest.TestCase):
    """Test cases for the ImageManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.manager = ImageManager()
        
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_image_path = os.path.join(self.temp_dir.name, "test_image.png")
        
        test_image = PILImage.new('RGB', (100, 100), color='red')
        test_image.save(self.test_image_path)
    
    def tearDown(self):
        """Clean up test fixtures."""
        self.temp_dir.cleanup()
    
    def test_load_image(self):
        """Test loading an image."""
        image_data = self.manager.load_image(self.test_image_path)
        
        self.assertIsNotNone(image_data)
        self.assertEqual(image_data["path"], self.test_image_path)
        self.assertEqual(image_data["size"]["width"], 100)
        self.assertEqual(image_data["size"]["height"], 100)
    
    def test_load_image_invalid_path(self):
        """Test loading an image with an invalid path."""
        with self.assertRaises(Exception):
            self.manager.load_image("/path/to/nonexistent/image.png")
    
    def test_resize_image(self):
        """Test resizing an image."""
        image_data = self.manager.load_image(self.test_image_path)
        
        resized_data = self.manager.resize_image(image_data, 50, 50)
        
        self.assertEqual(resized_data["size"]["width"], 50)
        self.assertEqual(resized_data["size"]["height"], 50)
    
    def test_crop_image(self):
        """Test cropping an image."""
        image_data = self.manager.load_image(self.test_image_path)
        
        cropped_data = self.manager.crop_image(image_data, 25, 25, 75, 75)
        
        self.assertEqual(cropped_data["size"]["width"], 50)
        self.assertEqual(cropped_data["size"]["height"], 50)
    
    def test_rotate_image(self):
        """Test rotating an image."""
        image_data = self.manager.load_image(self.test_image_path)
        
        rotated_data = self.manager.rotate_image(image_data, 90)
        
        self.assertEqual(rotated_data["rotation"], 90)
    
    def test_save_image(self):
        """Test saving an image."""
        image_data = self.manager.load_image(self.test_image_path)
        
        new_path = os.path.join(self.temp_dir.name, "saved_image.png")
        self.manager.save_image(image_data, new_path)
        
        self.assertTrue(os.path.exists(new_path))
        
        saved_image = PILImage.open(new_path)
        self.assertEqual(saved_image.width, 100)
        self.assertEqual(saved_image.height, 100)


if __name__ == "__main__":
    unittest.main()
