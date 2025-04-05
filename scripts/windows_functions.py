"""
Script to create common spreadsheet template functions for BigSheets on Windows.
"""

import os
import sys
from pathlib import Path

repo_root = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(repo_root))

def create_template_functions():
    """Create template functions and save them to the Windows AppData directory."""
    from src.bigsheets.function_engine.function_manager import FunctionManager
    
    windows_path = r"C:\Users\Pichau\AppData\Roaming\BigSheets\functions"
    print(f"Using Windows path: {windows_path}")
    
    function_manager = FunctionManager(storage_dir=windows_path)
    print(f"Created FunctionManager with storage directory: {function_manager.storage_dir}")
    
    templates = [
        {
            "name": "SUM", 
            "code": "def sum_function(data):\n    import pandas as pd\n    if isinstance(data, pd.DataFrame):\n        return data.sum().sum()\n    else:\n        return data.sum()",
            "description": "Calculates the sum of a range of values"
        },
        {
            "name": "AVERAGE", 
            "code": "def average_function(data):\n    import pandas as pd\n    if isinstance(data, pd.DataFrame):\n        return data.mean().mean()\n    else:\n        return data.mean()",
            "description": "Calculates the average of a range of values"
        },
        {
            "name": "COUNT", 
            "code": "def count_function(data):\n    import pandas as pd\n    if isinstance(data, pd.DataFrame):\n        return data.count().sum()\n    else:\n        return data.count()",
            "description": "Counts the number of cells that contain numbers"
        },
        {
            "name": "MAX", 
            "code": "def max_function(data):\n    import pandas as pd\n    if isinstance(data, pd.DataFrame):\n        return data.max().max()\n    else:\n        return data.max()",
            "description": "Returns the maximum value in a range of values"
        },
        {
            "name": "MIN", 
            "code": "def min_function(data):\n    import pandas as pd\n    if isinstance(data, pd.DataFrame):\n        return data.min().min()\n    else:\n        return data.min()",
            "description": "Returns the minimum value in a range of values"
        }
    ]
    
    created_templates = []
    
    for template_info in templates:
        try:
            template = function_manager.create_template(
                name=template_info["name"],
                code=template_info["code"],
                description=template_info["description"]
            )
            print(f"Created template: {template.name}")
            created_templates.append((template.name, template.id))
            
            persistent_name = f"Persistent {template_info['name']}"
            persistent_description = f"{template_info['description']}. Updates automatically when source values change."
            
            persistent_template = function_manager.create_template(
                name=persistent_name,
                code=template_info["code"],
                description=persistent_description,
                is_persistent=True
            )
            print(f"Created persistent template: {persistent_template.name}")
            created_templates.append((persistent_template.name, persistent_template.id))
        except Exception as e:
            print(f"Error creating template {template_info['name']}: {str(e)}")
    
    function_manager.save_templates()
    print(f"Saved templates to: {function_manager.storage_dir}")
    
    print(f"Total templates created: {len(created_templates)}")
    for name, template_id in created_templates:
        print(f"  - {name} (ID: {template_id})")

if __name__ == "__main__":
    create_template_functions()
