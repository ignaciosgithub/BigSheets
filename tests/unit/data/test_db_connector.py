"""
Unit tests for the Database Connector module.
"""

import unittest
import os
import tempfile
import pandas as pd
import sqlite3
from src.bigsheets.data.db_connector import DatabaseConnector


class TestDatabaseConnector(unittest.TestCase):
    """Test cases for the DatabaseConnector class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.connector = DatabaseConnector()
        
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_db_path = os.path.join(self.temp_dir.name, "test_db.sqlite")
        
        self.conn = sqlite3.connect(self.test_db_path)
        cursor = self.conn.cursor()
        
        cursor.execute('''
        CREATE TABLE employees (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            age INTEGER,
            department TEXT
        )
        ''')
        
        test_data = [
            (1, "John Doe", 30, "Engineering"),
            (2, "Jane Smith", 28, "Marketing"),
            (3, "Bob Johnson", 35, "Finance"),
            (4, "Alice Brown", 32, "Engineering")
        ]
        
        cursor.executemany(
            "INSERT INTO employees (id, name, age, department) VALUES (?, ?, ?, ?)",
            test_data
        )
        
        self.conn.commit()
        
        self.connection_string = f"sqlite:///{self.test_db_path}"
    
    def tearDown(self):
        """Clean up test fixtures."""
        self.conn.close()
        self.temp_dir.cleanup()
    
    def test_create_connection(self):
        """Test creating a database connection."""
        connection_id = "test_conn"
        self.connector.create_connection(connection_id, self.connection_string)
        
        self.assertIn(connection_id, self.connector.connections)
        
        self.connector.close_connection(connection_id)
    
    def test_execute_query(self):
        """Test executing a SQL query."""
        connection_id = "test_conn"
        self.connector.create_connection(connection_id, self.connection_string)
        
        query = "SELECT * FROM employees ORDER BY id"
        df = self.connector.execute_query(connection_id, query)
        
        self.assertEqual(len(df), 4)  # 4 data rows
        self.assertEqual(list(df.columns), ["id", "name", "age", "department"])
        self.assertEqual(df.iloc[0]["name"], "John Doe")
        self.assertEqual(df.iloc[1]["age"], 28)
        self.assertEqual(df.iloc[2]["department"], "Finance")
        
        self.connector.close_connection(connection_id)
    
    def test_list_tables(self):
        """Test listing tables in a database."""
        connection_id = "test_conn"
        self.connector.create_connection(connection_id, self.connection_string)
        
        tables = self.connector.list_tables(connection_id)
        
        self.assertIn("employees", tables)
        
        self.connector.close_connection(connection_id)
    
    def test_get_table_schema(self):
        """Test getting a table schema."""
        connection_id = "test_conn"
        self.connector.create_connection(connection_id, self.connection_string)
        
        schema = self.connector.get_table_schema(connection_id, "employees")
        
        column_names = [col["name"] for col in schema]
        self.assertIn("id", column_names)
        self.assertIn("name", column_names)
        self.assertIn("age", column_names)
        self.assertIn("department", column_names)
        
        self.connector.close_connection(connection_id)
    
    def test_connect_and_query(self):
        """Test connecting to a database and executing a query."""
        data = self.connector.connect_and_query(self.connection_string)
        
        self.assertTrue(len(data) > 0)  # At least header row
        
        self.assertIn("id", data[0])
        self.assertIn("name", data[0])
        self.assertIn("age", data[0])
        self.assertIn("department", data[0])
        
        self.assertEqual(data[1][0], 1)  # id
        self.assertEqual(data[1][1], "John Doe")  # name


if __name__ == "__main__":
    unittest.main()
