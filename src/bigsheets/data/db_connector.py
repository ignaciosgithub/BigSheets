"""
Database Connector Module

This module provides connectivity to various SQL and NoSQL databases.
"""

from typing import Dict, List, Any, Optional, Union, Tuple, Iterator
import sqlalchemy
from sqlalchemy import create_engine, text
import pandas as pd


class DatabaseConnector:
    """
    Provides connectivity to various database systems.
    """
    
    def __init__(self):
        """Initialize the database connector."""
        self.connections = {}  # Store active connections
        
    def connect_and_query(self, connection_string: str, query: str = None, 
                        streaming: bool = False, chunk_size: int = 1000) -> Union[List[List[Any]], Iterator[List[Any]]]:
        """
        Connect to a database and execute a query.
        
        Args:
            connection_string: SQLAlchemy connection string
            query: SQL query to execute (optional)
            streaming: Whether to return a streaming iterator instead of loading all data at once
            chunk_size: Number of rows to fetch at a time when streaming
            
        Returns:
            Either a list of lists containing all query results, or an iterator yielding chunks of results
        """
        connection_id = f"conn_{len(self.connections) + 1}"
        
        try:
            self.create_connection(connection_id, connection_string)
            
            if not query:
                tables = self.list_tables(connection_id)
                if not tables:
                    return [["No tables found in database"]]
                
                first_table = tables[0]
                query = f"SELECT * FROM {first_table} LIMIT 100"
            
            if streaming:
                return self.stream_query(connection_id, query, chunk_size=chunk_size)
            else:
                df = self.execute_query(connection_id, query)
                
                data = df.values.tolist()
                
                if not df.empty:
                    data.insert(0, df.columns.tolist())
                
                self.close_connection(connection_id)
                
                return data
        except Exception as e:
            if connection_id in self.connections:
                self.close_connection(connection_id)
            
            return [[f"Error: {str(e)}"]]
            
    def stream_query(self, connection_id: str, query: str, 
                    params: Optional[Dict[str, Any]] = None,
                    chunk_size: int = 1000):
        """
        Execute a SQL query and return a generator that yields chunks of results.
        This allows processing large datasets without loading everything into memory.
        
        Args:
            connection_id: Identifier for the connection to use
            query: SQL query to execute
            params: Parameters to bind to the query
            chunk_size: Number of rows to fetch at a time
            
        Yields:
            Lists of rows, with each list containing up to chunk_size rows
        """
        if connection_id not in self.connections:
            raise ValueError(f"Connection '{connection_id}' does not exist")
        
        engine = self.connections[connection_id]
        connection = None
        
        try:
            connection = engine.connect()
            connection = connection.execution_options(stream_results=True)
            
            if params:
                result = connection.execute(text(query), params)
            else:
                result = connection.execute(text(query))
            
            columns = result.keys()
            
            yield columns
            
            while True:
                chunk = result.fetchmany(chunk_size)
                if not chunk:
                    break
                
                yield chunk
                
        except Exception as e:
            raise RuntimeError(f"Error streaming query: {str(e)}")
        finally:
            if connection:
                connection.close()
    
    def create_connection(self, connection_id: str, connection_string: str) -> None:
        """
        Create a database connection.
        
        Args:
            connection_id: Identifier for this connection
            connection_string: SQLAlchemy connection string
        """
        try:
            engine = create_engine(connection_string)
            self.connections[connection_id] = engine
        except Exception as e:
            raise ConnectionError(f"Failed to connect to database: {str(e)}")
    
    def close_connection(self, connection_id: str) -> None:
        """
        Close a database connection.
        
        Args:
            connection_id: Identifier for the connection to close
        """
        if connection_id in self.connections:
            self.connections[connection_id].dispose()
            del self.connections[connection_id]
    
    def execute_query(self, connection_id: str, query: str, 
                     params: Optional[Dict[str, Any]] = None,
                     chunk_size: int = 1000) -> pd.DataFrame:
        """
        Execute a SQL query and return the results as a DataFrame.
        
        Args:
            connection_id: Identifier for the connection to use
            query: SQL query to execute
            params: Parameters to bind to the query
            chunk_size: Number of rows to fetch at a time (for streaming)
            
        Returns:
            DataFrame containing the query results
        """
        if connection_id not in self.connections:
            raise ValueError(f"Connection '{connection_id}' does not exist")
        
        engine = self.connections[connection_id]
        
        try:
            with engine.connect() as conn:
                if params:
                    result = conn.execution_options(stream_results=True).execute(text(query), params)
                else:
                    result = conn.execution_options(stream_results=True).execute(text(query))
                
                columns = result.keys()
                
                df = pd.DataFrame(columns=columns)
                
                while True:
                    chunk = result.fetchmany(chunk_size)
                    if not chunk:
                        break
                    
                    chunk_df = pd.DataFrame(chunk, columns=columns)
                    df = pd.concat([df, chunk_df], ignore_index=True)
                
                return df
        except Exception as e:
            raise RuntimeError(f"Error executing query: {str(e)}")
    
    def list_tables(self, connection_id: str) -> List[str]:
        """
        List all tables in the connected database.
        
        Args:
            connection_id: Identifier for the connection to use
            
        Returns:
            List of table names
        """
        if connection_id not in self.connections:
            raise ValueError(f"Connection '{connection_id}' does not exist")
        
        engine = self.connections[connection_id]
        
        try:
            inspector = sqlalchemy.inspect(engine)
            return inspector.get_table_names()
        except Exception as e:
            raise RuntimeError(f"Error listing tables: {str(e)}")
    
    def get_table_schema(self, connection_id: str, table_name: str) -> List[Dict[str, Any]]:
        """
        Get the schema for a table.
        
        Args:
            connection_id: Identifier for the connection to use
            table_name: Name of the table
            
        Returns:
            List of column definitions
        """
        if connection_id not in self.connections:
            raise ValueError(f"Connection '{connection_id}' does not exist")
        
        engine = self.connections[connection_id]
        
        try:
            inspector = sqlalchemy.inspect(engine)
            return inspector.get_columns(table_name)
        except Exception as e:
            raise RuntimeError(f"Error getting table schema: {str(e)}")
