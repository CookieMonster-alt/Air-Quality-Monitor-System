# Air Quality Monitor System
It is menu driven Python app about Air Quality Index Data


A comprehensive command-line application for monitoring and managing air quality index (AQI) data across different cities. This system allows users to input, store, search, and analyze air quality data with a focus on user-friendly terminal interface and data persistence.

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Data Storage](#data-storage)
- [Menu Options](#menu-options)
- [Admin Functions](#admin-functions)
- [References](#references)
- [Author](#author)
- [License](#license)

## Features

- **Data Entry**: Add new cities and their AQI measurements with automatic timestamp recording
- **City Management**: Choose from existing cities or add new ones dynamically
- **Search Functionality**: Search for specific cities and view their AQI history
- **Data Sorting & Analysis**:
  - Sort cities by AQI (highest to lowest, lowest to highest)
  - Sort cities alphabetically (A-Z, Z-A)
  - Calculate average AQI across all data
- **Administrative Controls**:
  - Database deletion (password-protected)
  - Database backup with timestamped filenames
- **Beautiful Terminal Interface**: Color-coded menus and formatted displays using custom display library
- **Persistent Storage**: Data saved to JSON file with automatic file creation

## Requirements

- **Python Version**: Python 3.x
- **Standard Libraries Used**:
  - `json` - For data serialization and storage
  - `datetime` - For timestamp generation
  - `os` - For file operations
  - `shutil` - For file copying (database backup)

## Dependencies

### Required Files
Both of the following files must be present in the same directory for the application to function properly:

- **`air_quality_index_app.py`** - Main application file
- **`display_library.py`** - Terminal display and formatting utilities (required dependency)

**Note**: No external Python packages are required - all dependencies are built-in standard library modules or the included display_library.py file.

## Installation

1. **Clone the Repository**:
   ```bash
   git clone [repository-url]
   cd [repository-directory]
   ```

2. **Verify Files**:
   Ensure both main files are present in the directory:
   - `air_quality_index_app.py` (Main application)
   - `display_library.py` (Display formatting utilities)

3. **Run the Application**:
   ```bash
   python air_quality_index_app.py
   ```

## Usage

### First-Time Setup
The application automatically creates a `cities.json` file if it doesn't exist when you first run the program.

### Main Menu Navigation
Upon running, you'll be presented with a main menu offering five options:

1. **Data Entry Menu** - Add new AQI records
2. **Search Menu** - Search and display existing city data
3. **Reports and Analysis Menu** - View sorted data and calculations
4. **Admin Menu** - Database management functions
5. **Exit Program** - Safely exit the application

### Example Workflow
1. Start the application
2. Choose option 1 for Data Entry
3. Either select an existing city or add a new one
4. Enter the AQI value (accepts decimal numbers)
5. Data is automatically saved with timestamp
6. Return to main menu or continue entering data

## Project Structure

```
air-quality-monitor/
├── air_quality_index_app.py    # Main application file with menu system and core functions
├── display_library.py          # Display utilities for terminal formatting and UI
├── cities.json                 # Database file (created automatically)
├── backup_file_*.json          # Backup files (created via admin menu)
└── README.md                   # This file
```

### File Descriptions

**`air_quality_index_app.py`**
- Main entry point of the application
- Contains all menu systems and core business logic
- Handles data manipulation, file operations, and calculations

**`display_library.py`**
- Terminal display and formatting utilities
- Provides color-coded output and aligned text display
- Contains functions for screen division and menu presentation
- Reusable for other terminal-based applications

## Data Storage

### JSON Database Structure
The application stores all data in a `cities.json` file with the following structure:

```json
{
  "London": [
    {
      "AQI": 45.2,
      "Timestamp": "2025-11-21 19:30"
    },
    {
      "AQI": 38.7,
      "Timestamp": "2025-11-21 18:45"
    }
  ],
  "Manchester": [
    {
      "AQI": 52.1,
      "Timestamp": "2025-11-21 19:15"
    }
  ]
}
```

### Automatic File Management
- JSON file is created automatically if it doesn't exist
- Timestamps use ISO format with minutes precision
- Data persists between application sessions

## Menu Options

### Data Entry Menu
- Display all existing cities as numbered options
- Option to add new cities dynamically
- Input validation for AQI values (accepts floats)
- Confirmation for multiple entries per city

### Reports and Analysis Menu
- **Sort by AQI**: High to low and low to high
- **Sort by City Name**: Alphabetical A-Z and Z-A
- **Average Calculation**: Overall AQI average with 2 decimal precision
- Formatted table display with borders

### Search Menu
- Case-insensitive city name search
- Displays formatted table of AQI history
- Informative messages for found/not found cities

## Admin Functions

### Delete Database
- Password-protected operation
- Deletes the entire `cities.json` file
- Confirmation dialog to prevent accidental deletion

### Backup Database
- Creates timestamped copies of the database
- Backup format: `backup_file_TIMESTAMP_cities.json`
- No password required for backup operations

## References

The development of this application referenced the following sources:

1. Real Python (2025). How to Write Beautiful Python Code With PEP 8.
2. GeeksforGeeks (2021). Isoformat() Method Of Datetime Class In Python.
3. Fadheli, A. (2024). Keyboard module: Controlling your Keyboard in Python.
4. Python Software Foundation (n.d.). os.path — Common pathname manipulations.
5. Mwiti, D. (2025). Python Try-Except Tutorial: Best Practices and Real-World Examples.
6. GeeksforGeeks (2025). How To Check If Variable Is Empty In Python?.
7. GeeksforGeeks (2025). Check If Value Is Int or Float in Python.
8. KDnuggets (2024). Convert Python Dict to JSON: A Tutorial for Beginners.
9. PyNative (n.d.). Python File Handling.
10. AskPython (n.d.). How to Copy a File in Python.
11. Zaric, D. (2022). How to sort with lambda key function in Python.
12. PythonExamples.org (n.d.). Python JSON to List.
13. Programiz (n.d.). Python String center() Method (With Examples).
14. Tutorials Point (2023). How to Align Text Strings using Python?.
15. Sentry (2023). Print colored text to terminal with Python.

## Author

**Iliya Metodiev**

- **Created**: October 17, 2025 - November 7, 2025
- **Purpose**: School assignment for Air Quality Monitor System
- **Additional Note**: `display_library.py` was developed as a reusable terminal display module

## License

This project was developed for educational purposes as part of a school assignment. All rights reserved.

---

**Important Notes:**
- Both `air_quality_index_app.py` and `display_library.py` must be in the same directory for the application to function properly.
- The display library includes color coding that works best on terminals supporting ANSI color codes.

