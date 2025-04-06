import os
import json
import sys

def update_template_code(code):
    """
    Update template code to use direct cell access methods instead of return statements.
    """
    if "get_cell_value(" in code and "set_cell_value(" in code:
        pass
    elif "def get_cell_value(" not in code and "def set_cell_value(" not in code:
        cell_access_comment = """
"""
        code = cell_access_comment + code
    
    imports_added = False
    if "import asyncio" not in code and "import time" not in code:
        code_lines = code.split('\n')
        import_section_end = 0
        for i, line in enumerate(code_lines):
            if line.strip().startswith('import ') or line.strip().startswith('from '):
                import_section_end = i + 1
        
        code_lines.insert(import_section_end, "    import asyncio")
        code_lines.insert(import_section_end, "    import time")
        imports_added = True
        code = '\n'.join(code_lines)
    
    if "return " in code and "set_cell_value" not in code:
        function_name = None
        for line in code.split('\n'):
            if line.strip().startswith('def '):
                function_name = line.strip().split('def ')[1].split('(')[0]
                break
        
        if "while True:" not in code:
            code = code.replace("def " + function_name + "(data", 
                               f"def {function_name}(data")
            
            lines = code.split('\n')
            content_start = 0
            for i, line in enumerate(lines):
                if i > 0 and not (line.strip().startswith('import ') or line.strip().startswith('from ')):
                    if line.strip() and not line.strip().startswith('#'):
                        content_start = i
                        break
            
            if "if data is None:" not in code:
                error_check = """
    if data is None:
        set_cell_value(0, 0, "Error: No data selected")
        return
        
    previous_data = None
    
    while True:
        if data != previous_data:
            previous_data = data.copy() if hasattr(data, "copy") else data
            
            try:"""
                
                indented_lines = []
                for i, line in enumerate(lines):
                    if i < content_start:
                        indented_lines.append(line)
                    elif i == content_start:
                        indented_lines.append(error_check)
                        indented_lines.append("                " + line)
                    else:
                        indented_lines.append("                " + line)
                
                indented_lines.append("""            except Exception as e:
                error_msg = f"Error: {str(e)}"
                set_cell_value(0, 0, error_msg)
        
        await asyncio.sleep(0.1)""")
                
                code = '\n'.join(indented_lines)
            
        lines = code.split('\n')
        updated_lines = []
        
        for line in lines:
            if "return " in line and not line.strip().startswith('#'):
                indent = len(line) - len(line.lstrip())
                spaces = ' ' * indent
                
                return_value = line.strip()[7:]  # Remove 'return '
                
                if "numeric_data.sum().sum()" in return_value or "numeric_data.stack().mean()" in return_value:
                    updated_lines.append(f"{spaces}result = {return_value}")
                    updated_lines.append(f"{spaces}set_cell_value(0, 0, result)")
                elif ".tolist()" in return_value:
                    updated_lines.append(f"{spaces}result = {return_value}")
                    updated_lines.append(f"{spaces}for i, val in enumerate(result):")
                    updated_lines.append(f"{spaces}    set_cell_value(0, i, val)")
                elif return_value.startswith('"') or return_value.startswith("'") or return_value.startswith('f"') or return_value.startswith("f'"):
                    updated_lines.append(f"{spaces}set_cell_value(0, 0, {return_value})")
                else:
                    updated_lines.append(f"{spaces}result = {return_value}")
                    updated_lines.append(f"{spaces}set_cell_value(0, 0, result)")
            else:
                updated_lines.append(line)
        
        code = '\n'.join(updated_lines)
    
    return code

def update_template_files(directory):
    """
    Update all template files in the specified directory to use direct cell access.
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
