"""
Sheet View Module

This module provides the UI component for displaying and interacting with a sheet.
"""

from PyQt5.QtWidgets import (
    QTableView, QHeaderView, QAbstractItemView, QMenu, QAction,
    QStyledItemDelegate, QStyleOptionViewItem, QWidget
)
from PyQt5.QtCore import Qt, QAbstractTableModel, QModelIndex, QVariant
from PyQt5.QtGui import QColor, QBrush, QPainter

from bigsheets.core.spreadsheet_engine import Sheet


class SheetTableModel(QAbstractTableModel):
    """
    Model for displaying sheet data in a QTableView.
    """
    
    def __init__(self, sheet: Sheet):
        super().__init__()
        self.sheet = sheet
    
    def rowCount(self, parent=None):
        return self.sheet.rows
    
    def columnCount(self, parent=None):
        return self.sheet.cols
    
    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return QVariant()
        
        row, col = index.row(), index.column()
        cell = self.sheet.get_cell(row, col)
        
        if role == Qt.DisplayRole or role == Qt.EditRole:
            return str(cell.value) if cell.value is not None else ""
        
        
        return QVariant()
    
    def setData(self, index, value, role=Qt.EditRole):
        if not index.isValid() or role != Qt.EditRole:
            return False
        
        row, col = index.row(), index.column()
        
        value_str = str(value)
        if value_str.startswith('='):
            formula = value_str
            result = None  # Placeholder for formula evaluation result
            self.sheet.set_cell_value(row, col, result, formula)
        else:
            self.sheet.set_cell_value(row, col, value)
        
        self.dataChanged.emit(index, index)
        return True
    
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return QVariant()
        
        if orientation == Qt.Horizontal:
            result = ""
            temp = section
            while temp >= 0:
                result = chr(65 + (temp % 26)) + result
                temp = temp // 26 - 1
            return result
        else:
            return str(section + 1)
    
    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable


class SheetView(QTableView):
    """
    Custom QTableView for displaying and interacting with a sheet.
    """
    
    def __init__(self, sheet: Sheet):
        super().__init__()
        self.sheet = sheet
        self.model = SheetTableModel(sheet)
        self.setModel(self.model)
        
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.verticalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.setSelectionMode(QAbstractItemView.ContiguousSelection)
        
        for col in range(self.model.columnCount()):
            self.setColumnWidth(col, 100)
        
        for row in range(self.model.rowCount()):
            self.setRowHeight(row, 25)
    
    def contextMenuEvent(self, event):
        """Handle right-click context menu."""
        menu = QMenu(self)
        
        insert_row_action = QAction("Insert Row", self)
        insert_row_action.triggered.connect(self.insert_row)
        menu.addAction(insert_row_action)
        
        insert_col_action = QAction("Insert Column", self)
        insert_col_action.triggered.connect(self.insert_column)
        menu.addAction(insert_col_action)
        
        menu.addSeparator()
        
        delete_row_action = QAction("Delete Row", self)
        delete_row_action.triggered.connect(self.delete_row)
        menu.addAction(delete_row_action)
        
        delete_col_action = QAction("Delete Column", self)
        delete_col_action.triggered.connect(self.delete_column)
        menu.addAction(delete_col_action)
        
        menu.addSeparator()
        
        insert_chart_action = QAction("Insert Chart...", self)
        insert_chart_action.triggered.connect(self.insert_chart)
        menu.addAction(insert_chart_action)
        
        insert_image_action = QAction("Insert Image...", self)
        insert_image_action.triggered.connect(self.insert_image)
        menu.addAction(insert_image_action)
        
        menu.exec_(event.globalPos())
    
    def insert_row(self):
        """Insert a row at the current position."""
        pass
    
    def insert_column(self):
        """Insert a column at the current position."""
        pass
    
    def delete_row(self):
        """Delete the current row."""
        pass
    
    def delete_column(self):
        """Delete the current column."""
        pass
    
    def insert_chart(self):
        """Insert a chart based on selected data."""
        pass
    
    def insert_image(self):
        """Insert an image at the current position."""
        pass
