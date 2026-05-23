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
import random
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


def orchestrate_intent(initial_prompt: str):
    tui.clear_screen()
    tui.show_msg("info", f"User Input: [bold white]{initial_prompt}[/]")
    tui.show_msg("info", "Initializing AILO (AI Local Operator)...")

    with tui.create_spinner("Loading Qwen2.5-Coder Model (this may take a while)...") as progress:
        task_id = progress.add_task("Loading Qwen2.5-Coder Model (this may take a while)...", total=None)
        ai = AIEngine()
        ai._ensure_model_loaded()

    current_prompt = initial_prompt

    while True:
        with tui.create_spinner("AILO is parsing your intent...") as progress:
            task_id = progress.add_task("AILO is parsing your intent...", total=None)
            intent_data = ai.parse_intent(current_prompt)

        if intent_data.get("intent") == "unknown" and "failed" in intent_data.get("ask_user", ""):
            with tui.create_spinner("Local AI failed. Reaching out to Cloud Oracle...") as progress:
                task_id = progress.add_task("Cloud Oracle analyzing intent...", total=None)
                fixed_intent_data, explanation = ai.ai_oracle_intent_fallback(current_prompt)

            if fixed_intent_data and fixed_intent_data.get("intent") != "unknown":
                tui.show_msg("info", f"Oracle Explanation: {explanation}")
                tui.show_msg("warning", f"Oracle Fixed Intent: [bold white]{fixed_intent_data.get('intent')}[/]")
                tui.show_msg("success", "AILO encountered an error but autonomously fixed it via Cloud Oracle.")
                
                # Save to intent memory so local AI learns it for next time
                if ai.save_intent_memory(current_prompt, fixed_intent_data):
                    from tui_engine import console
                    console.print("[success]Intent Memory Updated: Local model learned a new behavior![/success]")
                
                intent_data = fixed_intent_data
            else:
                tui.show_msg("error", f"Cloud Oracle also failed: {explanation}")
                tui.get_input("Press Enter to return")
                return

        status = intent_data.get("status")

        if status == "incomplete":
            ask_text = intent_data.get("ask_user", "Please provide more information.")
            tui.show_msg("warning", ask_text)
            user_reply = tui.get_input("Your response (or press Enter to cancel)")
            if not user_reply:
                return
            # Append context
            current_prompt = current_prompt + " " + user_reply
            continue

        # Status is complete
        intent = intent_data.get("intent")
        params = intent_data.get("parameters", {})

        if intent == "navigate":
            tui.show_msg("info", f"Navigating as requested...")
            tui.get_input("Press Enter to continue")
            return

        elif intent == "query":
            # Apply Fuzzy Matching Hint
            target_city = params.get("city")
            prompt_for_sql = current_prompt
            prompt_for_oracle = initial_prompt
            if target_city:
                matches, is_fuzzy = db.find_city_matches(target_city)
                if matches:
                    best_match = matches[0]
                    # Append hint if there's a fuzzy match or spelling correction needed
                    if is_fuzzy or best_match.lower() != target_city.lower():
                        hint_msg = f"\nHINT: The exact city name in the database the user is referring to is '{best_match}'. Use this exact string."
                        prompt_for_sql += hint_msg
                        prompt_for_oracle += hint_msg

            # HITL Self-Correction Loop
            while True:
                with tui.create_spinner("AILO is generating SQL...") as progress:
                    task_id = progress.add_task("AILO is generating SQL...", total=None)
                    sql_query = ai.translate_text_to_sql(prompt_for_sql)

                if not sql_query:
                    tui.show_msg("error", "AILO failed to generate a query.")
                    tui.get_input("Press Enter to return to menu")
                    return

                safe_sql = sql_query.replace("[", "\\[").replace("]", "\\]")
                tui.show_msg("warning", f"Generated SQL: [bold white]{safe_sql}[/]")

                with tui.create_spinner("Generating explanation...") as progress:
                    task_id = progress.add_task("Generating explanation...", total=None)
                    explanation = ai.explain_sql(sql_query)
                tui.show_msg("info", f"Explanation: {explanation}")

                success, result, cursor_description = db.execute_ai_read_query(sql_query)
                if not success:
                    error_msg = str(result)
                    with tui.create_spinner("Local AI failed. Reaching out to Cloud Oracle...") as progress:
                        task_id = progress.add_task("Cloud Oracle analyzing...", total=None)
                        fixed_sql, oracle_explanation = ai.ai_oracle_fallback(prompt_for_oracle, sql_query, error_msg)

                    if fixed_sql:
                        tui.show_msg("info", f"Oracle Explanation: {oracle_explanation}")
                        safe_sql = fixed_sql.replace("[", "\\[").replace("]", "\\]")
                        tui.show_msg("warning", f"Oracle Fixed SQL: [bold white]{safe_sql}[/]")
                        o_success, o_result, o_cursor_description = db.execute_ai_read_query(fixed_sql)

                        if o_success:
                            tui.show_msg("success", "AILO encountered an error but autonomously fixed it via Cloud Oracle.")

                            # Learn it to ai_memory.json
                            import json
                            memories = []
                            try:
                                with open("ai_memory.json", "r") as f:
                                    loaded_mem = json.load(f)
                                    if isinstance(loaded_mem, list):
                                        memories = loaded_mem
                            except:
                                pass
                            memories.append({"query": current_prompt, "sql": fixed_sql})
                            try:
                                with open("ai_memory.json", "w") as f:
                                    json.dump(memories, f, indent=4)
                            except:
                                pass

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
                    # Successful query

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
                tui.get_input("Press Enter to continue")
                return

        elif intent == "insert":
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

            date_val = params.get("date")
            if date_val:
                current_time = datetime.datetime.now().strftime("%H:%M")
                ts = f"{date_val} {current_time}"
            else:
                ts = time_stamp()

            new_record = CityRecord(city_name=city, aqi_value=float(aqi), timestamp=ts)
            is_new = db.add_record(new_record)
            if is_new:
                tui.show_msg("success", f"AQI data for {city} ({ts}) saved successfully!")
            else:
                tui.show_msg("info", f"AQI data for {city} at this timestamp ({ts}) already exists.")
            tui.get_input("Press Enter to continue")
            return

        elif intent == "delete":
            city = params.get("city")
            date = params.get("date")
            delete_all = params.get("delete_all")

            if delete_all:
                pwd = tui.get_input("ADMIN ACTION: Please enter the admin password to wipe the database:", password=True)
                if pwd == "admin123":
                    deleted = db.delete_records(delete_all=True)
                    tui.show_msg("success", f"Database wiped! Deleted {deleted} records.")
                else:
                    tui.show_msg("error", "Incorrect password. Deletion cancelled.")
                tui.get_input("Press Enter to continue...")
                return

            if city:
                city = city.title()
                
                # If date is provided natively by LLM, perform instant granular delete without UI prompt
                if date:
                    deleted = db.delete_records(city_name=city, start_date=date, end_date=date)
                    if deleted > 0:
                        tui.show_msg("success", f"Successfully deleted {deleted} records for {city} on {date}.")
                    else:
                        tui.show_msg("info", f"No records found for {city} on {date} to delete.")
                    tui.get_input("Press Enter to continue...")
                    return

                records = db.get_records_by_city(city)
                if not records:
                    tui.show_msg("info", f"No records found for {city}.")
                    tui.get_input("Press Enter to continue...")
                    return
                # Show Preview Table
                tui.clear_screen()
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
                # Without city, let's just abort to be safe, or redirect to menu_4
                tui.show_msg("warning", "Granular delete via AILO requires a specific city. Redirecting to admin menu.")
                menu_4()
            tui.get_input("Press Enter to continue...")
            return

        elif intent == "fetch_data":
            source = params.get("source")
            city = params.get("city")
            start_date = params.get("start_date")
            end_date = params.get("end_date")

            if not source:
                if city and not params.get("url"):
                    source = "api"
                else:
                    source = "csv"

            if source == "api":
                if not city:
                    tui.show_msg("error", "A specific city is required to fetch API data.")
                    tui.get_input("Press Enter to continue...")
                    return
                city = city.title()
                
                with tui.create_spinner(f"Fetching WAQI API data for [cyan]{city}[/]...") as progress:
                    task_id = progress.add_task("Fetching Live Data...", total=None)
                    live_aqi = api_integration.get_station_aqi_by_name(city)
                
                if live_aqi == 0.0:
                    tui.show_msg("error", f"Could not fetch API data for {city}. Station not found.")
                else:
                    if start_date and end_date:
                        # Generate mock history anchored to live value
                        sd = datetime.datetime.strptime(start_date, "%Y-%m-%d")
                        ed = datetime.datetime.strptime(end_date, "%Y-%m-%d")
                        delta = ed - sd
                        tui.show_msg("info", f"Generating {delta.days + 1} historical records based on WAQI API anchor value: [bold]{live_aqi}[/]")
                        count = 0
                        for i in range(delta.days + 1):
                            current_date = sd + datetime.timedelta(days=i)
                            # Add random noise to anchor value
                            mock_aqi = max(0.0, round(live_aqi + random.uniform(-15.0, 15.0), 1))
                            db.add_record(CityRecord(city_name=city, aqi_value=mock_aqi, timestamp=current_date.strftime("%Y-%m-%d %H:%M")))
                            count += 1
                        tui.show_msg("success", f"Inserted {count} API-based historical records for {city}.")
                    else:
                        # Just insert live
                        db.add_record(CityRecord(city_name=city, aqi_value=live_aqi, timestamp=time_stamp()))
                        tui.show_msg("success", f"Inserted live WAQI API data for {city}: {live_aqi}")
                
                tui.get_input("Press Enter to continue...")
                return

            else:
                # Default to CSV behavior
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

                if not file_path.startswith("http") and not os.path.exists(file_path):
                    tui.show_msg("error", "Invalid or missing local file path.")
                    tui.get_input("Press Enter to continue...")
                    return

                try:
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
                return

        else:
            tui.show_msg("error", f"Unknown intent: {intent}")
            tui.get_input("Press Enter to continue...")
            return



def menu_7():
    import time
    tui.clear_screen()
    tui.show_msg("info", "Welcome to the Autonomous AI Training Room!")

    options = [
        ("1", "Time/Date Analytics"),
        ("2", "Complex Aggregations"),
        ("3", "Edge Cases/Typos"),
        ("4", "Custom Simulation (User Defined)"),
        ("5", "[red]Return to Menu[/]")
    ]
    tui.show_menu("SELECT TRAINING THEME", options)
    choice = tui.get_input("Choose Theme (1-5)")

    if choice == "5" or not choice:
        return

    topic = ""
    if choice == "1":
        topic = "Time/Date Analytics"
    elif choice == "2":
        topic = "Complex Aggregations"
    elif choice == "3":
        topic = "Edge Cases/Typos"
    elif choice == "4":
        topic = tui.get_input("Enter your custom topic (e.g. 'industrial zones')")
        if not topic:
            return
    else:
        return

    count_str = tui.get_input("How many questions for this loop? (Max 10)")
    if not count_str or not count_str.isdigit():
        return
    count = min(int(count_str), 10)

    tui.clear_screen()
    with tui.create_spinner("Booting AI Engines...") as progress:
        task_id = progress.add_task("Booting AI Engines...", total=None)
        ai = AIEngine()
        ai._ensure_model_loaded()

    tui.show_msg("info", f"Generating {count} questions for topic: {topic}...")

    with tui.create_spinner("Oracle is creating syllabus...") as progress:
        task_id = progress.add_task("Creating syllabus...", total=None)
        questions = ai.generate_training_questions(topic, count)

    if not questions:
        tui.show_msg("error", "Oracle failed to generate questions. Check API key or connection.")
        tui.get_input("Press Enter to return")
        return

    from tui_engine import console

    tui.show_msg("success", "Training syllabus created. Starting autonomous loop...")
    print("\n")

    for idx, q in enumerate(questions, 1):
        console.print(f"\n[bold magenta]--- Test {idx}/{len(questions)} ---[/]")
        console.print(f"[info]Teacher (Gemini) asked:[/] {q}")

        with tui.create_spinner("Student (Qwen) is coding...") as progress:
            task_id = progress.add_task("Coding...", total=None)
            sql = ai.translate_text_to_sql(q)

        safe_sql = sql.replace("[", "\\[").replace("]", "\\]")
        console.print(f"[cyan]Student (Qwen) SQL:[/] {safe_sql}")

        success, result, cursor_description = db.execute_ai_read_query(sql)

        final_sql = sql
        passed = True

        if not success:
            error_msg = str(result)
            with tui.create_spinner("Student failed. Oracle intervening...") as progress:
                task_id = progress.add_task("Oracle intervening...", total=None)
                fixed_sql, explanation = ai.ai_oracle_fallback(q, sql, error_msg)

            if fixed_sql:
                safe_fixed = fixed_sql.replace("[", "\\[").replace("]", "\\]")
                console.print(f"[warning]Oracle Intervention: SQL Fixed[/warning] -> {safe_fixed}")
                console.print(f"[info]Oracle Explanation:[/info] {explanation}")
                o_success, o_result, _ = db.execute_ai_read_query(fixed_sql)
                if o_success:
                    final_sql = fixed_sql
                else:
                    passed = False
                    console.print(f"[danger]Oracle also failed: {o_result}[/danger]")
            else:
                passed = False
                console.print(f"[danger]Oracle failed to intervene: {explanation}[/danger]")
        else:
            console.print("[success]Test Passed![/success]")

        if passed and final_sql:
            saved = ai.save_to_memory(q, final_sql)
            if saved:
                console.print("[success]Memory Updated: New pattern learned![/success]")
            else:
                console.print("[muted]Memory Skipped: Duplicate or redundant pattern.[/muted]")

        if idx < len(questions):
            with tui.create_spinner("Cooling down API for 4 seconds...") as progress:
                task_id = progress.add_task("Cooling down...", total=None)
                console.print("[muted]Cooling down API for 4 seconds...[/muted]")
                time.sleep(4)

    tui.get_input("\n[bold white]Training Complete. Press Enter to return to menu.[/bold white]")

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
                ("6", "Autonomous AI Training Room"),
                ("7", "[red]Exit Program[/]")
            ]
            tui.show_menu("AIR QUALITY MONITOR SYSTEM", options)
            choice = tui.get_input("[brand]AILO Command Prompt (Select 1-7 OR type naturally) [/brand]")

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
                menu_7()
            elif choice == "7":
                exit_choice = tui.get_input("Do you want to Exit the program? (Y/N)", choices=["Y", "N", "y", "n"])
                if exit_choice.upper() == "Y":
                    tui.show_msg("info", "You logged out!!")
                    break
                elif exit_choice.upper() == "N":
                    continue
            elif choice == "":
                break
            else:
                # Natural language omnibar flow
                orchestrate_intent(choice)
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
def get_city_selection(prompt_text: str) -> str:
    """
    Centralized smart search engine.
    Uses DatabaseManager.find_city_matches to provide partial or fuzzy matched suggestions.
    """
    query = tui.get_input(prompt_text)
    if not query:
        return ""

    matches, is_fuzzy = db.find_city_matches(query)

    if not matches:
        return query.title()

    if len(matches) == 1 and matches[0].lower() == query.strip().lower():
        return matches[0]

    tui.clear_screen()
    if is_fuzzy:
        tui.show_msg("warning", "Exact match not found. Showing closest suggestions:")

    rows = [[str(idx), city] for idx, city in enumerate(matches, 1)]
    tui.show_table("Select a City", ["ID", "City Name"], rows)

    choice = tui.get_input("[info]Multiple cities found. Select ID to proceed, or press Enter to cancel[/]")
    if not choice or not choice.isdigit():
        return ""

    idx = int(choice) - 1
    if 0 <= idx < len(matches):
        return matches[idx]

    return ""

def menu_2():
    while True:
        try:
            tui.clear_screen()
            all_records = db.get_all_records()
            cities_from_db = list(set([record.city_name for record in all_records]))

            tui.show_menu("SEARCH MENU", []) # Just for title consistency
            city_name = get_city_selection("Enter city name to search (Local or WAQI Live)")
            if not city_name:
                return

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
                        rows = [[city_name, str(r.aqi_value), get_epa_category_raw(r.aqi_value), f"[{get_epa_color_hex(r.aqi_value)}]███[/]", r.timestamp] for r in records]
                        tui.show_table(f"Records for {city_name}", ['City', 'AQI', 'Category', 'Color', 'Timestamp'], rows)
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
            user_choice = tui.get_input("[brand]AILO Command Prompt (Select 1-6 OR type naturally):[/brand]")

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
                city_name = get_city_selection("Please enter city name for AI Prediction")
                if not city_name:
                    continue

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
def delete_data_menu():
    while True:
        try:
            tui.clear_screen()
            options = [
                ("1", "Delete by City"),
                ("2", "Delete by Date Range"),
                ("3", "[danger]Factory Reset (Delete ALL Data)[/]"),
                ("4", "[red]Return Admin Menu[/]")
            ]
            tui.show_menu("DELETE DATA", options)
            user_choice = tui.get_input("[brand]AILO Command Prompt (Select 1-6 OR type naturally):[/brand]")

            if user_choice == "" or user_choice == "4":
                return

            elif user_choice == "1":
                city_name = get_city_selection("Enter city name to delete")
                if not city_name:
                    continue

                records = db.get_records_by_city(city_name)
                if not records:
                    tui.show_msg("info", f"No records found for {city_name}.")
                    tui.get_input("Press Enter to continue...")
                    continue

                # Show Preview Table
                tui.clear_screen()
                rows = [[str(r.id), r.city_name, str(r.aqi_value), get_epa_category_raw(r.aqi_value), f"[{get_epa_color_hex(r.aqi_value)}]███[/]", r.timestamp] for r in records]
                tui.show_table(f"Preview: {city_name} Records", ['ID', 'City', 'AQI', 'Category', 'Color', 'Timestamp'], rows, use_pager=True)

                choice = tui.get_input("[info]Enter IDs to delete (e.g., 1, 4, 5)[/]\n[danger]Type 'ALL' to delete all listed records[/]\n[accent]Type 'C' to Cancel[/]\n> ")

                if not choice or choice.strip().upper() == 'C':
                    tui.show_msg("info", "Deletion cancelled.")
                    tui.get_input("Press Enter to continue...")
                    continue
                elif choice.strip().upper() == 'ALL':
                    deleted = db.delete_records(city_name=city_name)
                    tui.show_msg("success", f"Successfully deleted {deleted} records.")
                    tui.get_input("Press Enter to continue...")
                    continue
                else:
                    # Granular Deletion
                    try:
                        ids_to_delete = [int(x.strip()) for x in choice.split(",") if x.strip().isdigit()]
                        if not ids_to_delete:
                            raise ValueError()

                        deleted = db.delete_records_by_ids(ids_to_delete)
                        tui.show_msg("success", f"Successfully deleted {deleted} records.")
                    except ValueError:
                        tui.show_msg("error", "Invalid ID format. Operation cancelled.")

                    tui.get_input("Press Enter to continue...")

            elif user_choice == "2":
                start_date = tui.get_input("Enter Start Date (YYYY-MM-DD)")
                end_date = tui.get_input("Enter End Date (YYYY-MM-DD)")
                if not start_date or not end_date:
                    continue
                try:
                    datetime.datetime.strptime(start_date, "%Y-%m-%d")
                    datetime.datetime.strptime(end_date, "%Y-%m-%d")
                except ValueError:
                    tui.show_msg("error", "Invalid date format.")
                    tui.get_input("Press Enter to continue...")
                    continue

                count = db.count_records(start_date=start_date, end_date=end_date)
                if count == 0:
                    tui.show_msg("info", f"No records found between {start_date} and {end_date}.")
                    tui.get_input("Press Enter to continue...")
                    continue

                tui.show_msg("warning", f"Uyarı: Bu tarih aralığına ait {count} kayıt bulundu.")
                confirm = tui.get_input("[danger]Are you sure? Type 'DELETE' to confirm deletion, or press Enter to cancel[/]")

                if confirm.strip().upper() == "DELETE":
                    deleted = db.delete_records(start_date=start_date, end_date=end_date)
                    tui.show_msg("success", f"Successfully deleted {deleted} records.")
                else:
                    tui.show_msg("info", "Deletion cancelled.")
                tui.get_input("Press Enter to continue...")

            elif user_choice == "3":
                count = db.count_records(count_all=True)
                if count == 0:
                    tui.show_msg("info", "Database is already empty.")
                    tui.get_input("Press Enter to continue...")
                    continue

                tui.show_msg("warning", f"Uyarı: Veritabanındaki tüm ({count}) kayıtlar silinecek!")
                confirm = tui.get_input("[danger]Are you sure? Type 'DELETE ALL' to confirm deletion, or press Enter to cancel[/]")

                if confirm.strip().upper() == "DELETE ALL":
                    deleted = db.delete_records(delete_all=True)
                    tui.show_msg("success", f"Successfully deleted {deleted} records.")
                else:
                    tui.show_msg("info", "Deletion cancelled.")
                tui.get_input("Press Enter to continue...")

            else:
                tui.show_msg("error", "Invalid choice!")
                tui.get_input("Press Enter to continue...")

        except KeyboardInterrupt:
            tui.show_msg("info", "Action cancelled. Returning to menu...")
            return

def menu_4():
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
                    tui.get_input("Press Enter to continue...")
                    continue

                if not os.path.isfile(file_path):
                    tui.show_msg("error", "Path provided is a directory, not a file.")
                    tui.get_input("Press Enter to continue...")
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
            user_choice = tui.get_input("[brand]AILO Command Prompt (Select 1-6 OR type naturally):[/brand]")

            if user_choice == "":
                return
            elif user_choice == "4":
                break

            if user_choice not in ["1", "2", "3"]:
                tui.show_msg("error", "Invalid choice. Please try again!!")
                tui.get_input("Press Enter to continue...")
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
            tui.get_input("Press Enter to continue")
            return


# |----------------- End of Main Menu and Display Functions ------------------|

if __name__ == "__main__":
    main_menu()