"""
Run script for BigSheets desktop application.
"""

import sys
from PyQt5.QtWidgets import QApplication
from src.bigsheets.ui.app import BigSheetsApp

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BigSheetsApp()
    sys.exit(app.exec_())
