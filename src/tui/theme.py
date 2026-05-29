"""
Theme definitions for the AILO Full-Screen TUI.

This module defines the architectural color palette for the terminal user interface,
encapsulating both application-level semantic tokens (e.g., success, danger) and
domain-specific EPA AQI color codes.
"""

from rich.theme import Theme

AILO_THEME = Theme({
    # Semantic Tokens
    "brand": "bold #00E5FF",
    "success": "bold #00E676",
    "warning": "bold #FFEA00",
    "danger": "bold #FF1744",
    "info": "#29B6F6",
    "muted": "dim #78909C",

    # EPA AQI Domain Colors
    "aqi_good": "#00E400",
    "aqi_moderate": "#FFFF00",
    "aqi_sensitive": "#FF7E00",
    "aqi_unhealthy": "#FF0000",
    "aqi_very_unhealthy": "#8F3F97",
    "aqi_hazardous": "#7E0023",
})
