"""
Script to create common spreadsheet template functions for BigSheets on Windows.
"""

import os
import sys
from pathlib import Path

repo_root = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(repo_root))

from src.bigsheets.function_engine.function_manager import FunctionManager

def create_template_functions():
    """Create template functions and save them to the Windows AppData directory."""
    windows_path = r"C:\Users\Pichau\AppData\Roaming\BigSheets\functions"
    
    function_manager = FunctionManager(storage_dir=windows_path)
    
    templates = [
        {
            "name": "SUM",
            "code": """def sum_function(data):
    import pandas as pd
    import numpy as np
    
    if isinstance(data, pd.DataFrame):
        numeric_data = data.apply(pd.to_numeric, errors='coerce')
        return numeric_data.sum().sum()
    else:
        numeric_data = pd.to_numeric(data, errors='coerce')
        return numeric_data.sum()""",
            "description": "Calculates the sum of a range of values"
        },
        {
            "name": "AVERAGE",
            "code": """def average_function(data):
    import pandas as pd
    import numpy as np
    
    if isinstance(data, pd.DataFrame):
        numeric_data = data.apply(pd.to_numeric, errors='coerce')
        return numeric_data.stack().mean()
    else:
        numeric_data = pd.to_numeric(data, errors='coerce')
        return numeric_data.mean()""",
            "description": "Calculates the average of a range of values"
        },
        {
            "name": "COUNT",
            "code": """def count_function(data):
    import pandas as pd
    import numpy as np
    
    if isinstance(data, pd.DataFrame):
        numeric_data = data.apply(pd.to_numeric, errors='coerce')
        return numeric_data.count().sum()
    else:
        numeric_data = pd.to_numeric(data, errors='coerce')
        return numeric_data.count()""",
            "description": "Counts the number of cells that contain numbers"
        },
        {
            "name": "MAX",
            "code": """def max_function(data):
    import pandas as pd
    import numpy as np
    
    if isinstance(data, pd.DataFrame):
        numeric_data = data.apply(pd.to_numeric, errors='coerce')
        return numeric_data.max().max()
    else:
        numeric_data = pd.to_numeric(data, errors='coerce')
        return numeric_data.max()""",
            "description": "Returns the maximum value in a range of values"
        },
        {
            "name": "MIN",
            "code": """def min_function(data):
    import pandas as pd
    import numpy as np
    
    if isinstance(data, pd.DataFrame):
        numeric_data = data.apply(pd.to_numeric, errors='coerce')
        return numeric_data.min().min()
    else:
        numeric_data = pd.to_numeric(data, errors='coerce')
        return numeric_data.min()""",
            "description": "Returns the minimum value in a range of values"
        },
        {
            "name": "COUNTIF",
            "code": """def countif_function(data, condition="x > 0"):
    import pandas as pd
    import numpy as np
    
    if isinstance(data, pd.DataFrame):
        numeric_data = data.apply(pd.to_numeric, errors='coerce')
        condition_func = lambda x: eval(condition)
        return numeric_data.applymap(condition_func).sum().sum()
    else:
        numeric_data = pd.to_numeric(data, errors='coerce')
        condition_func = lambda x: eval(condition)
        return numeric_data.apply(condition_func).sum()""",
            "description": "Counts the number of cells that meet a specific condition"
        },
        {
            "name": "CONCATENATE",
            "code": """def concatenate_function(data, separator=""):
    import pandas as pd
    
    if isinstance(data, pd.DataFrame):
        result = ""
        for _, row in data.iterrows():
            for val in row:
                if pd.notna(val):
                    result += str(val) + separator
        if result and separator:
            result = result[:-len(separator)]
        return result
    else:
        result = ""
        for val in data:
            if pd.notna(val):
                result += str(val) + separator
        if result and separator:
            result = result[:-len(separator)]
        return result""",
            "description": "Joins text from multiple cells into one cell"
        },
        {
            "name": "VLOOKUP",
            "code": """def vlookup_function(lookup_value, data, col_index=1, exact_match=True):
    import pandas as pd
    import numpy as np
    
    if not isinstance(data, pd.DataFrame):
        return "Error: Data must be a DataFrame"
    
    col_index = col_index - 1
    
    if col_index < 0 or col_index >= data.shape[1]:
        return f"Error: Column index {col_index + 1} is out of range"
    
    lookup_column = data.iloc[:, 0]
    
    if exact_match:
        matches = lookup_column == lookup_value
        if matches.any():
            return data.iloc[matches.idxmax(), col_index]
        else:
            return f"Error: No exact match found for {lookup_value}"
    else:
        try:
            numeric_lookup = pd.to_numeric(lookup_column, errors='coerce')
            numeric_lookup_value = float(lookup_value)
            
            matches = numeric_lookup <= numeric_lookup_value
            
            if matches.any():
                sorted_indices = numeric_lookup[matches].sort_values(ascending=False).index
                return data.iloc[sorted_indices[0], col_index]
            else:
                return f"Error: No match found for {lookup_value}"
        except:
            return "Error: Non-exact match requires numeric values\"""",
            "description": "Looks up a value in the first column of a range and returns a value in the same row from a specified column"
        },
        {
            "name": "IF",
            "code": """def if_function(data, condition="x > 0", true_value=1, false_value=0):
    import pandas as pd
    import numpy as np
    
    if isinstance(data, pd.DataFrame):
        numeric_data = data.apply(pd.to_numeric, errors='coerce')
        condition_func = lambda x: true_value if pd.notna(x) and eval(condition) else false_value
        return numeric_data.applymap(condition_func)
    else:
        numeric_data = pd.to_numeric(data, errors='coerce')
        condition_func = lambda x: true_value if pd.notna(x) and eval(condition) else false_value
        return numeric_data.apply(condition_func)""",
            "description": "Performs a logical test and returns one value for TRUE and another for FALSE"
        },
        {
            "name": "ROUND",
            "code": """def round_function(data, decimals=0):
    import pandas as pd
    import numpy as np
    
    if isinstance(data, pd.DataFrame):
        numeric_data = data.apply(pd.to_numeric, errors='coerce')
        return numeric_data.round(decimals)
    else:
        numeric_data = pd.to_numeric(data, errors='coerce')
        return numeric_data.round(decimals)""",
            "description": "Rounds a number to a specified number of digits"
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
