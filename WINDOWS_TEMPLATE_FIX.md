# Fixing Template Functions on Windows

If you're experiencing the error "Function execution error: name 'set_cell_value' is not defined" when using template functions in BigSheets on Windows, follow these steps to fix the issue:

## Automatic Fix

1. Pull the latest changes from the main branch:
```bash
git pull origin main
```

2. Run the Windows template fix script:
```bash
python scripts/update_windows_appdata_templates.py
```

3. Restart the BigSheets application

## Manual Fix

If the automatic fix doesn't work, you can manually update the template files:

1. Navigate to your AppData folder: `C:\Users\[Username]\AppData\Roaming\BigSheets\functions`

2. For each JSON template file:
   - Open the file in a text editor
   - Find the function definition (`def function_name(data):`)
   - Add the following line immediately after the function definition:
     ```python
     global set_cell_value, get_cell_value
     ```
   - Save the file

3. Restart the BigSheets application

## Testing the Fix

To verify that the fix works:

1. Run the test script:
```bash
python scripts/test_global_access.py
```

2. If all tests pass, the fix has been successfully applied

3. Alternatively, create a simple template function that uses `set_cell_value` and verify that it works:
```python
def test_function(data):
    global set_cell_value, get_cell_value
    
    if data is None:
        set_cell_value(0, 0, "Error: No data provided")
        return
    
    total = sum(data)
    set_cell_value(0, 0, total)
```

## Troubleshooting

If you continue to experience issues:

1. Check the error message for clues
2. Verify that the template files have been updated by opening them in a text editor
3. Try creating a new template with the global declarations included
4. Restart the application after making changes
5. Check that the BigSheets application is using the correct AppData directory
6. Ensure that the template files are valid JSON with properly formatted Python code

## Technical Details

The issue occurs because template functions need explicit global declarations to access the `set_cell_value` and `get_cell_value` functions. These functions allow templates to directly manipulate cell values in the spreadsheet.

The fix works by:
1. Adding global declarations to template code
2. Ensuring that the functions are available in the global namespace during execution
3. Properly handling template compilation and execution errors

If you need further assistance, please open an issue on the GitHub repository.
