"""
UI Components for the AILO Full-Screen TUI.

This module provides the core data models and UI generator functions to render the
various zones of the AILO terminal interface using the `rich` library. It enforces
strict layout constraints and styling rules from the design specification, optimized
for execution on Raspberry Pi 5 hardware.
"""

from dataclasses import dataclass
from typing import Optional, Tuple
from rich.text import Text
from rich.panel import Panel
from rich.layout import Layout
from rich.table import Table
from rich import box

from src.tui.theme import AILO_THEME

@dataclass
class SystemStats:
    cpu_percent: float
    mem_percent: float
    mem_used_gb: float
    temp_celsius: float
    uptime_seconds: int
    disk_percent: float


@dataclass
class AQIReading:
    pm25: float
    pm10: float
    o3: float
    no2: float
    co: float
    timestamp: float

    def get_aqi(self) -> Tuple[int, str]:
        """
        Calculates the AQI value using EPA piecewise linear mapping for PM2.5,
        and returns the corresponding (aqi_value, color_hex) tuple.
        """
        # EPA PM2.5 breakpoints (ug/m3) and corresponding AQI index
        breakpoints = [
            (0.0, 12.0, 0, 50, "#00E400"),         # Good
            (12.1, 35.4, 51, 100, "#FFFF00"),      # Moderate
            (35.5, 55.4, 101, 150, "#FF7E00"),     # Sensitive
            (55.5, 150.4, 151, 200, "#FF0000"),    # Unhealthy
            (150.5, 250.4, 201, 300, "#8F3F97"),   # Very Unhealthy
            (250.5, 500.4, 301, 500, "#7E0023")    # Hazardous
        ]

        # Truncate PM2.5 to 1 decimal place per EPA guidelines
        c = float(f"{self.pm25:.1f}")

        # Find the correct breakpoint range
        for bp in breakpoints:
            c_low, c_high, i_low, i_high, hex_color = bp
            if c_low <= c <= c_high:
                # Calculate AQI
                aqi = ((i_high - i_low) / (c_high - c_low)) * (c - c_low) + i_low
                return (int(round(aqi)), hex_color)

        # Fallback for values > 500.4
        c_low, c_high, i_low, i_high, hex_color = breakpoints[-1]
        aqi = ((i_high - i_low) / (c_high - c_low)) * (c - c_low) + i_low
        return (int(round(aqi)), hex_color)


@dataclass
class ModelStats:
    model_name: str
    tokens_generated: int
    tokens_per_second: float
    cache_hit_rate: float
    total_inferences: int


@dataclass
class IntentLayerStatus:
    layer_name: str
    latency_ms: float
    intent: str
    confidence: float
    is_fallback: bool


@dataclass
class ConversationMessage:
    role: str  # "user" | "ailo"
    content: str
    timestamp: float
    intent: Optional[str] = None
    persona: Optional[str] = None
    layer_used: Optional[str] = None
    confidence: Optional[float] = None

def _create_progress_bar(value: float, max_value: float = 100.0, width: int = 10) -> Text:
    """
    Creates a simple, lightweight progress bar using Unicode block characters.
    This is highly optimized for Raspberry Pi 5 to avoid rich.progress overhead.
    """
    # Ensure value is bounded between 0 and max_value
    value = max(0.0, min(value, max_value))

    # Calculate how many filled blocks we need
    fill_ratio = value / max_value
    filled_blocks = int(round(fill_ratio * width))
    empty_blocks = width - filled_blocks

    # Use standard unicode blocks
    bar_str = ("█" * filled_blocks) + ("░" * empty_blocks)

    # Simple color coding based on threshold
    color = "[success]"
    if fill_ratio > 0.85:
        color = "[danger]"
    elif fill_ratio > 0.70:
        color = "[warning]"

    return Text.from_markup(f"{color}{bar_str}[/]")

def build_header(stats: SystemStats) -> Panel:
    """Builds the 3-line high header panel with the brand logo and uptime."""
    hours = stats.uptime_seconds // 3600
    minutes = (stats.uptime_seconds % 3600) // 60
    uptime_str = f"{hours}h {minutes}m"

    header_text = Text.assemble(
        ("[brand bold]AILO[/] Smart Node", ""),
        (f" | Uptime: {uptime_str}", "info")
    )

    return Panel(
        header_text,
        style="brand",
        border_style="brand",
        padding=(0, 2)
    )


def build_left_sidebar(sys_stats: SystemStats, aqi: AQIReading) -> Layout:
    """
    Constructs the left sidebar layout containing the System Stats and AQI tables.
    Tables are rendered without borders inside wrapping panels.
    """
    layout = Layout()
    layout.split_column(
        Layout(name="sys_panel", ratio=1),
        Layout(name="aqi_panel", ratio=1)
    )

    # --- System Stats Table ---
    sys_table = Table(box=None, padding=(0, 1), show_header=False, expand=True)
    sys_table.add_column("Metric", style="info")
    sys_table.add_column("Value")

    sys_table.add_row(
        "CPU",
        Text.assemble((f"{sys_stats.cpu_percent:04.1f}% ", "info"), _create_progress_bar(sys_stats.cpu_percent))
    )
    sys_table.add_row(
        "RAM",
        Text.assemble((f"{sys_stats.mem_percent:04.1f}% ", "info"), _create_progress_bar(sys_stats.mem_percent))
    )
    sys_table.add_row("Temp", f"[warning]{sys_stats.temp_celsius:.1f}°C[/]")
    sys_table.add_row("Disk", Text.assemble((f"{sys_stats.disk_percent:04.1f}% ", "info"), _create_progress_bar(sys_stats.disk_percent)))

    sys_panel = Panel(sys_table, title="[brand]System[/]", border_style="muted")
    layout["sys_panel"].update(sys_panel)

    # --- AQI Readings Table ---
    aqi_val, aqi_hex = aqi.get_aqi()

    aqi_table = Table(box=None, padding=(0, 1), show_header=False, expand=True)
    aqi_table.add_column("Pollutant", style="info")
    aqi_table.add_column("Value")

    # The main AQI index row uses the EPA color mapping
    aqi_table.add_row("Index", f"[{aqi_hex} bold]{aqi_val}[/]")
    aqi_table.add_row("PM2.5", f"{aqi.pm25:.1f} µg/m³")
    aqi_table.add_row("PM10", f"{aqi.pm10:.1f} µg/m³")
    aqi_table.add_row("O3", f"{aqi.o3:.1f} ppb")
    aqi_table.add_row("NO2", f"{aqi.no2:.1f} ppb")
    aqi_table.add_row("CO", f"{aqi.co:.1f} ppm")

    aqi_panel = Panel(aqi_table, title="[brand]AQI[/]", border_style="muted")
    layout["aqi_panel"].update(aqi_panel)

    return layout


def build_right_sidebar(model_stats: ModelStats, intent: IntentLayerStatus) -> Layout:
    """
    Constructs the right sidebar layout containing Model Stats and Intent Status tables.
    """
    layout = Layout()
    layout.split_column(
        Layout(name="model_panel", ratio=1),
        Layout(name="intent_panel", ratio=1)
    )

    # --- Model Stats Table ---
    model_table = Table(box=None, padding=(0, 1), show_header=False, expand=True)
    model_table.add_column("Metric", style="info")
    model_table.add_column("Value")

    model_table.add_row("Model", f"[brand]{model_stats.model_name}[/]")
    model_table.add_row("Tokens", f"{model_stats.tokens_generated}")
    model_table.add_row("T/s", f"{model_stats.tokens_per_second:.1f}")
    model_table.add_row("Hit Rate", f"[success]{model_stats.cache_hit_rate*100:.1f}%[/]")
    model_table.add_row("Inferences", f"{model_stats.total_inferences}")

    model_panel = Panel(model_table, title="[brand]Model[/]", border_style="muted")
    layout["model_panel"].update(model_panel)

    # --- Intent Layer Table ---
    intent_table = Table(box=None, padding=(0, 1), show_header=False, expand=True)
    intent_table.add_column("Property", style="info")
    intent_table.add_column("Value")

    intent_table.add_row("Layer", f"[brand]{intent.layer_name}[/]")
    intent_table.add_row("Latency", f"{intent.latency_ms:.1f}ms")
    intent_table.add_row("Intent", f"[success]{intent.intent}[/]")

    conf_color = "[success]" if intent.confidence > 0.8 else "[warning]"
    intent_table.add_row("Confidence", f"{conf_color}{intent.confidence*100:.1f}%[/]")

    fb_color = "[danger]YES[/]" if intent.is_fallback else "[success]NO[/]"
    intent_table.add_row("Fallback", fb_color)

    intent_panel = Panel(intent_table, title="[brand]Intent[/]", border_style="muted")
    layout["intent_panel"].update(intent_panel)

    return layout


def build_conversation_area(messages: list[ConversationMessage]) -> Panel:
    """
    Renders the main conversation area containing a list of messages.
    """
    chat_layout = Layout()

    # We will build a single column of messages. In a real system, you might
    # want to handle scrolling, but for this component, we just render them.
    # We use a Table here to nicely stack messages.

    msg_table = Table(box=None, padding=(0, 1, 1, 1), show_header=False, expand=True)
    msg_table.add_column("Message", ratio=1)

    for msg in messages:
        if msg.role == "user":
            header = Text("You", style="success bold")
            content = Text(msg.content, style="default")
        else:
            header = Text("AILO", style="brand bold")
            content = Text(msg.content, style="default")

        # Combine header and content
        full_msg = Text.assemble(header, "\n", content)
        msg_table.add_row(full_msg)

    return Panel(msg_table, title="[brand]Terminal[/]", border_style="brand")
