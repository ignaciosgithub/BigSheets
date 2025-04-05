"""
Unit tests for the Spreadsheet Engine module.
"""

import unittest
from src.bigsheets.core.spreadsheet_engine import Cell, Sheet, Workbook


class TestCell(unittest.TestCase):
    """Test cases for the Cell class."""
    
    def test_cell_initialization(self):
        """Test cell initialization with default values."""
        cell = Cell()
        self.assertIsNone(cell.value)
        self.assertIsNone(cell.formula)
        self.assertEqual(cell.formatting, {})
    
    def test_cell_with_value(self):
        """Test cell initialization with a value."""
        cell = Cell(value=42)
        self.assertEqual(cell.value, 42)
        self.assertIsNone(cell.formula)
    
    def test_cell_with_formula(self):
        """Test cell initialization with a formula."""
        cell = Cell(formula="=A1+B1")
        self.assertEqual(cell.formula, "=A1+B1")
    
    def test_cell_with_formatting(self):
        """Test cell initialization with formatting."""
        formatting = {"bold": True, "color": "red"}
        cell = Cell(formatting=formatting)
        self.assertEqual(cell.formatting, formatting)


class TestSheet(unittest.TestCase):
    """Test cases for the Sheet class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.sheet = Sheet("TestSheet")
    
    def test_sheet_initialization(self):
        """Test sheet initialization."""
        self.assertEqual(self.sheet.name, "TestSheet")
        self.assertEqual(self.sheet.rows, 100)
        self.assertEqual(self.sheet.cols, 26)
    
    def test_get_cell(self):
        """Test getting a cell."""
        cell = self.sheet.get_cell(0, 0)
        self.assertIsInstance(cell, Cell)
        self.assertIsNone(cell.value)
    
    def test_set_cell_value(self):
        """Test setting a cell value."""
        self.sheet.set_cell_value(0, 0, "Test")
        cell = self.sheet.get_cell(0, 0)
        self.assertEqual(cell.value, "Test")
    
    def test_insert_row(self):
        """Test inserting a row."""
        self.sheet.set_cell_value(5, 0, "Before")
        
        self.sheet.insert_row(5)
        
        self.assertIsNone(self.sheet.get_cell(5, 0).value)
        self.assertEqual(self.sheet.get_cell(6, 0).value, "Before")
        
        self.assertEqual(self.sheet.rows, 101)
    
    def test_insert_column(self):
        """Test inserting a column."""
        self.sheet.set_cell_value(0, 5, "Before")
        
        self.sheet.insert_column(5)
        
        self.assertIsNone(self.sheet.get_cell(0, 5).value)
        self.assertEqual(self.sheet.get_cell(0, 6).value, "Before")
        
        self.assertEqual(self.sheet.cols, 27)
    
    def test_delete_row(self):
        """Test deleting a row."""
        self.sheet.set_cell_value(5, 0, "Delete")
        self.sheet.set_cell_value(6, 0, "Keep")
        
        self.sheet.delete_row(5)
        
        self.assertEqual(self.sheet.get_cell(5, 0).value, "Keep")
        
        self.assertEqual(self.sheet.rows, 99)
    
    def test_delete_column(self):
        """Test deleting a column."""
        self.sheet.set_cell_value(0, 5, "Delete")
        self.sheet.set_cell_value(0, 6, "Keep")
        
        self.sheet.delete_column(5)
        
        self.assertEqual(self.sheet.get_cell(0, 5).value, "Keep")
        
        self.assertEqual(self.sheet.cols, 25)
    
    def test_undo_redo(self):
        """Test undo and redo operations."""
        self.sheet.set_cell_value(0, 0, "Original")
        
        self.sheet.set_cell_value(0, 0, "Changed")
        self.assertEqual(self.sheet.get_cell(0, 0).value, "Changed")
        
        result = self.sheet.undo()
        self.assertTrue(result)
        self.assertEqual(self.sheet.get_cell(0, 0).value, "Original")
        
        result = self.sheet.redo()
        self.assertTrue(result)
        self.assertEqual(self.sheet.get_cell(0, 0).value, "Changed")


class TestWorkbook(unittest.TestCase):
    """Test cases for the Workbook class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.workbook = Workbook()
    
    def test_workbook_initialization(self):
        """Test workbook initialization."""
        self.assertEqual(len(self.workbook.sheets), 0)
    
    def test_create_sheet(self):
        """Test creating a sheet."""
        sheet = self.workbook.create_sheet("Sheet1")
        self.assertIsInstance(sheet, Sheet)
        self.assertEqual(sheet.name, "Sheet1")
        self.assertIn("Sheet1", self.workbook.sheets)
    
    def test_get_sheet(self):
        """Test getting a sheet."""
        self.workbook.create_sheet("Sheet1")
        sheet = self.workbook.get_sheet("Sheet1")
        self.assertIsInstance(sheet, Sheet)
        self.assertEqual(sheet.name, "Sheet1")
    
    def test_delete_sheet(self):
        """Test deleting a sheet."""
        self.workbook.create_sheet("Sheet1")
        self.workbook.delete_sheet("Sheet1")
        self.assertNotIn("Sheet1", self.workbook.sheets)
    
    def test_rename_sheet(self):
        """Test renaming a sheet."""
        self.workbook.create_sheet("Sheet1")
        self.workbook.rename_sheet("Sheet1", "NewName")
        self.assertNotIn("Sheet1", self.workbook.sheets)
        self.assertIn("NewName", self.workbook.sheets)
        sheet = self.workbook.get_sheet("NewName")
        self.assertEqual(sheet.name, "NewName")
    
    def test_duplicate_sheet_name(self):
        """Test creating a sheet with a duplicate name."""
        self.workbook.create_sheet("Sheet1")
        with self.assertRaises(ValueError):
            self.workbook.create_sheet("Sheet1")


if __name__ == "__main__":
    unittest.main()
