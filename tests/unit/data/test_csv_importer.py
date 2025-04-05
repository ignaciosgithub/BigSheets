"""
Unit tests for the CSV Importer module.
"""

import unittest
import os
import tempfile
import pandas as pd
from src.bigsheets.data.csv_importer import CSVImporter


class TestCSVImporter(unittest.TestCase):
    """Test cases for the CSVImporter class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.importer = CSVImporter()
        
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_csv_path = os.path.join(self.temp_dir.name, "test_data.csv")
        
        self.test_data = [
            ["Name", "Age", "City"],
            ["John", 30, "New York"],
            ["Alice", 25, "Los Angeles"],
            ["Bob", 35, "Chicago"]
        ]
        
        with open(self.test_csv_path, "w") as f:
            f.write("Name,Age,City\n")
            f.write("John,30,New York\n")
            f.write("Alice,25,Los Angeles\n")
            f.write("Bob,35,Chicago\n")
    
    def tearDown(self):
        """Clean up test fixtures."""
        self.temp_dir.cleanup()
    
    def test_import_csv(self):
        """Test importing a CSV file."""
        data = self.importer.import_csv(self.test_csv_path)
        
        self.assertEqual(len(data), 4)  # 3 data rows + header
        self.assertEqual(data[0], ["Name", "Age", "City"])
        self.assertEqual(data[1], ["John", 30, "New York"])
        self.assertEqual(data[2], ["Alice", 25, "Los Angeles"])
        self.assertEqual(data[3], ["Bob", 35, "Chicago"])
    
    def test_parse_csv(self):
        """Test parsing a CSV file to DataFrame."""
        df = self.importer.parse_csv(self.test_csv_path)
        
        self.assertEqual(len(df), 3)  # 3 data rows
        self.assertEqual(list(df.columns), ["Name", "Age", "City"])
        self.assertEqual(df.iloc[0]["Name"], "John")
        self.assertEqual(df.iloc[1]["Age"], 25)
        self.assertEqual(df.iloc[2]["City"], "Chicago")
    
    def test_infer_column_types(self):
        """Test inferring column types."""
        df = pd.DataFrame({
            "int_col": [1, 2, 3],
            "float_col": [1.1, 2.2, 3.3],
            "str_col": ["a", "b", "c"],
            "bool_col": [True, False, True]
        })
        
        types = self.importer.infer_column_types(df)
        
        self.assertEqual(types["int_col"], "integer")
        self.assertEqual(types["float_col"], "float")
        self.assertEqual(types["str_col"], "string")
        self.assertEqual(types["bool_col"], "boolean")
    
    def test_preview_csv(self):
        """Test previewing a CSV file."""
        preview_df, types = self.importer.preview_csv(self.test_csv_path, max_rows=2)
        
        self.assertEqual(len(preview_df), 2)
        
        self.assertEqual(types["Name"], "string")
        self.assertEqual(types["Age"], "integer")
        self.assertEqual(types["City"], "string")


if __name__ == "__main__":
    unittest.main()
