"""
Command & Undo Manager Module

This module implements the Command Pattern to support independent undo/redo
functionality for each spreadsheet.
"""

from typing import Dict, List, Any, Callable, Optional
from abc import ABC, abstractmethod


class Command(ABC):
    """
    Abstract base class for all commands in the application.
    Follows the Command Pattern for encapsulating actions.
    """
    
    @abstractmethod
    def execute(self) -> None:
        """Execute the command."""
        pass
    
    @abstractmethod
    def undo(self) -> None:
        """Undo the command."""
        pass
    
    @abstractmethod
    def redo(self) -> None:
        """Redo the command."""
        pass


class CellEditCommand(Command):
    """Command for editing a cell's value or formula."""
    
    def __init__(self, sheet_id: str, row: int, col: int, 
                 old_value: Any, new_value: Any,
                 old_formula: Optional[str], new_formula: Optional[str],
                 update_cell_func: Callable):
        self.sheet_id = sheet_id
        self.row = row
        self.col = col
        self.old_value = old_value
        self.new_value = new_value
        self.old_formula = old_formula
        self.new_formula = new_formula
        self.update_cell_func = update_cell_func
    
    def execute(self) -> None:
        """Execute the cell edit."""
        self.update_cell_func(self.sheet_id, self.row, self.col, 
                             self.new_value, self.new_formula)
    
    def undo(self) -> None:
        """Undo the cell edit."""
        self.update_cell_func(self.sheet_id, self.row, self.col, 
                             self.old_value, self.old_formula)
    
    def redo(self) -> None:
        """Redo the cell edit."""
        self.execute()


class CommandManager:
    """
    Manages command history and undo/redo functionality for all sheets.
    Each sheet has its own independent command history.
    """
    
    def __init__(self, max_history: int = 100):
        """
        Initialize the command manager.
        
        Args:
            max_history: Maximum number of commands to keep in history per sheet.
        """
        self.max_history = max_history
        self.command_history: Dict[str, List[Command]] = {}  # sheet_id -> commands
        self.redo_stack: Dict[str, List[Command]] = {}  # sheet_id -> commands
    
    def _ensure_sheet_exists(self, sheet_id: str) -> None:
        """Ensure that history stacks exist for the given sheet."""
        if sheet_id not in self.command_history:
            self.command_history[sheet_id] = []
        if sheet_id not in self.redo_stack:
            self.redo_stack[sheet_id] = []
    
    def execute_command(self, sheet_id: str, command: Command) -> None:
        """
        Execute a command and add it to the command history.
        
        Args:
            sheet_id: ID of the sheet the command belongs to
            command: Command to execute
        """
        self._ensure_sheet_exists(sheet_id)
        
        command.execute()
        
        self.command_history[sheet_id].append(command)
        self.redo_stack[sheet_id].clear()
        
        if len(self.command_history[sheet_id]) > self.max_history:
            self.command_history[sheet_id].pop(0)
    
    def undo(self, sheet_id: str) -> bool:
        """
        Undo the last command for the specified sheet.
        
        Args:
            sheet_id: ID of the sheet to undo a command for
            
        Returns:
            True if a command was undone, False if there was nothing to undo
        """
        self._ensure_sheet_exists(sheet_id)
        
        if not self.command_history[sheet_id]:
            return False
        
        command = self.command_history[sheet_id].pop()
        command.undo()
        self.redo_stack[sheet_id].append(command)
        return True
    
    def redo(self, sheet_id: str) -> bool:
        """
        Redo the last undone command for the specified sheet.
        
        Args:
            sheet_id: ID of the sheet to redo a command for
            
        Returns:
            True if a command was redone, False if there was nothing to redo
        """
        self._ensure_sheet_exists(sheet_id)
        
        if not self.redo_stack[sheet_id]:
            return False
        
        command = self.redo_stack[sheet_id].pop()
        command.redo()
        self.command_history[sheet_id].append(command)
        return True
    
    def can_undo(self, sheet_id: str) -> bool:
        """Check if undo is available for the specified sheet."""
        self._ensure_sheet_exists(sheet_id)
        return len(self.command_history[sheet_id]) > 0
    
    def can_redo(self, sheet_id: str) -> bool:
        """Check if redo is available for the specified sheet."""
        self._ensure_sheet_exists(sheet_id)
        return len(self.redo_stack[sheet_id]) > 0
