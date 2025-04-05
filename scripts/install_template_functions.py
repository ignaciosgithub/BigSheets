"""
Script to install template functions to the Windows AppData directory.
This script creates common spreadsheet template functions and installs them
to the appropriate directory based on the operating system.
"""

import os
import json
import uuid
import time
import sys
import shutil

sum_function_code = '''
def sum_function(data=None):
    """Sum the values in the selected range."""
    import numpy as np
    
    if data is None:
        return 0
    
    try:
        flat_data = []
        for row in data:
            for cell in row:
                if isinstance(cell, (int, float)):
                    flat_data.append(cell)
        
        return sum(flat_data)
    except Exception as e:
        return f"Error: {str(e)}"
'''

persistent_sum_function_code = '''
def persistent_sum_function(data=None):
    """Sum the values in the selected range. Updates automatically when data changes."""
    import numpy as np
    import asyncio
    
    if data is None:
        yield 0
        return
    
    previous_data = None
    
    while True:
        if data != previous_data:
            previous_data = data.copy() if hasattr(data, "copy") else data
            
            try:
                flat_data = []
                for row in data:
                    for cell in row:
                        if isinstance(cell, (int, float)):
                            flat_data.append(cell)
                
                result = sum(flat_data)
                yield result
            except Exception as e:
                yield f"Error: {str(e)}"
        
        await asyncio.sleep(0.1)
'''

average_function_code = '''
def average_function(data=None):
    """Calculate the average of the values in the selected range."""
    import numpy as np
    
    if data is None:
        return 0
    
    try:
        flat_data = []
        for row in data:
            for cell in row:
                if isinstance(cell, (int, float)):
                    flat_data.append(cell)
        
        if len(flat_data) == 0:
            return 0
        
        return sum(flat_data) / len(flat_data)
    except Exception as e:
        return f"Error: {str(e)}"
'''

persistent_average_function_code = '''
def persistent_average_function(data=None):
    """Calculate the average of the values in the selected range. Updates automatically when data changes."""
    import numpy as np
    import asyncio
    
    if data is None:
        yield 0
        return
    
    previous_data = None
    
    while True:
        if data != previous_data:
            previous_data = data.copy() if hasattr(data, "copy") else data
            
            try:
                flat_data = []
                for row in data:
                    for cell in row:
                        if isinstance(cell, (int, float)):
                            flat_data.append(cell)
                
                if len(flat_data) == 0:
                    result = 0
                else:
                    result = sum(flat_data) / len(flat_data)
                
                yield result
            except Exception as e:
                yield f"Error: {str(e)}"
        
        await asyncio.sleep(0.1)
'''

count_function_code = '''
def count_function(data=None):
    """Count the number of values in the selected range."""
    if data is None:
        return 0
    
    try:
        count = 0
        for row in data:
            for cell in row:
                if cell is not None and cell != "":
                    count += 1
        
        return count
    except Exception as e:
        return f"Error: {str(e)}"
'''

persistent_count_function_code = '''
def persistent_count_function(data=None):
    """Count the number of values in the selected range. Updates automatically when data changes."""
    import asyncio
    
    if data is None:
        yield 0
        return
    
    previous_data = None
    
    while True:
        if data != previous_data:
            previous_data = data.copy() if hasattr(data, "copy") else data
            
            try:
                count = 0
                for row in data:
                    for cell in row:
                        if cell is not None and cell != "":
                            count += 1
                
                yield count
            except Exception as e:
                yield f"Error: {str(e)}"
        
        await asyncio.sleep(0.1)
'''

max_function_code = '''
def max_function(data=None):
    """Find the maximum value in the selected range."""
    import numpy as np
    
    if data is None:
        return 0
    
    try:
        flat_data = []
        for row in data:
            for cell in row:
                if isinstance(cell, (int, float)):
                    flat_data.append(cell)
        
        if len(flat_data) == 0:
            return 0
        
        return max(flat_data)
    except Exception as e:
        return f"Error: {str(e)}"
'''

persistent_max_function_code = '''
def persistent_max_function(data=None):
    """Find the maximum value in the selected range. Updates automatically when data changes."""
    import numpy as np
    import asyncio
    
    if data is None:
        yield 0
        return
    
    previous_data = None
    
    while True:
        if data != previous_data:
            previous_data = data.copy() if hasattr(data, "copy") else data
            
            try:
                flat_data = []
                for row in data:
                    for cell in row:
                        if isinstance(cell, (int, float)):
                            flat_data.append(cell)
                
                if len(flat_data) == 0:
                    result = 0
                else:
                    result = max(flat_data)
                
                yield result
            except Exception as e:
                yield f"Error: {str(e)}"
        
        await asyncio.sleep(0.1)
'''

min_function_code = '''
def min_function(data=None):
    """Find the minimum value in the selected range."""
    import numpy as np
    
    if data is None:
        return 0
    
    try:
        flat_data = []
        for row in data:
            for cell in row:
                if isinstance(cell, (int, float)):
                    flat_data.append(cell)
        
        if len(flat_data) == 0:
            return 0
        
        return min(flat_data)
    except Exception as e:
        return f"Error: {str(e)}"
'''

persistent_min_function_code = '''
def persistent_min_function(data=None):
    """Find the minimum value in the selected range. Updates automatically when data changes."""
    import numpy as np
    import asyncio
    
    if data is None:
        yield 0
        return
    
    previous_data = None
    
    while True:
        if data != previous_data:
            previous_data = data.copy() if hasattr(data, "copy") else data
            
            try:
                flat_data = []
                for row in data:
                    for cell in row:
                        if isinstance(cell, (int, float)):
                            flat_data.append(cell)
                
                if len(flat_data) == 0:
                    result = 0
                else:
                    result = min(flat_data)
                
                yield result
            except Exception as e:
                yield f"Error: {str(e)}"
        
        await asyncio.sleep(0.1)
'''

persistent_benford_function_code = '''
def persistent_benfords_law(data=None):
    """Analyze first digits using Benford's Law. Updates automatically when source values change."""
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    import io, base64
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    import time
    import asyncio
    
    if data is None:
        yield "Error: No data selected"
        return
        
    previous_data = None
    
    while True:
        if data != previous_data:
            previous_data = data.copy() if hasattr(data, "copy") else data
            
            try:
                df = pd.DataFrame(data)
                flat_data = df.values.flatten()
                
                first_digits = []
                for num in flat_data:
                    if num > 0:
                        str_num = str(abs(num)).strip('0.')
                        if str_num:
                            first_digits.append(int(str_num[0]))
                
                if not first_digits:
                    yield "No valid positive numbers found in selection"
                    continue
                
                digit_counts = {}
                for d in range(1, 10):  # Benford's Law applies to digits 1-9
                    digit_counts[d] = first_digits.count(d) / len(first_digits)
                
                benford_expected = {
                    1: 0.301, 2: 0.176, 3: 0.125, 4: 0.097, 
                    5: 0.079, 6: 0.067, 7: 0.058, 8: 0.051, 9: 0.046
                }
                
                fig = Figure(figsize=(8, 6))
                ax = fig.add_subplot(111)
                
                digits = list(range(1, 10))
                observed = [digit_counts.get(d, 0) for d in digits]
                expected = [benford_expected[d] for d in digits]
                
                x = np.arange(len(digits))
                width = 0.35
                
                ax.bar(x - width/2, observed, width, label='Observed')
                ax.bar(x + width/2, expected, width, label='Expected (Benford\\'s Law)')
                
                ax.set_xlabel('First Digit')
                ax.set_ylabel('Frequency')
                ax.set_title('Benford\\'s Law Analysis')
                ax.set_xticks(x)
                ax.set_xticklabels(digits)
                ax.legend()
                
                canvas = FigureCanvasAgg(fig)
                buf = io.BytesIO()
                canvas.print_png(buf)
                data_img = base64.b64encode(buf.getbuffer()).decode("ascii")
                
                result = {
                    "image": f"data:image/png;base64,{data_img}",
                    "summary": {d: {"observed": digit_counts.get(d, 0), "expected": benford_expected[d]} for d in range(1, 10)}
                }
                
                yield result
            except Exception as e:
                yield f"Error in Benford's analysis: {str(e)}"
        
        await asyncio.sleep(0.1)
'''

def create_template_json(name, code, description, is_persistent=False):
    """Create a template JSON object."""
    template_id = str(uuid.uuid4())
    created_at = time.time()
    
    template = {
        "id": template_id,
        "name": name,
        "code": code,
        "description": description,
        "created_at": created_at,
        "updated_at": created_at,
        "is_persistent": is_persistent
    }
    
    return template

def get_storage_dir():
    """Get the appropriate storage directory based on the OS."""
    if os.name == 'nt':  # Windows
        app_data = os.environ.get('APPDATA', os.path.expanduser('~'))
        storage_dir = os.path.join(app_data, 'BigSheets', 'functions')
    else:  # Unix-like
        storage_dir = os.path.expanduser("~/.bigsheets/functions")
    
    return storage_dir

def install_templates():
    """Install template functions to the appropriate directory."""
    storage_dir = get_storage_dir()
    
    if not os.path.exists(storage_dir):
        os.makedirs(storage_dir, exist_ok=True)
        print(f"Created directory: {storage_dir}")
    
    templates = [
        create_template_json("SUM", sum_function_code, "Sum of values in selected range"),
        create_template_json("AVERAGE", average_function_code, "Average of values in selected range"),
        create_template_json("COUNT", count_function_code, "Count of values in selected range"),
        create_template_json("MAX", max_function_code, "Maximum value in selected range"),
        create_template_json("MIN", min_function_code, "Minimum value in selected range"),
        
        create_template_json("Persistent SUM", persistent_sum_function_code, 
                           "Sum of values in selected range with real-time updates", True),
        create_template_json("Persistent AVERAGE", persistent_average_function_code, 
                           "Average of values in selected range with real-time updates", True),
        create_template_json("Persistent COUNT", persistent_count_function_code, 
                           "Count of values in selected range with real-time updates", True),
        create_template_json("Persistent MAX", persistent_max_function_code, 
                           "Maximum value in selected range with real-time updates", True),
        create_template_json("Persistent MIN", persistent_min_function_code, 
                           "Minimum value in selected range with real-time updates", True),
        
        create_template_json("Persistent Benford's Law Analysis", persistent_benford_function_code,
                           "Analyzes first digit frequencies using Benford's Law and updates automatically when source values change", True)
    ]
    
    for template in templates:
        template_file = os.path.join(storage_dir, f"{template['name'].replace(' ', '_').lower()}_{template['id']}.json")
        with open(template_file, 'w') as f:
            json.dump(template, f, indent=2)
        
        print(f"Installed template: {template['name']} to {template_file}")
    
    return True

if __name__ == "__main__":
    success = install_templates()
    
    if success:
        print("Successfully installed template functions.")
        print(f"Template functions installed to: {get_storage_dir()}")
        print("Restart BigSheets to load the new template functions.")
    else:
        print("Failed to install template functions.")
        sys.exit(1)
