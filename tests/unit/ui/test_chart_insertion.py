"""
Unit tests for chart insertion functionality in the sheet view.
"""

import unittest
from unittest.mock import MagicMock, patch
from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.QtCore import Qt

from src.bigsheets.ui.sheet_view import SheetView
from src.bigsheets.core.spreadsheet_engine import Sheet
from src.bigsheets.visualization.chart_engine import ChartEngine


class TestChartInsertion(unittest.TestCase):
    """Test cases for the chart insertion functionality."""
    
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
        self.sheet_view.model = MagicMock()
        self.sheet_view.model.index.return_value = MagicMock()
        self.sheet_view.model.dataChanged = MagicMock()
    
    @patch('src.bigsheets.ui.sheet_view.QDialog')
    @patch('src.bigsheets.visualization.chart_engine.ChartEngine.create_chart')
    def test_chart_type_conversion(self, mock_create_chart, mock_dialog):
        """Test that chart types are correctly converted from UI text to chart engine format."""
        mock_dialog_instance = MagicMock()
        mock_dialog.return_value = mock_dialog_instance
        mock_dialog_instance.exec_.return_value = QDialog.Accepted
        
        mock_chart_type = MagicMock()
        
        chart_types = {
            "Bar Chart": "bar",
            "Line Chart": "line",
            "Pie Chart": "pie",
            "Scatter Plot": "scatter"
        }
        
        for ui_text, expected_type in chart_types.items():
            mock_chart_type.currentText.return_value = ui_text
            
            with patch('PyQt5.QtWidgets.QComboBox', return_value=mock_chart_type):
                with patch.object(self.sheet_view, 'insert_chart') as mock_insert_chart:
                    self.sheet_view.insert_chart()
                    
                    mock_insert_chart.assert_called_once()
                    
                    mock_insert_chart.reset_mock()
        
        mock_create_chart.assert_called()
    
    @patch('src.bigsheets.ui.sheet_view.QDialog')
    @patch('src.bigsheets.visualization.chart_engine.ChartEngine.create_chart')
    @patch('src.bigsheets.ui.sheet_view.QMessageBox')
    def test_chart_error_handling(self, mock_message_box, mock_create_chart, mock_dialog):
        """Test that errors during chart creation are properly handled."""
        mock_dialog_instance = MagicMock()
        mock_dialog.return_value = mock_dialog_instance
        mock_dialog_instance.exec_.return_value = QDialog.Accepted
        
        mock_chart_type = MagicMock()
        mock_chart_type.currentText.return_value = "Bar Chart"
        
        mock_create_chart.side_effect = ValueError("Test error")
        
        with patch('PyQt5.QtWidgets.QComboBox', return_value=mock_chart_type):
            self.sheet_view.insert_chart()
            
            mock_message_box.warning.assert_called_once()
            self.assertIn("Failed to create chart", mock_message_box.warning.call_args[0][2])
    
    @patch('src.bigsheets.ui.sheet_view.QDialog')
    @patch('src.bigsheets.visualization.chart_engine.ChartEngine.create_chart')
    def test_chart_added_to_sheet(self, mock_create_chart, mock_dialog):
        """Test that the chart is added to the sheet after creation."""
        mock_dialog_instance = MagicMock()
        mock_dialog.return_value = mock_dialog_instance
        mock_dialog_instance.exec_.return_value = QDialog.Accepted
        
        mock_chart_type = MagicMock()
        mock_chart_type.currentText.return_value = "Bar Chart"
        
        mock_chart = {"type": "bar", "image": "test_image_data"}
        mock_create_chart.return_value = mock_chart
        
        with patch('PyQt5.QtWidgets.QComboBox', return_value=mock_chart_type):
            self.sheet_view.insert_chart()
            
            self.sheet.add_chart.assert_called_once()
            self.assertEqual(self.sheet.add_chart.call_args[0][0], mock_chart)
            
            self.sheet_view.model.dataChanged.emit.assert_called_once()


if __name__ == "__main__":
    unittest.main()
