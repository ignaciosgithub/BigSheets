# Fixing Template Functions on Windows

If you're experiencing the error "Function execution error: name 'set_cell_value' is not defined" when using template functions in BigSheets on Windows, follow these steps to fix the issue:

## Automatic Fix

1. Pull the latest changes from the main branch:
```bash
git pull origin main
```

2. Run the improved Windows template fix script:
```bash
python scripts/update_templates_to_current_sheet.py
```

3. Restart the BigSheets application

## Creating New Templates

With the latest update, you need to use `current_sheet.set_cell_value` and `current_sheet.get_cell_value` in your templates instead of just `set_cell_value` and `get_cell_value`. The sheet object is automatically passed to your template function as the first parameter.

Example of a template function that will work correctly:

```python
def my_template_function(current_sheet, data):
    if data is None:
        current_sheet.set_cell_value(0, 0, "Error: No data provided")
        return
    
    total = sum(data)
    current_sheet.set_cell_value(0, 0, total)
    
    for i, val in enumerate(data):
        current_sheet.set_cell_value(1, i, val)
```

## Testing the Fix

To verify that the fix works:

1. Run the verification script:
```bash
python scripts/test_current_sheet_access.py
```

2. If the test passes, the fix has been successfully applied

3. Alternatively, create a simple template function using `current_sheet.set_cell_value` and verify that it works

## Troubleshooting

If you continue to experience issues:

1. Check the error message for clues
2. Verify that you're using the latest version of the application
3. Try running the verification script to check if the execution context is working properly
4. Restart the application after making changes
5. Ensure that the BigSheets application is using the correct AppData directory
6. Check that your template functions are using `current_sheet.set_cell_value` and `current_sheet.get_cell_value` correctly

## Technical Details

The application now ensures that template functions have access to cell manipulation methods by:
1. Modifying template functions to accept a `current_sheet` parameter
2. Passing the sheet instance as the first argument to template functions
3. Using `current_sheet.set_cell_value` and `current_sheet.get_cell_value` in template code

This approach is more reliable than using global functions because it explicitly passes the sheet instance to template functions, ensuring they have direct access to the sheet methods regardless of the execution context.

If you need further assistance, please open an issue on the GitHub repository.
