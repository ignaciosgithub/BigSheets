"""
Database Connector Module

This module provides connectivity to various SQL and NoSQL databases.
"""

from typing import Dict, List, Any, Optional, Union, Tuple
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
                     params: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        """
        Execute a SQL query and return the results as a DataFrame.
        
        Args:
            connection_id: Identifier for the connection to use
            query: SQL query to execute
            params: Parameters to bind to the query
            
        Returns:
            DataFrame containing the query results
        """
        if connection_id not in self.connections:
            raise ValueError(f"Connection '{connection_id}' does not exist")
        
        engine = self.connections[connection_id]
        
        try:
            with engine.connect() as conn:
                if params:
                    result = conn.execute(text(query), params)
                else:
                    result = conn.execute(text(query))
                
                df = pd.DataFrame(result.fetchall())
                if df.shape[0] > 0:
                    df.columns = result.keys()
                
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
