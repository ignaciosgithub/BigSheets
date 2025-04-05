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
        current_index = self.currentIndex()
        if current_index.isValid():
            row = current_index.row()
            self.sheet.insert_row(row)
            self.model.beginInsertRows(QModelIndex(), row, row)
            self.model.endInsertRows()
            self.setRowHeight(row, 25)
    
    def insert_column(self):
        """Insert a column at the current position."""
        current_index = self.currentIndex()
        if current_index.isValid():
            col = current_index.column()
            self.sheet.insert_column(col)
            self.model.beginInsertColumns(QModelIndex(), col, col)
            self.model.endInsertColumns()
            self.setColumnWidth(col, 100)
    
    def delete_row(self):
        """Delete the current row."""
        current_index = self.currentIndex()
        if current_index.isValid():
            row = current_index.row()
            self.sheet.delete_row(row)
            self.model.beginRemoveRows(QModelIndex(), row, row)
            self.model.endRemoveRows()
    
    def delete_column(self):
        """Delete the current column."""
        current_index = self.currentIndex()
        if current_index.isValid():
            col = current_index.column()
            self.sheet.delete_column(col)
            self.model.beginRemoveColumns(QModelIndex(), col, col)
            self.model.endRemoveColumns()
    
    def insert_chart(self):
        """Insert a chart based on selected data."""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QComboBox, QPushButton, QLabel, QHBoxLayout
        from bigsheets.visualization.chart_engine import ChartEngine
        
        selected_ranges = self.selectedIndexes()
        if not selected_ranges:
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Insert Chart")
        layout = QVBoxLayout()
        
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Chart Type:"))
        chart_type = QComboBox()
        chart_type.addItems(["Bar Chart", "Line Chart", "Pie Chart", "Scatter Plot"])
        type_layout.addWidget(chart_type)
        layout.addLayout(type_layout)
        
        button_layout = QHBoxLayout()
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(dialog.reject)
        insert_button = QPushButton("Insert")
        insert_button.clicked.connect(dialog.accept)
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(insert_button)
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        
        if dialog.exec_() == QDialog.Accepted:
            data = []
            min_row = min(idx.row() for idx in selected_ranges)
            max_row = max(idx.row() for idx in selected_ranges)
            min_col = min(idx.column() for idx in selected_ranges)
            max_col = max(idx.column() for idx in selected_ranges)
            
            for row in range(min_row, max_row + 1):
                row_data = []
                for col in range(min_col, max_col + 1):
                    cell = self.sheet.get_cell(row, col)
                    row_data.append(cell.value)
                data.append(row_data)
            
            chart_engine = ChartEngine()
            chart_type_str = chart_type.currentText().lower().replace(" ", "_")
            
            chart = chart_engine.create_chart(
                chart_type=chart_type_str,
                data=data,
                title=f"{chart_type.currentText()} - {min_row},{min_col} to {max_row},{max_col}",
                x_label=f"Row {min_row}",
                y_label="Values"
            )
            
            self.sheet.add_chart(chart, min_row, min_col)
    
    def insert_image(self):
        """Insert an image at the current position."""
        from PyQt5.QtWidgets import QFileDialog
        from bigsheets.image.image_manager import ImageManager
        
        current_index = self.currentIndex()
        if not current_index.isValid():
            return
        
        row, col = current_index.row(), current_index.column()
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Select Image", 
            "", 
            "Image Files (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        
        if file_path:
            image_manager = ImageManager()
            try:
                image_data = image_manager.load_image(file_path)
                
                self.sheet.add_image(image_data, row, col)
                
                self.viewport().update()
            except Exception as e:
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.warning(self, "Error", f"Failed to load image: {str(e)}")
