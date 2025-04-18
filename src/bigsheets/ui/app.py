"""
BigSheets Application Module

This module provides the main application window for the BigSheets desktop application.
"""

from PyQt5.QtWidgets import (
    QMainWindow, QTabWidget, QAction, QFileDialog, QMessageBox,
    QVBoxLayout, QHBoxLayout, QWidget, QLabel, QComboBox, QPushButton,
    QDialog, QLineEdit, QFormLayout
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon

from bigsheets.core.spreadsheet_engine import Workbook, Sheet
from bigsheets.ui.sheet_view import SheetView
from bigsheets.data.csv_importer import CSVImporter
from bigsheets.data.db_connector import DatabaseConnector
from bigsheets.function_engine.function_manager import FunctionManager
from bigsheets.ui.function_editor import FunctionEditorDialog


class BigSheetsApp(QMainWindow):
    """
    Main application window for BigSheets.
    """
    
    def __init__(self):
        super().__init__()
        
        self.workbook = Workbook()
        self.workbook.create_sheet("Sheet1")
        
        self.function_manager = FunctionManager()
        
        self.init_ui()
        self.show()
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("BigSheets")
        self.setGeometry(100, 100, 1200, 800)
        
        self.menuBar().setVisible(True)
        self.create_menu_bar()
        self.menuBar().setVisible(True)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.main_layout = QVBoxLayout(self.central_widget)
        
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        
        self.add_sheet_tab("Sheet1")
        
        self.main_layout.addWidget(self.tab_widget)
        
        self.statusBar().showMessage("Ready")
    
    def create_menu_bar(self):
        """Create the application menu bar."""
        try:
            file_menu = self.menuBar().addMenu("&File")
            
            new_action = QAction("&New", self)
            new_action.setShortcut("Ctrl+N")
            new_action.triggered.connect(self.new_workbook)
            file_menu.addAction(new_action)
            
            open_action = QAction("&Open", self)
            open_action.setShortcut("Ctrl+O")
            open_action.triggered.connect(self.open_workbook)
            file_menu.addAction(open_action)
            
            save_action = QAction("&Save", self)
            save_action.setShortcut("Ctrl+S")
            save_action.triggered.connect(self.save_workbook)
            file_menu.addAction(save_action)
            
            save_as_action = QAction("Save &As", self)
            save_as_action.setShortcut("Ctrl+Shift+S")
            save_as_action.triggered.connect(self.save_workbook_as)
            file_menu.addAction(save_as_action)
            
            file_menu.addSeparator()
            
            exit_action = QAction("E&xit", self)
            exit_action.setShortcut("Ctrl+Q")
            exit_action.triggered.connect(self.close)
            file_menu.addAction(exit_action)
            
            edit_menu = self.menuBar().addMenu("&Edit")
            
            undo_action = QAction("&Undo", self)
            undo_action.setShortcut("Ctrl+Z")
            undo_action.triggered.connect(self.undo)
            edit_menu.addAction(undo_action)
            
            redo_action = QAction("&Redo", self)
            redo_action.setShortcut("Ctrl+Y")
            redo_action.triggered.connect(self.redo)
            edit_menu.addAction(redo_action)
            
            sheet_menu = self.menuBar().addMenu("&Sheet")
            
            add_sheet_action = QAction("&Add Sheet", self)
            add_sheet_action.triggered.connect(self.add_sheet)
            sheet_menu.addAction(add_sheet_action)
            
            rename_sheet_action = QAction("&Rename Sheet", self)
            rename_sheet_action.triggered.connect(self.rename_sheet)
            sheet_menu.addAction(rename_sheet_action)
            
            data_menu = self.menuBar().addMenu("&Data")
            
            import_csv_action = QAction("Import &CSV", self)
            import_csv_action.triggered.connect(self.import_csv)
            data_menu.addAction(import_csv_action)
            
            import_db_action = QAction("Import from &Database", self)
            import_db_action.triggered.connect(self.import_database)
            data_menu.addAction(import_db_action)
            
            insert_menu = self.menuBar().addMenu("&Insert")
            
            insert_chart_action = QAction("&Chart", self)
            insert_chart_action.triggered.connect(self.insert_chart)
            insert_menu.addAction(insert_chart_action)
            
            insert_image_action = QAction("&Image", self)
            insert_image_action.triggered.connect(self.insert_image)
            insert_menu.addAction(insert_image_action)
            
            functions_menu = self.menuBar().addMenu("&Functions")
            functions_menu.setVisible(True)
            
            function_editor_action = QAction("&Function Editor", self)
            function_editor_action.setShortcut("Ctrl+F")
            function_editor_action.triggered.connect(self.open_function_editor)
            functions_menu.addAction(function_editor_action)
            
            self.menuBar().setVisible(True)
            self.menuBar().update()
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Error creating menu bar: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to initialize menu bar: {str(e)}")
    
    def add_sheet_tab(self, sheet_name):
        """Add a new sheet tab to the tab widget."""
        sheet = self.workbook.get_sheet(sheet_name)
        sheet_view = SheetView(sheet)
        
        self.tab_widget.addTab(sheet_view, sheet_name)
        self.tab_widget.setCurrentIndex(self.tab_widget.count() - 1)
    
    def close_tab(self, index):
        """Close a sheet tab."""
        if self.tab_widget.count() > 1:
            sheet_name = self.tab_widget.tabText(index)
            
            self.tab_widget.removeTab(index)
            
    
    def new_workbook(self):
        """Create a new workbook."""
        
        self.workbook = Workbook()
        self.workbook.create_sheet("Sheet1")
        
        while self.tab_widget.count() > 0:
            self.tab_widget.removeTab(0)
        
        self.add_sheet_tab("Sheet1")
        
        self.statusBar().showMessage("New workbook created")
    
    def open_workbook(self):
        """Open an existing workbook."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open BigSheets File", "", "BigSheets Files (*.bgs);;All Files (*)"
        )
        
        if file_path:
            self.open_file(file_path)
    
    def open_file(self, file_path):
        """Open a BigSheets file from the given path."""
        try:
            self.statusBar().showMessage(f"Opening file: {file_path}")
            
            import json
            with open(file_path, 'r') as f:
                workbook_data = json.load(f)
            
            self.workbook = Workbook()
            
            while self.tab_widget.count() > 0:
                self.tab_widget.removeTab(0)
            
            for sheet_name, sheet_data in workbook_data["sheets"].items():
                sheet = self.workbook.create_sheet(sheet_name)
                sheet.rows = sheet_data["rows"]
                sheet.cols = sheet_data["cols"]
                
                for pos_str, cell_data in sheet_data["cells"].items():
                    row, col = map(int, pos_str.split(","))
                    sheet.set_cell_value(row, col, cell_data["value"], cell_data.get("formula"))
                    
                    cell = sheet.get_cell(row, col)
                    cell.formatting = cell_data.get("formatting", {})
                    
                    if "image" in cell_data:
                        cell.image = cell_data["image"]
                    
                    if "chart" in cell_data:
                        cell.chart = cell_data["chart"]
                
                self.add_sheet_tab(sheet_name)
            
            self.current_file_path = file_path
            filename = file_path.split("/")[-1]
            self.setWindowTitle(f"BigSheets - {filename}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open file: {str(e)}")
    
    def save_workbook(self):
        """Save the current workbook."""
        if not hasattr(self, 'current_file_path') or not self.current_file_path:
            self.save_workbook_as()
            return
            
        self._save_to_file(self.current_file_path)
        self.statusBar().showMessage(f"Workbook saved to: {self.current_file_path}")
    
    def save_workbook_as(self):
        """Save the current workbook with a new name."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save BigSheets File", "", "BigSheets Files (*.bgs);;All Files (*)"
        )
        
        if file_path:
            if not file_path.endswith('.bgs'):
                file_path += '.bgs'
            
            self.current_file_path = file_path
            self._save_to_file(file_path)
            
            filename = file_path.split("/")[-1]
            self.setWindowTitle(f"BigSheets - {filename}")
            self.statusBar().showMessage(f"Workbook saved to: {file_path}")
    
    def _save_to_file(self, file_path):
        """Save the workbook to a file."""
        try:
            workbook_data = {
                "sheets": {}
            }
            
            for sheet_name, sheet in self.workbook.sheets.items():
                sheet_data = {
                    "rows": sheet.rows,
                    "cols": sheet.cols,
                    "cells": {}
                }
                
                for pos, cell in sheet.cells.items():
                    row, col = pos
                    cell_data = {
                        "value": cell.value,
                        "formula": cell.formula,
                        "formatting": cell.formatting,
                    }
                    
                    if hasattr(cell, "image") and cell.image:
                        cell_data["image"] = cell.image
                        
                    if hasattr(cell, "chart") and cell.chart:
                        cell_data["chart"] = cell.chart
                    
                    sheet_data["cells"][f"{row},{col}"] = cell_data
                
                workbook_data["sheets"][sheet_name] = sheet_data
            
            import json
            with open(file_path, 'w') as f:
                json.dump(workbook_data, f, indent=2)
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save file: {str(e)}")
    
    def add_sheet(self):
        """Add a new sheet to the workbook."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Sheet")
        
        layout = QFormLayout(dialog)
        
        name_input = QLineEdit()
        layout.addRow("Sheet Name:", name_input)
        
        button_box = QHBoxLayout()
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(dialog.reject)
        add_button = QPushButton("Add")
        add_button.clicked.connect(dialog.accept)
        
        button_box.addWidget(cancel_button)
        button_box.addWidget(add_button)
        layout.addRow(button_box)
        
        if dialog.exec_() == QDialog.Accepted:
            sheet_name = name_input.text().strip()
            if sheet_name:
                try:
                    self.workbook.create_sheet(sheet_name)
                    self.add_sheet_tab(sheet_name)
                    self.statusBar().showMessage(f"Sheet '{sheet_name}' added")
                except ValueError as e:
                    QMessageBox.warning(self, "Error", str(e))
    
    def rename_sheet(self):
        """Rename the current sheet."""
        pass
    
    def undo(self):
        """Undo the last action in the current sheet."""
        current_index = self.tab_widget.currentIndex()
        if current_index >= 0:
            sheet_view = self.tab_widget.widget(current_index)
            sheet_name = self.tab_widget.tabText(current_index)
            
            sheet = self.workbook.get_sheet(sheet_name)
            if sheet.undo():
                sheet_view.model.layoutChanged.emit()
                self.statusBar().showMessage("Undo successful")
            else:
                self.statusBar().showMessage("Nothing to undo")
    
    def redo(self):
        """Redo the last undone action in the current sheet."""
        current_index = self.tab_widget.currentIndex()
        if current_index >= 0:
            sheet_view = self.tab_widget.widget(current_index)
            sheet_name = self.tab_widget.tabText(current_index)
            
            sheet = self.workbook.get_sheet(sheet_name)
            if sheet.redo():
                sheet_view.model.layoutChanged.emit()
                self.statusBar().showMessage("Redo successful")
            else:
                self.statusBar().showMessage("Nothing to redo")
    
    def import_csv(self):
        """Import data from a CSV file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import CSV File", "", "CSV Files (*.csv)"
        )
        
        if file_path:
            self.import_csv_file(file_path)
    
    def import_csv_file(self, file_path):
        """Import data from a CSV file at the given path."""
        try:
            self.statusBar().showMessage(f"Importing CSV: {file_path}")
            
            sheet_name = file_path.split("/")[-1].replace(".csv", "")
            
            base_name = sheet_name
            counter = 1
            while sheet_name in self.workbook.sheets:
                sheet_name = f"{base_name}_{counter}"
                counter += 1
            
            sheet = self.workbook.create_sheet(sheet_name)
            
            csv_importer = CSVImporter()
            data = csv_importer.import_csv(file_path)
            
            for row_idx, row in enumerate(data):
                for col_idx, value in enumerate(row):
                    sheet.set_cell_value(row_idx, col_idx, value)
            
            self.add_sheet_tab(sheet_name)
            
            self.statusBar().showMessage(f"CSV imported: {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to import CSV: {str(e)}")
    
    def import_database(self):
        """Import data from a database."""
        pass
    
    def connect_to_database(self, connection_string):
        """Connect to a database using the given connection string."""
        try:
            self.statusBar().showMessage(f"Connecting to database: {connection_string}")
            
            sheet_name = "Database_Data"
            
            base_name = sheet_name
            counter = 1
            while sheet_name in self.workbook.sheets:
                sheet_name = f"{base_name}_{counter}"
                counter += 1
            
            sheet = self.workbook.create_sheet(sheet_name)
            
            db_connector = DatabaseConnector()
            data = db_connector.connect_and_query(connection_string)
            
            for row_idx, row in enumerate(data):
                for col_idx, value in enumerate(row):
                    sheet.set_cell_value(row_idx, col_idx, value)
            
            self.add_sheet_tab(sheet_name)
            
            self.statusBar().showMessage(f"Database connected: {connection_string}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to connect to database: {str(e)}")
    
    def insert_chart(self):
        """Insert a chart in the current sheet."""
        current_index = self.tab_widget.currentIndex()
        if current_index >= 0:
            sheet_view = self.tab_widget.widget(current_index)
            sheet_view.insert_chart()
    
    def insert_image(self):
        """Insert an image in the current sheet."""
        current_index = self.tab_widget.currentIndex()
        if current_index >= 0:
            sheet_view = self.tab_widget.widget(current_index)
            sheet_view.insert_image()
    
    def open_function_editor(self):
        """Open the function editor dialog."""
        try:
            print("Opening function editor dialog...")
            if not hasattr(self, 'function_manager') or self.function_manager is None:
                self.function_manager = FunctionManager()
                self.function_manager.load_templates()  # Explicitly load templates
                print("Function manager initialized and templates loaded"); print(f"Available templates: {[t.get('name') for t in self.function_manager.list_templates()]}")
            
            dialog = FunctionEditorDialog(self, self.function_manager)
            print("Function editor dialog created successfully")
            dialog.setModal(True)
            dialog.show()  # Show the dialog first
            result = dialog.exec_()  # Then execute it
            print(f"Dialog execution result: {result}")
            self.statusBar().showMessage("Function templates updated")
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Error opening function editor: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to open function editor: {str(e)}")
            
    def keyPressEvent(self, event):
        """Handle key press events globally."""
        from PyQt5.QtGui import QKeySequence
        from PyQt5.QtCore import Qt
        
        if (event.modifiers() & Qt.ControlModifier) and event.key() == Qt.Key_F:
            if hasattr(self, 'function_manager'):
                self.function_manager.load_templates()  # Explicitly load templates
            self.open_function_editor()
            return
            
        if (event.modifiers() & Qt.ControlModifier) and (event.modifiers() & Qt.ShiftModifier) and event.key() == Qt.Key_F:
            current_index = self.tab_widget.currentIndex()
            if current_index >= 0:
                sheet_view = self.tab_widget.widget(current_index)
                sheet_view.insert_function()
            return
            
        super().keyPressEvent(event)
