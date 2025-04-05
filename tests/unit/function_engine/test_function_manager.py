"""
Unit tests for the function engine module.
"""

import unittest
import os
import tempfile
import asyncio
from unittest.mock import MagicMock, patch

from src.bigsheets.function_engine.function_manager import FunctionManager, FunctionTemplate


class TestFunctionTemplate(unittest.TestCase):
    """Test cases for the FunctionTemplate class."""
    
    def test_init(self):
        """Test initialization of a function template."""
        template = FunctionTemplate("Test Function", "def test_func(x):\n    return x * 2")
        
        self.assertIsNotNone(template.id)
        self.assertEqual(template.name, "Test Function")
        self.assertEqual(template.code, "def test_func(x):\n    return x * 2")
        self.assertEqual(template.description, "")
        self.assertIsNotNone(template.created_at)
        self.assertIsNotNone(template.updated_at)
        self.assertIsNone(template._compiled_function)
    
    def test_to_dict(self):
        """Test conversion of a template to a dictionary."""
        template = FunctionTemplate("Test Function", "def test_func(x):\n    return x * 2", "Test description")
        
        data = template.to_dict()
        
        self.assertEqual(data["id"], template.id)
        self.assertEqual(data["name"], "Test Function")
        self.assertEqual(data["code"], "def test_func(x):\n    return x * 2")
        self.assertEqual(data["description"], "Test description")
        self.assertEqual(data["created_at"], template.created_at)
        self.assertEqual(data["updated_at"], template.updated_at)
    
    def test_from_dict(self):
        """Test creation of a template from a dictionary."""
        data = {
            "id": "test-id",
            "name": "Test Function",
            "code": "def test_func(x):\n    return x * 2",
            "description": "Test description",
            "created_at": 1234567890,
            "updated_at": 1234567890
        }
        
        template = FunctionTemplate.from_dict(data)
        
        self.assertEqual(template.id, "test-id")
        self.assertEqual(template.name, "Test Function")
        self.assertEqual(template.code, "def test_func(x):\n    return x * 2")
        self.assertEqual(template.description, "Test description")
        self.assertEqual(template.created_at, 1234567890)
        self.assertEqual(template.updated_at, 1234567890)
    
    def test_compile_valid_function(self):
        """Test compilation of a valid function."""
        template = FunctionTemplate("Test Function", "def test_func(x):\n    return x * 2")
        
        result = template.compile()
        
        self.assertTrue(result)
        self.assertIsNotNone(template._compiled_function)
    
    def test_compile_invalid_function(self):
        """Test compilation of an invalid function."""
        template = FunctionTemplate("Test Function", "def test_func(x):\n    return x *")
        
        with self.assertRaises(ValueError):
            template.compile()
    
    def test_compile_no_function(self):
        """Test compilation of code with no function."""
        template = FunctionTemplate("Test Function", "x = 5\ny = 10")
        
        with self.assertRaises(ValueError):
            template.compile()
    
    def test_execute_sync_function(self):
        """Test execution of a synchronous function."""
        template = FunctionTemplate("Test Function", "def test_func(x):\n    return x * 2")
        
        result = asyncio.run(template.execute(5))
        
        self.assertEqual(result, 10)
    
    def test_execute_async_function(self):
        """Test execution of an asynchronous function."""
        template = FunctionTemplate(
            "Test Async Function", 
            "async def test_func(x):\n    await asyncio.sleep(0.1)\n    return x * 2"
        )
        
        result = asyncio.run(template.execute(5))
        
        self.assertEqual(result, 10)
    
    def test_execute_function_error(self):
        """Test error handling during function execution."""
        template = FunctionTemplate("Test Function", "def test_func(x):\n    raise ValueError('Test error')")
        
        with self.assertRaises(RuntimeError):
            asyncio.run(template.execute(5))


class TestFunctionManager(unittest.TestCase):
    """Test cases for the FunctionManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.function_manager = FunctionManager(storage_dir=self.temp_dir)
    
    def tearDown(self):
        """Tear down test fixtures."""
        for filename in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, filename))
        os.rmdir(self.temp_dir)
    
    def test_create_template(self):
        """Test creation of a function template."""
        template = self.function_manager.create_template(
            "Test Function", 
            "def test_func(x):\n    return x * 2",
            "Test description"
        )
        
        self.assertIsNotNone(template.id)
        self.assertEqual(template.name, "Test Function")
        self.assertEqual(template.code, "def test_func(x):\n    return x * 2")
        self.assertEqual(template.description, "Test description")
        self.assertIn(template.id, self.function_manager.templates)
    
    def test_create_template_invalid_code(self):
        """Test creation of a template with invalid code."""
        with self.assertRaises(ValueError):
            self.function_manager.create_template(
                "Test Function", 
                "def test_func(x):\n    return x *"
            )
    
    def test_update_template(self):
        """Test updating a function template."""
        template = self.function_manager.create_template(
            "Test Function", 
            "def test_func(x):\n    return x * 2"
        )
        
        updated_template = self.function_manager.update_template(
            template.id,
            name="Updated Function",
            code="def test_func(x):\n    return x * 3",
            description="Updated description"
        )
        
        self.assertEqual(updated_template.id, template.id)
        self.assertEqual(updated_template.name, "Updated Function")
        self.assertEqual(updated_template.code, "def test_func(x):\n    return x * 3")
        self.assertEqual(updated_template.description, "Updated description")
        self.assertGreater(updated_template.updated_at, template.created_at)
    
    def test_update_template_invalid_id(self):
        """Test updating a template with an invalid ID."""
        with self.assertRaises(ValueError):
            self.function_manager.update_template(
                "invalid-id",
                name="Updated Function"
            )
    
    def test_update_template_invalid_code(self):
        """Test updating a template with invalid code."""
        template = self.function_manager.create_template(
            "Test Function", 
            "def test_func(x):\n    return x * 2"
        )
        
        with self.assertRaises(ValueError):
            self.function_manager.update_template(
                template.id,
                code="def test_func(x):\n    return x *"
            )
    
    def test_delete_template(self):
        """Test deletion of a function template."""
        template = self.function_manager.create_template(
            "Test Function", 
            "def test_func(x):\n    return x * 2"
        )
        
        result = self.function_manager.delete_template(template.id)
        
        self.assertTrue(result)
        self.assertNotIn(template.id, self.function_manager.templates)
    
    def test_delete_template_invalid_id(self):
        """Test deletion of a template with an invalid ID."""
        result = self.function_manager.delete_template("invalid-id")
        
        self.assertFalse(result)
    
    def test_get_template(self):
        """Test getting a function template by ID."""
        template = self.function_manager.create_template(
            "Test Function", 
            "def test_func(x):\n    return x * 2"
        )
        
        retrieved_template = self.function_manager.get_template(template.id)
        
        self.assertEqual(retrieved_template.id, template.id)
        self.assertEqual(retrieved_template.name, template.name)
        self.assertEqual(retrieved_template.code, template.code)
    
    def test_get_template_invalid_id(self):
        """Test getting a template with an invalid ID."""
        retrieved_template = self.function_manager.get_template("invalid-id")
        
        self.assertIsNone(retrieved_template)
    
    def test_list_templates(self):
        """Test listing all function templates."""
        template1 = self.function_manager.create_template(
            "Test Function 1", 
            "def test_func1(x):\n    return x * 2"
        )
        
        template2 = self.function_manager.create_template(
            "Test Function 2", 
            "def test_func2(x):\n    return x * 3"
        )
        
        templates = self.function_manager.list_templates()
        
        self.assertEqual(len(templates), 2)
        self.assertIn(template1.id, [t["id"] for t in templates])
        self.assertIn(template2.id, [t["id"] for t in templates])
    
    def test_execute_function(self):
        """Test execution of a function template."""
        template = self.function_manager.create_template(
            "Test Function", 
            "def test_func(x):\n    return x * 2"
        )
        
        result = asyncio.run(self.function_manager.execute_function(template.id, 5))
        
        self.assertEqual(result, 10)
    
    def test_execute_function_invalid_id(self):
        """Test execution of a function with an invalid ID."""
        with self.assertRaises(ValueError):
            asyncio.run(self.function_manager.execute_function("invalid-id", 5))
    
    def test_save_and_load_templates(self):
        """Test saving and loading function templates."""
        template1 = self.function_manager.create_template(
            "Test Function 1", 
            "def test_func1(x):\n    return x * 2"
        )
        
        template2 = self.function_manager.create_template(
            "Test Function 2", 
            "def test_func2(x):\n    return x * 3"
        )
        
        self.function_manager.save_templates()
        
        new_manager = FunctionManager(storage_dir=self.temp_dir)
        
        self.assertEqual(len(new_manager.templates), 2)
        self.assertIn(template1.id, new_manager.templates)
        self.assertIn(template2.id, new_manager.templates)
        self.assertEqual(new_manager.templates[template1.id].name, "Test Function 1")
        self.assertEqual(new_manager.templates[template2.id].name, "Test Function 2")


if __name__ == "__main__":
    unittest.main()
