"""
Unit tests for the Command Manager module.
"""

import unittest
from unittest.mock import MagicMock, patch
from src.bigsheets.core.command_manager import Command, CommandManager


class TestCommand(unittest.TestCase):
    """Test cases for the Command class."""
    
    def test_command_initialization(self):
        """Test command initialization."""
        execute_func = MagicMock()
        undo_func = MagicMock()
        
        command = Command(execute_func, undo_func)
        
        self.assertEqual(command.execute_func, execute_func)
        self.assertEqual(command.undo_func, undo_func)
    
    def test_execute(self):
        """Test executing a command."""
        execute_func = MagicMock(return_value="result")
        undo_func = MagicMock()
        
        command = Command(execute_func, undo_func)
        result = command.execute()
        
        execute_func.assert_called_once()
        self.assertEqual(result, "result")
    
    def test_undo(self):
        """Test undoing a command."""
        execute_func = MagicMock()
        undo_func = MagicMock(return_value="undo_result")
        
        command = Command(execute_func, undo_func)
        result = command.undo()
        
        undo_func.assert_called_once()
        self.assertEqual(result, "undo_result")


class TestCommandManager(unittest.TestCase):
    """Test cases for the CommandManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.manager = CommandManager()
        
        self.command1 = MagicMock()
        self.command1.execute.return_value = "result1"
        self.command1.undo.return_value = "undo1"
        
        self.command2 = MagicMock()
        self.command2.execute.return_value = "result2"
        self.command2.undo.return_value = "undo2"
    
    def test_initialization(self):
        """Test command manager initialization."""
        self.assertEqual(len(self.manager.undo_stack), 0)
        self.assertEqual(len(self.manager.redo_stack), 0)
    
    def test_execute_command(self):
        """Test executing a command."""
        result = self.manager.execute_command(self.command1)
        
        self.command1.execute.assert_called_once()
        self.assertEqual(result, "result1")
        
        self.assertEqual(len(self.manager.undo_stack), 1)
        self.assertEqual(self.manager.undo_stack[0], self.command1)
        
        self.assertEqual(len(self.manager.redo_stack), 0)
    
    def test_undo(self):
        """Test undoing a command."""
        self.manager.execute_command(self.command1)
        self.manager.execute_command(self.command2)
        
        result = self.manager.undo()
        
        self.command2.undo.assert_called_once()
        self.assertEqual(result, "undo2")
        
        self.assertEqual(len(self.manager.undo_stack), 1)
        self.assertEqual(len(self.manager.redo_stack), 1)
        self.assertEqual(self.manager.redo_stack[0], self.command2)
    
    def test_redo(self):
        """Test redoing a command."""
        self.manager.execute_command(self.command1)
        self.manager.undo()
        
        result = self.manager.redo()
        
        self.command1.execute.assert_called_with()
        self.assertEqual(result, "result1")
        
        self.assertEqual(len(self.manager.undo_stack), 1)
        self.assertEqual(len(self.manager.redo_stack), 0)
        self.assertEqual(self.manager.undo_stack[0], self.command1)
    
    def test_undo_empty_stack(self):
        """Test undoing with an empty stack."""
        result = self.manager.undo()
        
        self.assertFalse(result)
        self.assertEqual(len(self.manager.undo_stack), 0)
        self.assertEqual(len(self.manager.redo_stack), 0)
    
    def test_redo_empty_stack(self):
        """Test redoing with an empty stack."""
        result = self.manager.redo()
        
        self.assertFalse(result)
        self.assertEqual(len(self.manager.undo_stack), 0)
        self.assertEqual(len(self.manager.redo_stack), 0)
    
    def test_clear_history(self):
        """Test clearing command history."""
        self.manager.execute_command(self.command1)
        self.manager.execute_command(self.command2)
        self.manager.undo()
        
        self.manager.clear_history()
        
        self.assertEqual(len(self.manager.undo_stack), 0)
        self.assertEqual(len(self.manager.redo_stack), 0)
    
    def test_max_history_size(self):
        """Test maximum history size."""
        manager = CommandManager(max_history_size=2)
        
        manager.execute_command(self.command1)
        manager.execute_command(self.command1)
        manager.execute_command(self.command2)
        
        self.assertEqual(len(manager.undo_stack), 2)
        self.assertEqual(manager.undo_stack[0], self.command1)
        self.assertEqual(manager.undo_stack[1], self.command2)


if __name__ == "__main__":
    unittest.main()
