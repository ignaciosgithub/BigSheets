"""
Spreadsheet Engine Module

This module provides the core spreadsheet functionality including:
- Grid organization with multi-sheet support
- Formula and expression evaluation
- Dependency tracking and recalculation
"""

from typing import Dict, List, Any, Optional, Tuple, Union, Callable, Awaitable
import numpy as np
import pandas as pd
import asyncio
from bigsheets.core.command_manager import CommandManager, CellEditCommand, Command


class Cell:
    """
    Represents a single cell in a spreadsheet with content, formatting, and formula support.
    """
    def __init__(self, value: Any = None, formula: Optional[str] = None):
        self.value = value
        self.formula = formula
        self.formatting = {}
        self.dependencies = set()  # Cells that this cell depends on for its value
        self.dependents = set()    # Cells that depend on this cell's value
        self.function_id = None    # Store reference to function template
        self.function_result = None  # Store the result of function execution
        self.source_cells = []     # Store source cell ranges for persistent functions
    
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
        self.command_manager = CommandManager()
    
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
        
        def update_cell(sheet_id, row, col, value, formula):
            cell = self.get_cell(row, col)
            cell.value = value
            cell.formula = formula
            
            self._update_dependent_cells(row, col)
        
        command = CellEditCommand(
            sheet_id=self.name,
            row=row,
            col=col,
            old_value=old_value,
            new_value=value,
            old_formula=old_formula,
            new_formula=formula,
            update_cell_func=update_cell
        )
        
        self.command_manager.execute_command(self.name, command)
    
    def undo(self) -> bool:
        """Undo the last command in this sheet."""
        return self.command_manager.undo(self.name)
    
    def redo(self) -> bool:
        """Redo the last undone command in this sheet."""
        return self.command_manager.redo(self.name)
        
    def _update_dependent_cells(self, row: int, col: int) -> None:
        """Update all cells that depend on the specified cell."""
        cell = self.get_cell(row, col)
        
        for dependent_row, dependent_col in cell.dependents:
            dependent_cell = self.get_cell(dependent_row, dependent_col)
            
            if dependent_cell.function_id is not None:
                if hasattr(dependent_cell, 'source_cells') and dependent_cell.source_cells:
                    selected_data = []
                    for src_row_range, src_col_range in dependent_cell.source_cells:
                        data = []
                        for r in range(src_row_range[0], src_row_range[1] + 1):
                            row_data = []
                            for c in range(src_col_range[0], src_col_range[1] + 1):
                                src_cell = self.get_cell(r, c)
                                try:
                                    value = float(src_cell.value) if src_cell.value is not None else 0.0
                                except (ValueError, TypeError):
                                    value = 0.0
                                row_data.append(value)
                            data.append(row_data)
                        selected_data.append(data)
                    
                    self.execute_function(dependent_row, dependent_col, dependent_cell.function_id, selected_data)
        
    def insert_row(self, row: int) -> None:
        """Insert a row at the specified position."""
        class InsertRowCommand(Command):
            def __init__(self, sheet, row):
                self.sheet = sheet
                self.row = row
                
            def execute(self):
                self.sheet._insert_row_impl(self.row)
                
            def undo(self):
                self.sheet._delete_row_impl(self.row, {})
                
            def redo(self):
                self.execute()
        
        command = InsertRowCommand(self, row)
        self.command_manager.execute_command(self.name, command)
    
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
        
        class DeleteRowCommand(Command):
            def __init__(self, sheet, row, deleted_cells):
                self.sheet = sheet
                self.row = row
                self.deleted_cells = deleted_cells
                
            def execute(self):
                self.sheet._delete_row_impl(self.row, self.deleted_cells)
                
            def undo(self):
                self.sheet._insert_row_impl(self.row)
                for pos, cell in self.deleted_cells.items():
                    self.sheet.cells[pos] = cell
                
            def redo(self):
                self.execute()
        
        command = DeleteRowCommand(self, row, deleted_cells)
        self.command_manager.execute_command(self.name, command)
    
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
        class InsertColumnCommand(Command):
            def __init__(self, sheet, col):
                self.sheet = sheet
                self.col = col
                
            def execute(self):
                self.sheet._insert_column_impl(self.col)
                
            def undo(self):
                self.sheet._delete_column_impl(self.col, {})
                
            def redo(self):
                self.execute()
        
        command = InsertColumnCommand(self, col)
        self.command_manager.execute_command(self.name, command)
    
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
        
        class DeleteColumnCommand(Command):
            def __init__(self, sheet, col, deleted_cells):
                self.sheet = sheet
                self.col = col
                self.deleted_cells = deleted_cells
                
            def execute(self):
                self.sheet._delete_column_impl(self.col, self.deleted_cells)
                
            def undo(self):
                self.sheet._insert_column_impl(self.col)
                for pos, cell in self.deleted_cells.items():
                    self.sheet.cells[pos] = cell
                
            def redo(self):
                self.execute()
        
        command = DeleteColumnCommand(self, col, deleted_cells)
        self.command_manager.execute_command(self.name, command)
    
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
        cell = self.get_cell(row, col)
        old_chart = getattr(cell, "chart", None)
        
        class AddChartCommand(Command):
            def __init__(self, sheet, row, col, new_chart, old_chart):
                self.sheet = sheet
                self.row = row
                self.col = col
                self.new_chart = new_chart
                self.old_chart = old_chart
                
            def execute(self):
                cell = self.sheet.get_cell(self.row, self.col)
                cell.chart = self.new_chart
                
            def undo(self):
                cell = self.sheet.get_cell(self.row, self.col)
                if self.old_chart:
                    cell.chart = self.old_chart
                else:
                    if hasattr(cell, "chart"):
                        delattr(cell, "chart")
                
            def redo(self):
                self.execute()
        
        command = AddChartCommand(self, row, col, chart, old_chart)
        self.command_manager.execute_command(self.name, command)
    
    def add_image(self, image_data: Dict[str, Any], row: int, col: int) -> None:
        """Add an image to the sheet at the specified position."""
        cell = self.get_cell(row, col)
        old_image = getattr(cell, "image", None)
        
        class AddImageCommand(Command):
            def __init__(self, sheet, row, col, new_image, old_image):
                self.sheet = sheet
                self.row = row
                self.col = col
                self.new_image = new_image
                self.old_image = old_image
                
            def execute(self):
                cell = self.sheet.get_cell(self.row, self.col)
                cell.image = self.new_image
                
            def undo(self):
                cell = self.sheet.get_cell(self.row, self.col)
                if self.old_image:
                    cell.image = self.old_image
                else:
                    if hasattr(cell, "image"):
                        delattr(cell, "image")
                
            def redo(self):
                self.execute()
        
        command = AddImageCommand(self, row, col, image_data, old_image)
        self.command_manager.execute_command(self.name, command)
        
    def execute_function(self, row: int, col: int, function_id: str, selected_data=None) -> None:
        """
        Assign a function to a cell and execute it.
        
        Args:
            row: Row index
            col: Column index
            function_id: ID of the function template to execute
            selected_data: Optional data from selected cells
        """
        from bigsheets.function_engine.function_manager import FunctionManager
        
        cell = self.get_cell(row, col)
        old_function_id = cell.function_id
        old_result = cell.function_result
        
        class ExecuteFunctionCommand(Command):
            def __init__(self, sheet, row, col, function_id, old_function_id, old_result, selected_data):
                self.sheet = sheet
                self.row = row
                self.col = col
                self.function_id = function_id
                self.old_function_id = old_function_id
                self.old_result = old_result
                self.selected_data = selected_data
                self.persistent = True  # Default to persistent functions
                
            def execute(self):
                cell = self.sheet.get_cell(self.row, self.col)
                cell.function_id = self.function_id
                
                for dep_row, dep_col in list(cell.dependencies):
                    dep_cell = self.sheet.get_cell(dep_row, dep_col)
                    if (self.row, self.col) in dep_cell.dependents:
                        dep_cell.dependents.remove((self.row, self.col))
                cell.dependencies.clear()
                
                if self.persistent and self.selected_data is not None:
                    cell.source_cells = []
                    min_row = min_col = float('inf')
                    max_row = max_col = -float('inf')
                    
                    for r_idx, row_data in enumerate(self.selected_data):
                        for c_idx, _ in enumerate(row_data):
                            min_row = min(min_row, r_idx)
                            max_row = max(max_row, r_idx)
                            min_col = min(min_col, c_idx)
                            max_col = max(max_col, c_idx)
                    
                    row_range = (int(min_row), int(max_row))
                    col_range = (int(min_col), int(max_col))
                    cell.source_cells.append((row_range, col_range))
                    
                    for r in range(int(min_row), int(max_row) + 1):
                        for c in range(int(min_col), int(max_col) + 1):
                            source_cell = self.sheet.get_cell(r, c)
                            source_cell.dependents.add((self.row, self.col))
                            cell.dependencies.add((r, c))
                
                cell.function_result = "Calculating..."
                cell.value = "Calculating..."
                
                asyncio.create_task(self._execute_function_async())
                
            async def _execute_function_async(self):
                try:
                    cell = self.sheet.get_cell(self.row, self.col)
                    function_manager = FunctionManager()
                    
                    if self.selected_data is not None:
                        result = await function_manager.execute_function(self.function_id, self.selected_data)
                    else:
                        result = await function_manager.execute_function(self.function_id)
                    
                    cell.function_result = result
                    cell.value = result
                except Exception as e:
                    cell.function_result = f"Error: {str(e)}"
                    cell.value = f"Error: {str(e)}"
                
            def undo(self):
                cell = self.sheet.get_cell(self.row, self.col)
                cell.function_id = self.old_function_id
                cell.function_result = self.old_result
                cell.value = self.old_result
                
            def redo(self):
                self.execute()
        
        command = ExecuteFunctionCommand(self, row, col, function_id, old_function_id, old_result, selected_data)
        self.command_manager.execute_command(self.name, command)


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
