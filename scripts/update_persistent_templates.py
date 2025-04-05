"""
Script to update persistent template functions with while loops for BigSheets on Windows.
"""

import os
import sys
import json
import uuid
import time
from pathlib import Path

WINDOWS_PATH = "C:/Users/Pichau/AppData/Roaming/BigSheets/functions"

def update_persistent_templates():
    """Update persistent templates with while loops."""
    if not os.path.exists(WINDOWS_PATH):
        os.makedirs(WINDOWS_PATH, exist_ok=True)
        print(f"Created directory: {WINDOWS_PATH}")
    
    template_files = [f for f in os.listdir(WINDOWS_PATH) if f.endswith('.json')]
    updated_count = 0
    
    print(f"Found {len(template_files)} template files in {WINDOWS_PATH}")
    
    for filename in template_files:
        filepath = os.path.join(WINDOWS_PATH, filename)
        
        try:
            with open(filepath, 'r') as f:
                template_data = json.load(f)
            
            if template_data.get('is_persistent', False):
                function_name = template_data.get('name', '')
                code = template_data.get('code', '')
                
                if 'while True:' in code:
                    print(f"Skipping {function_name} - already has a while loop")
                    continue
                
                lines = code.strip().split('\n')
                function_def_line = lines[0]
                import_lines = [line for line in lines[1:] if line.strip().startswith('import ')]
                
                return_lines = []
                core_logic_lines = []
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
                
                new_code = '\n'.join(new_code)
                
                template_data['code'] = new_code
                template_data['updated_at'] = time.time()
                
                with open(filepath, 'w') as f:
                    json.dump(template_data, f, indent=2)
                
                print(f"Updated template: {function_name}")
                updated_count += 1
        except Exception as e:
            print(f"Error updating template {filename}: {str(e)}")
    
    print(f"Total templates updated: {updated_count}")
    print("Note: Restart the BigSheets application to load the updated templates.")

if __name__ == "__main__":
    update_persistent_templates()
