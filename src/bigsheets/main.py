"""
BigSheets Main Module

This module provides the entry point for the BigSheets application.
"""

import sys
import argparse
from PyQt5.QtWidgets import QApplication

from bigsheets.ui.app import BigSheetsApp


def main():
    """Main entry point for the BigSheets application."""
    parser = argparse.ArgumentParser(description="BigSheets - A next-generation spreadsheet application")
    parser.add_argument("--file", help="Open a BigSheets file")
    parser.add_argument("--csv", help="Import a CSV file")
    parser.add_argument("--db", help="Connect to a database")
    args = parser.parse_args()
    
    app = QApplication(sys.argv)
    
    window = BigSheetsApp()
    
    if args.file:
        pass
    
    if args.csv:
        pass
    
    if args.db:
        pass
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
