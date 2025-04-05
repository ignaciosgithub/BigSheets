"""
Unit tests for the image rendering functionality in the sheet view.
"""

import unittest
from unittest.mock import MagicMock, patch
import base64
from PyQt5.QtWidgets import QApplication, QStyleOptionViewItem
from PyQt5.QtCore import QModelIndex, Qt
from PyQt5.QtGui import QPainter, QPixmap
from src.bigsheets.ui.sheet_view import SheetItemDelegate
from src.bigsheets.core.spreadsheet_engine import Sheet, Cell


class TestImageRendering(unittest.TestCase):
    """Test cases for the image rendering functionality."""
    
    @classmethod
    def setUpClass(cls):
        """Set up the QApplication instance once for all tests."""
        if not QApplication.instance():
            cls.app = QApplication([])
    
    def setUp(self):
        """Set up test fixtures."""
        self.sheet = MagicMock(spec=Sheet)
        self.delegate = SheetItemDelegate(self.sheet)
        
        self.cell_with_image = MagicMock(spec=Cell)
        self.cell_with_image.value = None
        self.cell_with_image.image = {
            "data": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
        }
        
        self.cell_with_chart = MagicMock(spec=Cell)
        self.cell_with_chart.value = None
        self.cell_with_chart.chart = {
            "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
        }
        
        self.cell_with_text = MagicMock(spec=Cell)
        self.cell_with_text.value = "Test Text"
        
        def get_cell(row, col):
            if row == 0 and col == 0:
                return self.cell_with_image
            elif row == 0 and col == 1:
                return self.cell_with_chart
            else:
                return self.cell_with_text
        
        self.sheet.get_cell.side_effect = get_cell
    
    @patch('PyQt5.QtGui.QPixmap.loadFromData')
    @patch('PyQt5.QtGui.QPixmap.scaled')
    @patch('PyQt5.QtGui.QPainter.drawPixmap')
    def test_paint_cell_with_image(self, mock_draw_pixmap, mock_scaled, mock_load_from_data):
        """Test painting a cell with an image."""
        mock_painter = MagicMock(spec=QPainter)
        mock_option = MagicMock(spec=QStyleOptionViewItem)
        mock_option.rect.width.return_value = 100
        mock_option.rect.height.return_value = 100
        mock_index = MagicMock(spec=QModelIndex)
        mock_index.row.return_value = 0
        mock_index.column.return_value = 0
        
        mock_pixmap = MagicMock(spec=QPixmap)
        mock_pixmap.width.return_value = 50
        mock_pixmap.height.return_value = 50
        mock_scaled.return_value = mock_pixmap
        
        self.delegate.paint(mock_painter, mock_option, mock_index)
        
        mock_load_from_data.assert_called_once()
        mock_scaled.assert_called_once()
        mock_draw_pixmap.assert_called_once()
    
    @patch('PyQt5.QtGui.QPixmap.loadFromData')
    @patch('PyQt5.QtGui.QPixmap.scaled')
    @patch('PyQt5.QtGui.QPainter.drawPixmap')
    def test_paint_cell_with_chart(self, mock_draw_pixmap, mock_scaled, mock_load_from_data):
        """Test painting a cell with a chart."""
        mock_painter = MagicMock(spec=QPainter)
        mock_option = MagicMock(spec=QStyleOptionViewItem)
        mock_option.rect.width.return_value = 100
        mock_option.rect.height.return_value = 100
        mock_index = MagicMock(spec=QModelIndex)
        mock_index.row.return_value = 0
        mock_index.column.return_value = 1
        
        mock_pixmap = MagicMock(spec=QPixmap)
        mock_pixmap.width.return_value = 50
        mock_pixmap.height.return_value = 50
        mock_scaled.return_value = mock_pixmap
        
        self.delegate.paint(mock_painter, mock_option, mock_index)
        
        mock_load_from_data.assert_called_once()
        mock_scaled.assert_called_once()
        mock_draw_pixmap.assert_called_once()
    
    @patch('PyQt5.QtWidgets.QStyledItemDelegate.paint')
    def test_paint_cell_with_text(self, mock_super_paint):
        """Test painting a cell with text."""
        mock_painter = MagicMock(spec=QPainter)
        mock_option = MagicMock(spec=QStyleOptionViewItem)
        mock_index = MagicMock(spec=QModelIndex)
        mock_index.row.return_value = 1
        mock_index.column.return_value = 0
        
        self.delegate.paint(mock_painter, mock_option, mock_index)
        
        mock_super_paint.assert_called_once_with(mock_painter, mock_option, mock_index)


if __name__ == "__main__":
    unittest.main()
