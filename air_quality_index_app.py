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
from data_manager import DatabaseManager, CityRecord, get_epa_category, get_epa_color_tag, get_epa_color_hex, get_epa_category_raw
import api_integration
import ai_engine
from ai_llm_engine import AIEngine

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


# ------------------ Shared Blackboard ------------------|
shared_blackboard = {'last_data': None}

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
    rows = [[r.city_name, str(r.aqi_value), get_epa_category_raw(r.aqi_value), f"[{get_epa_color_hex(r.aqi_value)}]███[/]", r.timestamp] for r in sorted_list]
    tui.show_table('Sorted by highest AQI', ['City', 'AQI', 'Category', 'Color', 'Timestamp'], rows)

def sort_by_lowest_aqi():
    list_data = db.get_all_records()
    sorted_list = sorted(list_data, key=lambda x: x.aqi_value, reverse=False)
    rows = [[r.city_name, str(r.aqi_value), get_epa_category_raw(r.aqi_value), f"[{get_epa_color_hex(r.aqi_value)}]███[/]", r.timestamp] for r in sorted_list]
    tui.show_table('Sorted by lowest AQI', ['City', 'AQI', 'Category', 'Color', 'Timestamp'], rows)

def sort_by_city_name_az():
    list_data = db.get_all_records()
    sorted_list = sorted(list_data, key=lambda x: x.city_name, reverse=False)
    rows = [[r.city_name, str(r.aqi_value), get_epa_category_raw(r.aqi_value), f"[{get_epa_color_hex(r.aqi_value)}]███[/]", r.timestamp] for r in sorted_list]
    tui.show_table('Sorted by city name  (A-Z)', ['City', 'AQI', 'Category', 'Color', 'Timestamp'], rows)

def sort_by_city_name_za():
    list_data = db.get_all_records()
    sorted_list = sorted(list_data, key=lambda x: x.city_name, reverse=True)
    rows = [[r.city_name, str(r.aqi_value), get_epa_category_raw(r.aqi_value), f"[{get_epa_color_hex(r.aqi_value)}]███[/]", r.timestamp] for r in sorted_list]
    tui.show_table('Sorted by city name  (Z-A)', ['City', 'AQI', 'Category', 'Color', 'Timestamp'], rows)


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



def handle_query_intent(current_prompt, ai):
    # SQL üretim ve insan döngülü (HITL) hata düzeltme sürecini yönetir.
    while True:
        with tui.create_spinner("AILO is generating SQL...") as progress:
            task_id = progress.add_task("AILO is generating SQL...", total=None)
            sql_query = ai.translate_text_to_sql(current_prompt)

        if not sql_query:
            tui.show_msg("error", "AILO failed to generate a query.")
            tui.get_input("Press Enter to return to menu")
            return

        safe_sql = sql_query.replace("[", "\\[").replace("]", "\\]")
        tui.show_msg("warning", f"Generated SQL: [bold white]{safe_sql}[/]")

        success, result, cursor_description = db.execute_ai_read_query(sql_query)
        if not success:
            error_msg = str(result)
            with tui.create_spinner("Local AI failed. Reaching out to Cloud Oracle...") as progress:
                task_id = progress.add_task("Cloud Oracle analyzing...", total=None)
                fixed_sql = ai.ai_oracle_fallback(current_prompt, sql_query, "sql")

            if fixed_sql:
                safe_sql = fixed_sql.replace("[", "\\[").replace("]", "\\]")
                tui.show_msg("warning", f"Oracle Fixed SQL: [bold white]{safe_sql}[/]")
                o_success, o_result, o_cursor_description = db.execute_ai_read_query(fixed_sql)

                if o_success:
                    tui.show_msg("success", "AILO encountered an error but autonomously fixed it via Cloud Oracle.")

                    # Doğru SQL'i ileride kullanmak üzere otonom hafızamıza işliyoruz.
                    ai.save_to_memory(current_prompt, fixed_sql, persona="router")

                    sql_query = fixed_sql
                    success = o_success
                    result = o_result
                    cursor_description = o_cursor_description
                else:
                    tui.show_msg("error", f"Cloud Oracle also failed: {o_result}")
                    tui.get_input("Press Enter to return")
                    return
            else:
                tui.show_msg("error", f"AI Error: {error_msg}")
                tui.get_input("Press Enter to return")
                return

        if success:
            if not result:
                tui.show_msg("info", "Query returned 0 rows.")
            else:
                headers = [desc[0] for desc in cursor_description]
                str_rows = []
                has_aqi = 'aqi_value' in headers
                aqi_idx = headers.index('aqi_value') if has_aqi else -1
                if has_aqi:
                    headers.extend(["Category", "Color"])
                for row in result:
                    str_row = [str(item) for item in row]
                    if has_aqi:
                        try:
                            aqi_val = float(str_row[aqi_idx])
                            cat = get_epa_category_raw(aqi_val)
                            color_hex = get_epa_color_hex(aqi_val)
                            str_row.append(cat)
                            str_row.append(f"[{color_hex}]███[/]")
                        except ValueError:
                            str_row.extend(["Unknown", ""])
                    str_rows.append(str_row)
                tui.show_table("AILO Results", headers, str_rows, use_pager=False)

                # Tablodaki veriyi diğer yapay zeka departmanlarının (Analist, Çizer) görebilmesi için RAM havuzuna atıyoruz.
                import pandas as pd
                try:
                    clean_headers = headers[:len(result[0])]
                    df = pd.DataFrame(result, columns=clean_headers)
                    shared_blackboard['last_data'] = df
                except Exception as e:
                    pass
        return

def handle_insert_intent(params):
    # Dışarıdan veya kullanıcının doğrudan verdiği hava kalitesi verisini sisteme dahil eder.
    city = params.get("city")
    if not city:
        tui.show_msg("error", "Missing city name for insert operation.")
        tui.get_input("Press Enter to continue")
        return

    city = city.title()
    aqi = params.get("aqi")

    if aqi is None:
        tui.show_msg("info", f"AQI not provided for {city}. Fetching autonomously from WAQI...")
        with tui.create_spinner(f"Fetching live AQI data for [cyan]{city}[/]...") as progress:
            task_id = progress.add_task(f"Fetching...", total=None)
            aqi = api_integration.get_station_aqi_by_name(city)

        if aqi == 0.0:
            tui.show_msg("error", f"Could not find live anchor data for {city}.")
            tui.get_input("Press Enter to continue")
            return
        tui.show_msg("info", f"Found live WAQI: [bold white]{aqi}[/] ({get_epa_category(aqi)})")

    new_record = CityRecord(city_name=city, aqi_value=float(aqi), timestamp=time_stamp())
    is_new = db.add_record(new_record)
    if is_new:
        tui.show_msg("success", f"AQI data for {city} saved successfully!")
    else:
        tui.show_msg("info", f"AQI data for {city} at this timestamp already exists.")
    tui.get_input("Press Enter to continue")

def handle_delete_intent(params):
    # İstenen şehre ait verileri dry-run yöntemiyle (önizlemeli) güvenli şekilde siler.
    city = params.get("city")
    if city:
        city = city.title()
        records = db.get_records_by_city(city)
        if not records:
            tui.show_msg("info", f"No records found for {city}.")
            tui.get_input("Press Enter to continue...")
            return

        # Silmeden önce ne silineceğini gösteriyoruz
        tui.clear_screen()
        from data_manager import get_epa_category_raw, get_epa_color_hex
        rows = [[str(r.id), r.city_name, str(r.aqi_value), get_epa_category_raw(r.aqi_value), f"[{get_epa_color_hex(r.aqi_value)}]███[/]", r.timestamp] for r in records]
        tui.show_table(f"Preview: {city} Records", ['ID', 'City', 'AQI', 'Category', 'Color', 'Timestamp'], rows, use_pager=True)

        choice = tui.get_input("[info]Enter IDs to delete (e.g., 1, 4, 5)[/]\n[danger]Type 'ALL' to delete all listed records[/]\n[accent]Type 'C' to Cancel[/]\n> ")
        if not choice or choice.strip().upper() == 'C':
            tui.show_msg("info", "Deletion cancelled.")
        elif choice.strip().upper() == 'ALL':
            deleted = db.delete_records(city_name=city)
            tui.show_msg("success", f"Successfully deleted {deleted} records.")
        else:
            try:
                ids_to_delete = [int(x.strip()) for x in choice.split(",") if x.strip().isdigit()]
                if not ids_to_delete:
                    raise ValueError()
                deleted = db.delete_records_by_ids(ids_to_delete)
                tui.show_msg("success", f"Successfully deleted {deleted} records.")
            except ValueError:
                tui.show_msg("error", "Invalid ID format. Operation cancelled.")
    else:
        tui.show_msg("warning", "Granular delete via AILO requires a specific city. Redirecting to admin menu.")
        delete_data_menu()
    tui.get_input("Press Enter to continue...")

def handle_fetch_intent(params):
    # WAQI geçmiş verilerini içeren devasa CSV dosyalarını sisteme yutar.
    start_date = params.get("start_date")
    end_date = params.get("end_date")
    file_path = params.get("url")

    if not file_path:
        tui.show_msg("warning", "File path missing.")
        file_path = tui.get_input("Please enter the path to the CSV file:")
        if not file_path:
            return
    if not start_date:
        start_date = tui.get_input("Please enter start date (YYYY-MM-DD):")
    if not end_date:
        end_date = tui.get_input("Please enter end date (YYYY-MM-DD):")

    if not start_date or not end_date or not file_path:
        tui.show_msg("error", "Missing required parameters for CSV extraction.")
        tui.get_input("Press Enter to continue...")
        return

    import os
    if not file_path.startswith("http") and not os.path.exists(file_path):
        tui.show_msg("error", "Invalid or missing local file path.")
        tui.get_input("Press Enter to continue...")
        return

    try:
        import datetime
        datetime.datetime.strptime(start_date, "%Y-%m-%d")
        datetime.datetime.strptime(end_date, "%Y-%m-%d")

        with tui.create_spinner("Processing Devormous CSV Data...") as progress:
            task_id = progress.add_task("Processing Data...", total=None)
            stats = db.import_historical_csv_with_pandas(file_path, start_date, end_date)

        from rich.panel import Panel
        from tui_engine import console

        report_text = f"[info]Total Rows Processed:[/] [bold white]{stats['total_processed']}[/]\n"
        report_text += f"[info]New Records Inserted:[/] [success]{stats['newly_inserted']}[/]"
        panel = Panel(report_text, title="[success]Import Complete[/]", border_style="success", expand=False)
        console.print(panel, justify="center")
    except ValueError as ve:
        tui.show_msg("error", f"Date format error: {str(ve)}")
    except Exception as e:
        tui.show_msg("error", f"Import failed: {str(e)}")
    tui.get_input("Press Enter to continue...")

def orchestrate_intent(initial_prompt: str, ai_instance=None):
    # Gelen doğal dil komutunun niyetini belirler ve ilgili alt fonksiyona yönlendirir.
    if ai_instance is None:
        ai = AIEngine()
        ai._ensure_model_loaded()
    else:
        ai = ai_instance

    current_prompt = initial_prompt

    while True:
        with tui.create_spinner("AILO is parsing your intent...") as progress:
            task_id = progress.add_task("AILO is parsing your intent...", total=None)
            intent_data = ai.parse_intent(current_prompt)

        status = intent_data.get("status")

        # Eğer kullanıcının cümlesi eksikse (örn: sadece 'sil' dediyse), ona hangi şehri sileceğini soralım.
        if status == "incomplete":
            ask_text = intent_data.get("ask_user", "Please provide more information.")
            tui.show_msg("warning", ask_text)
            user_reply = tui.get_input("Your response (or press Enter to cancel)")
            if not user_reply:
                return
            # Diyalog geçmişini koruyarak modele geri besliyoruz
            current_prompt = current_prompt + " " + user_reply
            continue

        intent = intent_data.get("intent")
        params = intent_data.get("parameters", {})

        if intent == "navigate":
            tui.show_msg("info", f"Navigating as requested...")
            tui.get_input("Press Enter to continue")
            return

        elif intent == "query":
            handle_query_intent(current_prompt, ai)
            return

        elif intent == "insert":
            handle_insert_intent(params)
            return

        elif intent == "delete":
            handle_delete_intent(params)
            return

        elif intent == "fetch_data":
            handle_fetch_intent(params)
            return

        else:
            tui.show_msg("error", f"Unknown intent: {intent}")
            tui.get_input("Press Enter to continue...")
            return


def delete_data_menu():
    while True:
        try:
            tui.clear_screen()
            options = [
                ("1", "Delete Data"),
                ("2", "Backup Database"),
                ("3", "Export Database to JSON"),
                ("4", "Import WAQI Historical CSV Database"),
                ("5", "[red]Return main menu[/]")
            ]
            tui.show_menu("ADMIN MENU", options)
            user_choice = tui.get_input("[brand]AILO Command Prompt (Select 1-6 OR type naturally):[/brand]")

            if user_choice == "":
                return
            elif user_choice == "1":
                password = tui.get_input("Please enter admin password to continue", password=True)
                if check_admin_password(password):
                    tui.show_msg("success", "Password correct")
                    delete_data_menu()
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
                file_path = tui.get_input("Enter the path to the WAQI CSV file")
                if not file_path or not os.path.exists(file_path):
                    tui.show_msg("error", "Invalid file path.")

                    continue

                if not os.path.isfile(file_path):
                    tui.show_msg("error", "Path provided is a directory, not a file.")

                    continue

                today = datetime.datetime.now().date()
                default_start = (today - datetime.timedelta(days=30)).strftime("%Y-%m-%d")
                default_end = today.strftime("%Y-%m-%d")

                start_date = tui.get_input(f"Enter Start Date (YYYY-MM-DD) [default: {default_start}]", default=default_start)
                end_date = tui.get_input(f"Enter End Date (YYYY-MM-DD) [default: {default_end}]", default=default_end)

                try:
                    # Quick check on format
                    datetime.datetime.strptime(start_date, "%Y-%m-%d")
                    datetime.datetime.strptime(end_date, "%Y-%m-%d")

                    with tui.create_spinner("Processing Data...") as progress:
                        task_id = progress.add_task("Processing Data...", total=None)
                        stats = db.import_historical_csv_with_pandas(file_path, start_date, end_date)

                    from rich.panel import Panel
                    from tui_engine import console

                    report_text = f"[info]Total Rows Processed:[/] [bold white]{stats['total_processed']}[/]\n"
                    report_text += f"[info]New Records Inserted:[/] [success]{stats['newly_inserted']}[/]"

                    panel = Panel(report_text, title="[success]Import Complete[/]", border_style="success", expand=False)
                    console.print(panel, justify="center")

                except ValueError as ve:
                    tui.show_msg("error", f"Date format error: {str(ve)}")
                except Exception as e:
                    tui.show_msg("error", f"Import failed: {str(e)}")

                tui.get_input("Press Enter to return to the admin menu")
            elif user_choice == "5":
                break
            else:
                tui.show_msg("error", "Invalid choice!")
                tui.get_input("Press Enter to return to the admin menu")
        except KeyboardInterrupt:
            tui.show_msg("info", "Action cancelled. Returning to menu...")

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
            user_choice = tui.get_input("[brand]AILO Command Prompt (Select 1-6 OR type naturally):[/brand]")

            if user_choice == "":
                return
            elif user_choice == "4":
                break

            if user_choice not in ["1", "2", "3"]:
                tui.show_msg("error", "Invalid choice. Please try again!!")

                continue

            city_name = get_city_selection("Enter city name to fetch data for")
            if not city_name:
                continue

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

            return


# |----------------- End of Main Menu and Display Functions ------------------|


def chat_loop():
    import sys
    import pandas as pd

    tui.show_splash_screen()

    ai = AIEngine()
    ai._ensure_model_loaded()

    current_persona = "router"

    while True:
        prompt = tui.get_omnibar_input(persona=current_persona)

        if not prompt:
            continue

        if prompt.lower() in ["/exit", "/quit"]:
            tui.show_msg("info", "AILO shutting down. Goodbye!")
            sys.exit(0)

        elif prompt.lower() == "/clear":
            tui.show_splash_screen()
            continue

        elif prompt.lower() == "/help":
            tui.show_msg("info", "Available Commands:\n/router - Default AI routing\n/analyst - Data science & Pandas logic\n/visualize - Terminal charting\n/train - AI vs AI synthetic training\n/backup - Backup database\n/export - Export to JSON\n/clear - Clear screen\n/exit - Quit")
            continue

        elif prompt.lower() == "/backup":
            backup_database(DB_FILE)
            continue

        elif prompt.lower() == "/export":
            filename = db.export_to_json()
            tui.show_msg("success", f"Exported to {filename}")
            continue

        # Switch Personas
        if prompt.lower() in ["/router", "/analyst", "/visualize", "/train"]:
            current_persona = prompt.lower().replace("/", "")
            tui.show_msg("info", f"Switched persona to: {current_persona.upper()}")
            continue

        # Handle Input based on Persona
        if current_persona == "router":
            orchestrate_intent(prompt, ai_instance=ai)

        elif current_persona == "analyst":
            from tui_engine import console
            console.print(f"[magenta][AILO-Analyst][/] Analyzing context...")
            df = shared_blackboard.get('last_data')
            if df is None or df.empty:
                tui.show_msg("warning", "Blackboard is empty. Ask /router to query data first.")
                continue

            # Simple Pandas stats
            stats = df.describe(include='all').to_json()
            with tui.create_spinner("Drafting Executive Summary...") as progress:
                task_id = progress.add_task("Drafting...", total=None)
                summary = ai.summarize_data(stats)
            tui.show_msg("info", f"[bold underline]Executive Summary[/]\n{summary}")

        elif current_persona == "visualize":
            try:
                import plotext as plt
                from tui_engine import console
                console.print(f"[yellow][AILO-Visualizer][/] Generating graph...")
                df = shared_blackboard.get('last_data')
                if df is None or df.empty:
                    tui.show_msg("warning", "Blackboard is empty. Ask /router to query data first.")
                    continue

                if 'aqi_value' not in df.columns or 'city_name' not in df.columns:
                    tui.show_msg("error", "Data does not contain 'aqi_value' and 'city_name' columns needed for plotting.")
                    continue

                # Plot
                plt.clear_figure()
                plt.theme("clear")
                # Group by city for simple bar
                grouped = df.groupby('city_name')['aqi_value'].mean().reset_index()
                plt.bar(grouped['city_name'].tolist(), grouped['aqi_value'].tolist())
                plt.title("Average AQI by City")
                plt.show()
                print("\n")
            except Exception as e:
                tui.show_msg("error", f"Plotting failed: {e}")

        elif current_persona == "train":
            # Direct call to the menu_7 training loop
            menu_7()
            # Switch back to router after training
            current_persona = "router"

# Override execution
if __name__ == "__main__":
    chat_loop()
