"""Custom Exception Classes for WeatherGPT Backend"""

from typing import Optional, Any


class WeatherGPTException(Exception):
    """Base exception for application errors."""
    def __init__(self, message: str, status_code: int = 500, detail: Optional[Any] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.detail = detail


class WeatherProviderError(WeatherGPTException):
    """Raised when an external weather provider fails, times out, or returns bad data."""
    def __init__(self, message: str = "Weather provider failed to respond", status_code: int = 502, detail: Optional[Any] = None):
        super().__init__(message, status_code=status_code, detail=detail)


class LocationNotFoundError(WeatherGPTException):
    """Raised when requested location cannot be resolved."""
    def __init__(self, message: str = "Location not found"):
        super().__init__(message, status_code=404)


class RateLimitExceededError(WeatherGPTException):
    """Raised when provider rate limits are exceeded."""
    def __init__(self, message: str = "Weather provider rate limit exceeded"):
        super().__init__(message, status_code=429)


class InvalidParameterError(WeatherGPTException):
    """Raised when request parameters are out of acceptable bounds."""
    def __init__(self, message: str):
        super().__init__(message, status_code=400)
