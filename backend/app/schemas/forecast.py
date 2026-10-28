from typing import List, Optional
from pydantic import BaseModel, Field


class HourlyForecastItem(BaseModel):
    """Hourly forecast slice."""
    time: str
    temperature: float = Field(..., description="Hourly temperature in °C")
    precipitation_probability: Optional[float] = Field(None, description="Precipitation probability (0-100%)")
    precipitation: Optional[float] = Field(None, description="Precipitation amount in mm")
    weather_code: int = Field(..., description="WMO weather code")
    weather_description: str = Field(..., description="Condition text in requested language")
    wind_speed: Optional[float] = Field(None, description="Wind speed in km/h")


class DailyForecastItem(BaseModel):
    """Daily summary forecast item."""
    date: str
    temperature_max: float = Field(..., description="Maximum temperature in °C")
    temperature_min: float = Field(..., description="Minimum temperature in °C")
    precipitation_sum: Optional[float] = Field(None, description="Total expected precipitation in mm")
    precipitation_probability_max: Optional[float] = Field(None, description="Maximum precipitation chance %")
    weather_code: int = Field(..., description="WMO weather code")
    weather_description: str = Field(..., description="Condition text in requested language")


class ForecastData(BaseModel):
    """Comprehensive forecast response payload."""
    latitude: float
    longitude: float
    timezone: str
    hourly: List[HourlyForecastItem] = Field(default_factory=list, description="Hourly forecasts for 24-48 hours")
    daily: List[DailyForecastItem] = Field(default_factory=list, description="Daily forecasts for up to 7-14 days")
    provider: str = Field(default="open-meteo")
