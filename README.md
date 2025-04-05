# BigSheets

A next-generation spreadsheet application that goes beyond traditional cell-based editing by supporting multiple data sources (CSV files and relational databases), interactive graph/chart generation, embedded images, and advanced multi‐sheet workflows with independent undo/redo histories.

## Overview

### 1. Purpose
- Build a next-generation spreadsheet application that goes beyond traditional cell-based editing by supporting multiple data sources (CSV files and relational databases), interactive graph/chart generation, embedded images, and advanced multi‐sheet workflows with independent undo/redo histories.

### 2. Scope
- The software is designed as a cross-platform desktop and/or web application, delivering rich data manipulation, advanced visualization, and an intuitive user interface.
- The product is targeted for business analysts, data scientists, educators, and any users requiring efficient data import/export, visualization, and document management.

## System Architecture

### 1. Overall Architecture
- The solution adopts a modular, layered architecture:
  - **Front-End/UI Layer**: A responsive interactive user interface using Python frameworks (such as PyQt, Tkinter, or web frameworks like Flask/Django with JavaScript frontend).
  - **Application Logic Layer**: Handles core spreadsheet functionalities, data import, graph generation, image handling, and command/undo management.
  - **Data Access Layer**: Abstracts data import from CSV, SQL/NoSQL databases, and manages any caching or temporary storage.
  - **Persistence Layer**: Manages file storage (proprietary file format and/or standard formats) and the undo/redo history logs per sheet.
- Modules communicate via well-defined interfaces and data models (e.g., JSON/XML for configuration and state persistence).

### 2. Key Components
- **CSV Importer Module**: Handles parsing and importing CSV files with various formats and configurations.
- **Database Connector Module**: Provides connectivity to SQL and NoSQL databases.
- **Spreadsheet Engine**: Manages grid model with cell calculation, formatting, and multi-sheet support.
- **Graphics Engine**: Handles interactive charting and graph generation.
- **Image Manager**: Allows insertion, sizing, moving, and anchoring images within sheets.
- **Command & Undo Manager**: Supports independent undo stacks per spreadsheet/tab.
- **Plugin/API Interface Layer**: Provides extensibility for future enhancements.

## Installation

### Dependencies

#### Linux
If you're running on Linux, you may need to install the following packages for Qt to function correctly:

```bash
sudo apt-get install -y libxcb1 libxcb-xinerama0 libxcb-icccm4 libxcb-image0 libxcb-keysyms1 libxcb-render-util0 libxcb-randr0 libxcb-xkb1 libxkbcommon-x11-0
```

#### Environment Variables
The application uses the following environment variables:

- `QT_QPA_PLATFORM`: Specifies the Qt platform plugin to use. Default is "xcb;offscreen" which will try xcb first, then fall back to offscreen.
- `QT_DEBUG_PLUGINS`: Set to "1" to enable debugging of Qt plugins.

*More installation instructions coming soon*

## Usage

*Coming soon*

## Contributing

*Coming soon*

## License

*Coming soon*
