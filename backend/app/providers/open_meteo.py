"""Open-Meteo Meteorological Provider Implementation

Interacts with the Open-Meteo REST API for live weather, forecasts, and geocoding.
Translates WMO weather codes into English, Hindi, and Marathi.
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
    InvalidParameterError,
)
from backend.app.utils.logger import logger

# WMO Weather Interpretation Codes translated to English, Hindi, and Marathi
WMO_DESCRIPTIONS: Dict[int, Dict[str, str]] = {
    0: {"en": "Clear sky", "hi": "साफ़ आसमान", "mr": "निरभ्र आकाश"},
    1: {"en": "Mainly clear", "hi": "मुख्य रूप से साफ़", "mr": "मुख्यतः निरभ्र"},
    2: {"en": "Partly cloudy", "hi": "आंशिक रूप से बादल", "mr": "अंशतः ढगाळ"},
    3: {"en": "Overcast", "hi": "घने बादल", "mr": "पूर्ण ढगाळ"},
    45: {"en": "Foggy", "hi": "कोहरा", "mr": "धुके"},
    48: {"en": "Depositing rime fog", "hi": "सघन कोहरा", "mr": "दाट धुके"},
    51: {"en": "Light drizzle", "hi": "हल्की बूंदाबांदी", "mr": "हलकी रिमझिम"},
    53: {"en": "Moderate drizzle", "hi": "मध्यम बूंदाबांदी", "mr": "मध्यम रिमझिम"},
    55: {"en": "Dense drizzle", "hi": "घनी बूंदाबांदी", "mr": "जोरदार रिमझिम"},
    61: {"en": "Slight rain", "hi": "हल्की बारिश", "mr": "हलका पाऊस"},
    63: {"en": "Moderate rain", "hi": "मध्यम बारिश", "mr": "मध्यम पाऊस"},
    65: {"en": "Heavy rain", "hi": "भारी बारिश", "mr": "मुसळधार पाऊस"},
    71: {"en": "Slight snow fall", "hi": "हल्की बर्फबारी", "mr": "हलकी हिमवृष्टी"},
    73: {"en": "Moderate snow fall", "hi": "मध्यम बर्फबारी", "mr": "मध्यम हिमवृष्टी"},
    75: {"en": "Heavy snow fall", "hi": "भारी बर्फबारी", "mr": "जोरदार हिमवृष्टी"},
    80: {"en": "Slight rain showers", "hi": "हल्की बौछारें", "mr": "पावसाच्या हलक्या सरी"},
    81: {"en": "Moderate rain showers", "hi": "मध्यम बौछारें", "mr": "पावसाच्या मध्यम सरी"},
    82: {"en": "Violent rain showers", "hi": "भीषण बौछारें", "mr": "पावसाच्या मुसळधार सरी"},
    95: {"en": "Thunderstorm", "hi": "गरज के साथ तूफान", "mr": "वादळी पाऊस"},
    96: {"en": "Thunderstorm with slight hail", "hi": "ओलावृष्टि के साथ तूफान", "mr": "हलक्या गारपिटीसह वादळ"},
    99: {"en": "Thunderstorm with heavy hail", "hi": "भारी ओलावृष्टि के साथ तूफान", "mr": "मोठ्या गारपिटीसह वादळ"},
}


class OpenMeteoProvider(WeatherProvider):
    """Adapter for Open-Meteo weather services."""

    def __init__(self, client: Optional[httpx.AsyncClient] = None):
        self.base_url = settings.WEATHER_API_BASE_URL.rstrip("/")
        self.geocoding_url = settings.WEATHER_GEOCODING_URL.rstrip("/")
        self.timeout = settings.HTTP_TIMEOUT_SECONDS
        self._external_client = client

    @property
    def name(self) -> str:
        return "open-meteo"

    def _get_description(self, code: int, lang: str = "en") -> str:
        descriptions = WMO_DESCRIPTIONS.get(code, {"en": "Variable conditions", "hi": "अनियमित मौसम", "mr": "बदलते हवामान"})
        return descriptions.get(lang, descriptions.get("en", "Unknown"))

    async def _request(self, url: str, params: dict) -> dict:
        """Execute async HTTP GET request with robust error parsing."""
        try:
            if self._external_client:
                response = await self._external_client.get(url, params=params, timeout=self.timeout)
            else:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.get(url, params=params)

            if response.status_code == 429:
                logger.warning("Open-Meteo rate limit encountered")
                raise RateLimitExceededError("Open-Meteo API rate limit reached. Please retry shortly.")

            if response.status_code == 400:
                logger.warning(f"Open-Meteo 400 bad request: {response.text}")
                raise InvalidParameterError(f"Invalid weather query parameters: {response.text}")

            response.raise_for_status()
            data = response.json()
            if "error" in data and data["error"]:
                raise WeatherProviderError(message=data.get("reason", "Open-Meteo provider error"))
            return data

        except httpx.TimeoutException:
            logger.error(f"Timeout connecting to Open-Meteo at {url}")
            raise WeatherProviderError("Weather provider request timed out. Please try again.")
        except httpx.ConnectError:
            logger.error(f"Network error connecting to Open-Meteo at {url}")
            raise WeatherProviderError("Network connection to meteorological service failed.")
        except (RateLimitExceededError, InvalidParameterError, WeatherProviderError):
            raise
        except Exception as e:
            logger.error(f"Unexpected error in Open-Meteo request: {str(e)}")
            raise WeatherProviderError(f"Unexpected provider error: {str(e)}")

    async def get_current_weather(
        self, latitude: float, longitude: float, language: str = "en"
    ) -> CurrentWeatherData:
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,surface_pressure,wind_speed_10m,wind_direction_10m",
            "timezone": "auto",
        }
        url = f"{self.base_url}/forecast"
        raw = await self._request(url, params)

        current = raw.get("current")
        if not current:
            raise WeatherProviderError("No current observation data returned by weather service")

        weather_code = int(current.get("weather_code", 0))
        return CurrentWeatherData(
            latitude=raw.get("latitude", latitude),
            longitude=raw.get("longitude", longitude),
            observation_time=current.get("time", datetime.now(timezone.utc).isoformat()),
            temperature=float(current.get("temperature_2m", 0.0)),
            apparent_temperature=current.get("apparent_temperature"),
            relative_humidity=current.get("relative_humidity_2m"),
            precipitation=current.get("precipitation"),
            weather_code=weather_code,
            weather_description=self._get_description(weather_code, language),
            wind_speed=current.get("wind_speed_10m"),
            wind_direction=current.get("wind_direction_10m"),
            surface_pressure=current.get("surface_pressure"),
            uv_index=None,
            provider=self.name,
        )

    async def get_forecast(
        self, latitude: float, longitude: float, days: int = 7, language: str = "en"
    ) -> ForecastData:
        days = max(1, min(days, 14))
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "hourly": "temperature_2m,precipitation_probability,precipitation,weather_code,wind_speed_10m",
            "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max",
            "forecast_days": days,
            "timezone": "auto",
        }
        url = f"{self.base_url}/forecast"
        raw = await self._request(url, params)

        hourly_items: List[HourlyForecastItem] = []
        raw_hourly = raw.get("hourly", {})
        times = raw_hourly.get("time", [])
        temps = raw_hourly.get("temperature_2m", [])
        precip_probs = raw_hourly.get("precipitation_probability", [])
        precips = raw_hourly.get("precipitation", [])
        codes = raw_hourly.get("weather_code", [])
        winds = raw_hourly.get("wind_speed_10m", [])

        # Include up to 48 hours for granular breakdown
        max_hourly_entries = min(len(times), 48)
        for i in range(max_hourly_entries):
            code = int(codes[i]) if i < len(codes) else 0
            hourly_items.append(
                HourlyForecastItem(
                    time=times[i],
                    temperature=float(temps[i]) if i < len(temps) else 0.0,
                    precipitation_probability=precip_probs[i] if i < len(precip_probs) else None,
                    precipitation=precips[i] if i < len(precips) else None,
                    weather_code=code,
                    weather_description=self._get_description(code, language),
                    wind_speed=winds[i] if i < len(winds) else None,
                )
            )

        daily_items: List[DailyForecastItem] = []
        raw_daily = raw.get("daily", {})
        d_dates = raw_daily.get("time", [])
        d_codes = raw_daily.get("weather_code", [])
        d_max = raw_daily.get("temperature_2m_max", [])
        d_min = raw_daily.get("temperature_2m_min", [])
        d_precip = raw_daily.get("precipitation_sum", [])
        d_precip_prob = raw_daily.get("precipitation_probability_max", [])

        for i in range(len(d_dates)):
            code = int(d_codes[i]) if i < len(d_codes) else 0
            daily_items.append(
                DailyForecastItem(
                    date=d_dates[i],
                    temperature_max=float(d_max[i]) if i < len(d_max) else 0.0,
                    temperature_min=float(d_min[i]) if i < len(d_min) else 0.0,
                    precipitation_sum=d_precip[i] if i < len(d_precip) else None,
                    precipitation_probability_max=d_precip_prob[i] if i < len(d_precip_prob) else None,
                    weather_code=code,
                    weather_description=self._get_description(code, language),
                )
            )

        return ForecastData(
            latitude=raw.get("latitude", latitude),
            longitude=raw.get("longitude", longitude),
            timezone=raw.get("timezone", "UTC"),
            hourly=hourly_items,
            daily=daily_items,
            provider=self.name,
        )

    async def search_locations(
        self, query: str, count: int = 10, language: str = "en"
    ) -> List[LocationResult]:
        if not query or len(query.strip()) < 2:
            return []

        params = {
            "name": query.strip(),
            "count": min(count, 20),
            "language": language if language in ["en", "hi"] else "en",
            "format": "json",
        }
        url = f"{self.geocoding_url}/search"
        raw = await self._request(url, params)
        raw_results = raw.get("results", [])

        results: List[LocationResult] = []
        for item in raw_results:
            results.append(
                LocationResult(
                    id=item.get("id"),
                    name=item.get("name", "Unknown"),
                    latitude=float(item.get("latitude")),
                    longitude=float(item.get("longitude")),
                    elevation=item.get("elevation"),
                    country=item.get("country"),
                    admin1=item.get("admin1"),
                    country_code=item.get("country_code"),
                )
            )
        return results

    async def get_alerts(
        self, latitude: float, longitude: float, language: str = "en"
    ) -> List[WeatherAlert]:
        """Fetch severe meteorological events derived from active atmospheric indices."""
        # Check current & forecast conditions to identify extreme hazards
        forecast = await self.get_forecast(latitude, longitude, days=3, language=language)
        alerts: List[WeatherAlert] = []

        now_str = datetime.now(timezone.utc).isoformat()
        for idx, daily in enumerate(forecast.daily):
            # Heavy Rain Alert (WMO 65, 82)
            if daily.weather_code in [65, 82] or (daily.precipitation_sum and daily.precipitation_sum >= 50.0):
                instruction = (
                    "Avoid waterlogged routes and secure agricultural drainage channels."
                    if language == "en"
                    else "जलभराव वाले रास्तों से बचें और खेतों में जल निकासी की व्यवस्था करें।"
                    if language == "hi"
                    else "पाणी साचलेल्या रस्त्यांवर जाणे टाळा आणि शेतातील निचऱ्याची सोय करा."
                )
                alerts.append(
                    WeatherAlert(
                        id=f"alert-rain-{daily.date}",
                        title="Severe Heavy Rainfall Warning" if language == "en" else "भारी बारिश की चेतावनी" if language == "hi" else "मुसळधार पावसाचा इशारा",
                        severity="warning",
                        urgency="Expected",
                        description=f"Expected precipitation: {daily.precipitation_sum or 50}mm on {daily.date}",
                        instruction=instruction,
                        areas=[f"Lat: {latitude:.2f}, Lon: {longitude:.2f}"],
                        effective=now_str,
                        source="Meteorological Advisory Engine",
                    )
                )

            # Thunderstorm & Hail Hazard (WMO 95, 96, 99)
            if daily.weather_code in [95, 96, 99]:
                instruction = (
                    "Seek indoor shelter immediately. Avoid sheltering under solitary trees or metallic structures."
                    if language == "en"
                    else "तुरंत सुरक्षित स्थान पर जाएं। अकेले पेड़ों या धातु की संरचनाओं के नीचे खड़े न हों।"
                    if language == "hi"
                    else "त्वरित सुरक्षित ठिकाणी आश्रय घ्या. झाडांखाली किंवा धातूच्या खांबाजवळ उभे राहू नका."
                )
                alerts.append(
                    WeatherAlert(
                        id=f"alert-storm-{daily.date}",
                        title="Thunderstorm & Lightning Alert" if language == "en" else "आकाशीय बिजली व आंधी चेतावनी" if language == "hi" else "विजांच्या कडकडाटासह वादळाचा इशारा",
                        severity="warning",
                        urgency="Immediate" if idx == 0 else "Expected",
                        description=f"Atmospheric instability with convective storms forecasted on {daily.date}",
                        instruction=instruction,
                        areas=[f"Lat: {latitude:.2f}, Lon: {longitude:.2f}"],
                        effective=now_str,
                        source="Meteorological Advisory Engine",
                    )
                )

            # Extreme Heatwave Alert (Temperature max >= 42°C)
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
                        id=f"alert-heat-{daily.date}",
                        title="Extreme Heatwave Warning" if language == "en" else "भीषण लू (हीटवेव) की चेतावनी" if language == "hi" else "तीव्र उष्णतेच्या लाटेचा इशारा",
                        severity="warning",
                        urgency="Expected",
                        description=f"Maximum temperature expected to touch {daily.temperature_max}°C",
                        instruction=instruction,
                        areas=[f"Lat: {latitude:.2f}, Lon: {longitude:.2f}"],
                        effective=now_str,
                        source="Meteorological Advisory Engine",
                    )
                )

        return alerts
