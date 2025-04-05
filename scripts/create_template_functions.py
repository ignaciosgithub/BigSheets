"""
Script to create common spreadsheet template functions for BigSheets.

This script creates a set of commonly used spreadsheet functions and saves them
to the appropriate directory for the BigSheets application.
"""

import os
import sys
import json
import uuid
import time
import importlib.util
from pathlib import Path

repo_root = Path(__file__).parent.parent.absolute()
function_manager_path = repo_root / "src" / "bigsheets" / "function_engine" / "function_manager.py"

spec = importlib.util.spec_from_file_location("function_manager", function_manager_path)
function_manager = importlib.util.module_from_spec(spec)
spec.loader.exec_module(function_manager)

FunctionManager = function_manager.FunctionManager
FunctionTemplate = function_manager.FunctionTemplate

TEMPLATE_FUNCTIONS = [
    {
        "name": "SUM",
        "persistent_name": "Persistent SUM",
        "description": "Calculates the sum of a range of values",
        "persistent_description": "Calculates the sum of a range of values. Updates automatically when source values change.",
        "code": """
def sum_function(data):
    \"\"\"
    Calculate the sum of values in the selected range.
    
    Args:
        data: DataFrame or Series containing the selected data
        
    Returns:
        The sum of all numeric values
    \"\"\"
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
        "persistent_name": "Persistent AVERAGE",
        "description": "Calculates the average (arithmetic mean) of a range of values",
        "persistent_description": "Calculates the average (arithmetic mean) of a range of values. Updates automatically when source values change.",
        "code": """
def average_function(data):
    \"\"\"
    Calculate the average (arithmetic mean) of values in the selected range.
    
    Args:
        data: DataFrame or Series containing the selected data
        
    Returns:
        The average of all numeric values
    \"\"\"
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
        "persistent_name": "Persistent COUNT",
        "description": "Counts the number of cells that contain numbers",
        "persistent_description": "Counts the number of cells that contain numbers. Updates automatically when source values change.",
        "code": """
def count_function(data):
    \"\"\"
    Count the number of cells that contain numbers in the selected range.
    
    Args:
        data: DataFrame or Series containing the selected data
        
    Returns:
        The count of numeric values
    \"\"\"
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
        "persistent_name": "Persistent MAX",
        "description": "Returns the maximum value in a range of values",
        "persistent_description": "Returns the maximum value in a range of values. Updates automatically when source values change.",
        "code": """
def max_function(data):
    \"\"\"
    Find the maximum value in the selected range.
    
    Args:
        data: DataFrame or Series containing the selected data
        
    Returns:
        The maximum numeric value
    \"\"\"
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
        "persistent_name": "Persistent MIN",
        "description": "Returns the minimum value in a range of values",
        "persistent_description": "Returns the minimum value in a range of values. Updates automatically when source values change.",
        "code": """
def min_function(data):
    \"\"\"
    Find the minimum value in the selected range.
    
    Args:
        data: DataFrame or Series containing the selected data
        
    Returns:
        The minimum numeric value
    \"\"\"
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
        "persistent_name": "Persistent COUNTIF",
        "description": "Counts the number of cells that meet a specific condition",
        "persistent_description": "Counts the number of cells that meet a specific condition. Updates automatically when source values change.",
        "code": """
def countif_function(data, condition="x > 0"):
    \"\"\"
    Count the number of cells that meet a specific condition.
    
    Args:
        data: DataFrame or Series containing the selected data
        condition: String condition to evaluate (default: "x > 0")
        
    Returns:
        The count of values meeting the condition
    \"\"\"
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
        "persistent_name": "Persistent CONCATENATE",
        "description": "Joins text from multiple cells into one cell",
        "persistent_description": "Joins text from multiple cells into one cell. Updates automatically when source values change.",
        "code": """
def concatenate_function(data, separator=""):
    \"\"\"
    Join text from multiple cells into one cell.
    
    Args:
        data: DataFrame or Series containing the selected data
        separator: String to insert between concatenated values (default: "")
        
    Returns:
        The concatenated string
    \"\"\"
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
        "persistent_name": "Persistent VLOOKUP",
        "description": "Looks up a value in the first column of a range and returns a value in the same row from a specified column",
        "persistent_description": "Looks up a value in the first column of a range and returns a value in the same row from a specified column. Updates automatically when source values change.",
        "code": """
def vlookup_function(lookup_value, data, col_index=1, exact_match=True):
    \"\"\"
    Look up a value in the first column of a range and return a value in the same row from a specified column.
    
    Args:
        lookup_value: The value to search for in the first column
        data: DataFrame containing the data to search in
        col_index: The column index (1-based) to return a value from (default: 1)
        exact_match: Whether to require an exact match (default: True)
        
    Returns:
        The value from the specified column in the matching row
    \"\"\"
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
        "persistent_name": "Persistent IF",
        "description": "Performs a logical test and returns one value for TRUE and another for FALSE",
        "persistent_description": "Performs a logical test and returns one value for TRUE and another for FALSE. Updates automatically when source values change.",
        "code": """
def if_function(data, condition="x > 0", true_value=1, false_value=0):
    \"\"\"
    Perform a logical test and return one value for TRUE and another for FALSE.
    
    Args:
        data: DataFrame or Series containing the selected data
        condition: String condition to evaluate (default: "x > 0")
        true_value: Value to return if condition is TRUE (default: 1)
        false_value: Value to return if condition is FALSE (default: 0)
        
    Returns:
        DataFrame or Series with values replaced based on the condition
    \"\"\"
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
        "persistent_name": "Persistent ROUND",
        "description": "Rounds a number to a specified number of digits",
        "persistent_description": "Rounds a number to a specified number of digits. Updates automatically when source values change.",
        "code": """
def round_function(data, decimals=0):
    \"\"\"
    Round numbers to a specified number of digits.
    
    Args:
        data: DataFrame or Series containing the selected data
        decimals: Number of decimal places to round to (default: 0)
        
    Returns:
        The rounded values
    \"\"\"
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

def create_template_functions():
    """Create template functions and save them to the appropriate directory."""
    windows_path = r"C:\Users\Pichau\AppData\Roaming\BigSheets\functions"
    
    function_manager = FunctionManager(storage_dir=windows_path)
    
    created_templates = []
    
    for template in TEMPLATE_FUNCTIONS:
        try:
            function_template = function_manager.create_template(
                template["name"],
                template["code"],
                template["description"]
            )
            print(f"Created template: {template['name']}")
            
            persistent_template = function_manager.create_template(
                template["persistent_name"],
                template["code"],
                template["persistent_description"],
                is_persistent=True
            )
            print(f"Created persistent template: {template['persistent_name']}")
        except Exception as e:
            print(f"Error creating template {template['name']}: {str(e)}")
    
    function_manager.save_templates()
    print(f"Saved templates to: {function_manager.storage_dir}")
    
    templates = function_manager.list_templates()
    print(f"Total templates created: {len(templates)}")
    for template in templates:
        print(f"  - {template['name']} (ID: {template['id']})")

if __name__ == "__main__":
    create_template_functions()
