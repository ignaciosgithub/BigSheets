"""
Script to update all template files in the Windows AppData directory to ensure
they work with the improved execution context.
"""

import os
import json
import sys

def update_template_code(code):
    """Remove unnecessary global declarations since they're now handled by the execution context."""
    if "global set_cell_value, get_cell_value" in code:
        lines = code.split('\n')
        updated_lines = []
        
        for line in lines:
            if "global set_cell_value, get_cell_value" not in line:
                updated_lines.append(line)
        
        updated_lines.insert(0, "# Updated to work with improved execution context")
        
        return '\n'.join(updated_lines)
    
    return code

def update_template_files(directory):
    """Update all template files in the specified directory."""
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
                    updated_code = update_template_code(original_code)
                    
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
