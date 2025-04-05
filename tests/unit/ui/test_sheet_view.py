"""
Unit tests for the Sheet View module.
"""

import unittest
from unittest.mock import MagicMock, patch
from PyQt5.QtWidgets import QApplication, QTableView, QHeaderView
from PyQt5.QtCore import Qt, QModelIndex
from src.bigsheets.ui.sheet_view import SheetView, SheetTableModel
from src.bigsheets.core.spreadsheet_engine import Sheet, Cell


class TestSheetTableModel(unittest.TestCase):
    """Test cases for the SheetTableModel class."""
    
    @classmethod
    def setUpClass(cls):
        """Set up the QApplication instance once for all tests."""
        if not QApplication.instance():
            cls.app = QApplication([])
    
    def setUp(self):
        """Set up test fixtures."""
        self.sheet = MagicMock(spec=Sheet)
        self.sheet.rows = 10
        self.sheet.cols = 5
        
        def mock_get_cell(row, col):
            if row == 0 and col == 0:
                return Cell(value="A1")
            elif row == 1 and col == 1:
                return Cell(value=42)
            elif row == 2 and col == 2:
                return Cell(formula="=A1+B1")
            else:
                return Cell()
        
        self.sheet.get_cell.side_effect = mock_get_cell
        
        self.model = SheetTableModel(self.sheet)
    
    def test_row_count(self):
        """Test row count."""
        self.assertEqual(self.model.rowCount(), 10)
    
    def test_column_count(self):
        """Test column count."""
        self.assertEqual(self.model.columnCount(), 5)
    
    def test_data(self):
        """Test data retrieval."""
        index = self.model.createIndex(0, 0)
        self.assertEqual(self.model.data(index, Qt.DisplayRole), "A1")
        
        index = self.model.createIndex(1, 1)
        self.assertEqual(self.model.data(index, Qt.DisplayRole), "42")
        
        index = self.model.createIndex(2, 2)
        self.assertEqual(self.model.data(index, Qt.DisplayRole), "")
        
        invalid_index = QModelIndex()
        self.assertEqual(self.model.data(invalid_index, Qt.DisplayRole).isValid(), False)
    
    def test_set_data(self):
        """Test setting data."""
        index = self.model.createIndex(0, 0)
        self.model.setData(index, "New Value", Qt.EditRole)
        self.sheet.set_cell_value.assert_called_with(0, 0, "New Value")
        
        index = self.model.createIndex(1, 1)
        self.model.setData(index, "=A1+B1", Qt.EditRole)
        self.sheet.set_cell_value.assert_called_with(1, 1, None, "=A1+B1")
        
        invalid_index = QModelIndex()
        result = self.model.setData(invalid_index, "Value", Qt.EditRole)
        self.assertFalse(result)
        
        index = self.model.createIndex(0, 0)
        result = self.model.setData(index, "Value", Qt.DecorationRole)
        self.assertFalse(result)
    
    def test_header_data(self):
        """Test header data."""
        self.assertEqual(self.model.headerData(0, Qt.Horizontal, Qt.DisplayRole), "A")
        self.assertEqual(self.model.headerData(1, Qt.Horizontal, Qt.DisplayRole), "B")
        self.assertEqual(self.model.headerData(25, Qt.Horizontal, Qt.DisplayRole), "Z")
        self.assertEqual(self.model.headerData(26, Qt.Horizontal, Qt.DisplayRole), "AA")
        
        self.assertEqual(self.model.headerData(0, Qt.Vertical, Qt.DisplayRole), "1")
        self.assertEqual(self.model.headerData(9, Qt.Vertical, Qt.DisplayRole), "10")
        
        self.assertEqual(self.model.headerData(0, Qt.Horizontal, Qt.DecorationRole).isValid(), False)
    
    def test_flags(self):
        """Test item flags."""
        index = self.model.createIndex(0, 0)
        flags = self.model.flags(index)
        
        self.assertTrue(flags & Qt.ItemIsEnabled)
        self.assertTrue(flags & Qt.ItemIsSelectable)
        self.assertTrue(flags & Qt.ItemIsEditable)


class TestSheetView(unittest.TestCase):
    """Test cases for the SheetView class."""
    
    @classmethod
    def setUpClass(cls):
        """Set up the QApplication instance once for all tests."""
        if not QApplication.instance():
            cls.app = QApplication([])
    
    def setUp(self):
        """Set up test fixtures."""
        self.sheet = MagicMock(spec=Sheet)
        self.sheet.rows = 10
        self.sheet.cols = 5
        
        def mock_get_cell(row, col):
            return Cell()
        
        self.sheet.get_cell.side_effect = mock_get_cell
        
        with patch.object(QTableView, '__init__', return_value=None):
            self.view = SheetView(self.sheet)
        
        self.view.model = MagicMock(spec=SheetTableModel)
        self.view.model.rowCount.return_value = 10
        self.view.model.columnCount.return_value = 5
        
        self.view.horizontalHeader = MagicMock()
        self.view.verticalHeader = MagicMock()
        
        self.view.viewport = MagicMock()
        
        self.view.currentIndex = MagicMock()
        index = MagicMock()
        index.isValid.return_value = True
        index.row.return_value = 1
        index.column.return_value = 1
        self.view.currentIndex.return_value = index
        
        self.view.selectedIndexes = MagicMock(return_value=[index])
        
        self.view.setRowHeight = MagicMock()
        self.view.setColumnWidth = MagicMock()
    
    def test_insert_row(self):
        """Test inserting a row."""
        self.view.insert_row()
        
        self.sheet.insert_row.assert_called_once_with(1)
        
        self.view.model.beginInsertRows.assert_called_once()
        self.view.model.endInsertRows.assert_called_once()
        
        self.view.setRowHeight.assert_called_once_with(1, 25)
    
    def test_insert_column(self):
        """Test inserting a column."""
        self.view.insert_column()
        
        self.sheet.insert_column.assert_called_once_with(1)
        
        self.view.model.beginInsertColumns.assert_called_once()
        self.view.model.endInsertColumns.assert_called_once()
        
        self.view.setColumnWidth.assert_called_once_with(1, 100)
    
    def test_delete_row(self):
        """Test deleting a row."""
        self.view.delete_row()
        
        self.sheet.delete_row.assert_called_once_with(1)
        
        self.view.model.beginRemoveRows.assert_called_once()
        self.view.model.endRemoveRows.assert_called_once()
    
    def test_delete_column(self):
        """Test deleting a column."""
        self.view.delete_column()
        
        self.sheet.delete_column.assert_called_once_with(1)
        
        self.view.model.beginRemoveColumns.assert_called_once()
        self.view.model.endRemoveColumns.assert_called_once()
    
    @patch('src.bigsheets.ui.sheet_view.QDialog')
    @patch('src.bigsheets.ui.sheet_view.ChartEngine')
    def test_insert_chart(self, mock_chart_engine_class, mock_dialog_class):
        """Test inserting a chart."""
        mock_dialog = MagicMock()
        mock_dialog_class.return_value = mock_dialog
        mock_dialog.exec_.return_value = mock_dialog.Accepted
        
        mock_chart_engine = MagicMock()
        mock_chart_engine_class.return_value = mock_chart_engine
        mock_chart = MagicMock()
        mock_chart_engine.create_chart.return_value = mock_chart
        
        self.view.insert_chart()
        
        mock_chart_engine.create_chart.assert_called_once()
        
        self.sheet.add_chart.assert_called_once()
    
    @patch('src.bigsheets.ui.sheet_view.QFileDialog')
    @patch('src.bigsheets.ui.sheet_view.ImageManager')
    def test_insert_image(self, mock_image_manager_class, mock_file_dialog):
        """Test inserting an image."""
        mock_file_dialog.getOpenFileName.return_value = ("/path/to/image.png", "")
        
        mock_image_manager = MagicMock()
        mock_image_manager_class.return_value = mock_image_manager
        mock_image_data = MagicMock()
        mock_image_manager.load_image.return_value = mock_image_data
        
        self.view.insert_image()
        
        mock_image_manager.load_image.assert_called_once_with("/path/to/image.png")
        
        self.sheet.add_image.assert_called_once_with(mock_image_data, 1, 1)
        
        self.view.viewport().update.assert_called_once()
    
    @patch('src.bigsheets.ui.sheet_view.QFileDialog')
    @patch('src.bigsheets.ui.sheet_view.ImageManager')
    @patch('src.bigsheets.ui.sheet_view.QMessageBox')
    def test_insert_image_error(self, mock_message_box, mock_image_manager_class, mock_file_dialog):
        """Test error handling when inserting an image."""
        mock_file_dialog.getOpenFileName.return_value = ("/path/to/image.png", "")
        
        mock_image_manager = MagicMock()
        mock_image_manager_class.return_value = mock_image_manager
        mock_image_manager.load_image.side_effect = Exception("Test error")
        
        self.view.insert_image()
        
        mock_message_box.warning.assert_called_once()


if __name__ == "__main__":
    unittest.main()
