"""
Layout skeleton for the AILO Full-Screen TUI.

This module constructs the 4-zone root layout grid used by the application,
designed to partition the terminal space into logical domains:
- Main conversation area and header.
- Left sidebar for system statistics and AQI readings.
- Right sidebar for model statistics and intent classification layers.
- A footer spanning the full width of the terminal bottom.
"""

from rich.layout import Layout
from rich.panel import Panel

def create_ailo_layout() -> Layout:
    """
    Constructs the root layout grid for the TUI.

    Returns:
        Layout: The root rich.layout.Layout instance populated with dummy Panels
                representing the target application zones.
    """
    # Root layout
    root = Layout(name="root")

    # 1. Split root horizontally into left, main, and right columns
    # We omit the footer here so prompt_toolkit can own the terminal's bottom line.
    root.split_row(
        Layout(name="left_sidebar", size=26),
        Layout(name="main_content", ratio=1),
        Layout(name="right_sidebar", size=28)
    )

    # 2. Split main_content vertically into header and conversation
    root["main_content"].split_column(
        Layout(name="header", size=3),
        Layout(name="conversation", ratio=1)
    )

    # 3. Split left_sidebar vertically into sys_stats and aqi_readings
    root["left_sidebar"].split_column(
        Layout(name="sys_stats", ratio=1),
        Layout(name="aqi_readings", ratio=1)
    )

    # 4. Split right_sidebar vertically into model_stats and intent_layer
    root["right_sidebar"].split_column(
        Layout(name="model_stats", ratio=1),
        Layout(name="intent_layer", ratio=1)
    )

    # Populate every leaf zone with a dummy Panel for visual testing
    root["header"].update(Panel("Header Area", title="Header"))
    root["conversation"].update(Panel("Conversation Area", title="Conversation"))

    root["sys_stats"].update(Panel("Sys Stats", title="System"))
    root["aqi_readings"].update(Panel("AQI Readings", title="AQI"))

    root["model_stats"].update(Panel("Model Stats", title="Model"))
    root["intent_layer"].update(Panel("Intent Layer", title="Intent"))

    return root
