"""
Script to update all Windows AppData templates with global declarations for cell access functions.
"""

import os
import json
import sys

def fix_template_globals(app_data_path):
    """
    Fix templates in Windows AppData directory to include global declarations.
    """
    template_dir = os.path.join(app_data_path, 'BigSheets', 'functions')
    
    if not os.path.exists(template_dir):
        print(f"Template directory not found: {template_dir}")
        return False
    
    updated_count = 0
    templates = [f for f in os.listdir(template_dir) if f.endswith('.json')]
    
    if not templates:
        print("No template files found.")
        return False
    
    for template_file in templates:
        file_path = os.path.join(template_dir, template_file)
        
        try:
            with open(file_path, 'r') as f:
                template_data = json.load(f)
            
            if "code" in template_data:
                code = template_data["code"]
                
                if "global set_cell_value" not in code and "global get_cell_value" not in code:
                    function_name = None
                    for line in code.split('\n'):
                        if line.strip().startswith('def '):
                            function_name = line.strip().split('def ')[1].split('(')[0]
                            break
                    
                    if function_name:
                        lines = code.split('\n')
                        function_line_index = -1
                        
                        for i, line in enumerate(lines):
                            if line.strip().startswith(f'def {function_name}'):
                                function_line_index = i
                                break
                        
                        if function_line_index >= 0:
                            indent = len(lines[function_line_index]) - len(lines[function_line_index].lstrip())
                            global_declaration = ' ' * (indent + 4) + "global set_cell_value, get_cell_value"
                            
                            lines.insert(function_line_index + 1, global_declaration)
                            
                            template_data["code"] = '\n'.join(lines)
                            
                            with open(file_path, 'w') as f:
                                json.dump(template_data, f, indent=2)
                            
                            print(f"Updated template: {template_data.get('name', template_file)}")
                            updated_count += 1
        except Exception as e:
            print(f"Error updating {template_file}: {str(e)}")
    
    print(f"\nTotal templates updated: {updated_count}")
    return updated_count > 0

if __name__ == "__main__":
    if os.name == 'nt':  # Windows
        app_data = os.environ.get('APPDATA', os.path.expanduser('~'))
        print(f"Updating templates in {app_data}...")
        success = fix_template_globals(app_data)
        
        if success:
            print("Templates updated successfully. Please restart the application to load the updated templates.")
        else:
            print("Failed to update templates. Please check the template directory and try again.")
    else:
        print("This script is intended for Windows. Please run on a Windows machine.")
