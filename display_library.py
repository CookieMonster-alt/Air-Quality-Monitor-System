"""
This is Display Functions Program
Mostly in this code 'f string formatting' is used
It can be use for other terminal based programs

It divides terminal screen into 3 parts:

| Left Side | Middle Side | Right Side |

It can print texts in 9 different part of screen

| (Left-left) (Left-Middle) (Right-Right) |
| (Middle-Left) (Middle-Middle) (Middle-Right) |
| (Right-Left) (Right-Middle) (Right-Right) |

It can print input text in 7 different part of screen

| (Left-left) (Right-Right) |
| (Middle-Left) (Middle-Middle) (Middle-Right) |
| (Right-Left) (Right-Right) |


It contains useful text alignment functions

This is code written by iliya METODIEV for school assignment,
part of Air Quality Monitor System Program
Started Date : 17/10/2025
Finished Date : 7/11/2025
"""

import shutil, os, re

# ---------------- Constant Variables ----------------
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

def screen_sizes():
    screen_sizes = shutil.get_terminal_size()
    return screen_sizes

def clear_screen():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

def create_three_columns():
    left_side_size= screen_sizes().columns // 3
    right_side_size = screen_sizes().columns // 3
    middle_size = screen_sizes().columns - left_side_size - right_side_size
    all_screen_sizes = {'Left size': left_side_size, 'Middle size': middle_size, 'Right size': right_side_size}
    return all_screen_sizes

def menu_title_centered(title, under_line , color):
    clear_screen()
    middle_size = create_three_columns()['Middle size']
    print(f'{under_line * (middle_size):^{screen_sizes().columns}}')
    print(f'{color}{title:^{screen_sizes().columns}}{RESET}')
    print(f'{under_line * (middle_size):^{screen_sizes().columns}}\n\n')
    

def left_padding():
    left_padding = create_three_columns()['Left size']
    return left_padding

def middle_padding():
    middle_padding = create_three_columns()['Middle size']
    return middle_padding

def right_padding():
    right_padding = create_three_columns()['Right size']
    return right_padding

def print_left_middle(text):
    padding = int(left_padding())
    print(f'{text:^{padding}}')
    
def print_middle_middle(text):
    left_pad = int(left_padding())
    middle_pad = int(middle_padding())
    visible_length = get_visible_string_length(text)
    padding =(middle_pad - visible_length) // 2
    print(f'{" " * (left_pad + padding)}{text}')
    
    
def print_right_middle(text):
    left_pad = int(left_padding())
    middle_pad = int(middle_padding())
    right_pad = int(right_padding())
    print(f'{" " * (left_pad + middle_pad)}{text:^{right_pad}}')
    
def print_left_left(text):
    padding = int(left_padding())
    print(f'{text:<{padding}}')

def print_middle_left(text):
    left_pad = int(left_padding())
    middle_pad = int(middle_padding())
    print(f'{" " * left_pad}{text:<{middle_pad}}')

def print_right_left(text):
    lef_pad = int(left_padding())
    middle_pad = int(middle_padding())
    right_pad = int(right_padding())
    print(f'{" " * (lef_pad + middle_pad)}{text:<{right_pad}}')
    
def print_left_right(text):
    padding = int(left_padding())
    print(f'{text:>{(padding)}}')

def print_middle_right(text):
    left_pad = int(left_padding())
    middle_pad = int(middle_padding())
    print(f'{" " * left_pad}{text:>{(middle_pad)}}')

def print_right_right(text):
    lef_pad = int(left_padding())
    middle_pad = int(middle_padding())
    right_pad = int(right_padding())
    print(f'{" " * (lef_pad + middle_pad)}{text:>{(right_pad)}}')
    
def submenu_text_print(text, color):
    print(f'{' ' * (left_padding()+middle_padding()//3+(int(3)))}{color}{text}\n{RESET}')
    
def print_and_get_input(text, column=str, align=str):
    """
    This function takes text input and formats it based on specified column and
    alignment parameters before returning user input.
    
    The function takes in three parameters: text, column, and
    align
    """
    if column == 'middle' and align == 'left':
        print(f'{" " * left_padding()}{text}', end='')
        
    elif column == 'middle' and align == 'right':
        print(f'{text:>{left_padding()+middle_padding()}}', end='')
    
    elif column == 'middle' and align == 'middle':
        left_pad = left_padding()
        middle_pad = middle_padding()
        visible_length = get_visible_string_length(text)
        padding =(middle_pad - visible_length) // 2
        print(f'{" " * (left_pad + padding)}{text}', end='')
        
    elif column == 'left' and align == 'left':
        print(f'{text}', end='')
        
    elif column == 'left' and align == 'right':
        print(f'{text:>{left_padding()}}', end='')
        
    elif column == 'right' and align == 'left':
        print(f'{' ' * int(left_padding() + middle_padding())}{text}', end='')
        
    elif column == 'right' and align == 'right':
        print(f'{text:>{left_padding() + middle_padding() + right_padding()}}', end='')
        
    return input()

def get_visible_string_length(text):
    return len(re.sub('\\033\[[0-9;]*m', '', text))

def middle_column_padding():
    middle_column_size = create_three_columns()['Middle size']
    return middle_column_size

def divide_middle_column_in_three():
    all_sizes = {}
    middle_column_size = middle_column_padding()
    all_sizes['Left size'] = middle_column_size // 3
    all_sizes['Right size'] = middle_column_size // 3
    all_sizes['Middle size'] = middle_column_size - all_sizes['Left size'] - all_sizes['Right size']
    return all_sizes

def draw_border_head(border_line, border_connection):
    # The function draws a border head line with specified line and connection characters.
    border_widths = [
        divide_middle_column_in_three()['Left size'], 
        divide_middle_column_in_three()['Middle size'], 
        divide_middle_column_in_three()['Right size']]
    return f'{border_connection}{border_line * border_widths[0]}{border_connection}{border_line * border_widths[1]}{border_connection}{border_line * border_widths[2]}{border_connection}'

def create_head_titles(titles=[]):
    all_sizes = divide_middle_column_in_three()
    return f'|{YELLOW}{titles[0]:^{all_sizes["Left size"]}}{WHITE}|{RESET}{YELLOW}{titles[1]:^{all_sizes["Middle size"]}}{WHITE}|{RESET}{YELLOW}{titles[2]:^{all_sizes["Right size"]}}{RESET}|'

def create_data_in_middle_row(data=[]):
    all_sizes = divide_middle_column_in_three()
    return f'|{data[0]:^{all_sizes["Left size"]}}|{data[1]:^{all_sizes["Middle size"]}}|{data[2]:^{all_sizes["Right size"]}}|'