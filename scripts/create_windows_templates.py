"""
Script to create common spreadsheet template functions for BigSheets on Windows.

This script creates template functions and saves them to the Windows AppData directory
at C:/Users/Pichau/AppData/Roaming/BigSheets/functions.
"""

import os
import sys
import json
import uuid
import time
from pathlib import Path

WINDOWS_PATH = "C:/Users/Pichau/AppData/Roaming/BigSheets/functions"

TEMPLATE_FUNCTIONS = [
    {
        "name": "SUM",
        "description": "Calculates the sum of a range of values",
        "code": """
def sum_function(data):
    import pandas as pd
    import numpy as np
    
    if isinstance(data, pd.DataFrame):
        numeric_data = data.apply(pd.to_numeric, errors='coerce')
        return numeric_data.sum().sum()
    else:
        numeric_data = pd.to_numeric(data, errors='coerce')
        return numeric_data.sum()
"""
    },
    {
        "name": "AVERAGE",
        "description": "Calculates the average (arithmetic mean) of a range of values",
        "code": """
def average_function(data):
    import pandas as pd
    import numpy as np
    
    if isinstance(data, pd.DataFrame):
        numeric_data = data.apply(pd.to_numeric, errors='coerce')
        return numeric_data.stack().mean()
    else:
        numeric_data = pd.to_numeric(data, errors='coerce')
        return numeric_data.mean()
"""
    },
    {
        "name": "COUNT",
        "description": "Counts the number of cells that contain numbers",
        "code": """
def count_function(data):
    import pandas as pd
    import numpy as np
    
    if isinstance(data, pd.DataFrame):
        numeric_data = data.apply(pd.to_numeric, errors='coerce')
        return numeric_data.count().sum()
    else:
        numeric_data = pd.to_numeric(data, errors='coerce')
        return numeric_data.count()
"""
    },
    {
        "name": "MAX",
        "description": "Returns the maximum value in a range of values",
        "code": """
def max_function(data):
    import pandas as pd
    import numpy as np
    
    if isinstance(data, pd.DataFrame):
        numeric_data = data.apply(pd.to_numeric, errors='coerce')
        return numeric_data.max().max()
    else:
        numeric_data = pd.to_numeric(data, errors='coerce')
        return numeric_data.max()
"""
    },
    {
        "name": "MIN",
        "description": "Returns the minimum value in a range of values",
        "code": """
def min_function(data):
    import pandas as pd
    import numpy as np
    
    if isinstance(data, pd.DataFrame):
        numeric_data = data.apply(pd.to_numeric, errors='coerce')
        return numeric_data.min().min()
    else:
        numeric_data = pd.to_numeric(data, errors='coerce')
        return numeric_data.min()
"""
    },
    {
        "name": "COUNTIF",
        "description": "Counts the number of cells that meet a specific condition",
        "code": """
def countif_function(data, condition="x > 0"):
    import pandas as pd
    import numpy as np
    
    if isinstance(data, pd.DataFrame):
        numeric_data = data.apply(pd.to_numeric, errors='coerce')
        condition_func = lambda x: eval(condition)
        return numeric_data.applymap(condition_func).sum().sum()
    else:
        numeric_data = pd.to_numeric(data, errors='coerce')
        condition_func = lambda x: eval(condition)
        return numeric_data.apply(condition_func).sum()
"""
    },
    {
        "name": "CONCATENATE",
        "description": "Joins text from multiple cells into one cell",
        "code": """
def concatenate_function(data, separator=""):
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
        return result
"""
    },
    {
        "name": "VLOOKUP",
        "description": "Looks up a value in the first column of a range and returns a value in the same row from a specified column",
        "code": """
def vlookup_function(lookup_value, data, col_index=1, exact_match=True):
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
            return "Error: Non-exact match requires numeric values"
"""
    },
    {
        "name": "IF",
        "description": "Performs a logical test and returns one value for TRUE and another for FALSE",
        "code": """
def if_function(data, condition="x > 0", true_value=1, false_value=0):
    import pandas as pd
    import numpy as np
    
    if isinstance(data, pd.DataFrame):
        numeric_data = data.apply(pd.to_numeric, errors='coerce')
        condition_func = lambda x: true_value if pd.notna(x) and eval(condition) else false_value
        return numeric_data.applymap(condition_func)
    else:
        numeric_data = pd.to_numeric(data, errors='coerce')
        condition_func = lambda x: true_value if pd.notna(x) and eval(condition) else false_value
        return numeric_data.apply(condition_func)
"""
    },
    {
        "name": "ROUND",
        "description": "Rounds a number to a specified number of digits",
        "code": """
def round_function(data, decimals=0):
    import pandas as pd
    import numpy as np
    
    if isinstance(data, pd.DataFrame):
        numeric_data = data.apply(pd.to_numeric, errors='coerce')
        return numeric_data.round(decimals)
    else:
        numeric_data = pd.to_numeric(data, errors='coerce')
        return numeric_data.round(decimals)
"""
    }
]

def convert_to_persistent_code(code):
    """Convert standard template code to persistent template code with while loops."""
    lines = code.strip().split('\n')
    
    function_def_line = lines[0]
    
    import_lines = [line for line in lines[1:] if line.strip().startswith('import ')]
    
    core_logic_lines = []
    return_lines = []
    
    for line in lines[1:]:
        if line.strip().startswith('return '):
            return_lines.append(line.replace('return ', ''))
        elif not line.strip().startswith('import ') and line.strip():
            core_logic_lines.append(line)
    
    new_code = []
    new_code.append(function_def_line)
    
    for imp in import_lines:
        new_code.append('    ' + imp)
    
    new_code.append('    import time')
    new_code.append('    import asyncio')
    new_code.append('')
    new_code.append('    # Initial state')
    new_code.append('    previous_data = None')
    new_code.append('')
    new_code.append('    # Continuous monitoring loop')
    new_code.append('    while True:')
    new_code.append('        # Only process if data has changed')
    new_code.append('        if data != previous_data:')
    new_code.append('            previous_data = data.copy() if hasattr(data, "copy") else data')
    new_code.append('')
    
    for line in core_logic_lines:
        indent_count = len(line) - len(line.lstrip())
        if indent_count > 0:
            new_code.append('            ' + line)
        else:
            new_code.append('            ' + line.lstrip())
    
    for ret in return_lines:
        new_code.append('            result_value = ' + ret.strip())
        new_code.append('            # Convert to simple types if needed')
        new_code.append('            if hasattr(result_value, "__iter__") and not isinstance(result_value, (list, dict, str)):')
        new_code.append('                try:')
        new_code.append('                    # Try to get the first value from the generator')
        new_code.append('                    result_value = next(result_value)')
        new_code.append('                except StopIteration:')
        new_code.append('                    result_value = None')
        new_code.append('            yield result_value')
    
    new_code.append('        # Brief pause to prevent CPU hogging')
    new_code.append('        await asyncio.sleep(0.1)')
    
    return '\n'.join(new_code)

def create_template_json():
    """Create template JSON files for Windows."""
    os.makedirs(WINDOWS_PATH, exist_ok=True)
    print(f"Ensuring directory exists: {WINDOWS_PATH}")
    
    created_templates = []
    
    for template_info in TEMPLATE_FUNCTIONS:
        try:
            template_id = str(uuid.uuid4())
            template_name = template_info["name"]
            template_data = {
                "id": template_id,
                "name": template_name,
                "code": template_info["code"],
                "description": template_info["description"],
                "created_at": time.time(),
                "updated_at": time.time(),
                "is_persistent": False
            }
            
            template_file = os.path.join(WINDOWS_PATH, f"{template_id}.json")
            with open(template_file, 'w') as f:
                json.dump(template_data, f, indent=2)
            
            print(f"Created template: {template_name}")
            created_templates.append((template_name, template_id))
            
            persistent_id = str(uuid.uuid4())
            persistent_name = f"Persistent {template_name}"
            persistent_description = f"{template_info['description']}. Updates automatically when source values change."
            
            persistent_code = convert_to_persistent_code(template_info["code"])
            
            persistent_data = {
                "id": persistent_id,
                "name": persistent_name,
                "code": persistent_code,
                "description": persistent_description,
                "created_at": time.time(),
                "updated_at": time.time(),
                "is_persistent": True
            }
            
            persistent_file = os.path.join(WINDOWS_PATH, f"{persistent_id}.json")
            with open(persistent_file, 'w') as f:
                json.dump(persistent_data, f, indent=2)
            
            print(f"Created persistent template: {persistent_name}")
            created_templates.append((persistent_name, persistent_id))
            
        except Exception as e:
            print(f"Error creating template {template_info['name']}: {str(e)}")
    
    print(f"Total templates created: {len(created_templates)}")
    for name, template_id in created_templates:
        print(f"  - {name} (ID: {template_id})")
    
    print(f"Templates saved to: {WINDOWS_PATH}")
    print("Note: This script creates JSON files directly in the Windows AppData directory.")
    print("These files will be loaded by the BigSheets application when it starts on Windows.")

if __name__ == "__main__":
    create_template_json()
