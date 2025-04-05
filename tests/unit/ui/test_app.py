"""
Unit tests for the BigSheets Application module.
"""

import unittest
from unittest.mock import MagicMock, patch
import os
import tempfile
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QMessageBox
from src.bigsheets.ui.app import BigSheetsApp
from src.bigsheets.core.spreadsheet_engine import Workbook, Sheet


class TestBigSheetsApp(unittest.TestCase):
    """Test cases for the BigSheetsApp class."""
    
    @classmethod
    def setUpClass(cls):
        """Set up the QApplication instance once for all tests."""
        if not QApplication.instance():
            cls.app = QApplication([])
    
    def setUp(self):
        """Set up test fixtures."""
        with patch.object(QMainWindow, '__init__', return_value=None):
            self.app_window = BigSheetsApp()
        
        self.app_window.workbook = MagicMock(spec=Workbook)
        
        self.app_window.tab_widget = MagicMock(spec=QTabWidget)
        
        self.app_window.statusBar = MagicMock()
    
    def test_add_sheet_tab(self):
        """Test adding a sheet tab."""
        mock_sheet = MagicMock(spec=Sheet)
        self.app_window.workbook.get_sheet.return_value = mock_sheet
        
        self.app_window.add_sheet_tab("TestSheet")
        
        self.app_window.workbook.get_sheet.assert_called_once_with("TestSheet")
        
        self.app_window.tab_widget.addTab.assert_called_once()
        self.app_window.tab_widget.setCurrentIndex.assert_called_once()
    
    def test_close_tab(self):
        """Test closing a sheet tab."""
        self.app_window.tab_widget.count.return_value = 2
        
        self.app_window.tab_widget.tabText.return_value = "TestSheet"
        
        self.app_window.close_tab(0)
        
        self.app_window.tab_widget.removeTab.assert_called_once_with(0)
    
    def test_new_workbook(self):
        """Test creating a new workbook."""
        self.app_window.tab_widget.count.return_value = 1
        
        self.app_window.new_workbook()
        
        self.app_window.workbook.create_sheet.assert_called_once_with("Sheet1")
        
        self.app_window.tab_widget.removeTab.assert_called_once_with(0)
        self.app_window.tab_widget.addTab.assert_called_once()
        
        self.app_window.statusBar().showMessage.assert_called_once_with("New workbook created")
    
    @patch('src.bigsheets.ui.app.QFileDialog')
    def test_open_workbook(self, mock_file_dialog):
        """Test opening a workbook."""
        mock_file_dialog.getOpenFileName.return_value = ("/path/to/file.bgs", "")
        
        self.app_window.open_file = MagicMock()
        
        self.app_window.open_workbook()
        
        self.app_window.open_file.assert_called_once_with("/path/to/file.bgs")
    
    def test_open_file(self):
        """Test opening a file."""
        self.app_window.tab_widget.count.return_value = 1
        
        self.app_window.open_file("/path/to/file.bgs")
        
        self.app_window.workbook.create_sheet.assert_called_once_with("Sheet1")
        
        self.app_window.tab_widget.removeTab.assert_called_once_with(0)
        self.app_window.tab_widget.addTab.assert_called_once()
        
        self.app_window.setWindowTitle.assert_called_once_with("BigSheets - file.bgs")
        
        self.app_window.statusBar().showMessage.assert_called_once_with("Opening file: /path/to/file.bgs")
    
    @patch('src.bigsheets.ui.app.QMessageBox')
    def test_open_file_error(self, mock_message_box):
        """Test error handling when opening a file."""
        self.app_window.workbook.create_sheet.side_effect = Exception("Test error")
        
        self.app_window.open_file("/path/to/file.bgs")
        
        mock_message_box.critical.assert_called_once()
    
    @patch('src.bigsheets.ui.app.QFileDialog')
    def test_import_csv(self, mock_file_dialog):
        """Test importing a CSV file."""
        mock_file_dialog.getOpenFileName.return_value = ("/path/to/file.csv", "")
        
        self.app_window.import_csv_file = MagicMock()
        
        self.app_window.import_csv()
        
        self.app_window.import_csv_file.assert_called_once_with("/path/to/file.csv")
    
    @patch('src.bigsheets.ui.app.CSVImporter')
    def test_import_csv_file(self, mock_csv_importer_class):
        """Test importing a CSV file from a path."""
        mock_csv_importer = MagicMock()
        mock_csv_importer_class.return_value = mock_csv_importer
        
        test_data = [["Header1", "Header2"], ["Value1", "Value2"]]
        mock_csv_importer.import_csv.return_value = test_data
        
        mock_sheet = MagicMock(spec=Sheet)
        self.app_window.workbook.create_sheet.return_value = mock_sheet
        
        self.app_window.workbook.sheets = {}
        
        self.app_window.import_csv_file("/path/to/file.csv")
        
        self.app_window.workbook.create_sheet.assert_called_once_with("file")
        
        mock_csv_importer.import_csv.assert_called_once_with("/path/to/file.csv")
        
        mock_sheet.set_cell_value.assert_any_call(0, 0, "Header1")
        mock_sheet.set_cell_value.assert_any_call(0, 1, "Header2")
        mock_sheet.set_cell_value.assert_any_call(1, 0, "Value1")
        mock_sheet.set_cell_value.assert_any_call(1, 1, "Value2")
        
        self.app_window.add_sheet_tab.assert_called_once_with("file")
        
        self.app_window.statusBar().showMessage.assert_called_with("CSV imported: /path/to/file.csv")
    
    @patch('src.bigsheets.ui.app.QMessageBox')
    @patch('src.bigsheets.ui.app.CSVImporter')
    def test_import_csv_file_error(self, mock_csv_importer_class, mock_message_box):
        """Test error handling when importing a CSV file."""
        mock_csv_importer = MagicMock()
        mock_csv_importer_class.return_value = mock_csv_importer
        mock_csv_importer.import_csv.side_effect = Exception("Test error")
        
        self.app_window.import_csv_file("/path/to/file.csv")
        
        mock_message_box.critical.assert_called_once()
    
    @patch('src.bigsheets.ui.app.DatabaseConnector')
    def test_connect_to_database(self, mock_db_connector_class):
        """Test connecting to a database."""
        mock_db_connector = MagicMock()
        mock_db_connector_class.return_value = mock_db_connector
        
        test_data = [["id", "name"], [1, "Test"]]
        mock_db_connector.connect_and_query.return_value = test_data
        
        mock_sheet = MagicMock(spec=Sheet)
        self.app_window.workbook.create_sheet.return_value = mock_sheet
        
        self.app_window.workbook.sheets = {}
        
        self.app_window.connect_to_database("sqlite:///test.db")
        
        self.app_window.workbook.create_sheet.assert_called_once_with("Database_Data")
        
        mock_db_connector.connect_and_query.assert_called_once_with("sqlite:///test.db")
        
        mock_sheet.set_cell_value.assert_any_call(0, 0, "id")
        mock_sheet.set_cell_value.assert_any_call(0, 1, "name")
        mock_sheet.set_cell_value.assert_any_call(1, 0, 1)
        mock_sheet.set_cell_value.assert_any_call(1, 1, "Test")
        
        self.app_window.add_sheet_tab.assert_called_once_with("Database_Data")
        
        self.app_window.statusBar().showMessage.assert_called_with("Database connected: sqlite:///test.db")


if __name__ == "__main__":
    unittest.main()
