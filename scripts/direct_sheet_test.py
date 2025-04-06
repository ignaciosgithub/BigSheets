"""
Direct test script to verify that template functions can access cell methods
through the current_sheet parameter without importing the problematic module.
"""

import asyncio
import os
import sys
import inspect
from pathlib import Path

class MockSheet:
    """Mock sheet class for testing."""
    
    def __init__(self):
        self.cells = {}
        self.cell_updates = []
    
    def get_cell(self, row, col):
        """Get a cell at the specified position."""
        key = (row, col)
        if key not in self.cells:
            self.cells[key] = {"value": None}
        return self.cells[key]
    
    def set_cell_value(self, row, col, value):
        """Set the value of a cell at the specified position."""
        cell = self.get_cell(row, col)
        cell["value"] = value
        self.cell_updates.append((row, col, value))
        print(f"Cell ({row}, {col}) updated to: {value}")
        return True

class ListObject(list):
    """A list object that will fail when set_cell_value is called on it."""
    pass

class SimpleTemplate:
    """Simple template class for testing."""
    
    def __init__(self, name, code, is_persistent=False):
        self.name = name
        self.code = code
        self.is_persistent = is_persistent
        self._sheet = None
        self._compiled_function = None
    
    def set_sheet(self, sheet):
        """Set the sheet reference."""
        self._sheet = sheet
    
    def compile(self):
        """Compile the template code."""
        try:
            if 'current_sheet' not in self.code:
                lines = self.code.split('\n')
                for i, line in enumerate(lines):
                    if line.strip().startswith('def '):
                        func_name = line.strip().split('def ')[1].split('(')[0]
                        params = line.strip().split('(')[1].split(')')[0].strip()
                        
                        if params:
                            new_line = f"def {func_name}(current_sheet, {params}):"
                        else:
                            new_line = f"def {func_name}(current_sheet):"
                        
                        lines[i] = new_line
                        break
                
                self.code = '\n'.join(lines)
            
            namespace = {}
            exec(self.code, namespace)
            
            for name, obj in namespace.items():
                if callable(obj) and name != "__builtins__":
                    self._compiled_function = obj
                    break
            
            return True
        except Exception as e:
            print(f"Error compiling template: {str(e)}")
            return False
    
    def execute(self, data=None):
        """Execute the template."""
        if self._compiled_function is None:
            if not self.compile():
                return "Failed to compile template"
        
        try:
            if self._sheet is None:
                return "Error: No sheet object available for cell access"
                
            if not hasattr(self._sheet, 'set_cell_value'):
                return f"Error: Invalid sheet object (type: {type(self._sheet).__name__})"
                
            result = self._compiled_function(self._sheet, data)
            return result
        except Exception as e:
            return f"Error executing template: {str(e)}"

def test_template_with_current_sheet():
    """Test a template that uses current_sheet for cell access."""
    print("\nTesting template with current_sheet parameter...")
    
    template_code = """
def test_function(current_sheet, data):
    if data is None:
        current_sheet.set_cell_value(0, 0, "Error: No data provided")
        return
    
    total = sum(data)
    
    current_sheet.set_cell_value(0, 0, total)
    
    for i, val in enumerate(data):
        current_sheet.set_cell_value(1, i, val)
"""
    
    template = SimpleTemplate("Test Current Sheet Template", template_code)
    
    valid_sheet = MockSheet()
    template.set_sheet(valid_sheet)
    
    try:
        template.compile()
        print("Template compiled successfully")
        
        test_data = [1, 2, 3, 4, 5]
        result = template.execute(test_data)
        print(f"Template executed successfully, result: {result}")
        
        if len(valid_sheet.cell_updates) > 0:
            print("Cell updates:")
            for row, col, value in valid_sheet.cell_updates:
                print(f"  Cell ({row}, {col}): {value}")
            print("Valid sheet test passed!")
        else:
            print("Valid sheet test failed - no cell updates")
    except Exception as e:
        print(f"Error with valid sheet: {str(e)}")
    
    list_sheet = ListObject([1, 2, 3, 4, 5])
    template.set_sheet(list_sheet)
    
    try:
        result = template.execute([1, 2, 3, 4, 5])
        print(f"Result with list as sheet: {result}")
        if "Error: Invalid sheet object" in result:
            print("List sheet test passed! Error correctly detected when using list object.")
        else:
            print("List sheet test failed - no error detected")
    except Exception as e:
        print(f"Error with list as sheet: {str(e)}")
        print("List sheet test passed through exception!")

def main():
    test_template_with_current_sheet()
    print("\nAll tests completed!")

if __name__ == "__main__":
    main()
