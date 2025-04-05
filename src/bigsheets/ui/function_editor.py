"""
Function Editor Module

This module provides a UI for creating and editing function templates.
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QLineEdit, 
    QTextEdit, QPushButton, QListWidget, QListWidgetItem, QMessageBox,
    QSplitter, QWidget
)
from PyQt5.QtCore import Qt, pyqtSignal

from bigsheets.function_engine.function_manager import FunctionManager, FunctionTemplate


class FunctionEditorDialog(QDialog):
    """
    Dialog for creating and editing function templates.
    """
    
    def __init__(self, parent=None, function_manager=None):
        super().__init__(parent)
        
        self.function_manager = function_manager or FunctionManager()
        
        self.setWindowTitle("Function Template Editor")
        self.setMinimumSize(800, 600)
        
        self.init_ui()
        self.load_templates()
    
    def init_ui(self):
        """Initialize the user interface."""
        main_layout = QHBoxLayout(self)
        
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        self.template_list = QListWidget()
        self.template_list.currentItemChanged.connect(self.on_template_selected)
        left_layout.addWidget(QLabel("Templates:"))
        left_layout.addWidget(self.template_list)
        
        template_btn_layout = QHBoxLayout()
        self.new_btn = QPushButton("New")
        self.new_btn.clicked.connect(self.create_new_template)
        self.delete_btn = QPushButton("Delete")
        self.delete_btn.clicked.connect(self.delete_template)
        
        template_btn_layout.addWidget(self.new_btn)
        template_btn_layout.addWidget(self.delete_btn)
        left_layout.addLayout(template_btn_layout)
        
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        form_layout = QFormLayout()
        
        self.name_input = QLineEdit()
        form_layout.addRow("Name:", self.name_input)
        
        self.description_input = QLineEdit()
        form_layout.addRow("Description:", self.description_input)
        
        right_layout.addLayout(form_layout)
        
        right_layout.addWidget(QLabel("Code:"))
        self.code_editor = QTextEdit()
        self.code_editor.setFont(self.code_editor.document().defaultFont())
        self.code_editor.setPlaceholderText("# Define your function here\n\ndef my_function(value):\n    # Your code here\n    return value * 2")
        right_layout.addWidget(self.code_editor)
        
        button_layout = QHBoxLayout()
        self.test_btn = QPushButton("Test")
        self.test_btn.clicked.connect(self.test_function)
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.save_template)
        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.close)
        
        button_layout.addWidget(self.test_btn)
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.close_btn)
        right_layout.addLayout(button_layout)
        
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([200, 600])
        
        main_layout.addWidget(splitter)
        
        self.current_template_id = None
    
    def load_templates(self):
        """Load templates into the list."""
        self.template_list.clear()
        
        templates = self.function_manager.list_templates()
        for template in templates:
            item = QListWidgetItem(template["name"])
            item.setData(Qt.UserRole, template["id"])
            self.template_list.addItem(item)
    
    def on_template_selected(self, current, previous):
        """Handle template selection."""
        if not current:
            self.current_template_id = None
            self.name_input.setText("")
            self.description_input.setText("")
            self.code_editor.setText("")
            return
        
        template_id = current.data(Qt.UserRole)
        template = self.function_manager.get_template(template_id)
        
        if template:
            self.current_template_id = template_id
            self.name_input.setText(template.name)
            self.description_input.setText(template.description)
            self.code_editor.setText(template.code)
    
    def create_new_template(self):
        """Create a new template."""
        try:
            template = self.function_manager.create_template(
                "New Function", 
                "def my_function(x):\n    return x * 2"
            )
            
            item = QListWidgetItem(template.name)
            item.setData(Qt.UserRole, template.id)
            self.template_list.addItem(item)
            self.template_list.setCurrentItem(item)
            
            self.function_manager.save_templates()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create template: {str(e)}")
    
    def delete_template(self):
        """Delete the current template."""
        if not self.current_template_id:
            return
        
        confirm = QMessageBox.question(
            self, 
            "Confirm Delete", 
            "Are you sure you want to delete this template?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            self.function_manager.delete_template(self.current_template_id)
            self.function_manager.save_templates()
            self.load_templates()
            self.current_template_id = None
    
    def save_template(self):
        """Save the current template."""
        name = self.name_input.text().strip()
        description = self.description_input.text().strip()
        code = self.code_editor.toPlainText().strip()
        
        if not name:
            QMessageBox.warning(self, "Validation Error", "Function name is required")
            return
        
        if not code:
            QMessageBox.warning(self, "Validation Error", "Function code is required")
            return
        
        try:
            if self.current_template_id:
                self.function_manager.update_template(
                    self.current_template_id,
                    name=name,
                    code=code,
                    description=description
                )
            else:
                template = self.function_manager.create_template(
                    name, code, description
                )
                self.current_template_id = template.id
            
            self.function_manager.save_templates()
            self.load_templates()
            
            QMessageBox.information(self, "Success", "Function template saved successfully")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save template: {str(e)}")
    
    def test_function(self):
        """Test the current function."""
        code = self.code_editor.toPlainText().strip()
        
        if not code:
            QMessageBox.warning(self, "Validation Error", "Function code is required")
            return
        
        try:
            temp_template = FunctionTemplate("Test", code)
            
            temp_template.compile()
            
            QMessageBox.information(self, "Success", "Function compiled successfully")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Function test failed: {str(e)}")
