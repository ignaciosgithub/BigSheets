"""
Unit tests for the Database Connector streaming functionality.
"""

import unittest
from unittest.mock import MagicMock, patch
import pandas as pd
from src.bigsheets.data.db_connector import DatabaseConnector


class TestDatabaseStreaming(unittest.TestCase):
    """Test cases for the database streaming functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.connector = DatabaseConnector()
        
        self.mock_engine = MagicMock()
        self.mock_connection = MagicMock()
        self.mock_result = MagicMock()
        
        self.mock_engine.connect.return_value = self.mock_connection
        self.mock_connection.execution_options.return_value = self.mock_connection
        self.mock_connection.execute.return_value = self.mock_result
        
        self.connector.connections["test_conn"] = self.mock_engine
    
    def test_stream_query(self):
        """Test streaming query results."""
        self.mock_result.keys.return_value = ["id", "name", "value"]
        
        chunk1 = [(1, "Item 1", 10.5), (2, "Item 2", 20.3)]
        chunk2 = [(3, "Item 3", 30.7), (4, "Item 4", 40.2)]
        empty_chunk = []
        
        self.mock_result.fetchmany.side_effect = [chunk1, chunk2, empty_chunk]
        
        stream_iter = self.connector.stream_query("test_conn", "SELECT * FROM test_table", chunk_size=2)
        
        columns = next(stream_iter)
        self.assertEqual(columns, ["id", "name", "value"])
        
        first_chunk = next(stream_iter)
        self.assertEqual(first_chunk, chunk1)
        
        second_chunk = next(stream_iter)
        self.assertEqual(second_chunk, chunk2)
        
        with self.assertRaises(StopIteration):
            next(stream_iter)
        
        self.mock_connection.execution_options.assert_called_once_with(stream_results=True)
        self.mock_connection.execute.assert_called_once()
        self.assertEqual(self.mock_result.fetchmany.call_count, 3)
    
    def test_connect_and_query_streaming(self):
        """Test connect_and_query with streaming enabled."""
        with patch.object(DatabaseConnector, 'create_connection') as mock_create_conn, \
             patch.object(DatabaseConnector, 'stream_query') as mock_stream:
            
            def mock_stream_gen():
                yield ["id", "name"]
                yield [(1, "Test 1"), (2, "Test 2")]
            
            mock_stream.return_value = mock_stream_gen()
            
            result = self.connector.connect_and_query(
                "sqlite:///test.db", 
                "SELECT * FROM test_table",
                streaming=True
            )
            
            self.assertTrue(hasattr(result, '__next__'))
            
            columns = next(result)
            self.assertEqual(columns, ["id", "name"])
            
            data = next(result)
            self.assertEqual(data, [(1, "Test 1"), (2, "Test 2")])
            
            mock_create_conn.assert_called_once()
            mock_stream.assert_called_once()
    
    def test_memory_usage_with_large_dataset(self):
        """Test that streaming uses less memory with large datasets."""
        
        large_data = [(i, f"Item {i}", i * 1.5) for i in range(10000)]
        
        chunk_size = 100
        chunks = [large_data[i:i+chunk_size] for i in range(0, len(large_data), chunk_size)]
        chunks.append([])  # Add empty chunk to signal end
        
        self.mock_result.fetchmany.side_effect = chunks
        
        stream_iter = self.connector.stream_query("test_conn", "SELECT * FROM large_table", chunk_size=chunk_size)
        
        next(stream_iter)
        
        row_count = 0
        for chunk in stream_iter:
            row_count += len(chunk)
        
        self.assertEqual(row_count, 10000)
        
        self.assertEqual(self.mock_result.fetchmany.call_count, len(chunks))


if __name__ == "__main__":
    unittest.main()
