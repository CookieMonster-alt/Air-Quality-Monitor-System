from rich.console import Console
from rich.panel import Panel
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

console = Console(theme=custom_theme)

from rich.padding import Padding

def clear_screen():
    console.clear()

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

def get_input(prompt_text: str, choices: list = None, default=None, password=False) -> str:
    """
    Wraps Rich Prompt. Handles KeyboardInterrupt cleanly by returning an empty string.
    """
    # Print the footer directly before the prompt as per CLIG
    print_footer()
    try:
        if choices:
            result = Prompt.ask(f"[accent]{prompt_text}[/]", console=console, choices=choices, default=default, password=password)
        else:
            result = Prompt.ask(f"[accent]{prompt_text}[/]", console=console, default=default, password=password)

        if result is None:
            return ""
        return str(result).strip()
    except KeyboardInterrupt:
        console.print("\n[info]Action cancelled. Returning to menu...[/]")
        return ""
    except EOFError:
        return ""

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

def show_table(title: str, columns: list, rows: list):
    """
    Displays a data table.
    """
    table = Table(title=f"[brand]{title}[/]", box=box.SQUARE, header_style="accent", border_style="muted", show_lines=True)
    for col in columns:
        table.add_column(col, justify="center")
    for row in rows:
        table.add_row(*[str(item) for item in row])

    console.print(table, justify="center")
    print()

def print_footer():
    """
    Footer explaining shortcuts.
    """
    footer_text = "[muted][ENTER] Submit/Skip  |  [CTRL+C] Cancel/Return[/]"
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
