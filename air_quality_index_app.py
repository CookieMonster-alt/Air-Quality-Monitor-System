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

# ------------------ Import Libraries ------------------|

import json
import datetime
import os, shutil
import display_library as dl
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
    if msg_type == 'error':
        color = BRIGHT_RED
    elif msg_type == 'success':
        color = BRIGHT_GREEN
    elif msg_type == 'info':
        color = BRIGHT_YELLOW
    else:
        color = RESET

    formatted_msg = f"{color}{text}{RESET}"
    dl.print_middle_middle(formatted_msg)

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
        print("Database deleted successfully!")
    else:
        print("No database found to delete")

# Reference 10
def backup_database(source_file):
    if os.path.exists(source_file):
        backup_file_name = f"backup_file_{time_stamp().replace(':', '-').replace(' ', '_')}_" + source_file
        shutil.copy(source_file, backup_file_name)
        dl.print_middle_middle(f"Database backed up to {GREEN}{backup_file_name}{RESET}")
    else:
        print("No database found to backup")


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
    dl.menu_title_centered('Sorted by highest AQI'.upper(), '=', YELLOW)
    dl.print_middle_middle(dl.draw_border_head('-','|'))
    dl.print_middle_middle(dl.create_head_titles(['City', 'AQI', 'Timestamp']))
    dl.print_middle_middle(dl.draw_border_head('-','|'))
    for each_item in sorted_list:
        
        data = [
            f'{each_item.city_name}',
            f'{each_item.aqi_value}',
            f'{each_item.timestamp}'
        ]
        dl.print_middle_middle(dl.create_data_in_middle_row(data))
        dl.print_middle_middle(dl.draw_border_head('-','|'))


def sort_by_lowest_aqi():
    list_data = db.get_all_records()
    sorted_list = sorted(list_data, key=lambda x: x.aqi_value, reverse=False)
    dl.menu_title_centered('Sorted by lowest AQI'.upper(), '=', YELLOW)
    dl.print_middle_middle(dl.draw_border_head('-','|'))
    dl.print_middle_middle(dl.create_head_titles(['City', 'AQI', 'Timestamp']))
    dl.print_middle_middle(dl.draw_border_head('-','|'))
    for each_item in sorted_list:
        
        data = [
            f'{each_item.city_name}',
            f'{each_item.aqi_value}',
            f'{each_item.timestamp}'
        ]
        dl.print_middle_middle(dl.create_data_in_middle_row(data))
        dl.print_middle_middle(dl.draw_border_head('-','|'))


def sort_by_city_name_az():
    list_data = db.get_all_records()
    sorted_list = sorted(list_data, key=lambda x: x.city_name, reverse=False)
    dl.menu_title_centered('Sorted by city name  (A-Z)'.upper(), '=', YELLOW)
    dl.print_middle_middle(dl.draw_border_head('-','|'))
    dl.print_middle_middle(dl.create_head_titles(['City', 'AQI', 'Timestamp']))
    dl.print_middle_middle(dl.draw_border_head('-','|'))
    for each_item in sorted_list:
        
        data = [
            f'{each_item.city_name}',
            f'{each_item.aqi_value}',
            f'{each_item.timestamp}'
        ]
        dl.print_middle_middle(dl.create_data_in_middle_row(data))
        dl.print_middle_middle(dl.draw_border_head('-','|'))


def sort_by_city_name_za():
    list_data = db.get_all_records()
    sorted_list = sorted(list_data, key=lambda x: x.city_name, reverse=True)
    dl.menu_title_centered('Sorted by city name  (Z-A)'.upper(), '=', YELLOW)
    dl.print_middle_middle(dl.draw_border_head('-','|'))
    dl.print_middle_middle(dl.create_head_titles(['City', 'AQI', 'Timestamp']))
    dl.print_middle_middle(dl.draw_border_head('-','|'))
    for each_item in sorted_list:
        
        data = [
            f'{each_item.city_name}',
            f'{each_item.aqi_value}',
            f'{each_item.timestamp}'
        ]
        dl.print_middle_middle(dl.create_data_in_middle_row(data))
        dl.print_middle_middle(dl.draw_border_head('-','|'))


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

def center_of_screen():
    center = os.get_terminal_size // 2
    return center

# Reference 13
def print_menu_title(title):
    screen_width = os.get_terminal_size().columns
    title_lenght = len(title)
    line = "=" * title_lenght
    print(f'{line:^{screen_width-9}}')
    print(f'{title:^{screen_width}}')
    print(f'{line:^{screen_width-9}}')
    
def draw_border_head():
    border_widths = [16, 10, 21]
    border_lines = []
    for width in border_widths:
        border_lines.append('-' * width)
    connected_border_lines = '|'.join(border_lines)
    print(f'|{connected_border_lines}|')


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
            dl.clear_screen()
            dl.menu_title_centered('Air Quality Monitor System'.upper(), '=', YELLOW)
            dl.submenu_text_print('1- Data Entry Menu', BLUE)
            dl.submenu_text_print('2- Search Menu', BLUE)
            dl.submenu_text_print('3- Analytics & Reports', BLUE)
            dl.submenu_text_print('4- Admin Menu', BLUE)
            dl.submenu_text_print('5- Fetch Historical Data', BLUE)
            dl.submenu_text_print('6- Exit Program', RED)
            dl.print_footer()
            choice =dl.print_and_get_input('Please choose one of option from menu :', 'middle', 'middle')

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
                exit_choice = dl.print_and_get_input(f"Do you want to {RED}Exit{RESET} the program? (Y/N) :", 'middle', 'middle')
                if exit_choice.upper() == "Y":
                    dl.print_middle_middle('You logged out!!')
                    break
                elif exit_choice.upper() == "N":
                    continue
                else:
                    dl.print_middle_middle("Invalid choice. Please enter Y or N.")
                    dl.print_and_get_input(f"Press {RED}Enter{RESET} to continue...", 'middle', 'middle')
            else:
                dl.print_and_get_input("Invalid choice. Please try again!!", 'middle', 'middle')
        except KeyboardInterrupt:
            print('\n')
            dl.print_middle_middle(f"{BRIGHT_YELLOW}Action cancelled. Returning to main menu...{RESET}")
            dl.print_and_get_input(f'Press Enter to continue', 'middle', 'middle')
            continue
            


# Main Menu Ends Here
# |---------------------------------------------------------------------------|


# |---------------------------------------------------------------------------|
# Data Entry Menu Starts Here
def menu_1():
    while True:
        dl.clear_screen()
        dl.menu_title_centered('Data Entry Menu'.upper(), '=', YELLOW)
        all_records = db.get_all_records()
        cities_from_db = list(set([record.city_name for record in all_records]))
        cities_from_db.sort()
        city_list_number = 1
        for city in cities_from_db:
            dl.submenu_text_print(f"{city_list_number}- {city}", GREEN)
            city_list_number += 1
        add_new_city_option = len(cities_from_db) + 1
        dl.submenu_text_print(f"{add_new_city_option}- Add New City", BLUE)
        try:
            dl.print_footer()
            city_number_input = dl.print_and_get_input(
                f"Please choose a city number, or choose to add new city or type {RED}'exit'{RESET} to return to the main menu : ", 'middle', 'middle'
            )
            if city_number_input.lower() == "exit":
                return
            city_name = None
            if city_number_input == "":
                return
            elif city_number_input.isdigit():
                city_number = int(city_number_input)
                if 0 < city_number <= len(cities_from_db):
                    city_name = cities_from_db[city_number - 1]
                elif city_number == add_new_city_option:
                    while True:
                        dl.print_footer()
                        raw_city_input = dl.print_and_get_input(
                            'Please enter the name of the new city to add : ', 'middle', 'middle'
                        )
                        clean_city_input = raw_city_input.strip()

                        if clean_city_input == "":
                            city_name = None
                            break

                        if clean_city_input.isdigit():
                            print_msg("error", "City name cannot be only numbers. Please try again.")
                            continue

                        new_city_name = clean_city_input.title()

                        if new_city_name in cities_from_db:
                            print_msg("info", f"{new_city_name} already exists in the list")
                            break
                        else:
                            city_name = new_city_name
                            break
            if city_name:
                while True:
                    dl.print_footer()
                    aqi_input = dl.print_and_get_input(
                        f'Please enter air quality index for {GREEN}{city_name}{RESET}: ', 'middle', 'middle'
                    )

                    if aqi_input == "":
                        break

                    try:
                        aqi = float(aqi_input)
                        if aqi < 0 or aqi > 500:
                            print_msg("error", "Invalid AQI. Please enter a number between 0 and 500.")
                            continue

                        new_record = CityRecord(city_name=city_name, aqi_value=aqi, timestamp=time_stamp())
                        db.add_record(new_record)
                        print_msg("success", f"AQI data for {city_name} saved successfully!")
                        continue_choice = dl.print_and_get_input(f'Do you want to add more data to {GREEN}{city_name}{RESET}? (Y/N) : ', 'middle', 'middle')
                        if continue_choice.upper() == "Y":
                            continue
                        elif continue_choice.upper() == "N" or continue_choice == "":
                            break
                        else:
                            print_msg("error", "Invalid choice. Please enter Y or N.")
                            continue
                    except ValueError:
                        print_msg("error", "Invalid AQI. Please enter a number between 0 and 500.")
            else:
                print('\n')
                print_msg("error", "Invalid choice.")
                dl.print_and_get_input(f'Press Enter to try again', 'middle', 'middle')

        except KeyboardInterrupt:
            print('\n')
            print_msg("info", "Action cancelled. Returning to menu...")
            dl.print_and_get_input(f'Press Enter to continue', 'middle', 'middle')
            return


# Data Entry Menu End Here
# |---------------------------------------------------------------------------|


# |---------------------------------------------------------------------------|
# Search Menu Start Here
def menu_2():
    while True:
        try:
            dl.clear_screen()
            dl.menu_title_centered('Search Menu'.upper(), '=', YELLOW)
            all_records = db.get_all_records()
            cities_from_db = list(set([record.city_name for record in all_records]))
            dl.print_footer()
            input_city = dl.print_and_get_input("Please enter city name to search (Local or WAQI Live) : ", 'middle', 'middle')
            if input_city == '':
                return
            city_name = input_city.title()

            # Step 1: WAQI API Live Search
            stations = api_integration.search_city_stations(city_name)
            if stations:
                print_msg("info", f"Found {len(stations)} live stations for {city_name} via WAQI API:")
                for idx, st in enumerate(stations[:5]): # Show top 5
                    dl.print_middle_middle(f"{idx + 1}- {st['station']['name']}")
                print('\n')

                dl.print_footer()
                choice = dl.print_and_get_input(f"Choose a station (1-{min(5, len(stations))}) or press Enter to skip to local DB: ", 'middle', 'middle')
                if choice.isdigit() and 1 <= int(choice) <= len(stations):
                    selected_st = stations[int(choice) - 1]
                    uid = selected_st['uid']
                    print_msg("info", f"Fetching live AQI data for {selected_st['station']['name']}...")

                    st_data = api_integration.get_station_aqi(uid)
                    live_aqi = st_data.get("aqi")
                    if live_aqi and isinstance(live_aqi, (int, float)):
                        aqi_val = float(live_aqi)

                        # Save to local DB
                        new_record = CityRecord(city_name=city_name, aqi_value=aqi_val, timestamp=time_stamp())
                        db.add_record(new_record)

                        dl.print_middle_middle(f"Live WAQI: {BRIGHT_WHITE}{aqi_val}{RESET} ({get_epa_category(aqi_val)})")
                        print_msg("success", "Live data saved to local database.")
                    else:
                        print_msg("error", "No valid AQI data available for this station currently.")

                    dl.print_and_get_input(f'Press Enter to return to the main menu!', 'middle', 'middle')
                    return
            else:
                print_msg("info", f"No live WAQI stations found for {city_name}. Searching local DB...")

            # Step 2: Local DB Search Fallback
            if city_name in cities_from_db:
                print_msg("success", f"{city_name} is found in the local database!")
                choice = dl.print_and_get_input(f"Do you want to see the {GREEN}AQI{RESET} data? {RED}(Y/N){RESET}: ", 'middle', 'middle').upper()
                print("\n")
                if choice == "Y":
                    records = [record for record in all_records if record.city_name == city_name]
                    if not records:
                        print_msg("info", f"No AQI records found for {city_name}.")
                    else:
                        dl.print_middle_middle(dl.draw_border_head('-','|'))
                        dl.print_middle_middle(dl.create_head_titles(['City', 'AQI', 'Timestamp']))
                        dl.print_middle_middle(dl.draw_border_head('-','|'))
                        for record in records:
                            data = [
                                f'{city_name}',
                                f'{record.aqi_value}',
                                f'{record.timestamp}'
                            ]
                            dl.print_middle_middle(dl.create_data_in_middle_row(data))
                            dl.print_middle_middle(dl.draw_border_head('-','|'))
                        print("\n")
                        dl.print_and_get_input(f'Press {RED}Enter{RESET} to return to the main menu!', 'middle', 'middle')
            else:
                print_msg("error", f"{city_name} is not found in the local database!")
                dl.print_and_get_input(f'Press Enter to return to the main menu!', 'middle', 'middle')
            return
        except KeyboardInterrupt:
            print('\n')
            print_msg("info", "Action cancelled. Returning to menu...")
            dl.print_and_get_input(f'Press Enter to continue', 'middle', 'middle')
            return


# Search Menu End Here
# |---------------------------------------------------------------------------|


# |---------------------------------------------------------------------------|
# Reports and Analysis Menu Start Here
def menu_3():
    dl.clear_screen()
    while True:
        try:
            dl.clear_screen()
            dl.menu_title_centered('Analytics & Reports'.upper(), '=', YELLOW)

            dl.print_middle_middle(f"{BLUE}1- Display from highest AQI data")
            print('\n')
            dl.print_middle_middle(f"2- Display from lowest AQI data")
            print('\n')
            dl.print_middle_middle(f"3- Display from city name (A-Z)")
            print('\n')
            dl.print_middle_middle(f"4- Display from city name (Z-A)")
            print('\n')
            dl.print_middle_middle(f"5- Executive Analytics Summary{RESET}")
            print('\n')
            dl.print_middle_middle(f"{MAGENTA}6- Run AI Engine Prediction{RESET}")
            print('\n')
            dl.print_middle_middle(RED + "7- Return main menu" + RESET)
            print('\n')
            dl.print_footer()
            user_choice = dl.print_and_get_input("Please choose one of option from menu : ", 'middle', 'middle')

            if user_choice == "":
                return
            elif user_choice == "1":
                dl.clear_screen()
                sort_by_highest_aqi()
                print('\n')
                dl.print_and_get_input(f"Press {RED}Enter{RESET} to return to the main menu", 'middle', 'middle')
                continue
            elif user_choice == "2":
                dl.clear_screen()
                sort_by_lowest_aqi()
                print('\n')
                dl.print_and_get_input(f"Press {RED}Enter{RESET} to return to the main menu", 'middle', 'middle')
                continue
            elif user_choice == "3":
                dl.clear_screen()
                sort_by_city_name_az()
                print('\n')
                dl.print_and_get_input(f"Press {RED}Enter{RESET} to return to the main menu", 'middle', 'middle')
                continue
            elif user_choice == "4":
                dl.clear_screen()
                sort_by_city_name_za()
                print('\n')
                dl.print_and_get_input(f"Press {RED}Enter{RESET} to return to the main menu", 'middle', 'middle')
                continue
            elif user_choice == "5":
                dl.clear_screen()
                dl.menu_title_centered('Executive Analytics Summary'.upper(), '=', YELLOW)

                avg_aqi = db.get_average_aqi()
                highest_city = db.get_city_with_highest_aqi()

                print('\n')
                dl.print_middle_middle(f"Average System AQI: {avg_aqi:.2f} ({get_epa_category(avg_aqi)})")
                print('\n')

                if highest_city:
                    dl.print_middle_middle(f"Highest Pollution: {highest_city[0]} - {highest_city[1]} ({get_epa_category(highest_city[1])})")
                else:
                    dl.print_middle_middle("Highest Pollution: No records available")

                print('\n')
                dl.print_footer()
                dl.print_and_get_input(f"Press Enter to return to the Reports menu", 'middle', 'middle')
                continue
            elif user_choice == "6":
                dl.clear_screen()
                dl.menu_title_centered('AI Prediction Engine'.upper(), '=', YELLOW)
                all_records = db.get_all_records()
                cities_from_db = list(set([record.city_name for record in all_records]))
                dl.print_footer()
                input_city = dl.print_and_get_input("Please enter city name for AI Prediction : ", 'middle', 'middle')
                if input_city == "":
                    continue
                city_name = input_city.title()

                print('\n')
                print_msg("info", f"Running AI Analysis on {city_name}...")
                predicted_aqi = ai_engine.predict_next_aqi(city_name)

                if predicted_aqi == 0.0:
                    print_msg("error", "Insufficient data to run prediction.")
                else:
                    decision = ai_engine.evaluate_prediction(predicted_aqi)

                    # Print dynamically
                    dl.print_middle_middle(f"Predicted AQI: {BRIGHT_WHITE}{predicted_aqi}{RESET} ({get_epa_category(predicted_aqi)})")

                    if "NORMAL" in decision:
                        print_msg("success", decision)
                    else:
                        print_msg("error", decision)

                    # Save AI state
                    db.add_prediction(
                        city_name=city_name,
                        predicted_aqi=predicted_aqi,
                        prediction_date=time_stamp(),
                        target_date=time_stamp(), # For demo purposes, we project next current instance
                        decision_made=decision
                    )

                dl.print_footer()
                dl.print_and_get_input(f"Press Enter to return to the Reports menu", 'middle', 'middle')
                continue
            elif user_choice == "7":
                break
            elif user_choice > "7" or user_choice < "1":
                print('\n')
                print_msg("error", "Invalid choice. Please try again!!")
                dl.print_and_get_input(f"Press Enter to continue...", 'middle', 'middle')
                continue
            else:
                print('\n')
                return f"{RED}Invalid choice. Please try again!!{RESET}"
        except KeyboardInterrupt:
            print('\n')
            print_msg("info", "Action cancelled. Returning to menu...")
            dl.print_and_get_input(f'Press Enter to continue', 'middle', 'middle')
            return


# Reports and Analysis Menu End Here
# |---------------------------------------------------------------------------|


# |---------------------------------------------------------------------------|
# Admin Menu Sarts Here
def menu_4():
    dl.clear_screen()
    dl.menu_title_centered('Admin Menu'.upper(), '=', YELLOW)
    while True:
        try:
            dl.clear_screen()
            dl.menu_title_centered('Admin Menu'.upper(), '=', YELLOW)
            print('\n')
            dl.print_middle_middle(f"{BLUE}1- Delete Database{RESET}")
            print('\n')
            dl.print_middle_middle(f"{BLUE}2- Backup Database{RESET}")
            print('\n')
            dl.print_middle_middle(f"{BLUE}3- Export Database to JSON{RESET}")
            print('\n')
            dl.print_middle_middle(f"{RED}4- Return main menu{RESET}")
            print('\n')
            dl.print_footer()
            user_choice = dl.print_and_get_input("Please choose one of option from menu : ", 'middle', 'middle')

            if user_choice == "":
                return
            elif user_choice == "1":
                password = dl.print_and_get_input("Please enter admin password to continue : ", 'middle', 'middle')
                if check_admin_password(password):
                    dl.print_middle_middle("Password correct")
                    choice = dl.print_and_get_input(
                        f"{RED}Do you want to delete database? (Y/N) :{RESET} ", 'middle', 'middle'
                    )
                    choice = choice.upper()
                    if choice == "Y":
                        delete_database()
                        dl.print_and_get_input(f"Press {RED}Enter{RESET} to return to the admin menu", 'middle', 'middle')
                        continue
                    elif choice == "N":
                        dl.print_middle_middle("Database not deleted!")
                        dl.print_and_get_input(f"Press {RED}Enter{RESET} to return to the admin menu", 'middle', 'middle')
                        continue
                    else:
                        dl.print_middle_middle("Invalid choice!")
                        dl.print_and_get_input(f"Press {RED}Enter{RESET} to return to the admin menu", 'middle', 'middle')
                        continue
                else:
                    dl.print_middle_middle("Password not correct!")
                    dl.print_and_get_input(f"Press {RED}Enter{RESET} to return to the admin menu", 'middle', 'middle')
                    continue
            elif user_choice == "2":
                choice = dl.print_and_get_input(f"{GREEN}Do you want to backup database? (Y/N) :{RESET} ", 'middle', 'middle')
                choice = choice.upper()
                if choice == "Y":
                    backup_database(DB_FILE)
                    dl.print_and_get_input(f"Press {RED}Enter{RESET} to return to the admin menu", 'middle', 'middle')
                    continue
                elif choice == "N":
                    dl.print_middle_middle("Database not backed up!")
                    dl.print_and_get_input(f"Press {RED}Enter{RESET} to return to the admin menu", 'middle', 'middle')
                    continue
                else:
                    dl.print_middle_middle("Invalid choice!")
                    dl.print_and_get_input(f"Press {RED}Enter{RESET} to return to the admin menu")
                    continue
            elif user_choice == "3":
                filename = db.export_to_json()
                print_msg("success", f"Data successfully exported to {filename}")
                dl.print_and_get_input(f"Press Enter to return to the admin menu", 'middle', 'middle')
                continue
            elif user_choice == "4":
                break
            else:
                dl.print_middle_middle("Invalid choice!")
                dl.print_and_get_input(f"Press {RED}Enter{RESET} to return to the admin menu")
                continue
        except KeyboardInterrupt:
            print('\n')
            print_msg("info", "Action cancelled. Returning to menu...")
            dl.print_and_get_input(f'Press Enter to continue', 'middle', 'middle')
            return

# Admin Menu Ends Here
# |---------------------------------------------------------------------------|

def menu_5():
    import random
    import time
    from datetime import timedelta

    while True:
        try:
            dl.clear_screen()
            dl.menu_title_centered('Fetch Historical Data'.upper(), '=', YELLOW)
            dl.print_middle_middle(f"{BLUE}1- Last 7 Days")
            print('\n')
            dl.print_middle_middle(f"2- Last 30 Days")
            print('\n')
            dl.print_middle_middle(f"3- Custom Date Range{RESET}")
            print('\n')
            dl.print_middle_middle(f"{RED}4- Return main menu{RESET}")
            print('\n')
            dl.print_footer()
            user_choice = dl.print_and_get_input("Please choose one of option from menu : ", 'middle', 'middle')

            if user_choice == "":
                return
            elif user_choice == "4":
                break

            if user_choice not in ["1", "2", "3"]:
                print_msg("error", "Invalid choice. Please try again!!")
                dl.print_and_get_input(f"Press Enter to continue...", 'middle', 'middle')
                continue

            dl.print_footer()
            input_city = dl.print_and_get_input("Enter city name to fetch data for: ", 'middle', 'middle')
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
                        dl.print_footer()
                        s_date_str = dl.print_and_get_input("Enter start date (YYYY-MM-DD): ", 'middle', 'middle')
                        if s_date_str == "":
                            break
                        start_date = datetime.datetime.strptime(s_date_str, "%Y-%m-%d").date()

                        dl.print_footer()
                        e_date_str = dl.print_and_get_input("Enter end date (YYYY-MM-DD): ", 'middle', 'middle')
                        if e_date_str == "":
                            break
                        end_date = datetime.datetime.strptime(e_date_str, "%Y-%m-%d").date()

                        if start_date > end_date:
                            print_msg("error", "Start date cannot be after end date.")
                            continue

                        break
                    except ValueError:
                        print_msg("error", "Invalid date format. Please use YYYY-MM-DD.")

                if not start_date or not end_date:
                    continue # Cancelled out of custom date input

            print_msg("info", f"Locating WAQI anchor data for {city_name}...")
            base_aqi = api_integration.get_station_aqi_by_name(city_name)

            if base_aqi == 0.0:
                print_msg("error", f"Could not find live anchor data for {city_name}. Proceeding with default baseline of 50.0")
                base_aqi = 50.0

            print_msg("info", f"Starting historical fetch simulation...")

            current_date = start_date
            inserted_count = 0

            while current_date <= end_date:
                print_msg("info", f"Fetching data for {current_date.strftime('%Y-%m-%d')}...")
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

            print_msg("success", f"Successfully fetched and added {inserted_count} new unique records.")
            dl.print_and_get_input("Press Enter to return to the Historical Data menu...", 'middle', 'middle')

        except KeyboardInterrupt:
            print('\n')
            print_msg("info", "Action cancelled. Returning to menu...")
            dl.print_and_get_input(f'Press Enter to continue', 'middle', 'middle')
            return


# |----------------- End of Main Menu and Display Functions ------------------|

if __name__ == "__main__":
    main_menu()