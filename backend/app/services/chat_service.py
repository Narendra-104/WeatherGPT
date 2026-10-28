"""Conversational Weather Assistant Service

Orchestrates intent parsing, location resolution, meteorological context injection,
and grounded multilingual response generation.
"""

import re
from typing import Any, Dict, List, Optional
from backend.app.ai.base import AIAssistantService
from backend.app.ai.mock_assistant import SafeAIAssistant
from backend.app.schemas.chat import ChatRequest, ChatResponse
from backend.app.services.weather_service import weather_service
from backend.app.services.location_service import location_service
from backend.app.utils.logger import logger


class ChatService:
    def __init__(self, ai_assistant: Optional[AIAssistantService] = None):
        self.assistant = ai_assistant or SafeAIAssistant()

    def _extract_cities(self, text: str) -> List[str]:
        """Attempt to extract city names from query patterns like 'in Pune', 'compare Pune and Mumbai'."""
        cleaned = text.strip()
        
        # Check comparison pattern: "compare X and Y", "X vs Y"
        comp_match = re.search(r"compare\s+([A-Za-z\u0900-\u097F]+)\s+(?:and|vs|with)\s+([A-Za-z\u0900-\u097F]+)", cleaned, re.IGNORECASE)
        if comp_match:
            return [comp_match.group(1).strip(), comp_match.group(2).strip()]
        
        vs_match = re.search(r"([A-Za-z\u0900-\u097F]+)\s+vs\.?\s+([A-Za-z\u0900-\u097F]+)", cleaned, re.IGNORECASE)
        if vs_match:
            return [vs_match.group(1).strip(), vs_match.group(2).strip()]

        # Check single city pattern with word boundaries: "in Pune", "for Mumbai", "at Delhi"
        stopwords = {
            "the", "this", "my", "our", "today", "tomorrow", "simple", "two", 
            "english", "hindi", "marathi", "language", "weather", "forecast", "climate"
        }
        in_matches = re.findall(r"\b(?:in|for|at|around|of)\s+([A-Za-z\u0900-\u097F]+)", cleaned, re.IGNORECASE)
        for cand in reversed(in_matches):
            cand_clean = cand.strip()
            if cand_clean.lower() not in stopwords and len(cand_clean) >= 2:
                return [cand_clean]

        # Hindi / Marathi patterns: "पुणे में", "पुण्याचे", "मुंबईत"
        hi_match = re.search(r"([A-Za-z\u0900-\u097F]+)\s+(?:में|का|की|चे|मध्ये|त|ला)", cleaned)
        if hi_match:
            return [hi_match.group(1).strip()]

        return []

    async def chat(self, request: ChatRequest) -> ChatResponse:
        weather_context: Optional[Dict[str, Any]] = None
        comparison_context: Optional[Dict[str, Any]] = None

        extracted_cities = self._extract_cities(request.message)

        # Check if city comparison intent
        if len(extracted_cities) >= 2:
            city_a, city_b = extracted_cities[0], extracted_cities[1]
            try:
                res_a = await location_service.search_locations(city_a, count=1, language=request.language)
                res_b = await location_service.search_locations(city_b, count=1, language=request.language)
                if res_a.results and res_b.results:
                    loc_a = res_a.results[0]
                    loc_b = res_b.results[0]
                    w_a = await weather_service.get_current_weather(loc_a.latitude, loc_a.longitude, language=request.language)
                    w_b = await weather_service.get_current_weather(loc_b.latitude, loc_b.longitude, language=request.language)
                    comparison_context = {
                        "city_a": {
                            "name": loc_a.name,
                            "temp": w_a.temperature,
                            "desc": w_a.weather_description,
                            "humidity": w_a.relative_humidity,
                            "wind": w_a.wind_speed,
                            "precip": w_a.precipitation,
                        },
                        "city_b": {
                            "name": loc_b.name,
                            "temp": w_b.temperature,
                            "desc": w_b.weather_description,
                            "humidity": w_b.relative_humidity,
                            "wind": w_b.wind_speed,
                            "precip": w_b.precipitation,
                        },
                    }
            except Exception as e:
                logger.warning(f"City comparison fetch failed: {str(e)}")

        # Single city / coordinate resolution
        resolved_lat = request.latitude
        resolved_lon = request.longitude
        resolved_name = request.location_name

        if (resolved_lat is None or resolved_lon is None) and extracted_cities:
            candidate = extracted_cities[0]
            try:
                geo = await location_service.search_locations(candidate, count=1, language=request.language)
                if geo.results:
                    match = geo.results[0]
                    resolved_lat = match.latitude
                    resolved_lon = match.longitude
                    resolved_name = match.name
            except Exception as e:
                logger.warning(f"Could not resolve extracted city '{candidate}': {str(e)}")

        if resolved_lat is not None and resolved_lon is not None:
            try:
                current = await weather_service.get_current_weather(
                    resolved_lat, resolved_lon, language=request.language
                )
                
                # Fetch forecast if query asks for tomorrow or 5 days
                forecast_data = None
                query_lower = request.message.lower()
                if any(k in query_lower for k in ["tomorrow", "कल", "उद्या", "5 day", "five day", "week", "पुढील", "अगले"]):
                    try:
                        forecast = await weather_service.get_forecast(resolved_lat, resolved_lon, days=5, language=request.language)
                        forecast_data = [
                            {
                                "date": d.date,
                                "temp_max": d.temperature_max,
                                "temp_min": d.temperature_min,
                                "desc": d.weather_description,
                                "rain": d.precipitation_sum,
                                "pop": d.precipitation_probability_max,
                            }
                            for d in forecast.daily
                        ]
                    except Exception as fe:
                        logger.warning(f"Could not fetch forecast for chat: {str(fe)}")

                weather_context = {
                    "latitude": current.latitude,
                    "longitude": current.longitude,
                    "location_name": resolved_name or current.location_name,
                    "temperature": current.temperature,
                    "apparent_temperature": current.apparent_temperature,
                    "weather_description": current.weather_description,
                    "precipitation": current.precipitation or 0.0,
                    "relative_humidity": current.relative_humidity or 50.0,
                    "wind_speed": current.wind_speed or 0.0,
                    "surface_pressure": current.surface_pressure,
                    "uv_index": current.uv_index,
                    "sunrise": current.sunrise,
                    "sunset": current.sunset,
                    "forecast": forecast_data,
                    "comparison": comparison_context,
                }
            except Exception as e:
                logger.warning(f"Could not fetch weather context for chat: {str(e)}")

        elif comparison_context:
            weather_context = {"comparison": comparison_context}

        return await self.assistant.generate_response(request, weather_context=weather_context)


chat_service = ChatService()
