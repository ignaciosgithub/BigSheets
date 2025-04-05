"""
Image Manager Module

This module provides functionality for handling and managing images.
"""

from typing import Dict, List, Any, Optional, Union, Tuple
from PIL import Image
import io
import base64
import os


class ImageManager:
    """
    Provides functionality for handling and managing images.
    """
    
    def __init__(self):
        """Initialize the image manager."""
        self.supported_formats = ["jpg", "jpeg", "png", "gif", "bmp"]
    
    def load_image(self, file_path: str) -> Dict[str, Any]:
        """
        Load an image from a file.
        
        Args:
            file_path: Path to the image file
            
        Returns:
            Dictionary containing image data and metadata
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Image file not found: {file_path}")
        
        file_ext = os.path.splitext(file_path)[1].lower().lstrip(".")
        if file_ext not in self.supported_formats:
            raise ValueError(f"Unsupported image format: {file_ext}")
        
        with Image.open(file_path) as img:
            width, height = img.size
            format_name = img.format
            
            buffer = io.BytesIO()
            img.save(buffer, format=format_name)
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.read()).decode("utf-8")
        
        return {
            "width": width,
            "height": height,
            "format": format_name,
            "data": f"data:image/{file_ext};base64,{image_base64}",
            "original_path": file_path
        }
    
    def resize_image(
        self,
        image_data: Dict[str, Any],
        width: Optional[int] = None,
        height: Optional[int] = None,
        maintain_aspect_ratio: bool = True
    ) -> Dict[str, Any]:
        """
        Resize an image.
        
        Args:
            image_data: Image data dictionary
            width: New width
            height: New height
            maintain_aspect_ratio: Whether to maintain the aspect ratio
            
        Returns:
            Dictionary containing resized image data and metadata
        """
        data_url = image_data["data"]
        header, encoded = data_url.split(",", 1)
        binary_data = base64.b64decode(encoded)
        
        with Image.open(io.BytesIO(binary_data)) as img:
            original_width, original_height = img.size
            
            if width is None and height is None:
                return image_data
            
            if maintain_aspect_ratio:
                if width is None:
                    aspect_ratio = original_width / original_height
                    width = int(height * aspect_ratio)
                elif height is None:
                    aspect_ratio = original_height / original_width
                    height = int(width * aspect_ratio)
                else:
                    width_ratio = width / original_width
                    height_ratio = height / original_height
                    
                    if width_ratio < height_ratio:
                        height = int(original_height * width_ratio)
                    else:
                        width = int(original_width * height_ratio)
            
            resized_img = img.resize((width, height), Image.LANCZOS)
            
            buffer = io.BytesIO()
            format_name = img.format or "PNG"
            resized_img.save(buffer, format=format_name)
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.read()).decode("utf-8")
        
        result = image_data.copy()
        result["width"] = width
        result["height"] = height
        result["data"] = f"{header},{image_base64}"
        
        return result
    
    def crop_image(
        self,
        image_data: Dict[str, Any],
        left: int,
        top: int,
        right: int,
        bottom: int
    ) -> Dict[str, Any]:
        """
        Crop an image.
        
        Args:
            image_data: Image data dictionary
            left: Left coordinate
            top: Top coordinate
            right: Right coordinate
            bottom: Bottom coordinate
            
        Returns:
            Dictionary containing cropped image data and metadata
        """
        data_url = image_data["data"]
        header, encoded = data_url.split(",", 1)
        binary_data = base64.b64decode(encoded)
        
        with Image.open(io.BytesIO(binary_data)) as img:
            cropped_img = img.crop((left, top, right, bottom))
            
            width, height = cropped_img.size
            
            buffer = io.BytesIO()
            format_name = img.format or "PNG"
            cropped_img.save(buffer, format=format_name)
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.read()).decode("utf-8")
        
        result = image_data.copy()
        result["width"] = width
        result["height"] = height
        result["data"] = f"{header},{image_base64}"
        
        return result
    
    def rotate_image(
        self,
        image_data: Dict[str, Any],
        angle: float
    ) -> Dict[str, Any]:
        """
        Rotate an image.
        
        Args:
            image_data: Image data dictionary
            angle: Rotation angle in degrees
            
        Returns:
            Dictionary containing rotated image data and metadata
        """
        data_url = image_data["data"]
        header, encoded = data_url.split(",", 1)
        binary_data = base64.b64decode(encoded)
        
        with Image.open(io.BytesIO(binary_data)) as img:
            rotated_img = img.rotate(angle, expand=True)
            
            width, height = rotated_img.size
            
            buffer = io.BytesIO()
            format_name = img.format or "PNG"
            rotated_img.save(buffer, format=format_name)
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.read()).decode("utf-8")
        
        result = image_data.copy()
        result["width"] = width
        result["height"] = height
        result["data"] = f"{header},{image_base64}"
        
        return result
