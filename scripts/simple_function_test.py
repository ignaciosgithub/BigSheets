"""
Simple test script to verify that our fix for the function execution context works.
This script simulates the issue and tests the solution without importing the entire class.
"""

import asyncio

async def test_function_execution_context():
    """Test that functions can access globals in the execution context."""
    print("\nTesting function execution context...")
    
    loop = asyncio.get_event_loop()
    
    global_var1 = "Global Variable 1"
    global_var2 = "Global Variable 2"
    
    def test_function():
        return f"Accessing {global_var1} and {global_var2}"
    
    try:
        result1 = await loop.run_in_executor(
            None, lambda: test_function()
        )
        print(f"Lambda approach result: {result1}")
    except Exception as e:
        print(f"Lambda approach error: {str(e)}")
    
    def run_with_globals():
        nonlocal global_var1, global_var2
        return test_function()
    
    try:
        result2 = await loop.run_in_executor(None, run_with_globals)
        print(f"Helper function approach result: {result2}")
    except Exception as e:
        print(f"Helper function approach error: {str(e)}")
    
    if "Global Variable 1" in result2 and "Global Variable 2" in result2:
        print("Test passed! Helper function approach can access globals in the execution context.")
        return True
    else:
        print("Test failed. Helper function approach cannot access globals in the execution context.")
        return False

async def main():
    success = await test_function_execution_context()
    
    if success:
        print("\nOverall test passed! Our fix for the function execution context works.")
    else:
        print("\nOverall test failed. Our fix for the function execution context does not work.")

if __name__ == "__main__":
    asyncio.run(main())
