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
        self._result_value = None
        self._sheet = None  # Reference to the sheet for direct cell access
        
    def __repr__(self):
        """Return a string representation of the function result."""
        return str(self._result_value) if self._result_value is not None else ""
        
    def __str__(self):
        """Return a string representation of the function result."""
        return str(self._result_value) if self._result_value is not None else ""
    
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
            function_name = None
            function_sig = None
            for line in self.code.split('\n'):
                if line.strip().startswith('def '):
                    function_name = line.strip().split('def ')[1].split('(')[0]
                    function_sig = line.strip()
                    break
            
            if function_name is None:
                raise ValueError("No function defined in code")
            
            if 'current_sheet' not in function_sig:
                code_lines = self.code.split('\n')
                function_line_index = -1
                
                for i, line in enumerate(code_lines):
                    if line.strip().startswith(f'def {function_name}'):
                        function_line_index = i
                        break
                
                if function_line_index >= 0:
                    sig_parts = code_lines[function_line_index].split('(')
                    params_part = sig_parts[1].split(')')[0].strip()
                    
                    if params_part:
                        new_sig = f"{sig_parts[0]}(current_sheet, {params_part})"
                    else:
                        new_sig = f"{sig_parts[0]}(current_sheet)"
                    
                    if len(sig_parts[1].split(')')) > 1:
                        new_sig += f"){sig_parts[1].split(')')[1]}"
                    else:
                        new_sig += "):"
                    
                    code_lines[function_line_index] = new_sig
                    self.code = '\n'.join(code_lines)
            
            namespace = {
                'get_cell_value': self.get_cell_value,
                'set_cell_value': self.set_cell_value
            }
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
    
    def set_sheet(self, sheet):
        """Set the sheet reference for direct cell access."""
        self._sheet = sheet
        
    def get_cell_value(self, row: int, col: int) -> Any:
        """
        Get the value of a cell at the specified position.
        
        Args:
            row: Row index
            col: Column index
            
        Returns:
            The cell value or None if the cell doesn't exist
        """
        if self._sheet is None:
            return None
        
        try:
            cell = self._sheet.get_cell(row, col)
            return cell.value
        except Exception as e:
            error_msg = f"Error getting cell value: {str(e)}"
            self._result_value = error_msg
            return None
    
    def set_cell_value(self, row: int, col: int, value: Any) -> bool:
        """
        Set the value of a cell at the specified position.
        
        Args:
            row: Row index
            col: Column index
            value: New cell value
            
        Returns:
            True if successful, False otherwise
        """
        if self._sheet is None:
            return False
        
        try:
            self._sheet.set_cell_value(row, col, value)
            return True
        except Exception as e:
            error_msg = f"Error setting cell value: {str(e)}"
            self._result_value = error_msg
            return False
    
    async def execute(self, data=None, sheet=None):
        """Execute the function asynchronously."""
        if sheet is not None:
            self.set_sheet(sheet)
            
        if self._compiled_function is None:
            try:
                self.compile()
            except Exception as e:
                error_msg = f"Error compiling function: {str(e)}"
                self._result_value = error_msg
                if self.is_persistent:
                    yield error_msg
                    return
                return error_msg
            
        if self._compiled_function is None:
            error_msg = "No function defined in template"
            self._result_value = error_msg
            if self.is_persistent:
                yield error_msg
                return
            return error_msg
        
        try:
            if inspect.iscoroutinefunction(self._compiled_function):
                result = await self._compiled_function(self._sheet, data)
            else:
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                
                if self.is_persistent:
                    try:
                        def run_with_current_sheet():
                            return self._compiled_function(self._sheet, data) if self._compiled_function is not None else None
                            
                        gen_result = await loop.run_in_executor(None, run_with_current_sheet)
                        
                        if hasattr(gen_result, '__iter__') and not isinstance(gen_result, (list, dict, str)):
                            for value in gen_result:
                                if hasattr(value, '__iter__') and not isinstance(value, (list, dict, str)):
                                    try:
                                        simple_value = float(value) if isinstance(value, (int, float)) else str(value)
                                        self._result_value = simple_value  # Set result value for __repr__ and __str__
                                        yield simple_value
                                    except (ValueError, TypeError):
                                        self._result_value = str(value)  # Set result value for __repr__ and __str__
                                        yield str(value)
                                else:
                                    self._result_value = value  # Set result value for __repr__ and __str__
                                    yield value
                                await asyncio.sleep(0.1)
                        else:
                            result = gen_result
                            prev_values = data
                            
                            while True:
                                current_values = data
                                
                                if current_values != prev_values:
                                    def run_with_current_sheet():
                                        return self._compiled_function(self._sheet, data) if self._compiled_function is not None else None
                                    
                                    result = await loop.run_in_executor(None, run_with_current_sheet)
                                    prev_values = current_values
                                    
                                    if hasattr(result, '__iter__') and not isinstance(result, (list, dict, str)):
                                        try:
                                            simple_result = next(result)
                                            self._result_value = simple_result  # Set result value for __repr__ and __str__
                                            yield simple_result
                                        except StopIteration:
                                            self._result_value = None  # Set result value for __repr__ and __str__
                                            yield None
                                    else:
                                        self._result_value = result  # Set result value for __repr__ and __str__
                                        yield result
                                
                                await asyncio.sleep(0.1)
                    except Exception as e:
                        error_msg = f"Error in persistent function: {str(e)}"
                        self._result_value = error_msg  # Set result value for error messages
                        yield error_msg
                else:
                    def run_with_current_sheet():
                        return self._compiled_function(self._sheet, data) if self._compiled_function is not None else None
                    
                    result = await loop.run_in_executor(None, run_with_current_sheet)
            
            self._result_value = result  # Set result value for __repr__ and __str__
            return result
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self._result_value = error_msg  # Set result value for error messages
            return error_msg


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
    
    async def execute_function(self, template_id: str, data=None, sheet=None) -> Any:
        """Execute a function template."""
        template = self.get_template(template_id)
        if not template:
            raise ValueError(f"Template with ID {template_id} not found")
        
        return await template.execute(data, sheet)
    
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
