"""
Unit tests for the custom cell sizing functionality in the sheet view.
"""

import unittest
from unittest.mock import MagicMock, patch
from PyQt5.QtWidgets import QApplication, QInputDialog
from PyQt5.QtCore import QEvent, QPoint
from PyQt5.QtGui import QMouseEvent, QFontMetrics
from src.bigsheets.ui.sheet_view import SheetView
from src.bigsheets.core.spreadsheet_engine import Sheet


class TestCellSizing(unittest.TestCase):
    """Test cases for the custom cell sizing functionality."""
    
    @classmethod
    def setUpClass(cls):
        """Set up the QApplication instance once for all tests."""
        if not QApplication.instance():
            cls.app = QApplication([])
    
    def setUp(self):
        """Set up test fixtures."""
        self.sheet = MagicMock(spec=Sheet)
        
        with patch.object(SheetView, '__init__', return_value=None):
            self.sheet_view = SheetView(self.sheet)
        
        self.sheet_view.sheet = self.sheet
        self.sheet_view.setRowHeight = MagicMock()
        self.sheet_view.setColumnWidth = MagicMock()
        self.sheet_view.rowHeight = MagicMock(return_value=25)
        self.sheet_view.columnWidth = MagicMock(return_value=100)
        self.sheet_view.currentIndex = MagicMock()
        self.sheet_view.horizontalHeader = MagicMock()
        self.sheet_view.verticalHeader = MagicMock()
        self.sheet_view.model = MagicMock()
        self.sheet_view.model.rowCount.return_value = 10
        self.sheet_view.model.columnCount.return_value = 10
    
    @patch('PyQt5.QtWidgets.QInputDialog.getInt')
    def test_resize_row(self, mock_get_int):
        """Test resizing a row."""
        mock_index = MagicMock()
        mock_index.isValid.return_value = True
        mock_index.row.return_value = 5
        self.sheet_view.currentIndex.return_value = mock_index
        
        mock_get_int.return_value = (50, True)  # (new_height, ok)
        
        self.sheet_view.resize_row()
        
        mock_get_int.assert_called_once()
        self.assertEqual(mock_get_int.call_args[0][2], "Enter new height for row 6:")
        self.assertEqual(mock_get_int.call_args[0][3], 25)  # Current height
        
        self.sheet_view.setRowHeight.assert_called_once_with(5, 50)
    
    @patch('PyQt5.QtWidgets.QInputDialog.getInt')
    def test_resize_column(self, mock_get_int):
        """Test resizing a column."""
        mock_index = MagicMock()
        mock_index.isValid.return_value = True
        mock_index.column.return_value = 2  # Column C
        self.sheet_view.currentIndex.return_value = mock_index
        
        mock_get_int.return_value = (150, True)  # (new_width, ok)
        
        self.sheet_view.resize_column()
        
        mock_get_int.assert_called_once()
        self.assertEqual(mock_get_int.call_args[0][2], "Enter new width for column C:")
        self.assertEqual(mock_get_int.call_args[0][3], 100)  # Current width
        
        self.sheet_view.setColumnWidth.assert_called_once_with(2, 150)
    
    @patch('PyQt5.QtWidgets.QTableView.mouseDoubleClickEvent')
    def test_mouse_double_click_on_horizontal_header(self, mock_super_event):
        """Test double-clicking on a horizontal header to auto-size a column."""
        mock_h_header = MagicMock()
        mock_h_header.rect.return_value.contains.return_value = True
        mock_h_header.logicalIndexAt.return_value = 3
        mock_h_header.height.return_value = 20
        
        mock_v_header = MagicMock()
        mock_v_header.rect.return_value.contains.return_value = False
        
        self.sheet_view.horizontalHeader.return_value = mock_h_header
        self.sheet_view.verticalHeader.return_value = mock_v_header
        
        self.sheet_view.auto_size_column = MagicMock()
        
        mock_event = MagicMock(spec=QMouseEvent)
        mock_event.pos.return_value = QPoint(150, 10)  # Inside horizontal header
        
        self.sheet_view.mouseDoubleClickEvent(mock_event)
        
        self.sheet_view.auto_size_column.assert_called_once_with(3)
        
        mock_super_event.assert_not_called()
    
    @patch('PyQt5.QtWidgets.QTableView.mouseDoubleClickEvent')
    def test_mouse_double_click_on_vertical_header(self, mock_super_event):
        """Test double-clicking on a vertical header to auto-size a row."""
        mock_h_header = MagicMock()
        mock_h_header.rect.return_value.contains.return_value = False
        
        mock_v_header = MagicMock()
        mock_v_header.rect.return_value.contains.return_value = True
        mock_v_header.logicalIndexAt.return_value = 4
        mock_v_header.width.return_value = 30
        
        self.sheet_view.horizontalHeader.return_value = mock_h_header
        self.sheet_view.verticalHeader.return_value = mock_v_header
        
        self.sheet_view.auto_size_row = MagicMock()
        
        mock_event = MagicMock(spec=QMouseEvent)
        mock_event.pos.return_value = QPoint(15, 100)  # Inside vertical header
        
        self.sheet_view.mouseDoubleClickEvent(mock_event)
        
        self.sheet_view.auto_size_row.assert_called_once_with(4)
        
        mock_super_event.assert_not_called()
    
    @patch('PyQt5.QtGui.QFontMetrics')
    def test_auto_size_column(self, mock_font_metrics_class):
        """Test auto-sizing a column based on content."""
        mock_font_metrics = MagicMock(spec=QFontMetrics)
        mock_font_metrics_class.return_value = mock_font_metrics
        mock_font_metrics.width.side_effect = lambda text: len(text) * 10  # Simple width calculation
        
        mock_header = MagicMock()
        mock_header.sectionSize.return_value = 80
        self.sheet_view.horizontalHeader.return_value = mock_header
        
        mock_cell1 = MagicMock()
        mock_cell1.value = "Short"
        
        mock_cell2 = MagicMock()
        mock_cell2.value = "This is a longer text"
        
        mock_cell3 = MagicMock()
        mock_cell3.value = None
        
        self.sheet.get_cell.side_effect = [mock_cell1, mock_cell2, mock_cell3]
        
        self.sheet_view.auto_size_column(2)
        
        self.sheet_view.setColumnWidth.assert_called_once_with(2, 230)
    
    @patch('PyQt5.QtGui.QFontMetrics')
    def test_auto_size_row(self, mock_font_metrics_class):
        """Test auto-sizing a row based on content."""
        mock_font_metrics = MagicMock(spec=QFontMetrics)
        mock_font_metrics_class.return_value = mock_font_metrics
        mock_font_metrics.height.return_value = 14  # Font height
        
        mock_header = MagicMock()
        mock_header.sectionSize.return_value = 20
        self.sheet_view.verticalHeader.return_value = mock_header
        
        self.sheet_view.auto_size_row(3)
        
        self.sheet_view.setRowHeight.assert_called_once_with(3, 20)


if __name__ == "__main__":
    unittest.main()
