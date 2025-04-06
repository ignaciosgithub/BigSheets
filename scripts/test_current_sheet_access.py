"""
Test script to verify that template functions can access set_cell_value and get_cell_value
through the current_sheet parameter.
"""

import asyncio
import os
import sys
from pathlib import Path

project_root = str(Path(__file__).parent.parent)
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "src"))

from bigsheets.function_engine.function_manager import FunctionTemplate

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
    
    template = FunctionTemplate("Test Current Sheet Template", template_code, "Test template with current_sheet parameter")
    
    sheet = MockSheet()
    
    template.set_sheet(sheet)
    
    try:
        template.compile()
        print("Template compiled successfully")
        
        if "def test_function(current_sheet, current_sheet, data)" in template.code:
            print("ERROR: Function signature was incorrectly modified")
            return False
    except Exception as e:
        print(f"Error compiling template: {str(e)}")
        return False
    
    test_data = [1, 2, 3, 4, 5]
    
    try:
        result = await template.execute(test_data, sheet)
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

async def test_persistent_template_with_current_sheet():
    """Test a persistent template that uses current_sheet for cell access."""
    print("\nTesting persistent template with current_sheet parameter...")
    
    template_code = """
def persistent_function(current_sheet, data):
    if data is None:
        current_sheet.set_cell_value(0, 0, "Error: No data provided")
        return
    
    previous_data = None
    
    while True:
        if data != previous_data:
            previous_data = data.copy() if hasattr(data, "copy") else data
            
            try:
                total = sum(data)
                current_sheet.set_cell_value(0, 0, total)
                
                for i, val in enumerate(data):
                    current_sheet.set_cell_value(1, i, val)
            except Exception as e:
                current_sheet.set_cell_value(0, 0, f"Error: {str(e)}")
        
        await asyncio.sleep(0.1)
"""
    
    template = FunctionTemplate("Test Persistent Current Sheet Template", template_code, "Test persistent template with current_sheet parameter", True)
    
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
        gen = template.execute(test_data, sheet)
        result = await anext(gen)
        print(f"First result from persistent template: {result}")
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
    test1_success = await test_template_with_current_sheet()
    test2_success = await test_persistent_template_with_current_sheet()
    
    if test1_success and test2_success:
        print("\nAll tests passed!")
    else:
        print("\nSome tests failed.")

if __name__ == "__main__":
    asyncio.run(main())
