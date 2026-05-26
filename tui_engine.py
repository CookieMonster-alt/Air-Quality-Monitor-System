from rich.console import Console, Group
from rich.panel import Panel
from rich.align import Align
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich import box
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.theme import Theme

custom_theme = Theme({
    "brand": "bold #00E5FF",
    "accent": "#B388FF",
    "success": "bold #00E676",
    "warning": "bold #FFEA00",
    "danger": "bold #FF1744",
    "info": "italic #29B6F6",
    "muted": "dim #78909C",
    "aqi_good": "bold black on #00E400",
    "aqi_moderate": "bold black on #FFFF00",
    "aqi_sensitive": "bold white on #FF7E00",
    "aqi_unhealthy": "bold white on #FF0000",
    "aqi_very_unhealthy": "bold white on #8F3F97",
    "aqi_hazardous": "bold white on #7E0023"
})

import os
# Ensure LESS is configured to interpret raw ANSI escape sequences
os.environ["LESS"] = os.environ.get("LESS", "") + " -R"

# Let rich auto-detect the optimal color system to prevent ANSI escape bleed
# on terminals that do not support or misinterpret the forced '256' flag (or dim attributes).
console = Console(theme=custom_theme)

from rich.padding import Padding

def clear_screen():
    pass # Disabled to support Zero-UI scrollback Chat Paradigm

def show_splash_screen():
    console.clear()
    logo = """[brand]
    █████╗ ██╗██╗      ██████╗
   ██╔══██╗██║██║     ██╔═══██╗
   ███████║██║██║     ██║   ██║
   ██╔══██║██║██║     ██║   ██║
   ██║  ██║██║███████╗╚██████╔╝
   ╚═╝  ╚═╝╚═╝╚══════╝ ╚═════╝
    [/brand]"""
    console.print(logo, justify="center")
    console.print("[muted]Akıllı Otonom Hava Kalitesi Analiz Uzmanı[/muted]\n", justify="center")

def get_omnibar_input(persona="router") -> str:
    from prompt_toolkit import PromptSession
    from prompt_toolkit.completion import WordCompleter
    from prompt_toolkit.styles import Style

    # Set up our commands for Ghost Text completion
    commands = ['/router', '/analyst', '/visualize', '/train', '/backup', '/export', '/clear', '/help', '/exit']
    completer = WordCompleter(commands, ignore_case=True)

    # Determine prompt color and name
    if persona == "router":
        prompt_html = '<ansicyan>[AILO-Router] ❯</ansicyan> '
    elif persona == "analyst":
        prompt_html = '<ansimagenta>[AILO-Analyst] ❯</ansimagenta> '
    elif persona == "visualize":
        prompt_html = '<ansiyellow>[AILO-Visualizer] ❯</ansiyellow> '
    elif persona == "train":
        prompt_html = '<ansigreen>[AILO-Trainer] ❯</ansigreen> '
    else:
        prompt_html = '<ansicyan>[AILO-Router] ❯</ansicyan> '

    style = Style.from_dict({
        'prompt': 'ansicyan bold',
        '': 'ansiwhite'
    })

    # We maintain a global session so prompt history persists in memory
    global prompt_session
    if 'prompt_session' not in globals():
        prompt_session = PromptSession()

    try:
        from prompt_toolkit.formatted_text import HTML
        # Print standard line break for readability before prompt
        print()
        user_input = prompt_session.prompt(
            HTML(prompt_html),
            completer=completer,
            complete_while_typing=True
        )
        return user_input.strip()
    except KeyboardInterrupt:
        console.print("\n[info]Action cancelled.[/info]")
        return ""
    except EOFError:
        return "/exit"


def show_menu(title: str, options: list):
    """
    Shows a menu centered in a panel.
    options is a list of tuples: (key, description)
    """
    print("\n") # Add top margin
    table = Table(box=None, show_header=False, padding=(0, 2))
    for key, desc in options:
        table.add_row(f"[accent]{key}[/]", desc)

    panel = Panel(
        table,
        title=f"[brand]{title}[/]",
        expand=False,
        border_style="muted",
        padding=(1, 4) # Internal padding
    )
    console.print(panel, justify="center")
    print("\n") # Add bottom margin


def show_msg(msg_type: str, text: str):
    """
    Replaces old print_msg. No prefix tags, just colored text.
    """
    print() # spacing before message
    if msg_type == 'error':
        console.print(f"[danger]{text}[/]", justify="center")
    elif msg_type == 'success':
        console.print(f"[success]{text}[/]", justify="center")
    elif msg_type == 'info':
        console.print(f"[info]{text}[/]", justify="center")
    elif msg_type == 'warning':
        console.print(f"[warning]{text}[/]", justify="center")
    else:
        console.print(text, justify="center")
    print() # spacing after message

def show_table(title: str, columns: list, rows: list, use_pager: bool = False):
    """
    Displays a data table.
    """
    table = Table(title=f"[brand]{title}[/]", box=box.SQUARE, header_style="accent", border_style="muted", show_lines=True)
    for col in columns:
        table.add_column(col, justify="center")
    for row in rows:
        table.add_row(*[str(item) for item in row])

    if use_pager:
        with console.pager(styles=True):
            console.print(Align.center(table))
    else:
        console.print(Align.center(table))
    print()

def print_footer():
    """
    Footer explaining shortcuts.
    """
    footer_text = r"[muted]\[ENTER] Submit/Skip  |  \[CTRL+C] Cancel/Return[/]"
    console.print(footer_text, justify="center")


def create_spinner(text: str):
    """
    Returns a Progress context manager configured as a spinner.
    """
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True
    )

def get_input(prompt_text: str, password: bool = False, choices: list = None, default: str = None) -> str:
    """
    Get user input using rich Prompt.
    """
    return Prompt.ask(prompt_text, password=password, choices=choices, default=default)
