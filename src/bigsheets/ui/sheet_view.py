"""
Sheet View Module

This module provides the UI component for displaying and interacting with a sheet.
"""

from PyQt5.QtWidgets import (
    QTableView, QHeaderView, QAbstractItemView, QMenu, QAction,
    QStyledItemDelegate, QStyleOptionViewItem, QWidget, QDialog
)
from PyQt5.QtCore import Qt, QAbstractTableModel, QModelIndex, QVariant
from PyQt5.QtGui import QColor, QBrush, QPainter

from bigsheets.core.spreadsheet_engine import Sheet
from bigsheets.function_engine.function_manager import FunctionManager
from bigsheets.ui.function_editor import FunctionEditorDialog


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
            if hasattr(cell, "image") and cell.image:
                return ""
            if hasattr(cell, "chart") and cell.chart:
                return ""
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


class SheetItemDelegate(QStyledItemDelegate):
    """
    Custom item delegate for rendering cells with different content types.
    """

    def __init__(self, sheet):
        super().__init__()
        self.sheet = sheet

    def paint(self, painter, option, index):
        row, col = index.row(), index.column()
        cell = self.sheet.get_cell(row, col)

        if hasattr(cell, "image") and cell.image:
            painter.fillRect(option.rect, QBrush(QColor(255, 255, 255)))
            

            from PyQt5.QtGui import QPixmap
            from PyQt5.QtCore import QByteArray, QBuffer, QIODevice
            import base64

            image_data = cell.image["data"]
            if "," in image_data:
                _, data = image_data.split(",", 1)
            else:
                data = image_data

            decoded_data = base64.b64decode(data)
            pixmap = QPixmap()
            pixmap.loadFromData(decoded_data)

            scaled_pixmap = pixmap.scaled(
                option.rect.width(),
                option.rect.height(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )

            x = option.rect.x() + (option.rect.width() - scaled_pixmap.width()) / 2
            y = option.rect.y() + (option.rect.height() - scaled_pixmap.height()) / 2

            painter.drawPixmap(int(x), int(y), scaled_pixmap)

        elif hasattr(cell, "chart") and cell.chart:
            painter.fillRect(option.rect, QBrush(QColor(255, 255, 255)))
            

            from PyQt5.QtGui import QPixmap
            import base64
            
            image_data = cell.chart["image"]
            if "," in image_data:
                _, data = image_data.split(",", 1)
            else:
                data = image_data

            decoded_data = base64.b64decode(data)
            pixmap = QPixmap()
            pixmap.loadFromData(decoded_data)

            scaled_pixmap = pixmap.scaled(
                option.rect.width(),
                option.rect.height(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )

            x = option.rect.x() + (option.rect.width() - scaled_pixmap.width()) / 2
            y = option.rect.y() + (option.rect.height() - scaled_pixmap.height()) / 2

            painter.drawPixmap(int(x), int(y), scaled_pixmap)
        else:
            super().paint(painter, option, index)


class SheetView(QTableView):
    """
    Custom QTableView for displaying and interacting with a sheet.
    """

    def __init__(self, sheet: Sheet):
        super().__init__()
        self.sheet = sheet
        self.model = SheetTableModel(sheet)
        self.setModel(self.model)

        self.delegate = SheetItemDelegate(sheet)
        self.setItemDelegate(self.delegate)

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

        resize_row_action = QAction("Resize Row...", self)
        resize_row_action.triggered.connect(self.resize_row)
        menu.addAction(resize_row_action)

        resize_column_action = QAction("Resize Column...", self)
        resize_column_action.triggered.connect(self.resize_column)
        menu.addAction(resize_column_action)

        menu.addSeparator()

        insert_chart_action = QAction("Insert Chart...", self)
        insert_chart_action.triggered.connect(self.insert_chart)
        menu.addAction(insert_chart_action)

        insert_image_action = QAction("Insert Image...", self)
        insert_image_action.triggered.connect(self.insert_image)
        menu.addAction(insert_image_action)
        
        menu.addSeparator()
        
        insert_function_action = QAction("Insert Function...", self)
        insert_function_action.setShortcut("Ctrl+F")  # Update shortcut to match requirement
        insert_function_action.triggered.connect(self.insert_function)
        menu.addAction(insert_function_action)
        
        modify_function_action = QAction("Modify Function...", self)
        modify_function_action.triggered.connect(self.modify_function)
        menu.addAction(modify_function_action)
        
        manage_functions_action = QAction("Manage Functions...", self)
        manage_functions_action.triggered.connect(self.manage_functions)
        menu.addAction(manage_functions_action)

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

    def resize_row(self):
        """Resize the current row."""
        from PyQt5.QtWidgets import QInputDialog

        current_index = self.currentIndex()
        if current_index.isValid():
            row = current_index.row()
            current_height = self.rowHeight(row)

            new_height, ok = QInputDialog.getInt(
                self,
                "Resize Row",
                f"Enter new height for row {row + 1}:",
                current_height,
                10,  # Min height
                500  # Max height
            )

            if ok:
                self.setRowHeight(row, new_height)

    def resize_column(self):
        """Resize the current column."""
        from PyQt5.QtWidgets import QInputDialog

        current_index = self.currentIndex()
        if current_index.isValid():
            col = current_index.column()
            current_width = self.columnWidth(col)

            col_letter = ""
            temp = col
            while temp >= 0:
                col_letter = chr(65 + (temp % 26)) + col_letter
                temp = temp // 26 - 1

            new_width, ok = QInputDialog.getInt(
                self,
                "Resize Column",
                f"Enter new width for column {col_letter}:",
                current_width,
                10,  # Min width
                500  # Max width
            )

            if ok:
                self.setColumnWidth(col, new_width)

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
            chart_type_str = chart_type.currentText().lower().split()[0]  # Use first word only (bar, line, pie, scatter)

            try:
                chart = chart_engine.create_chart(
                    chart_type=chart_type_str,
                    data=data,
                    title=f"{chart_type.currentText()} - {min_row},{min_col} to {max_row},{max_col}",
                    x_label=f"Row {min_row}",
                    y_label="Values"
                )
                
                self.sheet.add_chart(chart, min_row, min_col)
                self.model.dataChanged.emit(self.model.index(min_row, min_col), self.model.index(min_row, min_col))
            except ValueError as e:
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.warning(self, "Chart Error", f"Failed to create chart: {str(e)}")

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

                self.model.dataChanged.emit(current_index, current_index)
                self.viewport().update()
            except Exception as e:
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.warning(self, "Error", f"Failed to load image: {str(e)}")

    def mouseDoubleClickEvent(self, event):
        """Handle double-click events for auto-sizing."""
        header_h = self.horizontalHeader()
        header_v = self.verticalHeader()
        pos = event.pos()

        if header_h.rect().contains(pos.x(), header_h.height()):
            col = header_h.logicalIndexAt(pos.x())
            self.auto_size_column(col)
            return

        if header_v.rect().contains(header_v.width(), pos.y()):
            row = header_v.logicalIndexAt(pos.y())
            self.auto_size_row(row)
            return

        super().mouseDoubleClickEvent(event)

    def auto_size_column(self, col):
        """Automatically size column based on content."""
        from PyQt5.QtGui import QFontMetrics

        max_width = self.horizontalHeader().sectionSize(col)  # Start with header width

        font_metrics = QFontMetrics(self.font())

        for row in range(self.model.rowCount()):
            cell = self.sheet.get_cell(row, col)

            if (hasattr(cell, "image") and cell.image) or (hasattr(cell, "chart") and cell.chart):
                continue

            if cell.value is not None:
                item_width = font_metrics.width(str(cell.value)) + 20  # Add padding
                max_width = max(max_width, item_width)

        max_width = max(50, min(max_width, 300))

        self.setColumnWidth(col, max_width)

    def auto_size_row(self, row):
        """Automatically size row based on content."""
        from PyQt5.QtGui import QFontMetrics

        max_height = self.verticalHeader().sectionSize(row)  # Start with header height

        font_metrics = QFontMetrics(self.font())

        line_height = font_metrics.height() + 6  # Add padding

        self.setRowHeight(row, line_height)
        
    def insert_function(self):
        """Insert a function at the current position."""
        current_index = self.currentIndex()
        if not current_index.isValid():
            return
        
        row, col = current_index.row(), current_index.column()
        
        function_manager = FunctionManager()
        function_manager.load_templates()  # Explicitly load templates
        templates = function_manager.list_templates()
        
        if not any(t.get("name") == "Sum Columns" for t in templates) or not any(t.get("name") == "Persistent Sum Columns" for t in templates):
            self.create_predefined_templates(function_manager)
            templates = function_manager.list_templates()
        
        if not templates:
            from PyQt5.QtWidgets import QMessageBox
            result = QMessageBox.question(
                self,
                "No Functions Available",
                "No function templates found. Would you like to create one?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            
            if result == QMessageBox.Yes:
                self.manage_functions()
            
            return
        
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QListWidget, QDialogButtonBox, QLabel
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Select Function")
        layout = QVBoxLayout(dialog)
        
        layout.addWidget(QLabel("Select a function template:"))
        
        function_list = QListWidget()
        for template in templates:
            function_list.addItem(template["name"])
            function_list.item(function_list.count() - 1).setData(Qt.UserRole, template["id"])
        
        layout.addWidget(function_list)
        
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        
        if dialog.exec_() == QDialog.Accepted and function_list.currentItem():
            function_id = function_list.currentItem().data(Qt.UserRole)
            
            selected_data = self.get_selected_data()
            
            self.sheet.execute_function(row, col, function_id, selected_data)
            
            self.model.dataChanged.emit(
                self.model.index(row, col),
                self.model.index(row, col)
            )
    
    def modify_function(self):
        """Modify a function at the current cell position."""
        current_index = self.currentIndex()
        if not current_index.isValid():
            return
            
        row, col = current_index.row(), current_index.column()
        cell = self.sheet.get_cell(row, col)
        
        if not hasattr(cell, "function_id") or not cell.function_id:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.information(
                self,
                "No Function Found",
                "This cell does not contain a function. Please select a cell with a function to modify."
            )
            return
            
        function_manager = FunctionManager()
        function_template = function_manager.get_template(cell.function_id)
        
        if not function_template:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(
                self,
                "Function Not Found",
                "The function associated with this cell could not be found."
            )
            return
            
        from PyQt5.QtWidgets import QDialog
        dialog = FunctionEditorDialog(self, function_manager, function_template.id)
        if dialog.exec_() == QDialog.Accepted:
            selected_data = self.get_selected_data()
            self.sheet.execute_function(row, col, function_template.id, selected_data)
            
            self.model.dataChanged.emit(
                self.model.index(row, col),
                self.model.index(row, col)
            )
    
    def manage_functions(self):
        """Open the function template editor."""
        function_manager = FunctionManager()
        function_manager.load_templates()  # Explicitly load templates
        dialog = FunctionEditorDialog(self, function_manager=function_manager)
        dialog.exec_()
    def get_selected_data(self):
        """Extract data from selected cells."""
        selected_ranges = self.selectedIndexes()
        if not selected_ranges:
            return None
            
        min_row = min(idx.row() for idx in selected_ranges)
        max_row = max(idx.row() for idx in selected_ranges)
        min_col = min(idx.column() for idx in selected_ranges)
        max_col = max(idx.column() for idx in selected_ranges)
        
        data = []
        for row in range(min_row, max_row + 1):
            row_data = []
            for col in range(min_col, max_col + 1):
                cell = self.sheet.get_cell(row, col)
                try:
                    if isinstance(cell.value, list):
                        value = cell.value  # Keep lists intact
                    else:
                        value = float(cell.value) if cell.value is not None else 0.0
                except (ValueError, TypeError):
                    value = 0.0  # Default for non-numeric values
                row_data.append(value)
            data.append(row_data)
            
        return data
    def create_predefined_templates(self, function_manager):
        """Create predefined function templates."""
        sum_function_code = '''
def sum_columns(data=None):
    """Sum the values in the selected columns."""
    import pandas as pd
    import numpy as np
    
    if data is None:
        return "Error: No data selected"
    
    try:
        df = pd.DataFrame(data)
        
        if len(df) == 1 or len(df.columns) == 1:
            flat_data = df.values.flatten()
            return float(np.sum(flat_data))
        
        return df.sum().tolist()
    except Exception as e:
        return f"Error: {str(e)}"
'''
        
        avg_function_code = '''
def average_columns(data=None):
    """Calculate the average of values in the selected columns."""
    import pandas as pd
    import numpy as np
    
    if data is None:
        return "Error: No data selected"
    
    try:
        df = pd.DataFrame(data)
        
        if len(df) == 1 or len(df.columns) == 1:
            flat_data = df.values.flatten()
            return float(np.mean(flat_data))
        
        return df.mean().tolist()
    except Exception as e:
        return f"Error: {str(e)}"
'''
        
        benford_function_code = '''
def benfords_law(data=None):
    """Analyze first digits using Benford's Law."""
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    import io, base64
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    
    if data is None:
        return "Error: No data selected"
    
    try:
        df = pd.DataFrame(data)
        flat_data = df.values.flatten()
        
        first_digits = []
        for num in flat_data:
            if num > 0:
                str_num = str(abs(num)).strip('0.')
                if str_num:
                    first_digits.append(int(str_num[0]))
        
        if not first_digits:
            return "No valid positive numbers found in selection"
        
        digit_counts = {}
        for d in range(1, 10):  # Benford's Law applies to digits 1-9
            digit_counts[d] = first_digits.count(d) / len(first_digits)
        
        benford_expected = {
            1: 0.301, 2: 0.176, 3: 0.125, 4: 0.097, 
            5: 0.079, 6: 0.067, 7: 0.058, 8: 0.051, 9: 0.046
        }
        
        fig = Figure(figsize=(8, 6))
        ax = fig.add_subplot(111)
        
        digits = list(range(1, 10))
        observed = [digit_counts.get(d, 0) for d in digits]
        expected = [benford_expected[d] for d in digits]
        
        x = np.arange(len(digits))
        width = 0.35
        
        ax.bar(x - width/2, observed, width, label='Observed')
        ax.bar(x + width/2, expected, width, label='Expected (Benford\\'s Law)')
        
        ax.set_xlabel('First Digit')
        ax.set_ylabel('Frequency')
        ax.set_title('Benford\\'s Law Analysis')
        ax.set_xticks(x)
        ax.set_xticklabels(digits)
        ax.legend()
        
        canvas = FigureCanvasAgg(fig)
        buf = io.BytesIO()
        canvas.print_png(buf)
        data = base64.b64encode(buf.getbuffer()).decode("ascii")
        
        result = {
            "image": f"data:image/png;base64,{data}",
            "summary": {d: {"observed": digit_counts.get(d, 0), "expected": benford_expected[d]} for d in range(1, 10)}
        }
        
        return result
    except Exception as e:
        return f"Error in Benford's analysis: {str(e)}"
'''
        
        try:
            function_manager.create_template("Sum Columns", sum_function_code, 
                                           "Sums values in selected cells")
            function_manager.create_template("Average Columns", avg_function_code, 
                                           "Calculates average of values in selected cells")
            function_manager.create_template("Benford's Law Analysis", benford_function_code, 
                                           "Analyzes first digit frequencies using Benford's Law")
            
            row_sum_function_code = '''
def row_sum(data=None):
    """Sum the values in each row of the selected columns."""
    import pandas as pd
    import numpy as np
    
    if data is None:
        return "Error: No data selected"
    
    try:
        df = pd.DataFrame(data)
        
        row_sums = df.sum(axis=1).tolist()
        
        return row_sums
    except Exception as e:
        return f"Error: {str(e)}"
'''
            
            row_avg_function_code = '''
def row_average(data=None):
    """Calculate the average of values in each row of the selected columns."""
    import pandas as pd
    import numpy as np
    
    if data is None:
        return "Error: No data selected"
    
    try:
        df = pd.DataFrame(data)
        
        row_avgs = df.mean(axis=1).tolist()
        
        return row_avgs
    except Exception as e:
        return f"Error: {str(e)}"
'''
            
            function_manager.create_template("Row Sum", row_sum_function_code, 
                                           "Sums values across each row of selected columns")
            function_manager.create_template("Row Average", row_avg_function_code, 
                                           "Calculates average across each row of selected columns")
            

            persistent_sum_function_code = '''
def persistent_sum_columns(data=None):
    """Sum the values in the selected columns. Updates automatically when source values change."""
    import pandas as pd
    import numpy as np
    import time
    import asyncio
    
    if data is None:
        yield "Error: No data selected"
        return
    
    previous_data = None
    
    while True:
        if data != previous_data:
            previous_data = data.copy() if hasattr(data, "copy") else data
            
            try:
                df = pd.DataFrame(data)
                
                if len(df) == 1 or len(df.columns) == 1:
                    flat_data = df.values.flatten()
                    result = float(np.sum(flat_data))
                else:
                    result = df.sum().tolist()
                
                yield result
            except Exception as e:
                yield f"Error: {str(e)}"
        
        await asyncio.sleep(0.1)
'''
            
            persistent_avg_function_code = '''
def persistent_average_columns(data=None):
    """Calculate the average of values in the selected columns. Updates automatically when source values change."""
    import pandas as pd
    import numpy as np
    import time
    import asyncio
    
    if data is None:
        yield "Error: No data selected"
        return
    
    previous_data = None
    
    while True:
        if data != previous_data:
            previous_data = data.copy() if hasattr(data, "copy") else data
            
            try:
                df = pd.DataFrame(data)
                
                if len(df) == 1 or len(df.columns) == 1:
                    flat_data = df.values.flatten()
                    result = float(np.mean(flat_data))
                else:
                    result = df.mean().tolist()
                
                yield result
            except Exception as e:
                yield f"Error: {str(e)}"
        
        await asyncio.sleep(0.1)
'''

            persistent_row_sum_function_code = '''
def persistent_row_sum(data=None):
    """Sum the values in each row of the selected columns. Updates automatically when source values change."""
    import pandas as pd
    import numpy as np
    import time
    import asyncio
    
    if data is None:
        yield "Error: No data selected"
        return
    
    previous_data = None
    
    while True:
        if data != previous_data:
            previous_data = data.copy() if hasattr(data, "copy") else data
            
            try:
                df = pd.DataFrame(data)
                result = df.sum(axis=1).tolist()
                yield result
            except Exception as e:
                yield f"Error: {str(e)}"
        
        await asyncio.sleep(0.1)
'''
            
            persistent_row_avg_function_code = '''
def persistent_row_average(data=None):
    """Calculate the average of values in each row of the selected columns. Updates automatically when source values change."""
    import pandas as pd
    import numpy as np
    import time
    import asyncio
    
    if data is None:
        yield "Error: No data selected"
        return
    
    previous_data = None
    
    while True:
        if data != previous_data:
            previous_data = data.copy() if hasattr(data, "copy") else data
            
            try:
                df = pd.DataFrame(data)
                result = df.mean(axis=1).tolist()
                yield result
            except Exception as e:
                yield f"Error: {str(e)}"
        
        await asyncio.sleep(0.1)
'''

            persistent_benford_function_code = '''
def persistent_benfords_law(data=None):
    """Analyze first digits using Benford's Law. Updates automatically when source values change."""
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    import io, base64
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    import time
    import asyncio
    
    if data is None:
        yield "Error: No data selected"
        return
        
    previous_data = None
    
    while True:
        if data != previous_data:
            previous_data = data.copy() if hasattr(data, "copy") else data
    
    try:
        df = pd.DataFrame(data)
        flat_data = df.values.flatten()
        
        first_digits = []
        for num in flat_data:
            if num > 0:
                str_num = str(abs(num)).strip('0.')
                if str_num:
                    first_digits.append(int(str_num[0]))
        
        if not first_digits:
            return "No valid positive numbers found in selection"
        
        digit_counts = {}
        for d in range(1, 10):  # Benford's Law applies to digits 1-9
            digit_counts[d] = first_digits.count(d) / len(first_digits)
        
        benford_expected = {
            1: 0.301, 2: 0.176, 3: 0.125, 4: 0.097, 
            5: 0.079, 6: 0.067, 7: 0.058, 8: 0.051, 9: 0.046
        }
        
        fig = Figure(figsize=(8, 6))
        ax = fig.add_subplot(111)
        
        digits = list(range(1, 10))
        observed = [digit_counts.get(d, 0) for d in digits]
        expected = [benford_expected[d] for d in digits]
        
        x = np.arange(len(digits))
        width = 0.35
        
        ax.bar(x - width/2, observed, width, label='Observed')
        ax.bar(x + width/2, expected, width, label='Expected (Benford\\'s Law)')
        
        ax.set_xlabel('First Digit')
        ax.set_ylabel('Frequency')
        ax.set_title('Benford\\'s Law Analysis')
        ax.set_xticks(x)
        ax.set_xticklabels(digits)
        ax.legend()
        
        canvas = FigureCanvasAgg(fig)
        buf = io.BytesIO()
        canvas.print_png(buf)
        data = base64.b64encode(buf.getbuffer()).decode("ascii")
        
        result = {
            "image": f"data:image/png;base64,{data}",
            "summary": {d: {"observed": digit_counts.get(d, 0), "expected": benford_expected[d]} for d in range(1, 10)}
        }
        
        return result
    except Exception as e:
        return f"Error in Benford's analysis: {str(e)}"
'''
            
            function_manager.create_template("Persistent Sum Columns", persistent_sum_function_code, 
                                           "Sums values in selected cells and updates automatically when source values change",
                                           is_persistent=True)
            function_manager.create_template("Persistent Average Columns", persistent_avg_function_code, 
                                           "Calculates average of values in selected cells and updates automatically when source values change",
                                           is_persistent=True)
            function_manager.create_template("Persistent Row Sum", persistent_row_sum_function_code, 
                                           "Sums values across each row of selected columns and updates automatically when source values change",
                                           is_persistent=True)
            function_manager.create_template("Persistent Row Average", persistent_row_avg_function_code, 
                                           "Calculates average across each row of selected columns and updates automatically when source values change",
                                           is_persistent=True)
            function_manager.create_template("Persistent Benford's Law Analysis", persistent_benford_function_code, 
                                           "Analyzes first digit frequencies using Benford's Law and updates automatically when source values change",
                                           is_persistent=True)
            

            function_manager.save_templates()
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Error", f"Failed to create predefined templates: {str(e)}")
