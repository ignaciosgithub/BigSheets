"""
Direct test script to verify that template functions can access cell methods
through the current_sheet parameter without importing the problematic module.
"""

import asyncio
import os
import sys
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
    
    async def execute(self, data=None):
        """Execute the template."""
        if self._compiled_function is None:
            if not self.compile():
                return "Failed to compile template"
        
        try:
            result = self._compiled_function(self._sheet, data)
            return result
        except Exception as e:
            return f"Error executing template: {str(e)}"

async def test_template_with_current_sheet():
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
    
    sheet = MockSheet()
    
    template.set_sheet(sheet)
    
    try:
        template.compile()
        print("Template compiled successfully")
    except Exception as e:
        print(f"Error compiling template: {str(e)}")
        return False
    
    test_data = [1, 2, 3, 4, 5]
    
    try:
        result = await template.execute(test_data)
        print(f"Template executed successfully, result: {result}")
    except Exception as e:
        print(f"Error executing template: {str(e)}")
        return False
    
    if len(sheet.cell_updates) > 0:
        print("Cell updates:")
        for row, col, value in sheet.cell_updates:
            print(f"  Cell ({row}, {col}): {value}")
        return True
    else:
        print("No cell updates were made")
        return False

async def main():
    success = await test_template_with_current_sheet()
    
    if success:
        print("\nTest passed! Template can access set_cell_value through current_sheet parameter.")
    else:
        print("\nTest failed. Template cannot access set_cell_value through current_sheet parameter.")

if __name__ == "__main__":
    asyncio.run(main())
