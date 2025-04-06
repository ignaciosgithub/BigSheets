"""
Script to update Windows templates with global declarations for cell access functions.
This ensures that template functions can access set_cell_value and get_cell_value methods.
"""

import os
import json
import sys

def add_globals_to_template_code(code):
    """
    Add global declarations for set_cell_value and get_cell_value to template code.
    """
    if "global set_cell_value" in code and "global get_cell_value" in code:
        return code
    
    global_declarations = """
global set_cell_value, get_cell_value

"""
    
    lines = code.split('\n')
    function_line_index = -1
    
    for i, line in enumerate(lines):
        if line.strip().startswith('def '):
            function_line_index = i
            break
    
    if function_line_index >= 0:
        indent = len(lines[function_line_index]) - len(lines[function_line_index].lstrip())
        indent_spaces = ' ' * (indent + 4)
        global_lines = [indent_spaces + line for line in global_declarations.strip().split('\n')]
        
        insert_index = function_line_index + 1
        while insert_index < len(lines) and (not lines[insert_index].strip() or lines[insert_index].strip().startswith('#')):
            insert_index += 1
        
        lines[insert_index:insert_index] = global_lines
        
        error_handling = f"""
{indent_spaces}# Add error handling for cell access functions
{indent_spaces}try:
{indent_spaces}    # Test if cell access functions are available
{indent_spaces}    if 'set_cell_value' not in globals() or 'get_cell_value' not in globals():
{indent_spaces}        raise NameError("Cell access functions not available")
{indent_spaces}except NameError as e:
{indent_spaces}    print(f"Error: {{e}}")
{indent_spaces}    return "Error: Cell access functions not available"
"""
        
        lines[insert_index+len(global_lines):insert_index+len(global_lines)] = error_handling.strip().split('\n')
        
        return '\n'.join(lines)
    
    return code

def update_template_files(directory):
    """
    Update all template files in the specified directory with global declarations.
    """
    if not os.path.exists(directory):
        print(f"Directory not found: {directory}")
        return
    
    updated_count = 0
    
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            file_path = os.path.join(directory, filename)
            
            try:
                with open(file_path, 'r') as f:
                    template_data = json.load(f)
                
                if "code" in template_data:
                    original_code = template_data["code"]
                    updated_code = add_globals_to_template_code(original_code)
                    
                    if original_code != updated_code:
                        template_data["code"] = updated_code
                        
                        with open(file_path, 'w') as f:
                            json.dump(template_data, f, indent=2)
                        
                        print(f"Updated template: {template_data.get('name', filename)}")
                        updated_count += 1
            except Exception as e:
                print(f"Error updating {filename}: {str(e)}")
    
    print(f"\nTotal templates updated: {updated_count}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        directory = sys.argv[1]
    else:
        if os.name == 'nt':  # Windows
            app_data = os.environ.get('APPDATA', os.path.expanduser('~'))
            directory = os.path.join(app_data, 'BigSheets', 'functions')
        else:  # Unix-like
            directory = os.path.expanduser("~/.bigsheets/functions")
    
    print(f"Updating template files in: {directory}")
    update_template_files(directory)
    print("Template update complete. Please restart the application to load the updated templates.")
