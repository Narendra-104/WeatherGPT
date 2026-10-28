from typing import Optional
from pydantic import BaseModel, Field


class CurrentWeatherQuery(BaseModel):
    """Query parameters for current weather."""
    city: Optional[str] = Field(None, description="City name (e.g. Pune)")
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0, description="Latitude between -90 and 90")
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0, description="Longitude between -180 and 180")
    language: str = Field(default="en", description="Target language code: 'en', 'hi', or 'mr'")
    units: str = Field(default="metric", description="Unit system: metric or imperial")


class CurrentWeatherData(BaseModel):
    """Normalized current meteorological observation."""
    latitude: float
    longitude: float
    location_name: Optional[str] = None
    observation_time: str
    temperature: float = Field(..., description="Temperature in degrees Celsius")
    apparent_temperature: Optional[float] = Field(None, description="Feels like temperature in degrees Celsius")
    relative_humidity: Optional[float] = Field(None, description="Relative humidity percentage")
    precipitation: Optional[float] = Field(None, description="Current precipitation rate in mm")
    weather_code: int = Field(..., description="WMO weather interpretation code")
    weather_description: str = Field(..., description="Human-readable condition description")
    wind_speed: Optional[float] = Field(None, description="Wind speed in km/h")
    wind_direction: Optional[float] = Field(None, description="Wind direction in degrees")
    surface_pressure: Optional[float] = Field(None, description="Surface atmospheric pressure in hPa")
    uv_index: Optional[float] = Field(None, description="UV index rating")
    sunrise: Optional[str] = Field(None, description="Sunrise ISO timestamp or time string")
    sunset: Optional[str] = Field(None, description="Sunset ISO timestamp or time string")
    provider: str = Field(default="open-meteo", description="Meteorological provider source")
