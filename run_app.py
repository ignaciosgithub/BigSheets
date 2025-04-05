"""
Run script for BigSheets desktop application.
"""

import sys
import os
import traceback
from PyQt5.QtWidgets import QApplication, QMessageBox
from src.bigsheets.ui.app import BigSheetsApp

def handle_exception(exc_type, exc_value, exc_traceback):
    """Handle uncaught exceptions."""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
        
    traceback.print_exception(exc_type, exc_value, exc_traceback)
    error_msg = f"{exc_type.__name__}: {exc_value}"
    print(f"An error occurred: {error_msg}")
    
    app = QApplication.instance()
    if app is not None:
        QMessageBox.critical(None, "Error", error_msg)

if __name__ == "__main__":
    sys.excepthook = handle_exception
    
    os.environ["QT_DEBUG_PLUGINS"] = "1"  # Enable plugin debugging
    
    qt_platforms = os.environ.get("QT_QPA_PLATFORM", "")
    if not qt_platforms:
        os.environ["QT_QPA_PLATFORM"] = "xcb;offscreen"
        
    try:
        app = QApplication(sys.argv)
        window = BigSheetsApp()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"Error starting application: {str(e)}")
        
        if "xcb" in os.environ.get("QT_QPA_PLATFORM", ""):
            print("Attempting to start with offscreen platform...")
            os.environ["QT_QPA_PLATFORM"] = "offscreen"
            try:
                app = QApplication(sys.argv)
                window = BigSheetsApp()
                sys.exit(app.exec_())
            except Exception as e2:
                print(f"Error starting with offscreen platform: {str(e2)}")
                sys.exit(1)
        else:
            sys.exit(1)
