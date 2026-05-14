import datetime
# pyrefly: ignore [missing-import]
from data_manager import DatabaseManager

# Strict output constants
STATUS_NORMAL = 'STATUS_NORMAL: No automated action required.'
STATUS_ALERT = 'STATUS_ALERT: Triggering Environmental Protocol.'

def evaluate_prediction(aqi: float) -> str:
    """Strict 1 Input, 2 Output logic."""
    if aqi <= 100.0:
        return STATUS_NORMAL
    else:
        return STATUS_ALERT

def get_recent_history(city_name: str) -> list:
    db = DatabaseManager()
    all_records = db.get_all_records()
    city_records = [r for r in all_records if r.city_name.lower() == city_name.lower()]
    # Sort by timestamp, oldest to newest
    city_records.sort(key=lambda x: x.timestamp)
    return city_records

try:
    # Try importing Transformers for potential complex TS modeling
    # pyrefly: ignore [missing-import]
    import transformers
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

def predict_next_aqi(city_name: str) -> float:
    """
    Predicts the next AQI. If Transformers is installed, it attempts AI modeling.
    If not, falls back to a Simple Moving Average (SMA).
    """
    city_records = get_recent_history(city_name)
    if not city_records:
        return 0.0 # No history, return default 0.0

    recent_values = [r.aqi_value for r in city_records[-5:]] # take last 5 records

    if TRANSFORMERS_AVAILABLE:
        # Placeholder for HF implementation when package is installed.
        # e.g., using TimeSeriesTransformer or similar architectures.
        # For the epic task, we will fall through to SMA since model weights are not loaded.
        pass

    # Fallback / SMA Logic
    sma_prediction = sum(recent_values) / len(recent_values)
    return round(sma_prediction, 1)
