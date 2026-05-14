"""This is Air Quality Monitor System Program

This program allows to user enter the cities and
their air quality index data (AQI) of the UK or any other country.
It saves the data in a JSON file.

Some of the program features:

Allow user to enter city name and aqi data
It saves data in JSON file with timestamp
It allows user to make search by city name
It sort data by AQI higer to lower, lower to higher
It sort data by City name A to Z and Z to A
It shows avarage AQI data
It allows user to delete database
It allows user to backup database

This is code written by iliya METODIEV for school assignment
Started Date : 17/10/2025
Finished Date : 7/11/2025

References checked during development of this program:

1- Real Python (2025) How to Write Beautiful Python Code With PEP 8.
Available at: https://realpython.com/python-pep8/

2- GeeksforGeeks (2021) Isoformat() Method Of Datetime Class In Python.
Available at: https://www.geeksforgeeks.org/python/isoformat-method-of-datetime-class-in-python/

3- Fadheli, A. (2024) Keyboard module: Controlling your Keyboard in Python.
Available at: https://thepythoncode.com/article/control-keyboard-python

4- Python Software Foundation (n.d.) os.path — Common pathname manipulations.
Available at: https://docs.python.org/3/library/os.path.html

5- Mwiti, D. (2025) Python Try-Except Tutorial: Best Practices and Real-World Examples.
Available at: https://www.datacamp.com/tutorial/python-try-except

6- GeeksforGeeks (2025) How To Check If Variable Is Empty In Python?.
Available at: https://www.geeksforgeeks.org/python/how-to-check-if-variable-is-empty-in-python/

7- GeeksforGeeks (2025) Check If Value Is Int or Float in Python.
Available at: https://www.geeksforgeeks.org/python/check-if-value-is-int-or-float-in-python/

8- KDnuggets (2024) Convert Python Dict to JSON: A Tutorial for Beginners.
Available at: https://www.kdnuggets.com/convert-python-dict-to-json-a-tutorial-for-beginners

9- PyNative (n.d.) Python File Handling.
Available at: https://pynative.com/python/file-handling/

10- AskPython (n.d.) How to Copy a File in Python.
Available at: https://www.askpython.com/python/copy-a-file-in-python

11- Zaric, D. (2022) How to sort with lambda key function in Python.
Available at: https://blogboard.io/blog/knowledge/python-sorted-lambda/

12- PythonExamples.org (n.d.) Python JSON to List.
Available at: https://pythonexamples.org/python-json-to-list/

13- Programiz (n.d.) Python String center() (With Examples).
Available at: https://www.programiz.com/python-programming/methods/string/center

14- Tutorials Point (2023) How to Align Text Strings using Python?.
Available at: https://www.tutorialspoint.com/how-to-align-text-strings-using-python

15- Sentry (2023) Print colored text to terminal with Python.
Available at: https://sentry.io/answers/print-colored-text-to-terminal-with-python/
"""

# This is a simple comment added for testing purposes

# ------------------ Import Libraries ------------------|

import json
import datetime
import os, shutil
import tui_engine as tui
from data_manager import DatabaseManager, CityRecord, get_epa_category
import api_integration
import ai_engine

# ------------------ Constant Variables ------------------|

DB_FILE = "aqi_data.db"
db = DatabaseManager(DB_FILE)

# Reference 15
# Color Codes
BLACK = "\033[30m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
LIGHT_GRAY = "\033[37m"
DARK_GRAY = "\033[90m"
BRIGHT_RED = "\033[91m"
BRIGHT_GREEN = "\033[92m"
BRIGHT_YELLOW = "\033[93m"
BRIGHT_BLUE = "\033[94m"
BRIGHT_MAGENTA = "\033[95m"
BRIGHT_CYAN = "\033[96m"
WHITE = "\033[97m"
RESET = "\033[0m"
BOLD = "\033[1m"
UNDERLINE = "\033[4m"
BRIGHT_WHITE = "\033[1m\033[97m"

# ------------------ Data Functions ------------------|
# This is the data functions block. It includes functions for data entry,
# updating, finding, and deleting. It is used for data manipulation.


def time_stamp():
    time_stamp = datetime.datetime.now()  # Reference 2
    return time_stamp.isoformat(" ", "minutes")

def print_msg(msg_type: str, text: str):
    tui.show_msg(msg_type, text)

# |--------------- End of Data Functions --------------|


# |------------------ File Functions ------------------|
# Reference 9
"""
This section contains all functions for managing the SQLite database file.
It handles deleting the database file and backing it up.
"""

def delete_database():
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
        tui.show_msg("success", "Database deleted successfully!")
    else:
        tui.show_msg("error", "No database found to delete")

# Reference 10
def backup_database(source_file):
    if os.path.exists(source_file):
        backup_file_name = f"backup_file_{time_stamp().replace(':', '-').replace(' ', '_')}_" + source_file
        shutil.copy(source_file, backup_file_name)
        tui.show_msg("success", f"Database backed up to {backup_file_name}")
    else:
        tui.show_msg("error", "No database found to backup")


# |--------------- End of File Functions --------------|


# |------------- Report/Analysis Functions ------------|

# Reference 11
# Reference 14
"""
This functions for sorting and analyzing the AQI data.
It can sort all records by AQI value (highest or lowest), by city name
(A-Z or Z-A), and calculate the overall average AQI from all records.
"""

def sort_by_highest_aqi():
    list_data = db.get_all_records()
    sorted_list = sorted(list_data, key=lambda x: x.aqi_value, reverse=True)
    rows = [[r.city_name, r.aqi_value, r.timestamp] for r in sorted_list]
    tui.show_table('Sorted by highest AQI', ['City', 'AQI', 'Timestamp'], rows)

def sort_by_lowest_aqi():
    list_data = db.get_all_records()
    sorted_list = sorted(list_data, key=lambda x: x.aqi_value, reverse=False)
    rows = [[r.city_name, r.aqi_value, r.timestamp] for r in sorted_list]
    tui.show_table('Sorted by lowest AQI', ['City', 'AQI', 'Timestamp'], rows)

def sort_by_city_name_az():
    list_data = db.get_all_records()
    sorted_list = sorted(list_data, key=lambda x: x.city_name, reverse=False)
    rows = [[r.city_name, r.aqi_value, r.timestamp] for r in sorted_list]
    tui.show_table('Sorted by city name  (A-Z)', ['City', 'AQI', 'Timestamp'], rows)

def sort_by_city_name_za():
    list_data = db.get_all_records()
    sorted_list = sorted(list_data, key=lambda x: x.city_name, reverse=True)
    rows = [[r.city_name, r.aqi_value, r.timestamp] for r in sorted_list]
    tui.show_table('Sorted by city name  (Z-A)', ['City', 'AQI', 'Timestamp'], rows)


def calculate_average_aqi():
    aiq_sum = 0
    aiq_count = 0
    list_data = db.get_all_records()
    if not list_data:
        return 0
    for a in list_data:
        aiq_sum += a.aqi_value
        aiq_count += 1
    average = aiq_sum / aiq_count
    return average


# |--------- End of Report/Analysis Functions ---------|


# |---------------- Admin Functions ------------------|


def check_admin_password(password):
    if password == "password":
        return True
    else:
        return False


# |------------- End of Admin Functions ---------------|


# |--------- Main Menu and Display Functions ----------|



# |---------------------------------------------------------------------------|
# Main Menu Starts Here
"""
Menus:

- main_menu: Displays the primary options and directs the user.
- menu_1: Manages data entry for new cities and AQI records.
- menu_2: Allows users to search for data on a specific city.
- menu_3: Provides options for viewing sorted reports and data analysis.
- menu_4: Contains administrative functions like deleting or backing up data.
"""

def main_menu():
    while True:
        try:
            tui.clear_screen()
            options = [
                ("1", "Data Entry Menu"),
                ("2", "Search Menu"),
                ("3", "Analytics & Reports"),
                ("4", "Admin Menu"),
                ("5", "Fetch Historical Data"),
                ("6", "[red]Exit Program[/]")
            ]
            tui.show_menu("AIR QUALITY MONITOR SYSTEM", options)
            choice = tui.get_input("Please choose an option from the menu")

            if choice == "1":
                menu_1()
            elif choice == "2":
                menu_2()
            elif choice == "3":
                menu_3()
            elif choice == "4":
                menu_4()
            elif choice == "5":
                menu_5()
            elif choice == "6":
                exit_choice = tui.get_input("Do you want to Exit the program? (Y/N)", choices=["Y", "N", "y", "n"])
                if exit_choice.upper() == "Y":
                    tui.show_msg("info", "You logged out!!")
                    break
                elif exit_choice.upper() == "N":
                    continue
            elif choice == "":
                break
            else:
                tui.show_msg("error", "Invalid choice. Please try again!!")
                tui.get_input("Press Enter to continue...")
        except KeyboardInterrupt:
            tui.show_msg("info", "Action cancelled. Returning to main menu...")
            tui.get_input("Press Enter to continue")
            continue
            


# Main Menu Ends Here
# |---------------------------------------------------------------------------|


# |---------------------------------------------------------------------------|
# Data Entry Menu Starts Here
def menu_1():
    while True:
        try:
            tui.clear_screen()
            all_records = db.get_all_records()
            cities_from_db = list(set([record.city_name for record in all_records]))
            cities_from_db.sort()

            options = []
            for idx, city in enumerate(cities_from_db, 1):
                options.append((str(idx), city))

            add_new_city_option = len(cities_from_db) + 1
            options.append((str(add_new_city_option), "[blue]Add New City[/]"))

            tui.show_menu("DATA ENTRY MENU", options)
            city_number_input = tui.get_input("Choose a city number, or type 'exit'")

            if city_number_input.lower() == "exit" or city_number_input == "":
                return

            city_name = None
            if city_number_input.isdigit():
                city_number = int(city_number_input)
                if 0 < city_number <= len(cities_from_db):
                    city_name = cities_from_db[city_number - 1]
                elif city_number == add_new_city_option:
                    while True:
                        raw_city_input = tui.get_input("Enter the name of the new city to add:")
                        clean_city_input = raw_city_input.strip()

                        if clean_city_input == "":
                            city_name = None
                            break

                        if clean_city_input.isdigit():
                            tui.show_msg("error", "City name cannot be only numbers. Please try again.")
                            continue

                        new_city_name = clean_city_input.title()

                        if new_city_name in cities_from_db:
                            tui.show_msg("info", f"{new_city_name} already exists in the list")
                            break
                        else:
                            city_name = new_city_name
                            break
            if city_name:
                while True:
                    aqi_input = tui.get_input(f"Enter air quality index for [green]{city_name}[/]:")

                    if aqi_input == "":
                        return

                    try:
                        aqi = float(aqi_input)
                        if aqi < 0 or aqi > 500:
                            tui.show_msg("error", "AQI must be between 0 and 500. Please try again.")
                            continue

                        new_record = CityRecord(city_name=city_name, aqi_value=aqi, timestamp=time_stamp())
                        is_new = db.add_record(new_record)
                        if is_new:
                            tui.show_msg("success", f"AQI data for {city_name} saved successfully!")
                        else:
                            tui.show_msg("info", f"AQI data for {city_name} at this timestamp already exists.")

                        continue_choice = tui.get_input(f"Do you want to add more data to {city_name}? (Y/N)", choices=["Y", "N", "y", "n"])
                        if continue_choice.upper() == "N" or continue_choice == "":
                            break
                    except ValueError:
                        tui.show_msg("error", "Invalid AQI. Please enter a number between 0 and 500.")
            else:
                tui.show_msg("error", "Invalid choice.")
                tui.get_input("Press Enter to try again")

        except KeyboardInterrupt:
            tui.show_msg("info", "Action cancelled. Returning to menu...")
            tui.get_input("Press Enter to continue")
            return


# Data Entry Menu End Here
# |---------------------------------------------------------------------------|


# |---------------------------------------------------------------------------|
# Search Menu Start Here
def menu_2():
    while True:
        try:
            tui.clear_screen()
            all_records = db.get_all_records()
            cities_from_db = list(set([record.city_name for record in all_records]))

            tui.show_menu("SEARCH MENU", []) # Just for title consistency
            input_city = tui.get_input("Enter city name to search (Local or WAQI Live)")
            if input_city == '':
                return
            city_name = input_city.title()

            # Step 1: WAQI API Live Search
            stations = api_integration.search_city_stations(city_name)
            if stations:
                tui.show_msg("info", f"Found {len(stations)} live stations for {city_name} via WAQI API")

                st_options = []
                for idx, st in enumerate(stations[:5]):
                    st_options.append((str(idx + 1), st['station']['name']))

                tui.show_menu("Live WAQI Stations", st_options)

                choice = tui.get_input(f"Choose a station (1-{min(5, len(stations))}) or press Enter to skip to local DB")
                if choice.isdigit() and 1 <= int(choice) <= len(stations):
                    selected_st = stations[int(choice) - 1]
                    uid = selected_st['uid']

                    with tui.create_spinner(f"Fetching live AQI data for [cyan]{selected_st['station']['name']}[/]...") as progress:
                        st_data = api_integration.get_station_aqi(uid)

                    live_aqi = st_data.get("aqi")
                    if live_aqi and isinstance(live_aqi, (int, float)) or (isinstance(live_aqi, str) and live_aqi.isdigit()):
                        aqi_val = float(live_aqi)

                        # Save to local DB
                        new_record = CityRecord(city_name=city_name, aqi_value=aqi_val, timestamp=time_stamp())
                        db.add_record(new_record)

                        tui.show_msg("info", f"Live WAQI: [bold white]{aqi_val}[/] ({get_epa_category(aqi_val)})")
                        tui.show_msg("success", "Live data saved to local database.")
                    else:
                        tui.show_msg("error", "No valid AQI data available for this station currently.")

                    tui.get_input("Press Enter to return to the main menu!")
                    return
            else:
                tui.show_msg("info", f"No live WAQI stations found for {city_name}. Searching local DB...")

            # Step 2: Local DB Search Fallback
            if city_name in cities_from_db:
                tui.show_msg("success", f"{city_name} is found in the local database!")
                choice = tui.get_input("Do you want to see the AQI data? (Y/N)", choices=["Y", "N", "y", "n"])

                if choice.upper() == "Y":
                    records = [record for record in all_records if record.city_name == city_name]
                    if not records:
                        tui.show_msg("info", f"No AQI records found for {city_name}.")
                    else:
                        rows = [[city_name, str(r.aqi_value), r.timestamp] for r in records]
                        tui.show_table(f"Records for {city_name}", ['City', 'AQI', 'Timestamp'], rows)
                        tui.get_input("Press Enter to return to the main menu!")
            else:
                tui.show_msg("error", f"{city_name} is not found in the local database!")
                tui.get_input("Press Enter to return to the main menu!")
            return
        except KeyboardInterrupt:
            tui.show_msg("info", "Action cancelled. Returning to menu...")
            tui.get_input("Press Enter to continue")
            return


# Search Menu End Here
# |---------------------------------------------------------------------------|


# |---------------------------------------------------------------------------|
# Reports and Analysis Menu Start Here
def menu_3():
    while True:
        try:
            tui.clear_screen()
            options = [
                ("1", "Display from highest AQI data"),
                ("2", "Display from lowest AQI data"),
                ("3", "Display from city name (A-Z)"),
                ("4", "Display from city name (Z-A)"),
                ("5", "Executive Analytics Summary"),
                ("6", "[magenta]Run AI Engine Prediction[/]"),
                ("7", "[red]Return main menu[/]")
            ]
            tui.show_menu("ANALYTICS & REPORTS", options)
            user_choice = tui.get_input("Please choose an option from the menu")

            if user_choice == "":
                return
            elif user_choice == "1":
                tui.clear_screen()
                sort_by_highest_aqi()
                tui.get_input("Press Enter to return to the main menu")
                continue
            elif user_choice == "2":
                tui.clear_screen()
                sort_by_lowest_aqi()
                tui.get_input("Press Enter to return to the main menu")
                continue
            elif user_choice == "3":
                tui.clear_screen()
                sort_by_city_name_az()
                tui.get_input("Press Enter to return to the main menu")
                continue
            elif user_choice == "4":
                tui.clear_screen()
                sort_by_city_name_za()
                tui.get_input("Press Enter to return to the main menu")
                continue
            elif user_choice == "5":
                tui.clear_screen()

                avg_aqi = db.get_average_aqi()
                highest_city = db.get_city_with_highest_aqi()

                tui.show_msg("info", f"Average System AQI: {avg_aqi:.2f} ({get_epa_category(avg_aqi)})")

                if highest_city:
                    tui.show_msg("error", f"Highest Pollution: {highest_city[0]} - {highest_city[1]} ({get_epa_category(highest_city[1])})")
                else:
                    tui.show_msg("info", "Highest Pollution: No records available")

                tui.get_input("Press Enter to return to the Reports menu")
                continue
            elif user_choice == "6":
                tui.clear_screen()
                input_city = tui.get_input("Please enter city name for AI Prediction")
                if input_city == "":
                    continue
                city_name = input_city.title()

                tui.show_msg("info", f"Running AI Analysis on {city_name}...")
                predicted_aqi = ai_engine.predict_next_aqi(city_name)

                if predicted_aqi == 0.0:
                    tui.show_msg("error", "Insufficient data to run prediction.")
                else:
                    decision = ai_engine.evaluate_prediction(predicted_aqi)

                    # Print dynamically
                    tui.show_msg("info", f"Predicted AQI: [bold white]{predicted_aqi}[/] ({get_epa_category(predicted_aqi)})")

                    if "NORMAL" in decision:
                        tui.show_msg("success", decision)
                    else:
                        tui.show_msg("error", decision)

                    # Save AI state
                    db.add_prediction(
                        city_name=city_name,
                        predicted_aqi=predicted_aqi,
                        prediction_date=time_stamp(),
                        target_date=time_stamp(), # For demo purposes, we project next current instance
                        decision_made=decision
                    )

                tui.get_input("Press Enter to return to the Reports menu")
                continue
            elif user_choice == "7":
                break
            else:
                tui.show_msg("error", "Invalid choice. Please try again!!")
                tui.get_input("Press Enter to continue...")
                continue
        except KeyboardInterrupt:
            tui.show_msg("info", "Action cancelled. Returning to menu...")
            tui.get_input("Press Enter to continue")
            return


# Reports and Analysis Menu End Here
# |---------------------------------------------------------------------------|


# |---------------------------------------------------------------------------|
# Admin Menu Sarts Here
def menu_4():
    while True:
        try:
            tui.clear_screen()
            options = [
                ("1", "Delete Database"),
                ("2", "Backup Database"),
                ("3", "Export Database to JSON"),
                ("4", "[red]Return main menu[/]")
            ]
            tui.show_menu("ADMIN MENU", options)
            user_choice = tui.get_input("Please choose an option from the menu")

            if user_choice == "":
                return
            elif user_choice == "1":
                password = tui.get_input("Please enter admin password to continue", password=True)
                if check_admin_password(password):
                    tui.show_msg("success", "Password correct")
                    choice = tui.get_input("Do you want to delete database? (Y/N)", choices=["Y", "N", "y", "n"])
                    if choice.upper() == "Y":
                        delete_database()
                    else:
                        tui.show_msg("info", "Database not deleted!")
                    tui.get_input("Press Enter to return to the admin menu")
                else:
                    tui.show_msg("error", "Password not correct!")
                    tui.get_input("Press Enter to return to the admin menu")
            elif user_choice == "2":
                choice = tui.get_input("Do you want to backup database? (Y/N)", choices=["Y", "N", "y", "n"])
                if choice.upper() == "Y":
                    backup_database(DB_FILE)
                else:
                    tui.show_msg("info", "Database not backed up!")
                tui.get_input("Press Enter to return to the admin menu")
            elif user_choice == "3":
                filename = db.export_to_json()
                tui.show_msg("success", f"Data successfully exported to {filename}")
                tui.get_input("Press Enter to return to the admin menu")
            elif user_choice == "4":
                break
            else:
                tui.show_msg("error", "Invalid choice!")
                tui.get_input("Press Enter to return to the admin menu")
        except KeyboardInterrupt:
            tui.show_msg("info", "Action cancelled. Returning to menu...")
            tui.get_input("Press Enter to continue")
            return

# Admin Menu Ends Here
# |---------------------------------------------------------------------------|

def menu_5():
    import random
    import time
    from datetime import timedelta

    while True:
        try:
            tui.clear_screen()
            options = [
                ("1", "Last 7 Days"),
                ("2", "Last 30 Days"),
                ("3", "Custom Date Range"),
                ("4", "[red]Return main menu[/]")
            ]
            tui.show_menu("FETCH HISTORICAL DATA", options)
            user_choice = tui.get_input("Please choose an option from the menu")

            if user_choice == "":
                return
            elif user_choice == "4":
                break

            if user_choice not in ["1", "2", "3"]:
                tui.show_msg("error", "Invalid choice. Please try again!!")
                tui.get_input("Press Enter to continue...")
                continue

            input_city = tui.get_input("Enter city name to fetch data for")
            if input_city == "":
                continue
            city_name = input_city.strip().title()

            # Determine Date Range
            today = datetime.datetime.now().date()
            start_date = None
            end_date = today

            if user_choice == "1":
                start_date = today - timedelta(days=7)
            elif user_choice == "2":
                start_date = today - timedelta(days=30)
            elif user_choice == "3":
                while True:
                    try:
                        s_date_str = tui.get_input("Enter start date (YYYY-MM-DD)")
                        if s_date_str == "":
                            break
                        start_date = datetime.datetime.strptime(s_date_str, "%Y-%m-%d").date()

                        e_date_str = tui.get_input("Enter end date (YYYY-MM-DD)")
                        if e_date_str == "":
                            break
                        end_date = datetime.datetime.strptime(e_date_str, "%Y-%m-%d").date()

                        if start_date > end_date:
                            tui.show_msg("error", "Start date cannot be after end date.")
                            continue

                        break
                    except ValueError:
                        tui.show_msg("error", "Invalid date format. Please use YYYY-MM-DD.")

                if not start_date or not end_date:
                    continue # Cancelled out of custom date input

            tui.show_msg("info", f"Locating WAQI anchor data for {city_name}...")
            base_aqi = api_integration.get_station_aqi_by_name(city_name)

            if base_aqi == 0.0:
                tui.show_msg("error", f"Could not find live anchor data for {city_name}. Proceeding with default baseline of 50.0")
                base_aqi = 50.0

            current_date = start_date
            inserted_count = 0

            with tui.create_spinner("Starting historical fetch simulation...") as progress:
                task_id = progress.add_task("Starting historical fetch simulation...", total=None)
                while current_date <= end_date:
                    # Update progress description
                    progress.update(task_id, description=f"Fetching data for [cyan]{current_date.strftime('%Y-%m-%d')}[/]...")
                    time.sleep(0.2)

                    # Apply +/- 5% change
                    variation = random.uniform(-0.05, 0.05)
                    simulated_aqi = round(base_aqi * (1 + variation), 1)

                    # Ensure within 0-500 bounds
                    simulated_aqi = max(0.0, min(500.0, simulated_aqi))

                    timestamp_str = datetime.datetime.combine(current_date, datetime.time(12, 0)).isoformat(" ", "minutes")
                    record = CityRecord(city_name=city_name, aqi_value=simulated_aqi, timestamp=timestamp_str)

                    is_new = db.add_record(record)
                    if is_new:
                        inserted_count += 1

                    # Update base for next day for a random walk feel
                    base_aqi = simulated_aqi
                    current_date += timedelta(days=1)

            tui.show_msg("success", f"Successfully fetched and added {inserted_count} new unique records.")
            tui.get_input("Press Enter to return to the Historical Data menu...")

        except KeyboardInterrupt:
            tui.show_msg("info", "Action cancelled. Returning to menu...")
            tui.get_input("Press Enter to continue")
            return


# |----------------- End of Main Menu and Display Functions ------------------|

if __name__ == "__main__":
    main_menu()