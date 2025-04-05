"""
BigSheets API - Models Module

This module defines the Pydantic models used for request/response validation.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union


class CellData(BaseModel):
    """Model representing a cell's data."""
    value: Any = None
    formula: Optional[str] = None
    formatting: Dict[str, Any] = Field(default_factory=dict)


class SheetData(BaseModel):
    """Model representing a sheet's data."""
    name: str
    cells: Dict[str, CellData] = Field(default_factory=dict)


class WorkbookData(BaseModel):
    """Model representing a workbook's data."""
    name: str
    sheets: List[SheetData] = Field(default_factory=list)
    active_sheet: Optional[str] = None


class CSVImportOptions(BaseModel):
    """Model for CSV import options."""
    delimiter: str = ','
    has_header: bool = True
    encoding: str = 'utf-8'
    quotechar: str = '"'
    skip_rows: int = 0


class DatabaseConnectionInfo(BaseModel):
    """Model for database connection information."""
    connection_string: str
    query: Optional[str] = None


class GraphData(BaseModel):
    """Model for graph data."""
    type: str  # bar, line, scatter, pie
    title: str
    data: List[Dict[str, Any]]
    options: Dict[str, Any] = Field(default_factory=dict)


class ImageData(BaseModel):
    """Model for image data."""
    url: str
    position: Dict[str, int]  # x, y coordinates
    size: Dict[str, int]  # width, height
    anchor_cell: Optional[str] = None  # e.g., "A1"
