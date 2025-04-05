"""
Unit tests for the undo functionality in the spreadsheet engine.
"""

import unittest
from unittest.mock import MagicMock, patch
from src.bigsheets.core.spreadsheet_engine import Sheet, Cell
from src.bigsheets.core.command_manager import CommandManager, Command


class TestUndoFunctionality(unittest.TestCase):
    """Test cases for the undo functionality in the Sheet class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.sheet = Sheet("TestSheet")
    
    def test_set_cell_value_command(self):
        """Test that setting a cell value creates a command in the command manager."""
        original_execute_command = self.sheet.command_manager.execute_command
        self.sheet.command_manager.execute_command = MagicMock(wraps=original_execute_command)
        
        self.sheet.set_cell_value(0, 0, "Test Value")
        
        self.sheet.command_manager.execute_command.assert_called_once()
        
        cell = self.sheet.get_cell(0, 0)
        self.assertEqual(cell.value, "Test Value")
    
    def test_undo_cell_value(self):
        """Test undoing a cell value change."""
        self.sheet.set_cell_value(0, 0, "Original Value")
        
        self.sheet.set_cell_value(0, 0, "New Value")
        
        cell = self.sheet.get_cell(0, 0)
        self.assertEqual(cell.value, "New Value")
        
        result = self.sheet.undo()
        
        self.assertTrue(result)
        
        cell = self.sheet.get_cell(0, 0)
        self.assertEqual(cell.value, "Original Value")
    
    def test_redo_cell_value(self):
        """Test redoing a cell value change."""
        self.sheet.set_cell_value(0, 0, "Original Value")
        
        self.sheet.set_cell_value(0, 0, "New Value")
        
        self.sheet.undo()
        
        cell = self.sheet.get_cell(0, 0)
        self.assertEqual(cell.value, "Original Value")
        
        result = self.sheet.redo()
        
        self.assertTrue(result)
        
        cell = self.sheet.get_cell(0, 0)
        self.assertEqual(cell.value, "New Value")
    
    def test_multiple_undo_redo(self):
        """Test multiple undo and redo operations."""
        self.sheet.set_cell_value(0, 0, "Value 1")
        self.sheet.set_cell_value(0, 1, "Value 2")
        self.sheet.set_cell_value(1, 0, "Value 3")
        
        self.sheet.undo()  # Undo "Value 3"
        self.sheet.undo()  # Undo "Value 2"
        self.sheet.undo()  # Undo "Value 1"
        
        self.assertIsNone(self.sheet.get_cell(0, 0).value)
        self.assertIsNone(self.sheet.get_cell(0, 1).value)
        self.assertIsNone(self.sheet.get_cell(1, 0).value)
        
        self.sheet.redo()  # Redo "Value 1"
        self.sheet.redo()  # Redo "Value 2"
        self.sheet.redo()  # Redo "Value 3"
        
        self.assertEqual(self.sheet.get_cell(0, 0).value, "Value 1")
        self.assertEqual(self.sheet.get_cell(0, 1).value, "Value 2")
        self.assertEqual(self.sheet.get_cell(1, 0).value, "Value 3")
    
    def test_undo_most_recent_action(self):
        """Test that undo undoes the most recent action, not a previous one."""
        self.sheet.set_cell_value(0, 0, "First")
        self.sheet.set_cell_value(0, 1, "Second")
        self.sheet.set_cell_value(0, 2, "Third")  # Most recent action
        
        self.sheet.undo()
        
        self.assertEqual(self.sheet.get_cell(0, 0).value, "First")
        self.assertEqual(self.sheet.get_cell(0, 1).value, "Second")
        self.assertIsNone(self.sheet.get_cell(0, 2).value)
        
        self.sheet.undo()
        
        self.assertEqual(self.sheet.get_cell(0, 0).value, "First")
        self.assertIsNone(self.sheet.get_cell(0, 1).value)
        self.assertIsNone(self.sheet.get_cell(0, 2).value)
    
    def test_undo_redo_with_other_operations(self):
        """Test undo/redo with other operations like insert/delete row/column."""
        self.sheet.set_cell_value(0, 0, "Original")
        
        self.sheet.insert_row(0)
        
        self.assertEqual(self.sheet.get_cell(1, 0).value, "Original")
        self.assertIsNone(self.sheet.get_cell(0, 0).value)
        
        self.sheet.undo()
        
        self.assertEqual(self.sheet.get_cell(0, 0).value, "Original")
        
        self.sheet.redo()
        
        self.assertEqual(self.sheet.get_cell(1, 0).value, "Original")
        self.assertIsNone(self.sheet.get_cell(0, 0).value)


if __name__ == "__main__":
    unittest.main()
