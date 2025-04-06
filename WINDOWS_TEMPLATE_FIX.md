# Fixing Template Functions on Windows

If you're experiencing the error "Function execution error: name 'set_cell_value' is not defined" when using template functions in BigSheets on Windows, follow these steps to fix the issue:

## Automatic Fix

1. Pull the latest changes from the main branch:
```bash
git pull origin main
```

2. Run the improved Windows template fix script:
```bash
python scripts/update_all_windows_templates.py
```

3. Restart the BigSheets application

## Creating New Templates

With the latest update, you no longer need to explicitly add global declarations for `set_cell_value` and `get_cell_value` in your templates. The execution context now handles this automatically.

Example of a template function that will work correctly:

```python
def my_template_function(data):
    # No need for global declarations
    
    if data is None:
        set_cell_value(0, 0, "Error: No data provided")
        return
    
    total = sum(data)
    set_cell_value(0, 0, total)
    
    for i, val in enumerate(data):
        set_cell_value(1, i, val)
```

## Testing the Fix

To verify that the fix works:

1. Run the verification script:
```bash
python scripts/verify_function_execution.py
```

2. If the test passes, the fix has been successfully applied

3. Alternatively, create a simple template function without global declarations and verify that it works

## Troubleshooting

If you continue to experience issues:

1. Check the error message for clues
2. Verify that you're using the latest version of the application
3. Try running the verification script to check if the execution context is working properly
4. Restart the application after making changes
5. Ensure that the BigSheets application is using the correct AppData directory
6. Check that your template functions are using `set_cell_value` and `get_cell_value` correctly

## Technical Details

The application now ensures that template functions have access to `set_cell_value` and `get_cell_value` functions in all execution contexts, including when running in a separate thread or process.

The improved fix works by:
1. Modifying the execution context to automatically provide access to cell manipulation functions
2. Using helper functions with proper global declarations in all execution contexts
3. Ensuring consistent behavior across different types of templates (standard and persistent)

If you need further assistance, please open an issue on the GitHub repository.
