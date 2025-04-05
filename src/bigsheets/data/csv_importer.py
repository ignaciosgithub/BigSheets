"""
CSV Importer Module

This module provides functionality for importing CSV files with various
configurations and options.
"""

import csv
import io
from typing import List, Dict, Any, Optional, Union, Tuple
import pandas as pd


class CSVImporter:
    """
    Handles importing CSV files with various configurations.
    """
    
    def __init__(self):
        """Initialize the CSV importer."""
        self.default_options = {
            'delimiter': ',',
            'has_header': True,
            'encoding': 'utf-8',
            'quotechar': '"',
            'skip_rows': 0
        }
        
    def import_csv(self, file_path: str, **options) -> List[List[Any]]:
        """
        Import a CSV file and return the data as a list of lists.
        
        Args:
            file_path: Path to the CSV file
            **options: Additional options to override defaults
            
        Returns:
            List of lists containing the CSV data
        """
        opts = {**self.default_options, **options}
        
        df = self.parse_csv(
            file_path,
            delimiter=opts['delimiter'],
            has_header=opts['has_header'],
            encoding=opts['encoding'],
            quotechar=opts['quotechar'],
            skip_rows=opts['skip_rows']
        )
        
        data = df.values.tolist()
        
        if opts['has_header']:
            data.insert(0, df.columns.tolist())
        
        return data
    
    def parse_csv(self, file_path: str, delimiter: str = ',', 
                 has_header: bool = True, encoding: str = 'utf-8',
                 quotechar: str = '"', skip_rows: int = 0) -> pd.DataFrame:
        """
        Parse a CSV file and return the data as a pandas DataFrame.
        
        Args:
            file_path: Path to the CSV file
            delimiter: Character used to separate fields
            has_header: Whether the first row contains column names
            encoding: File encoding
            quotechar: Character used for quoting fields
            skip_rows: Number of rows to skip at the beginning
            
        Returns:
            DataFrame containing the CSV data
        """
        try:
            header = 0 if has_header else None
            
            df = pd.read_csv(
                file_path,
                delimiter=delimiter,
                header=header,
                encoding=encoding,
                quotechar=quotechar,
                skiprows=skip_rows
            )
            
            return df
        except Exception as e:
            raise ValueError(f"Error parsing CSV file: {str(e)}")
    
    def infer_column_types(self, df: pd.DataFrame) -> Dict[str, str]:
        """
        Infer the data types of columns in a DataFrame.
        
        Args:
            df: DataFrame to analyze
            
        Returns:
            Dictionary mapping column names to inferred types
        """
        type_mapping = {}
        
        for column in df.columns:
            if pd.api.types.is_numeric_dtype(df[column]):
                if pd.api.types.is_integer_dtype(df[column]):
                    type_mapping[column] = 'integer'
                else:
                    type_mapping[column] = 'float'
            elif pd.api.types.is_datetime64_dtype(df[column]):
                type_mapping[column] = 'datetime'
            elif pd.api.types.is_bool_dtype(df[column]):
                type_mapping[column] = 'boolean'
            else:
                type_mapping[column] = 'string'
        
        return type_mapping
    
    def preview_csv(self, file_path: str, max_rows: int = 10, **kwargs) -> Tuple[pd.DataFrame, Dict[str, str]]:
        """
        Preview a CSV file and infer column types.
        
        Args:
            file_path: Path to the CSV file
            max_rows: Maximum number of rows to preview
            **kwargs: Additional arguments to pass to parse_csv
            
        Returns:
            Tuple of (preview DataFrame, column type mapping)
        """
        df = self.parse_csv(file_path, **kwargs)
        preview_df = df.head(max_rows)
        column_types = self.infer_column_types(df)
        
        return preview_df, column_types
