import os
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.styles import Style
from rich.console import Console

class TUIEngine:
    """
    Object-oriented wrapper for prompt_toolkit.
    Ensures safe, asynchronous, scrollback-friendly terminal interaction.
    """
    def __init__(self):
        # Enforce 256 colors for older terminals silently
        os.environ["LESS"] = os.environ.get("LESS", "") + " -R"

        self.session = PromptSession()

        # We do not enforce color_system="256" here to prevent ANSI bleeding,
        # allowing rich to auto-detect optimal settings.
        self.rich_console = Console()

        self.commands = [
            '/router', '/analyst', '/visualize', '/train',
            '/backup', '/export', '/clear', '/help', '/exit'
        ]
        self.completer = WordCompleter(self.commands, ignore_case=True)

        # We define simple colors using standard ANSI HTML tags provided by prompt_toolkit
        self.style = Style.from_dict({
            'brand': 'ansicyan bold',
            'system': 'ansigray',
            'error': 'ansired bold',
        })

    def show_splash_screen(self):
        """Clears screen once and prints the ASCII logo."""
        from prompt_toolkit.shortcuts import clear
        clear()

        logo = """
    █████╗ ██╗██╗      ██████╗
   ██╔══██╗██║██║     ██╔═══██╗
   ███████║██║██║     ██║   ██║
   ██╔══██║██║██║     ██║   ██║
   ██║  ██║██║███████╗╚██████╔╝
   ╚═╝  ╚═╝╚═╝╚══════╝ ╚═════╝
        """
        from prompt_toolkit import print_formatted_text
        print_formatted_text(HTML(f'<brand>{logo}</brand>'), style=self.style)
        print_formatted_text(HTML('<system>Intelligent Autonomous Air Quality Analysis Expert</system>\n'), style=self.style)

    def print_system_message(self, message: str, level: str = "system"):
        """
        Thread-safe alternative to standard print().
        Uses prompt_toolkit to flush to terminal buffer securely.
        """
        from prompt_toolkit import print_formatted_text
        if level == "error":
            print_formatted_text(HTML(f'<error>[ERROR]</error> {message}'), style=self.style)
        else:
            print_formatted_text(HTML(f'<system>[AILO]</system> {message}'), style=self.style)

    def print_rich_table(self, table):
        """
        Delegates the rendering of a rich object securely to the initialized console.
        """
        self.rich_console.print(table)

    async def get_omnibar_input_async(self, persona: str = "router") -> str:
        """
        Yields an asynchronous prompt, preventing event-loop blocking.
        """
        if persona == "router":
            prompt_html = '<ansicyan>[AILO-Router] ❯</ansicyan> '
        else:
            prompt_html = f'<ansigreen>[AILO-{persona.title()}] ❯</ansigreen> '

        # Using prompt_async yields control to the asyncio event loop while waiting for user typing
        result = await self.session.prompt_async(
            HTML(prompt_html),
            completer=self.completer,
            complete_while_typing=True,
            style=self.style
        )
        return result.strip()
