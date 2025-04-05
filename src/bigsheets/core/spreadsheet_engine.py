"""
Spreadsheet Engine Module

This module provides the core spreadsheet functionality including:
- Grid organization with multi-sheet support
- Formula and expression evaluation
- Dependency tracking and recalculation
"""

from typing import Dict, List, Any, Optional, Tuple, Union
import numpy as np
import pandas as pd


class Cell:
    """
    Represents a single cell in a spreadsheet with content, formatting, and formula support.
    """
    def __init__(self, value: Any = None, formula: str = None):
        self.value = value
        self.formula = formula
        self.formatting = {}
        self.dependencies = set()
        self.dependents = set()
    
    def __repr__(self) -> str:
        if self.formula:
            return f"Cell(formula='{self.formula}', value={self.value})"
        return f"Cell(value={self.value})"


class Sheet:
    """
    Represents a single sheet/tab in a spreadsheet workbook.
    Manages a grid of cells and provides operations for cell manipulation.
    """
    def __init__(self, name: str, rows: int = 1000, cols: int = 100):
        self.name = name
        self.rows = rows
        self.cols = cols
        self.cells: Dict[Tuple[int, int], Cell] = {}
        self.command_history = []
        self.redo_stack = []
    
    def get_cell(self, row: int, col: int) -> Cell:
        """Get a cell at the specified position, creating it if it doesn't exist."""
        if (row, col) not in self.cells:
            self.cells[(row, col)] = Cell()
        return self.cells[(row, col)]
    
    def set_cell_value(self, row: int, col: int, value: Any, formula: Optional[str] = None) -> None:
        """Set the value and optional formula for a cell."""
        cell = self.get_cell(row, col)
        
        old_value = cell.value
        old_formula = cell.formula
        
        command = {
            'type': 'cell_edit',
            'row': row,
            'col': col,
            'old_value': old_value,
            'new_value': value,
            'old_formula': old_formula,
            'new_formula': formula
        }
        
        cell.value = value
        cell.formula = formula
        
        self.command_history.append(command)
        self.redo_stack.clear()
        
    
    def undo(self) -> bool:
        """Undo the last command in this sheet."""
        if not self.command_history:
            return False
        
        command = self.command_history.pop()
        self.redo_stack.append(command)
        
        if command['type'] == 'cell_edit':
            row, col = command['row'], command['col']
            cell = self.get_cell(row, col)
            cell.value = command['old_value']
            cell.formula = command['old_formula']
        
        
        return True
    
    def redo(self) -> bool:
        """Redo the last undone command in this sheet."""
        if not self.redo_stack:
            return False
        
        command = self.redo_stack.pop()
        self.command_history.append(command)
        
        if command['type'] == 'cell_edit':
            row, col = command['row'], command['col']
            cell = self.get_cell(row, col)
            cell.value = command['new_value']
            cell.formula = command['new_formula']
        elif command['type'] == 'insert_row':
            self._insert_row_impl(command['row'])
        elif command['type'] == 'delete_row':
            self._delete_row_impl(command['row'], command['cells'])
        elif command['type'] == 'insert_column':
            self._insert_column_impl(command['col'])
        elif command['type'] == 'delete_column':
            self._delete_column_impl(command['col'], command['cells'])
        
        return True
        
    def insert_row(self, row: int) -> None:
        """Insert a row at the specified position."""
        command = {
            'type': 'insert_row',
            'row': row
        }
        
        self._insert_row_impl(row)
        
        self.command_history.append(command)
        self.redo_stack.clear()
    
    def _insert_row_impl(self, row: int) -> None:
        """Implementation of row insertion."""
        cells_to_move = {}
        for (r, c), cell in self.cells.items():
            if r >= row:
                cells_to_move[(r + 1, c)] = cell
        
        for (r, c) in list(self.cells.keys()):
            if r >= row:
                del self.cells[(r, c)]
        
        for pos, cell in cells_to_move.items():
            self.cells[pos] = cell
        
        self.rows += 1
    
    def delete_row(self, row: int) -> None:
        """Delete a row at the specified position."""
        deleted_cells = {}
        for (r, c), cell in self.cells.items():
            if r == row:
                deleted_cells[(r, c)] = cell
        
        command = {
            'type': 'delete_row',
            'row': row,
            'cells': deleted_cells
        }
        
        self._delete_row_impl(row, deleted_cells)
        
        self.command_history.append(command)
        self.redo_stack.clear()
    
    def _delete_row_impl(self, row: int, deleted_cells: Dict[Tuple[int, int], Cell]) -> None:
        """Implementation of row deletion."""
        for (r, c) in list(self.cells.keys()):
            if r == row:
                del self.cells[(r, c)]
        
        cells_to_move = {}
        for (r, c), cell in self.cells.items():
            if r > row:
                cells_to_move[(r - 1, c)] = cell
        
        for (r, c) in list(self.cells.keys()):
            if r > row:
                del self.cells[(r, c)]
        
        for pos, cell in cells_to_move.items():
            self.cells[pos] = cell
        
        self.rows -= 1
    
    def insert_column(self, col: int) -> None:
        """Insert a column at the specified position."""
        command = {
            'type': 'insert_column',
            'col': col
        }
        
        self._insert_column_impl(col)
        
        self.command_history.append(command)
        self.redo_stack.clear()
    
    def _insert_column_impl(self, col: int) -> None:
        """Implementation of column insertion."""
        cells_to_move = {}
        for (r, c), cell in self.cells.items():
            if c >= col:
                cells_to_move[(r, c + 1)] = cell
        
        for (r, c) in list(self.cells.keys()):
            if c >= col:
                del self.cells[(r, c)]
        
        for pos, cell in cells_to_move.items():
            self.cells[pos] = cell
        
        self.cols += 1
    
    def delete_column(self, col: int) -> None:
        """Delete a column at the specified position."""
        deleted_cells = {}
        for (r, c), cell in self.cells.items():
            if c == col:
                deleted_cells[(r, c)] = cell
        
        command = {
            'type': 'delete_column',
            'col': col,
            'cells': deleted_cells
        }
        
        self._delete_column_impl(col, deleted_cells)
        
        self.command_history.append(command)
        self.redo_stack.clear()
    
    def _delete_column_impl(self, col: int, deleted_cells: Dict[Tuple[int, int], Cell]) -> None:
        """Implementation of column deletion."""
        for (r, c) in list(self.cells.keys()):
            if c == col:
                del self.cells[(r, c)]
        
        cells_to_move = {}
        for (r, c), cell in self.cells.items():
            if c > col:
                cells_to_move[(r, c - 1)] = cell
        
        for (r, c) in list(self.cells.keys()):
            if c > col:
                del self.cells[(r, c)]
        
        for pos, cell in cells_to_move.items():
            self.cells[pos] = cell
        
        self.cols -= 1
    
    def add_chart(self, chart: Dict[str, Any], row: int, col: int) -> None:
        """Add a chart to the sheet at the specified position."""
        command = {
            'type': 'add_chart',
            'row': row,
            'col': col,
            'chart': chart
        }
        
        cell = self.get_cell(row, col)
        cell.chart = chart
        
        self.command_history.append(command)
        self.redo_stack.clear()
    
    def add_image(self, image_data: Dict[str, Any], row: int, col: int) -> None:
        """Add an image to the sheet at the specified position."""
        command = {
            'type': 'add_image',
            'row': row,
            'col': col,
            'image_data': image_data
        }
        
        cell = self.get_cell(row, col)
        cell.image = image_data
        
        self.command_history.append(command)
        self.redo_stack.clear()


class Workbook:
    """
    Represents a workbook containing multiple sheets/tabs.
    """
    def __init__(self):
        self.sheets: Dict[str, Sheet] = {}
        self.active_sheet: Optional[str] = None
    
    def create_sheet(self, name: str) -> Sheet:
        """Create a new sheet with the given name."""
        if name in self.sheets:
            raise ValueError(f"Sheet '{name}' already exists")
        
        sheet = Sheet(name)
        self.sheets[name] = sheet
        
        if self.active_sheet is None:
            self.active_sheet = name
        
        return sheet
    
    def get_sheet(self, name: str) -> Sheet:
        """Get a sheet by name."""
        if name not in self.sheets:
            raise ValueError(f"Sheet '{name}' does not exist")
        return self.sheets[name]
    
    def get_active_sheet(self) -> Sheet:
        """Get the currently active sheet."""
        if self.active_sheet is None:
            raise ValueError("No active sheet")
        return self.sheets[self.active_sheet]
    
    def set_active_sheet(self, name: str) -> None:
        """Set the active sheet by name."""
        if name not in self.sheets:
            raise ValueError(f"Sheet '{name}' does not exist")
        self.active_sheet = name
