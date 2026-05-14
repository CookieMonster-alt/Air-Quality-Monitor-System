# AILO Smart Node - TUI Design System

## 1. Design Philosophy
This document serves as the Single Source of Truth (SSOT) for the AILO CLI Terminal User Interface.
All UI components must adhere to the Command Line Interface Guidelines (CLIG).
- **Clarity over decoration:** Colors must have semantic meaning.
- **Consistency:** Use centralized tokens for all styling via `rich.theme`.

## 2. Color Palette (Semantic Tokens)
| Token Name | HEX Code  | Style / Weight | Usage |
| :--- | :--- | :--- | :--- |
| `brand` | `#00E5FF` | bold | Main logos, primary system names |
| `accent` | `#B388FF` | normal | Secondary highlights, prompts |
| `success` | `#00E676` | bold | Successful operations, safe statuses |
| `warning` | `#FFEA00` | bold | Alerts, moderate risks |
| `danger` | `#FF1744` | bold | Errors, critical system alerts |
| `info` | `#29B6F6` | italic | System messages, hints |
| `muted` | `#78909C` | dim | Borders, inactive text |

## 3. Domain Specific: EPA AQI Colors
- `aqi_good` (0-50): `#00E400`
- `aqi_moderate` (51-100): `#FFFF00`
- `aqi_sensitive` (101-150): `#FF7E00`
- `aqi_unhealthy` (151-200): `#FF0000`
- `aqi_very_unhealthy` (201-300): `#8F3F97`
- `aqi_hazardous` (301+): `bold #7E0023`
