"""
Main Asynchronous TUI application for AILO.

Orchestrates `rich.live.Live` for a dynamic grid UI and `prompt_toolkit` for non-blocking
user input, running entirely within an asyncio event loop to handle background tasks seamlessly.
"""

import asyncio
from dataclasses import dataclass, field
import random

from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.formatted_text import HTML
from rich.live import Live
from rich.layout import Layout
from rich.console import Console

from src.tui.layout import create_ailo_layout
from src.tui.theme import AILO_THEME
from src.tui.components import (
    SystemStats,
    AQIReading,
    ModelStats,
    IntentLayerStatus,
    ConversationMessage,
    build_header,
    build_left_sidebar,
    build_right_sidebar,
    build_conversation_area
)

@dataclass
class AILOState:
    """Central mutable state object for the TUI."""
    sys_stats: SystemStats = field(default_factory=lambda: SystemStats(25.0, 45.0, 3.6, 42.1, 86400, 60.0))
    aqi_reading: AQIReading = field(default_factory=lambda: AQIReading(18.5, 20.0, 30.0, 15.0, 0.5, 0.0))
    model_stats: ModelStats = field(default_factory=lambda: ModelStats("Qwen2.5-Coder", 15430, 24.5, 0.92, 145))
    intent_status: IntentLayerStatus = field(default_factory=lambda: IntentLayerStatus("Layer 4 (LLM)", 850.5, "chat", 0.95, True))
    messages: list[ConversationMessage] = field(default_factory=list)


def build_ui(state: AILOState) -> Layout:
    """
    Builds the current snapshot of the UI layout using the application state.
    This acts as the dynamic callback for rich.live.Live.
    """
    layout = create_ailo_layout()

    layout["header"].update(build_header(state.sys_stats))
    layout["left_sidebar"].update(build_left_sidebar(state.sys_stats, state.aqi_reading))
    layout["right_sidebar"].update(build_right_sidebar(state.model_stats, state.intent_status))
    layout["conversation"].update(build_conversation_area(state.messages))

    return layout


class AILOTUIApplication:
    """
    The main asynchronous terminal application class.
    """
    def __init__(self):
        self.state = AILOState()
        self.state.messages.append(ConversationMessage("ailo", "AILO System Initialized. Awaiting input...", 0.0))
        self.console = Console(theme=AILO_THEME)
        self.session = PromptSession()
        self._running = True

    async def _async_worker(self):
        """
        Background worker that periodically updates system state and triggers UI refreshes.
        This proves that background work does not block the input prompt.
        """
        while self._running:
            await asyncio.sleep(5)

            # Oscillate system stats to simulate activity
            self.state.sys_stats.cpu_percent = random.uniform(10.0, 95.0)
            self.state.sys_stats.mem_percent = random.uniform(40.0, 80.0)
            self.state.sys_stats.uptime_seconds += 5

            # Occasionally inject a system message
            if random.random() > 0.7:
                self.state.messages.append(ConversationMessage("ailo", "System Check: All edge nodes nominal.", 0.0))
                # Keep conversation area tidy for the mock demo
                if len(self.state.messages) > 10:
                    self.state.messages = self.state.messages[-10:]

    async def run(self):
        """
        Main execution loop orchestrating Live UI and Prompt Toolkit input.
        """
        worker_task = asyncio.create_task(self._async_worker())

        # rich.live.Live automatically redraws based on the get_renderable callback
        with Live(get_renderable=lambda: build_ui(self.state), console=self.console, refresh_per_second=4, screen=True):
            # patch_stdout ensures print/Live output doesn't corrupt the prompt_toolkit line
            with patch_stdout():
                while self._running:
                    try:
                        # Non-blocking async prompt input
                        user_input = await self.session.prompt_async(HTML("<b><skyblue>AILO></skyblue></b> "))
                        user_input = user_input.strip()

                        if not user_input:
                            continue

                        if user_input.lower() in ('/quit', 'exit'):
                            self._running = False
                            break

                        self.state.messages.append(ConversationMessage("user", user_input, 0.0))

                    except (EOFError, KeyboardInterrupt):
                        self._running = False
                        break

        # Ensure worker is cancelled on exit
        worker_task.cancel()
        try:
            await worker_task
        except asyncio.CancelledError:
            pass

if __name__ == "__main__":
    app = AILOTUIApplication()
    asyncio.run(app.run())
