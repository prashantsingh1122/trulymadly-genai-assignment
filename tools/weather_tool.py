import time
import requests
from typing import Dict, Any


def get_weather(city: str, retries: int = 3, backoff: float = 1.0) -> Dict[str, Any]:
    geo_url = "https://geocoding-api.open-meteo.com/v1/search"

    last_exc = None
    for attempt in range(1, retries + 1):
        try:
            geo_resp = requests.get(
                geo_url,
                params={"name": city, "count": 1},
                timeout=10
            )
            geo_resp.raise_for_status()

            geo_data = geo_resp.json()

            if "results" not in geo_data or not geo_data["results"]:
                return {"error": "City not found"}

            lat = geo_data["results"][0]["latitude"]
            lon = geo_data["results"][0]["longitude"]

            weather_url = "https://api.open-meteo.com/v1/forecast"
            weather_resp = requests.get(
                weather_url,
                params={
                    "latitude": lat,
                    "longitude": lon,
                    "current_weather": True
                },
                timeout=10
            )
            weather_resp.raise_for_status()

            w = weather_resp.json().get("current_weather", {})

            return {
                "temperature": w.get("temperature"),
                "windspeed": w.get("windspeed"),
                "time": w.get("time")
            }

        except Exception as e:
            last_exc = e
            if attempt < retries:
                time.sleep(backoff * attempt)
                continue
            else:
                raise

    raise last_exc
