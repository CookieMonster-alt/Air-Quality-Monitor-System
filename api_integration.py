import urllib.request
import urllib.parse
import json

WAQI_TOKEN = "demo"

def search_city_stations(keyword: str) -> list:
    encoded_keyword = urllib.parse.quote(keyword)
    url = f"https://api.waqi.info/search/?keyword={encoded_keyword}&token={WAQI_TOKEN}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            if data.get("status") == "ok":
                return data.get("data", [])
    except Exception as e:
        pass
    return []

def get_station_aqi(uid: int) -> dict:
    url = f"https://api.waqi.info/feed/@{uid}/?token={WAQI_TOKEN}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            if data.get("status") == "ok":
                return data.get("data", {})
    except Exception as e:
        pass
    return {}

def get_station_aqi_by_name(city_name: str) -> float:
    """Helper to just fetch current AQI float by city name for historical generation."""
    stations = search_city_stations(city_name)
    if not stations:
        return 0.0
    # grab the first one
    uid = stations[0].get('uid')
    data = get_station_aqi(uid)
    val = data.get('aqi')
    if val and isinstance(val, (int, float)):
        return float(val)
    # try converting string if it's digit
    if str(val).isdigit():
        return float(val)
    return 0.0
