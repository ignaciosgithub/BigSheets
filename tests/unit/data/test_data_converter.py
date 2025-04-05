"""
Unit tests for the Data Converter module.
"""

import unittest
from unittest.mock import MagicMock, patch
import pandas as pd
import os
import tempfile
import sqlite3
from src.bigsheets.data.data_converter import DataConverter


class TestDataConverter(unittest.TestCase):
    """Test cases for the DataConverter class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.converter = DataConverter()
        
        self.csv_data = [
            ["Name", "Age", "Score"],
            ["Alice", 25, 95.5],
            ["Bob", 30, 85.0],
            ["Charlie", 22, 90.5]
        ]
        
        self.db_data = [
            ["ID", "Product", "Price"],
            [1, "Laptop", 1200.50],
            [2, "Phone", 800.75],
            [3, "Tablet", 350.25]
        ]
        
        self.temp_dir = tempfile.TemporaryDirectory()
    
    def tearDown(self):
        """Clean up test fixtures."""
        self.temp_dir.cleanup()
    
    def test_csv_to_dataframe(self):
        """Test converting CSV data to DataFrame."""
        df = self.converter.csv_to_dataframe(self.csv_data)
        
        self.assertEqual(list(df.columns), ["Name", "Age", "Score"])
        self.assertEqual(len(df), 3)
        self.assertEqual(df.iloc[0]["Name"], "Alice")
        self.assertEqual(df.iloc[1]["Age"], 30)
        self.assertEqual(df.iloc[2]["Score"], 90.5)
    
    def test_dataframe_to_csv(self):
        """Test converting DataFrame to CSV data."""
        df = self.converter.csv_to_dataframe(self.csv_data)
        
        csv_result = self.converter.dataframe_to_csv(df)
        
        self.assertEqual(csv_result, self.csv_data)
    
    def test_database_to_dataframe(self):
        """Test converting database data to DataFrame."""
        df = self.converter.database_to_dataframe(self.db_data)
        
        self.assertEqual(list(df.columns), ["ID", "Product", "Price"])
        self.assertEqual(len(df), 3)
        self.assertEqual(df.iloc[0]["ID"], 1)
        self.assertEqual(df.iloc[1]["Product"], "Phone")
        self.assertEqual(df.iloc[2]["Price"], 350.25)
    
    def test_csv_to_database_file(self):
        """Test converting CSV data to a SQLite database file."""
        db_path = os.path.join(self.temp_dir.name, "test.db")
        
        result = self.converter.csv_to_database_file(self.csv_data, db_path)
        self.assertTrue(result)
        
        self.assertTrue(os.path.exists(db_path))
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM csv_data")
        rows = cursor.fetchall()
        conn.close()
        
        self.assertEqual(len(rows), 3)
        
        self.assertEqual(rows[0][0], "Alice")
        self.assertEqual(rows[0][1], 25)
        self.assertEqual(rows[0][2], 95.5)
    
    def test_database_to_csv_file(self):
        """Test converting database query results to a CSV file."""
        db_path = os.path.join(self.temp_dir.name, "test.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("CREATE TABLE test_table (ID INTEGER, Product TEXT, Price REAL)")
        cursor.execute("INSERT INTO test_table VALUES (1, 'Laptop', 1200.50)")
        cursor.execute("INSERT INTO test_table VALUES (2, 'Phone', 800.75)")
        cursor.execute("INSERT INTO test_table VALUES (3, 'Tablet', 350.25)")
        conn.commit()
        conn.close()
        
        csv_path = os.path.join(self.temp_dir.name, "test.csv")
        
        result = self.converter.database_to_csv_file(
            f"sqlite:///{db_path}",
            "SELECT * FROM test_table",
            csv_path
        )
        self.assertTrue(result)
        
        self.assertTrue(os.path.exists(csv_path))
        
        df = pd.read_csv(csv_path)
        
        self.assertEqual(len(df), 3)
        
        self.assertEqual(df.iloc[0]["ID"], 1)
        self.assertEqual(df.iloc[0]["Product"], "Laptop")
        self.assertEqual(df.iloc[0]["Price"], 1200.50)
    
    def test_stream_csv_to_database(self):
        """Test streaming a CSV file to a database."""
        csv_path = os.path.join(self.temp_dir.name, "test.csv")
        pd.DataFrame({
            "Name": ["Alice", "Bob", "Charlie"],
            "Age": [25, 30, 22],
            "Score": [95.5, 85.0, 90.5]
        }).to_csv(csv_path, index=False)
        
        db_path = os.path.join(self.temp_dir.name, "test.db")
        
        result = self.converter.stream_csv_to_database(
            csv_path,
            f"sqlite:///{db_path}",
            "test_table"
        )
        self.assertTrue(result)
        
        self.assertTrue(os.path.exists(db_path))
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM test_table")
        rows = cursor.fetchall()
        conn.close()
        
        self.assertEqual(len(rows), 3)
    
    def test_stream_database_to_csv(self):
        """Test streaming database query results to a CSV file."""
        db_path = os.path.join(self.temp_dir.name, "test.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("CREATE TABLE test_table (ID INTEGER, Value TEXT)")
        
        for i in range(1000):
            cursor.execute(f"INSERT INTO test_table VALUES ({i}, 'Value{i}')")
        
        conn.commit()
        conn.close()
        
        csv_path = os.path.join(self.temp_dir.name, "test.csv")
        
        result = self.converter.stream_database_to_csv(
            f"sqlite:///{db_path}",
            "SELECT * FROM test_table",
            csv_path,
            chunk_size=100
        )
        self.assertTrue(result)
        
        self.assertTrue(os.path.exists(csv_path))
        
        df = pd.read_csv(csv_path)
        
        self.assertEqual(len(df), 1000)
    
    def test_cross_compatibility(self):
        """Test cross-compatibility between CSV and database formats."""
        csv_data = [
            ["ID", "Name", "Value"],
            [1, "Item1", 10.5],
            [2, "Item2", 20.3],
            [3, "Item3", 30.7]
        ]
        
        db_path = os.path.join(self.temp_dir.name, "test.db")
        self.converter.csv_to_database_file(csv_data, db_path)
        
        csv_path = os.path.join(self.temp_dir.name, "test.csv")
        self.converter.database_to_csv_file(
            f"sqlite:///{db_path}",
            "SELECT * FROM csv_data",
            csv_path
        )
        
        df = pd.read_csv(csv_path)
        
        self.assertEqual(len(df), 3)
        
        self.assertEqual(df.iloc[0]["ID"], 1)
        self.assertEqual(df.iloc[0]["Name"], "Item1")
        self.assertEqual(df.iloc[0]["Value"], 10.5)
        
        db_path2 = os.path.join(self.temp_dir.name, "test2.db")
        self.converter.stream_csv_to_database(
            csv_path,
            f"sqlite:///{db_path2}",
            "test_table"
        )
        
        conn = sqlite3.connect(db_path2)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM test_table")
        rows = cursor.fetchall()
        conn.close()
        
        self.assertEqual(len(rows), 3)
        
        self.assertEqual(rows[0][0], 1)
        self.assertEqual(rows[0][1], "Item1")
        self.assertEqual(rows[0][2], 10.5)


if __name__ == "__main__":
    unittest.main()
