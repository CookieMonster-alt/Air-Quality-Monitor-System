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
