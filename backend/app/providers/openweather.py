"""OpenWeather Meteorological Provider Implementation

Interacts with the OpenWeather API (data/2.5 and geo/1.0) for live weather observations,
5-day forecasts, and geographical search.
Translates condition IDs into English, Hindi, and Marathi.
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional
import httpx

from backend.app.config import settings
from backend.app.providers.base import WeatherProvider
from backend.app.schemas.weather import CurrentWeatherData
from backend.app.schemas.forecast import ForecastData, HourlyForecastItem, DailyForecastItem
from backend.app.schemas.location import LocationResult
from backend.app.schemas.alert import WeatherAlert
from backend.app.utils.exceptions import (
    WeatherProviderError,
    RateLimitExceededError,
    LocationNotFoundError,
    InvalidParameterError,
)
from backend.app.utils.logger import logger

# Condition code translation dictionary for OpenWeather ID ranges
OPENWEATHER_CONDITION_TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "thunderstorm": {"en": "Thunderstorm", "hi": "गरज के साथ तूफान", "mr": "वादळी पाऊस"},
    "drizzle": {"en": "Drizzle", "hi": "बूंदाबांदी", "mr": "रिमझिम पाऊस"},
    "rain": {"en": "Rain", "hi": "बारिश", "mr": "पाऊस"},
    "heavy_rain": {"en": "Heavy Rain", "hi": "भारी बारिश", "mr": "मुसळधार पाऊस"},
    "snow": {"en": "Snow", "hi": "बर्फबारी", "mr": "हिमवृष्टी"},
    "atmosphere": {"en": "Foggy / Mist", "hi": "कोहरा / धुंध", "mr": "धुके"},
    "clear": {"en": "Clear sky", "hi": "साफ़ आसमान", "mr": "निरभ्र आकाश"},
    "few_clouds": {"en": "Few clouds", "hi": "हल्के बादल", "mr": "हलके ढग"},
    "scattered_clouds": {"en": "Scattered clouds", "hi": "आंशिक बादल", "mr": "अंशतः ढगाळ"},
    "broken_clouds": {"en": "Broken clouds", "hi": "बादलों से घिरा", "mr": "ढगाळ"},
    "overcast": {"en": "Overcast clouds", "hi": "घने बादल", "mr": "पूर्ण ढगाळ"},
}


class OpenWeatherProvider(WeatherProvider):
    """Adapter for OpenWeather API services."""

    def __init__(self, client: Optional[httpx.AsyncClient] = None):
        self.base_url = settings.OPENWEATHER_BASE_URL.rstrip("/")
        self.geocoding_url = settings.OPENWEATHER_GEOCODING_URL.rstrip("/")
        self.timeout = settings.HTTP_TIMEOUT_SECONDS
        self._external_client = client

    @property
    def name(self) -> str:
        return "openweather"

    def _check_api_key(self) -> str:
        api_key = settings.WEATHER_API_KEY.strip()
        if not api_key:
            logger.error("OpenWeather provider invoked but WEATHER_API_KEY is not configured")
            raise WeatherProviderError(
                "OpenWeather API key is not configured. Please add WEATHER_API_KEY to backend/.env",
                status_code=500,
            )
        return api_key

    def _translate_condition(self, weather_id: int, original_description: str, lang: str = "en") -> str:
        """Map OpenWeather condition ID to trilingual description."""
        key = "clear"
        if 200 <= weather_id < 300:
            key = "thunderstorm"
        elif 300 <= weather_id < 400:
            key = "drizzle"
        elif 500 <= weather_id < 600:
            key = "heavy_rain" if weather_id in [502, 503, 504, 522] else "rain"
        elif 600 <= weather_id < 700:
            key = "snow"
        elif 700 <= weather_id < 800:
            key = "atmosphere"
        elif weather_id == 800:
            key = "clear"
        elif weather_id == 801:
            key = "few_clouds"
        elif weather_id == 802:
            key = "scattered_clouds"
        elif weather_id in [803, 804]:
            key = "overcast" if weather_id == 804 else "broken_clouds"

        translations = OPENWEATHER_CONDITION_TRANSLATIONS.get(key, {})
        if lang == "mr":
            return translations.get("mr", original_description)
        elif lang == "hi":
            return translations.get("hi", original_description)
        return original_description.capitalize() if original_description else translations.get("en", "Clear")

    async def _request(self, url: str, params: dict) -> dict:
        """Execute async HTTP GET request to OpenWeather with error parsing."""
        try:
            if self._external_client:
                response = await self._external_client.get(url, params=params, timeout=self.timeout)
            else:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.get(url, params=params)

            if response.status_code == 401:
                logger.error("OpenWeather responded with 401 Unauthorized (Invalid API Key)")
                raise WeatherProviderError(
                    "Invalid OpenWeather API key. Please verify your WEATHER_API_KEY in backend/.env",
                    status_code=401,
                )

            if response.status_code == 404:
                logger.warning(f"OpenWeather 404 Not Found: {url}")
                raise LocationNotFoundError("Location not found on OpenWeather.")

            if response.status_code == 429:
                logger.warning("OpenWeather rate limit encountered")
                raise RateLimitExceededError("OpenWeather API rate limit reached. Please retry shortly.")

            if response.status_code == 400:
                logger.warning(f"OpenWeather 400 bad request: {response.text}")
                raise InvalidParameterError(f"Invalid weather query parameters: {response.text}")

            response.raise_for_status()
            data = response.json()
            return data

        except httpx.TimeoutException:
            logger.error(f"Timeout connecting to OpenWeather at {url}")
            raise WeatherProviderError("OpenWeather request timed out. Please try again.")
        except httpx.ConnectError:
            logger.error(f"Network error connecting to OpenWeather at {url}")
            raise WeatherProviderError("Network connection to OpenWeather failed.")
        except (RateLimitExceededError, LocationNotFoundError, InvalidParameterError, WeatherProviderError):
            raise
        except Exception as e:
            logger.error(f"Unexpected error in OpenWeather request: {str(e)}")
            raise WeatherProviderError(f"Unexpected provider error: {str(e)}")

    async def get_current_weather(
        self, latitude: float, longitude: float, language: str = "en"
    ) -> CurrentWeatherData:
        api_key = self._check_api_key()
        ow_lang = "hi" if language == "hi" else "en"

        params = {
            "lat": latitude,
            "lon": longitude,
            "appid": api_key,
            "units": "metric",
            "lang": ow_lang,
        }
        url = f"{self.base_url}/data/2.5/weather"
        raw = await self._request(url, params)

        main = raw.get("main")
        if not main:
            raise WeatherProviderError("Malformed response received from OpenWeather (missing 'main' block)")

        weather_list = raw.get("weather", [])
        weather_info = weather_list[0] if weather_list else {}
        weather_id = int(weather_info.get("id", 800))
        raw_desc = weather_info.get("description", "Clear sky")

        # Wind speed in OpenWeather metric units is meters/sec -> convert to km/h (1 m/s = 3.6 km/h)
        wind_data = raw.get("wind", {})
        wind_speed_ms = wind_data.get("speed")
        wind_speed_kmh = round(wind_speed_ms * 3.6, 1) if wind_speed_ms is not None else None

        # Precipitation: check rain.1h or rain.3h
        rain_data = raw.get("rain", {})
        precip = rain_data.get("1h", rain_data.get("3h", 0.0))

        # Observation timestamp
        dt_val = raw.get("dt")
        obs_time = datetime.fromtimestamp(dt_val, timezone.utc).isoformat() if dt_val else datetime.now(timezone.utc).isoformat()

        return CurrentWeatherData(
            latitude=raw.get("coord", {}).get("lat", latitude),
            longitude=raw.get("coord", {}).get("lon", longitude),
            location_name=raw.get("name"),
            observation_time=obs_time,
            temperature=float(main.get("temp", 0.0)),
            apparent_temperature=main.get("feels_like"),
            relative_humidity=main.get("humidity"),
            precipitation=float(precip) if precip is not None else 0.0,
            weather_code=weather_id,
            weather_description=self._translate_condition(weather_id, raw_desc, language),
            wind_speed=wind_speed_kmh,
            wind_direction=wind_data.get("deg"),
            surface_pressure=main.get("pressure"),
            uv_index=None,
            provider=self.name,
        )

    async def get_forecast(
        self, latitude: float, longitude: float, days: int = 7, language: str = "en"
    ) -> ForecastData:
        # OpenWeather standard 2.5 API offers 5 days / 3-hour forecasts
        if days > 5:
            raise InvalidParameterError(
                f"OpenWeather 2.5 forecast supports up to 5 days (requested: {days} days). "
                f"For extended 7-14 day forecasts, configure WEATHER_PROVIDER=open_meteo."
            )

        api_key = self._check_api_key()
        ow_lang = "hi" if language == "hi" else "en"

        params = {
            "lat": latitude,
            "lon": longitude,
            "appid": api_key,
            "units": "metric",
            "lang": ow_lang,
        }
        url = f"{self.base_url}/data/2.5/forecast"
        raw = await self._request(url, params)

        raw_list = raw.get("list")
        if not raw_list:
            raise WeatherProviderError("Malformed forecast response received from OpenWeather (missing 'list')")

        hourly_items: List[HourlyForecastItem] = []
        daily_groups: Dict[str, List[dict]] = {}

        for item in raw_list:
            dt_txt = item.get("dt_txt", "")
            time_str = dt_txt.replace(" ", "T") if dt_txt else ""
            date_str = dt_txt.split(" ")[0] if " " in dt_txt else ""

            w_list = item.get("weather", [])
            w_info = w_list[0] if w_list else {}
            w_id = int(w_info.get("id", 800))
            raw_desc = w_info.get("description", "Clear sky")

            item_main = item.get("main", {})
            temp = float(item_main.get("temp", 0.0))

            wind_val = item.get("wind", {}).get("speed")
            wind_kmh = round(wind_val * 3.6, 1) if wind_val is not None else None

            pop = item.get("pop", 0.0)
            precip_prob = round(pop * 100, 1) if pop is not None else None

            rain_3h = item.get("rain", {}).get("3h", 0.0)

            hourly_items.append(
                HourlyForecastItem(
                    time=time_str,
                    temperature=temp,
                    precipitation_probability=precip_prob,
                    precipitation=float(rain_3h) if rain_3h is not None else 0.0,
                    weather_code=w_id,
                    weather_description=self._translate_condition(w_id, raw_desc, language),
                    wind_speed=wind_kmh,
                )
            )

            if date_str:
                daily_groups.setdefault(date_str, []).append({
                    "temp": temp,
                    "w_id": w_id,
                    "desc": raw_desc,
                    "rain": rain_3h or 0.0,
                    "pop": precip_prob or 0.0,
                })

        # Aggregate daily statistics
        daily_items: List[DailyForecastItem] = []
        for d_date, records in list(daily_groups.items())[:days]:
            temps = [r["temp"] for r in records]
            rains = [r["rain"] for r in records]
            pops = [r["pop"] for r in records]
            dominant_record = records[len(records) // 2] if records else {}
            w_id = dominant_record.get("w_id", 800)
            raw_desc = dominant_record.get("desc", "Clear sky")

            daily_items.append(
                DailyForecastItem(
                    date=d_date,
                    temperature_max=round(max(temps), 1) if temps else 0.0,
                    temperature_min=round(min(temps), 1) if temps else 0.0,
                    precipitation_sum=round(sum(rains), 1),
                    precipitation_probability_max=round(max(pops), 1) if pops else None,
                    weather_code=w_id,
                    weather_description=self._translate_condition(w_id, raw_desc, language),
                )
            )

        city_data = raw.get("city", {})
        return ForecastData(
            latitude=city_data.get("coord", {}).get("lat", latitude),
            longitude=city_data.get("coord", {}).get("lon", longitude),
            timezone=str(city_data.get("timezone", "UTC")),
            hourly=hourly_items,
            daily=daily_items,
            provider=self.name,
        )

    async def search_locations(
        self, query: str, count: int = 10, language: str = "en"
    ) -> List[LocationResult]:
        if not query or len(query.strip()) < 2:
            return []

        api_key = self._check_api_key()
        params = {
            "q": query.strip(),
            "limit": min(count, 20),
            "appid": api_key,
        }
        url = f"{self.geocoding_url}/direct"
        raw_list = await self._request(url, params)
        if not isinstance(raw_list, list):
            return []

        results: List[LocationResult] = []
        for item in raw_list:
            local_names = item.get("local_names", {})
            name = item.get("name", "Unknown")
            if language == "hi" and local_names.get("hi"):
                name = local_names["hi"]
            elif language == "mr" and (local_names.get("mr") or local_names.get("hi")):
                name = local_names.get("mr") or local_names.get("hi")

            results.append(
                LocationResult(
                    id=None,
                    name=name,
                    latitude=float(item.get("lat")),
                    longitude=float(item.get("lon")),
                    elevation=None,
                    country=item.get("country"),
                    admin1=item.get("state"),
                    country_code=item.get("country"),
                )
            )
        return results

    async def get_alerts(
        self, latitude: float, longitude: float, language: str = "en"
    ) -> List[WeatherAlert]:
        """Evaluate real forecasted conditions for severe hazards without fabricating false warnings."""
        forecast = await self.get_forecast(latitude, longitude, days=3, language=language)
        alerts: List[WeatherAlert] = []
        now_str = datetime.now(timezone.utc).isoformat()

        for idx, daily in enumerate(forecast.daily):
            # Heavy Rain Warning (precipitation sum >= 50 mm)
            if daily.precipitation_sum and daily.precipitation_sum >= 50.0:
                instruction = (
                    "Avoid waterlogged routes and secure agricultural drainage channels."
                    if language == "en"
                    else "जलभराव वाले रास्तों से बचें और खेतों में जल निकासी की व्यवस्था करें।"
                    if language == "hi"
                    else "पाणी साचलेल्या रस्त्यांवर जाणे टाळा आणि शेतातील निचऱ्याची सोय करा."
                )
                alerts.append(
                    WeatherAlert(
                        id=f"ow-alert-rain-{daily.date}",
                        title="Severe Heavy Rainfall Warning" if language == "en" else "भारी बारिश की चेतावनी" if language == "hi" else "मुसळधार पावसाचा इशारा",
                        severity="warning",
                        urgency="Expected",
                        description=f"Expected precipitation: {daily.precipitation_sum}mm on {daily.date}",
                        instruction=instruction,
                        areas=[f"Lat: {latitude:.2f}, Lon: {longitude:.2f}"],
                        effective=now_str,
                        source="OpenWeather Meteorological Feed",
                    )
                )

            # Thunderstorm Warning (OpenWeather 2xx codes)
            if 200 <= daily.weather_code < 300:
                instruction = (
                    "Seek indoor shelter immediately. Avoid sheltering under solitary trees."
                    if language == "en"
                    else "तुरंत सुरक्षित स्थान पर जाएं। अकेले पेड़ों के नीचे खड़े न हों।"
                    if language == "hi"
                    else "त्वरित सुरक्षित ठिकाणी आश्रय घ्या. झाडांखाली उभे राहू नका."
                )
                alerts.append(
                    WeatherAlert(
                        id=f"ow-alert-storm-{daily.date}",
                        title="Thunderstorm & Lightning Alert" if language == "en" else "आकाशीय बिजली व आंधी चेतावनी" if language == "hi" else "विजांच्या कडकडाटासह वादळाचा इशारा",
                        severity="warning",
                        urgency="Immediate" if idx == 0 else "Expected",
                        description=f"Thunderstorm activity forecasted on {daily.date}",
                        instruction=instruction,
                        areas=[f"Lat: {latitude:.2f}, Lon: {longitude:.2f}"],
                        effective=now_str,
                        source="OpenWeather Meteorological Feed",
                    )
                )

            # Extreme Heatwave Warning (>= 42°C)
            if daily.temperature_max >= 42.0:
                instruction = (
                    "Stay hydrated and avoid direct sun exposure between 12:00 PM and 4:00 PM."
                    if language == "en"
                    else "पर्याप्त पानी पिएं और दोपहर 12 से 4 बजे के बीच सीधी धूप से बचें।"
                    if language == "hi"
                    else "भरपूर पाणी प्या आणि दुपारी १२ ते ४ दरम्यान थेट उन्हात जाणे टाळा."
                )
                alerts.append(
                    WeatherAlert(
                        id=f"ow-alert-heat-{daily.date}",
                        title="Extreme Heatwave Warning" if language == "en" else "भीषण लू (हीटवेव) की चेतावनी" if language == "hi" else "तीव्र उष्णतेच्या लाटेचा इशारा",
                        severity="warning",
                        urgency="Expected",
                        description=f"Maximum temperature expected to touch {daily.temperature_max}°C",
                        instruction=instruction,
                        areas=[f"Lat: {latitude:.2f}, Lon: {longitude:.2f}"],
                        effective=now_str,
                        source="OpenWeather Meteorological Feed",
                    )
                )

        return alerts
