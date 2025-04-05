"""
BigSheets API - Main Module

This module provides the FastAPI application entry point and defines the API routes.
"""

from fastapi import FastAPI, HTTPException, Depends, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import uvicorn
import json
import os
from datetime import datetime

from bigsheets.core.spreadsheet_engine import Workbook, Sheet, Cell
from bigsheets.core.command_manager import CommandManager
from bigsheets.data.csv_importer import CSVImporter
from bigsheets.data.db_connector import DatabaseConnector

app = FastAPI(
    title="BigSheets API",
    description="API for BigSheets - A next-generation spreadsheet application",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

workbooks = {}
command_manager = CommandManager()

class CellData(BaseModel):
    value: Any = None
    formula: Optional[str] = None
    formatting: Dict[str, Any] = Field(default_factory=dict)

class SheetData(BaseModel):
    name: str
    cells: Dict[str, CellData] = Field(default_factory=dict)

class WorkbookData(BaseModel):
    name: str
    sheets: List[SheetData] = Field(default_factory=list)
    active_sheet: Optional[str] = None

class CSVImportOptions(BaseModel):
    delimiter: str = ','
    has_header: bool = True
    encoding: str = 'utf-8'
    quotechar: str = '"'
    skip_rows: int = 0

class DatabaseConnectionInfo(BaseModel):
    connection_string: str
    query: Optional[str] = None

@app.get("/")
async def root():
    """Root endpoint providing API information."""
    return {
        "message": "Welcome to BigSheets API",
        "version": "0.1.0",
        "documentation": "/docs"
    }

@app.get("/workbooks", response_model=List[str])
async def list_workbooks():
    """List all available workbooks."""
    return list(workbooks.keys())

@app.post("/workbooks", response_model=str)
async def create_workbook(name: str = Body(..., embed=True)):
    """Create a new workbook."""
    if name in workbooks:
        raise HTTPException(status_code=400, detail=f"Workbook '{name}' already exists")
    
    workbook = Workbook()
    workbook.create_sheet("Sheet1")  # Create default sheet
    workbooks[name] = workbook
    
    return name

@app.get("/workbooks/{workbook_name}", response_model=WorkbookData)
async def get_workbook(workbook_name: str):
    """Get workbook details."""
    if workbook_name not in workbooks:
        raise HTTPException(status_code=404, detail=f"Workbook '{workbook_name}' not found")
    
    workbook = workbooks[workbook_name]
    sheets_data = []
    
    for sheet_name, sheet in workbook.sheets.items():
        cells_data = {}
        for (row, col), cell in sheet.cells.items():
            cell_key = f"{row},{col}"
            cells_data[cell_key] = {
                "value": cell.value,
                "formula": cell.formula,
                "formatting": cell.formatting
            }
        
        sheets_data.append({
            "name": sheet_name,
            "cells": cells_data
        })
    
    return {
        "name": workbook_name,
        "sheets": sheets_data,
        "active_sheet": workbook.active_sheet
    }

@app.post("/workbooks/{workbook_name}/sheets")
async def create_sheet(workbook_name: str, sheet_name: str = Body(..., embed=True)):
    """Create a new sheet in a workbook."""
    if workbook_name not in workbooks:
        raise HTTPException(status_code=404, detail=f"Workbook '{workbook_name}' not found")
    
    workbook = workbooks[workbook_name]
    
    try:
        sheet = workbook.create_sheet(sheet_name)
        return {"message": f"Sheet '{sheet_name}' created successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/workbooks/{workbook_name}/sheets/{sheet_name}/cells/{row}/{col}")
async def update_cell(
    workbook_name: str, 
    sheet_name: str, 
    row: int, 
    col: int, 
    cell_data: CellData
):
    """Update a cell in a sheet."""
    if workbook_name not in workbooks:
        raise HTTPException(status_code=404, detail=f"Workbook '{workbook_name}' not found")
    
    workbook = workbooks[workbook_name]
    
    try:
        sheet = workbook.get_sheet(sheet_name)
        sheet.set_cell_value(row, col, cell_data.value, cell_data.formula)
        
        if cell_data.formatting:
            cell = sheet.get_cell(row, col)
            cell.formatting = cell_data.formatting
        
        return {"message": f"Cell ({row}, {col}) updated successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/workbooks/{workbook_name}/sheets/{sheet_name}/undo")
async def undo_action(workbook_name: str, sheet_name: str):
    """Undo the last action in a sheet."""
    if workbook_name not in workbooks:
        raise HTTPException(status_code=404, detail=f"Workbook '{workbook_name}' not found")
    
    workbook = workbooks[workbook_name]
    
    try:
        sheet = workbook.get_sheet(sheet_name)
        if sheet.undo():
            return {"message": "Undo successful"}
        else:
            return {"message": "Nothing to undo"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/workbooks/{workbook_name}/sheets/{sheet_name}/redo")
async def redo_action(workbook_name: str, sheet_name: str):
    """Redo the last undone action in a sheet."""
    if workbook_name not in workbooks:
        raise HTTPException(status_code=404, detail=f"Workbook '{workbook_name}' not found")
    
    workbook = workbooks[workbook_name]
    
    try:
        sheet = workbook.get_sheet(sheet_name)
        if sheet.redo():
            return {"message": "Redo successful"}
        else:
            return {"message": "Nothing to redo"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/import/csv")
async def import_csv(
    file_path: str = Body(...),
    options: CSVImportOptions = Body(CSVImportOptions())
):
    """Import data from a CSV file."""
    try:
        csv_importer = CSVImporter()
        df, column_types = csv_importer.preview_csv(
            file_path,
            delimiter=options.delimiter,
            has_header=options.has_header,
            encoding=options.encoding,
            quotechar=options.quotechar,
            skip_rows=options.skip_rows
        )
        
        preview_data = df.to_dict(orient="records")
        
        return {
            "preview": preview_data,
            "column_types": column_types,
            "total_rows": len(df),
            "total_columns": len(df.columns)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/import/database")
async def import_database(connection_info: DatabaseConnectionInfo):
    """Import data from a database."""
    try:
        db_connector = DatabaseConnector()
        connection_id = f"conn_{datetime.now().timestamp()}"
        
        db_connector.create_connection(connection_id, connection_info.connection_string)
        
        if connection_info.query:
            df = db_connector.execute_query(connection_id, connection_info.query)
            result_data = df.to_dict(orient="records")
            
            db_connector.close_connection(connection_id)
            
            return {
                "data": result_data,
                "total_rows": len(df),
                "total_columns": len(df.columns) if len(df) > 0 else 0
            }
        else:
            tables = db_connector.list_tables(connection_id)
            
            db_connector.close_connection(connection_id)
            
            return {
                "tables": tables
            }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
