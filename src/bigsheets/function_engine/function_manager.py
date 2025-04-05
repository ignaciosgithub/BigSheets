"""
Function Manager Module

This module provides functionality for managing and executing custom Python functions.
"""

import asyncio
import inspect
import json
import os
import time
import uuid
from typing import Dict, List, Any, Optional, Callable, Union, Awaitable


class FunctionTemplate:
    """
    Represents a user-defined function template.
    """
    
    def __init__(self, name: str, code: str, description: str = "", is_persistent: bool = False):
        self.id = str(uuid.uuid4())
        self.name = name
        self.code = code
        self.description = description
        self.created_at = time.time()
        self.updated_at = time.time()
        self.is_persistent = is_persistent
        self._compiled_function = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert template to dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "code": self.code,
            "description": self.description,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "is_persistent": self.is_persistent
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FunctionTemplate':
        """Create template from dictionary."""
        is_persistent = data.get("is_persistent", False)
        template = cls(data["name"], data["code"], data["description"], is_persistent)
        template.id = data["id"]
        template.created_at = data["created_at"]
        template.updated_at = data["updated_at"]
        return template
    
    def compile(self):
        """Compile the function code."""
        try:
            namespace = {}
            exec(self.code, namespace)
            
            function_name = None
            for name, obj in namespace.items():
                if callable(obj) and name != "__builtins__":
                    function_name = name
                    break
            
            if function_name is None:
                raise ValueError("No function defined in code")
            
            self._compiled_function = namespace[function_name]
            return True
        except Exception as e:
            raise ValueError(f"Failed to compile function: {str(e)}")
    
    async def execute(self, *args, **kwargs) -> Any:
        """Execute the function asynchronously."""
        if self._compiled_function is None:
            self.compile()
            
        if self._compiled_function is None:
            return None
        
        try:
            if inspect.iscoroutinefunction(self._compiled_function):
                result = await self._compiled_function(*args, **kwargs)
            else:
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                
                if self.is_persistent:
                    result = None
                    prev_values = None
                    
                    while True:
                        current_values = args[0] if args else None
                        
                        if current_values != prev_values:
                            result = await loop.run_in_executor(
                                None, lambda: self._compiled_function(*args, **kwargs) if self._compiled_function is not None else None
                            )
                            prev_values = current_values
                            yield result
                            
                        await asyncio.sleep(0.1)
                else:
                    result = await loop.run_in_executor(
                        None, lambda: self._compiled_function(*args, **kwargs) if self._compiled_function is not None else None
                    )
            
            return result
        except Exception as e:
            return f"Error: {str(e)}"


class FunctionManager:
    """
    Manages user-defined function templates.
    """
    
    def __init__(self, storage_dir: Optional[str] = None):
        self.templates: Dict[str, FunctionTemplate] = {}
        
        if storage_dir:
            self.storage_dir = storage_dir
        else:
            if os.name == 'nt':  # Windows
                app_data = os.environ.get('APPDATA', os.path.expanduser('~'))
                self.storage_dir = os.path.join(app_data, 'BigSheets', 'functions')
            else:  # Unix-like
                self.storage_dir = os.path.expanduser("~/.bigsheets/functions")
        
        if self.storage_dir and not os.path.exists(self.storage_dir):
            os.makedirs(self.storage_dir, exist_ok=True)
            print(f"Created function templates directory: {self.storage_dir}")
        
        if self.storage_dir and os.path.exists(self.storage_dir):
            self.load_templates()
    
    def create_template(self, name: str, code: str, description: str = "", is_persistent: bool = False) -> FunctionTemplate:
        """Create a new function template."""
        template = FunctionTemplate(name, code, description, is_persistent)
        
        template.compile()
        
        self.templates[template.id] = template
        return template
    
    def update_template(self, template_id: str, name: Optional[str] = None, 
                       code: Optional[str] = None, description: Optional[str] = None) -> FunctionTemplate:
        """Update an existing template."""
        if template_id not in self.templates:
            raise ValueError(f"Template with ID {template_id} not found")
        
        template = self.templates[template_id]
        
        if name is not None:
            template.name = name
        if code is not None:
            template.code = code
            template._compiled_function = None  # Reset compiled function
        if description is not None:
            template.description = description
        
        template.updated_at = time.time()
        
        if code is not None:
            template.compile()
        
        return template
    
    def delete_template(self, template_id: str) -> bool:
        """Delete a template."""
        if template_id in self.templates:
            del self.templates[template_id]
            return True
        return False
    
    def get_template(self, template_id: str) -> Optional[FunctionTemplate]:
        """Get a template by ID."""
        return self.templates.get(template_id)
    
    def list_templates(self) -> List[Dict[str, Any]]:
        """List all templates."""
        return [template.to_dict() for template in self.templates.values()]
    
    async def execute_function(self, template_id: str, *args, **kwargs) -> Any:
        """Execute a function template."""
        template = self.get_template(template_id)
        if not template:
            raise ValueError(f"Template with ID {template_id} not found")
        
        return await template.execute(*args, **kwargs)
    
    def save_templates(self):
        """Save all templates to disk."""
        if not self.storage_dir:
            return
        
        for template_id, template in self.templates.items():
            file_path = os.path.join(self.storage_dir, f"{template_id}.json")
            with open(file_path, "w") as f:
                json.dump(template.to_dict(), f, indent=2)
    
    def load_templates(self):
        """Load all templates from disk."""
        if not self.storage_dir or not os.path.exists(self.storage_dir):
            return
        
        for filename in os.listdir(self.storage_dir):
            if filename.endswith(".json"):
                file_path = os.path.join(self.storage_dir, filename)
                try:
                    with open(file_path, "r") as f:
                        data = json.load(f)
                        template = FunctionTemplate.from_dict(data)
                        self.templates[template.id] = template
                except Exception as e:
                    print(f"Error loading template {filename}: {str(e)}")
