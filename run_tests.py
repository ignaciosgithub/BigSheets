"""
Test runner script for BigSheets.
"""

import unittest
import sys

if __name__ == "__main__":
    test_suite = unittest.defaultTestLoader.discover('tests')
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)
    
    sys.exit(not result.wasSuccessful())
