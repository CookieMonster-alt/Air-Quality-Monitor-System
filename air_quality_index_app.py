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

# ------------------ Constant Variables ------------------|

JSON_FILE = "cities.json"

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


def display_aqi_data(city_name):
    with open(JSON_FILE, "r") as file:
        data = json.load(file)
        return data.get(city_name, [])
    return []


def time_stamp():
    time_stamp = datetime.datetime.now()  # Reference 2
    return time_stamp.isoformat(" ", "minutes")


def read_json_file_convert_to_list():  # Reference 12
    all_records = []
    with open(JSON_FILE, "r") as file:
        data = json.load(file)
        for city, records in data.items():
            for record in records:
                record["City"] = city
                all_records.append(record)
    return all_records


# |--------------- End of Data Functions --------------|


# |------------------ File Functions ------------------|
# Reference 9
"""
This section contains all functions for managing the JSON database file.
It handles creating the file if it doesn't exist, reading city data,
saving new AQI records, creating backups, and deleting the database file.
"""

def read_cities_json_and_return_city_names():  # Reference 5
    with open(JSON_FILE, "r") as file:
        data = json.load(file)
        return list(data.keys())
    return []

def delete_database():
    if os.path.exists(JSON_FILE):
        os.remove(JSON_FILE)
        print("Database deleted successfully!")
    else:
        print("No database found to delete")

def save_aqi_record(city_name, aqi):
    all_city_data = {}
    try:
        with open(JSON_FILE, "r") as json_file:
            all_city_data = json.load(json_file)
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    if city_name in all_city_data:
        all_city_data[city_name].append(
            {"AQI": aqi, "Timestamp": time_stamp()}
        )
    else:
        all_city_data[city_name] = [{"AQI": aqi, "Timestamp": time_stamp()}]
    with open(JSON_FILE, "w") as json_file:
        json.dump(all_city_data, json_file, indent=4)

def check_file_exists():
    if not os.path.exists(JSON_FILE):
        with open(JSON_FILE, "w") as file:
            json.dump({}, file)

# Reference 10
def backup_database(source_file):
    if os.path.exists(source_file):
        backup_file_name = f"backup_file_{time_stamp()}_" + source_file
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
    list_data = read_json_file_convert_to_list()
    sorted_list = sorted(list_data, key=lambda x: x["AQI"], reverse=True)
    dl.menu_title_centered('Sorted by highest AQI'.upper(), '=', YELLOW)
    dl.print_middle_middle(dl.draw_border_head('-','|'))
    dl.print_middle_middle(dl.create_head_titles(['City', 'AQI', 'Timestamp']))
    dl.print_middle_middle(dl.draw_border_head('-','|'))
    for each_item in sorted_list:
        
        data = [
            f'{each_item.get("City")}',
            f'{each_item.get("AQI")}',
            f'{each_item.get("Timestamp")}'
        ]
        dl.print_middle_middle(dl.create_data_in_middle_row(data))
        dl.print_middle_middle(dl.draw_border_head('-','|'))


def sort_by_lowest_aqi():
    list_data = read_json_file_convert_to_list()
    sorted_list = sorted(list_data, key=lambda x: x["AQI"], reverse=False)
    dl.menu_title_centered('Sorted by lowest AQI'.upper(), '=', YELLOW)
    dl.print_middle_middle(dl.draw_border_head('-','|'))
    dl.print_middle_middle(dl.create_head_titles(['City', 'AQI', 'Timestamp']))
    dl.print_middle_middle(dl.draw_border_head('-','|'))
    for each_item in sorted_list:
        
        data = [
            f'{each_item.get("City")}',
            f'{each_item.get("AQI")}',
            f'{each_item.get("Timestamp")}'
        ]
        dl.print_middle_middle(dl.create_data_in_middle_row(data))
        dl.print_middle_middle(dl.draw_border_head('-','|'))


def sort_by_city_name_az():
    list_data = read_json_file_convert_to_list()
    sorted_list = sorted(list_data, key=lambda x: x["City"], reverse=False)
    dl.menu_title_centered('Sorted by city name  (A-Z)'.upper(), '=', YELLOW)
    dl.print_middle_middle(dl.draw_border_head('-','|'))
    dl.print_middle_middle(dl.create_head_titles(['City', 'AQI', 'Timestamp']))
    dl.print_middle_middle(dl.draw_border_head('-','|'))
    for each_item in sorted_list:
        
        data = [
            f'{each_item.get("City")}',
            f'{each_item.get("AQI")}',
            f'{each_item.get("Timestamp")}'
        ]
        dl.print_middle_middle(dl.create_data_in_middle_row(data))
        dl.print_middle_middle(dl.draw_border_head('-','|'))


def sort_by_city_name_za():
    list_data = read_json_file_convert_to_list()
    sorted_list = sorted(list_data, key=lambda x: x["City"], reverse=True)
    dl.menu_title_centered('Sorted by city name  (Z-A)'.upper(), '=', YELLOW)
    dl.print_middle_middle(dl.draw_border_head('-','|'))
    dl.print_middle_middle(dl.create_head_titles(['City', 'AQI', 'Timestamp']))
    dl.print_middle_middle(dl.draw_border_head('-','|'))
    for each_item in sorted_list:
        
        data = [
            f'{each_item.get("City")}',
            f'{each_item.get("AQI")}',
            f'{each_item.get("Timestamp")}'
        ]
        dl.print_middle_middle(dl.create_data_in_middle_row(data))
        dl.print_middle_middle(dl.draw_border_head('-','|'))


def calculate_average_aqi():
    aiq_sum = 0
    aiq_count = 0
    list_data = read_json_file_convert_to_list()
    for a in list_data:
        aiq_sum += a["AQI"]
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
    check_file_exists()
    while True:
        dl.clear_screen()
        dl.menu_title_centered('Air Quality Monitor System'.upper(), '=', YELLOW)
        dl.submenu_text_print('1- Data Entry Menu', BLUE)
        dl.submenu_text_print('2- Search Menu', BLUE)
        dl.submenu_text_print('3- Reports and Analysis Menu', BLUE)
        dl.submenu_text_print('4- Admin Menu', BLUE)
        dl.submenu_text_print('5- Exit Program', RED)
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
            


# Main Menu Ends Here
# |---------------------------------------------------------------------------|


# |---------------------------------------------------------------------------|
# Data Entry Menu Starts Here
def menu_1():
    while True:
        dl.clear_screen()
        dl.menu_title_centered('Data Entry Menu'.upper(), '=', YELLOW)
        cities_from_file = read_cities_json_and_return_city_names()
        city_list_number = 1
        for city in cities_from_file:
            dl.submenu_text_print(f"{city_list_number}- {city}", GREEN)
            city_list_number += 1
        add_new_city_option = len(cities_from_file) + 1
        dl.submenu_text_print(f"{add_new_city_option}- Add New City", BLUE)
        city_number_input = dl.print_and_get_input(
            f"Please choose a city number, or choose to add new city or type {RED}'exit'{RESET} to return to the main menu : ", 'middle', 'middle'
        )
        if city_number_input.lower() == "exit":
            return
        city_name = None
        if city_number_input.isdigit():
            city_number = int(city_number_input)
            if 0 < city_number <= len(cities_from_file):
                city_name = cities_from_file[city_number - 1]
            elif city_number == add_new_city_option:
                new_city_name = dl.print_and_get_input(
                    "Please enter the name of the new city to add : ", 'middle', 'middle'
                ).title()
                if new_city_name in cities_from_file:
                    dl.print_middle_middle(f"{GREEN}{new_city_name}{RESET} already exists in the list")
                else:
                    city_name = new_city_name
        if city_name:
            while True:
                aqi_input = dl.print_and_get_input(
                    f"Please enter air quality index for {GREEN}{city_name}{RESET}: ", 'middle', 'middle'
                )
                try:
                    aqi = float(aqi_input)
                    save_aqi_record(city_name, aqi)
                    dl.print_middle_middle(f"AQI data for {GREEN}{city_name}{RESET} saved successfully!")
                    continue_choice = dl.print_and_get_input(f'Do you want to add more data to {GREEN}{city_name}{RESET}? (Y/N) : ', 'middle', 'middle')
                    if continue_choice.upper() == "Y":
                        continue
                    elif continue_choice.upper() == "N":
                        break
                    else:
                        dl.print_middle_middle("Invalid choice. Please enter Y or N.")
                        continue
                except ValueError:
                    dl.print_middle_middle("Invalid AQI. Please enter a valid number!")
        else:
            print('\n')
            dl.print_and_get_input(f'{RED}Invalid choice.{RESET} Press Enter to try again', 'middle', 'middle')


# Data Entry Menu End Here
# |---------------------------------------------------------------------------|


# |---------------------------------------------------------------------------|
# Search Menu Start Here
def menu_2():
    while True:
        dl.clear_screen()
        dl.menu_title_centered('Search Menu'.upper(), '=', YELLOW)
        city = read_cities_json_and_return_city_names()
        input_city = dl.print_and_get_input("Please enter city name to search : ", 'middle', 'middle')
        if input_city == '':
            dl.print_middle_middle(f'{RED}Please enter city name!{RESET}')
            dl.print_and_get_input('Press Enter to continue...', 'middle', 'middle')
            continue
        city_name = input_city.title()
        if city_name in city:
            dl.print_middle_middle(f"{GREEN}{city_name}{RESET} is found in the database!")
            choice = dl.print_and_get_input(f"Do you want to see the {GREEN}AQI{RESET} data? {RED}(Y/N){RESET}: ", 'middle', 'middle').upper()
            print("\n")
            if choice == "Y":
                records = display_aqi_data(city_name)
                if not records:
                    dl.print_middle_middle(f"No AQI records found for {GREEN}{city_name}.{RESET}")
                else:
                    dl.print_middle_middle(dl.draw_border_head('-','|'))
                    dl.print_middle_middle(dl.create_head_titles(['City', 'AQI', 'Timestamp']))
                    dl.print_middle_middle(dl.draw_border_head('-','|'))
                    for record in records:
                        data = [
                            f'{city_name}',
                            f'{record.get("AQI")}',
                            f'{record.get("Timestamp")}'
                        ]
                        dl.print_middle_middle(dl.create_data_in_middle_row(data))
                        dl.print_middle_middle(dl.draw_border_head('-','|'))
                    print("\n")
                    dl.print_and_get_input(f'Press {RED}Enter{RESET} to return to the main menu!', 'middle', 'middle')
        else:
            dl.print_middle_middle(f"{GREEN}{city_name}{RESET} is not found in the database!")
            dl.print_and_get_input(f'Press {RED}Enter{RESET} to return to the main menu!', 'middle', 'middle')
        return


# Search Menu End Here
# |---------------------------------------------------------------------------|


# |---------------------------------------------------------------------------|
# Reports and Analysis Menu Start Here
def menu_3():
    dl.clear_screen()
    while True:
        dl.clear_screen()
        dl.menu_title_centered('Reports and Analysis Menu'.upper(), '=', YELLOW)
        dl.print_middle_middle(f"{BLUE}1- Display from highest AQI data")
        print('\n')
        dl.print_middle_middle(f"2- Display from lowest AQI data")
        print('\n')
        dl.print_middle_middle(f"3- Display from city name (A-Z)")
        print('\n')
        dl.print_middle_middle(f"4- Display from city name (Z-A)")
        print('\n')
        dl.print_middle_middle(f"5- Average AQI data{RESET}")
        print('\n')
        dl.print_middle_middle(RED + "6- Return main menu" + RESET)
        print('\n')
        user_choice = dl.print_and_get_input("Please choose one of option from menu : ", 'middle', 'middle')

        if user_choice == "1":
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
            sort_by_city_name_az()
            print('\n')
            dl.print_middle_middle(
                f"Average AQI data is : {BRIGHT_GREEN}{calculate_average_aqi():.2f}{RESET}"
            )
            print('\n')
            dl.print_and_get_input(f"Press {RED}Enter{RESET} to return to the main menu", 'middle', 'middle')
            continue
        elif user_choice == "6":
            break
        elif user_choice > "6" or user_choice < "1":
            print('\n')
            dl.print_and_get_input(f"Invalid choice. Press {RED}Enter{RESET} to try again!!", 'middle', 'middle')
            continue
        else:
            print('\n')
            return f"{RED}Invalid choice. Please try again!!{RESET}"


# Reports and Analysis Menu End Here
# |---------------------------------------------------------------------------|


# |---------------------------------------------------------------------------|
# Admin Menu Sarts Here
def menu_4():
    dl.clear_screen()
    dl.menu_title_centered('Admin Menu'.upper(), '=', YELLOW)
    while True:
        dl.clear_screen()
        dl.menu_title_centered('Admin Menu'.upper(), '=', YELLOW)
        print('\n')
        dl.print_middle_middle(f"{BLUE}1- Delete Database{RESET}")
        print('\n')
        dl.print_middle_middle(f"{BLUE}2- Backup Database{RESET}")
        print('\n')
        dl.print_middle_middle(f"{RED} 3- Return main menu{RESET}")
        print('\n')
        user_choice = dl.print_and_get_input("Please choose one of option from menu : ", 'middle', 'middle')

        if user_choice == "1":
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
                backup_database(JSON_FILE)
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
            break
        else:
            dl.print_middle_middle("Invalid choice!")
            dl.print_and_get_input(f"Press {RED}Enter{RESET} to return to the admin menu")
            continue

# Admin Menu Ends Here
# |---------------------------------------------------------------------------|

# |----------------- End of Main Menu and Display Functions ------------------|

main_menu()