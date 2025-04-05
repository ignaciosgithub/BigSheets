"""
Data Converter Module

This module provides functionality for converting between different data formats,
particularly between CSV and database data.
"""

from typing import List, Dict, Any, Optional, Union, Tuple, Iterator
import pandas as pd
import sqlalchemy
from sqlalchemy import Table, Column, MetaData, create_engine, text
import tempfile
import os


class DataConverter:
    """
    Handles conversion between different data formats.
    """
    
    def __init__(self):
        """Initialize the data converter."""
        pass
    
    def csv_to_dataframe(self, csv_data: List[List[Any]]) -> pd.DataFrame:
        """
        Convert CSV data (list of lists) to a pandas DataFrame.
        
        Args:
            csv_data: CSV data as a list of lists, with the first row optionally containing headers
            
        Returns:
            DataFrame representation of the CSV data
        """
        if not csv_data:
            return pd.DataFrame()
        
        if isinstance(csv_data[0][0], str) and all(isinstance(item, str) for item in csv_data[0]):
            headers = csv_data[0]
            data = csv_data[1:]
            df = pd.DataFrame(data, columns=headers)
        else:
            df = pd.DataFrame(csv_data)
        
        return df
    
    def dataframe_to_csv(self, df: pd.DataFrame, include_headers: bool = True) -> List[List[Any]]:
        """
        Convert a pandas DataFrame to CSV data (list of lists).
        
        Args:
            df: DataFrame to convert
            include_headers: Whether to include column names as the first row
            
        Returns:
            CSV data as a list of lists
        """
        data = df.values.tolist()
        
        if include_headers and not df.empty:
            data.insert(0, df.columns.tolist())
        
        return data
    
    def database_to_dataframe(self, db_data: List[List[Any]]) -> pd.DataFrame:
        """
        Convert database query results to a pandas DataFrame.
        
        Args:
            db_data: Database data as a list of lists, with the first row containing column names
            
        Returns:
            DataFrame representation of the database data
        """
        if not db_data or len(db_data) < 2:
            return pd.DataFrame()
        
        headers = db_data[0]
        data = db_data[1:]
        
        df = pd.DataFrame(data, columns=headers)
        return df
    
    def dataframe_to_database(self, df: pd.DataFrame, table_name: str, 
                             connection_string: str) -> bool:
        """
        Convert a DataFrame to a database table.
        
        Args:
            df: DataFrame to convert
            table_name: Name of the table to create
            connection_string: SQLAlchemy connection string
            
        Returns:
            True if successful, False otherwise
        """
        try:
            engine = create_engine(connection_string)
            df.to_sql(table_name, engine, if_exists='replace', index=False)
            return True
        except Exception as e:
            print(f"Error converting DataFrame to database: {str(e)}")
            return False
    
    def csv_to_database(self, csv_data: List[List[Any]], table_name: str, 
                       connection_string: str) -> bool:
        """
        Convert CSV data directly to a database table.
        
        Args:
            csv_data: CSV data as a list of lists
            table_name: Name of the table to create
            connection_string: SQLAlchemy connection string
            
        Returns:
            True if successful, False otherwise
        """
        df = self.csv_to_dataframe(csv_data)
        return self.dataframe_to_database(df, table_name, connection_string)
    
    def database_to_csv(self, db_data: List[List[Any]]) -> List[List[Any]]:
        """
        Convert database query results to CSV format.
        
        Args:
            db_data: Database data as a list of lists
            
        Returns:
            CSV data as a list of lists
        """
        return db_data
    
    def csv_to_database_file(self, csv_data: List[List[Any]], db_file_path: str, 
                            table_name: str = "csv_data") -> bool:
        """
        Convert CSV data to a SQLite database file.
        
        Args:
            csv_data: CSV data as a list of lists
            db_file_path: Path where the SQLite database file should be created
            table_name: Name of the table to create
            
        Returns:
            True if successful, False otherwise
        """
        connection_string = f"sqlite:///{db_file_path}"
        return self.csv_to_database(csv_data, table_name, connection_string)
    
    def database_to_csv_file(self, connection_string: str, query: str, 
                            csv_file_path: str) -> bool:
        """
        Convert database query results to a CSV file.
        
        Args:
            connection_string: SQLAlchemy connection string
            query: SQL query to execute
            csv_file_path: Path where the CSV file should be created
            
        Returns:
            True if successful, False otherwise
        """
        try:
            engine = create_engine(connection_string)
            
            with engine.connect() as conn:
                result = conn.execute(text(query))
                df = pd.DataFrame(result.fetchall())
                
                if df.shape[0] > 0:
                    df.columns = result.keys()
                
                df.to_csv(csv_file_path, index=False)
                return True
        except Exception as e:
            print(f"Error converting database to CSV file: {str(e)}")
            return False
    
    def stream_database_to_csv(self, connection_string: str, query: str, 
                              csv_file_path: str, chunk_size: int = 1000) -> bool:
        """
        Stream database query results to a CSV file without loading everything into memory.
        
        Args:
            connection_string: SQLAlchemy connection string
            query: SQL query to execute
            csv_file_path: Path where the CSV file should be created
            chunk_size: Number of rows to process at a time
            
        Returns:
            True if successful, False otherwise
        """
        try:
            engine = create_engine(connection_string)
            
            with engine.connect() as conn:
                conn = conn.execution_options(stream_results=True)
                result = conn.execute(text(query))
                
                columns = result.keys()
                
                with open(csv_file_path, 'w', newline='') as f:
                    f.write(','.join(columns) + '\n')
                    
                    while True:
                        chunk = result.fetchmany(chunk_size)
                        if not chunk:
                            break
                        
                        chunk_df = pd.DataFrame(chunk, columns=columns)
                        
                        chunk_df.to_csv(f, index=False, header=False, mode='a')
                
                return True
        except Exception as e:
            print(f"Error streaming database to CSV file: {str(e)}")
            return False
    
    def stream_csv_to_database(self, csv_file_path: str, connection_string: str, 
                              table_name: str, chunk_size: int = 1000) -> bool:
        """
        Stream a CSV file to a database table without loading everything into memory.
        
        Args:
            csv_file_path: Path to the CSV file
            connection_string: SQLAlchemy connection string
            table_name: Name of the table to create
            chunk_size: Number of rows to process at a time
            
        Returns:
            True if successful, False otherwise
        """
        try:
            engine = create_engine(connection_string)
            
            csv_iter = pd.read_csv(csv_file_path, chunksize=chunk_size)
            
            for i, chunk_df in enumerate(csv_iter):
                if i == 0:
                    chunk_df.to_sql(table_name, engine, if_exists='replace', index=False)
                else:
                    chunk_df.to_sql(table_name, engine, if_exists='append', index=False)
            
            return True
        except Exception as e:
            print(f"Error streaming CSV to database: {str(e)}")
            return False
