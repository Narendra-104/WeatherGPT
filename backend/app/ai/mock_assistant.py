"""Safe AI Assistant Service Interface

Operates as a reliable grounding engine that translates real meteorological observations
into helpful conversational responses in English, Hindi, and Marathi without requiring external LLM API keys.
Ready to be augmented or replaced with direct LLM calls in Phase 3.
"""

from typing import Any, Dict, List, Optional
from backend.app.ai.base import AIAssistantService
from backend.app.schemas.chat import ChatRequest, ChatResponse


class SafeAIAssistant(AIAssistantService):
    """Rule-based, grounded conversational assistant strictly using verified weather facts."""

    async def generate_response(
        self, request: ChatRequest, weather_context: Optional[Dict[str, Any]] = None
    ) -> ChatResponse:
        lang = request.language if request.language in ["en", "hi", "mr"] else "en"
        query = request.message.lower().strip()

        # If no location or weather context is available
        if not weather_context:
            if lang == "hi":
                reply = (
                    "कृपया अपने शहर या स्थान का नाम बताएं, या सटीक मौसम जानकारी पाने के लिए जीपीएस लोकेशन साझा करें।"
                )
                suggestions = ["दिल्ली का मौसम क्या है?", "मुंबई में बारिश होगी क्या?", "किसानों के लिए सलाह"]
            elif lang == "mr":
                reply = (
                    "कृपया अचूक हवामान माहिती मिळवण्यासाठी आपल्या शहराचे नाव सांगा किंवा जीपीएस स्थान शेअर करा."
                )
                suggestions = ["पुण्याचे आजचे हवामान कसे आहे?", "शेतीसाठी आजचा सल्ला काय आहे?", "उद्या पाऊस पडेल का?"]
            else:
                reply = (
                    "Please specify a city or enable your location coordinates to retrieve accurate live weather updates."
                )
                suggestions = ["What is the weather in Pune?", "Is it raining today?", "Agricultural weather advisory"]

            return ChatResponse(
                reply=reply,
                language=lang,
                model="WeatherGPT-GroundedCore (Safe)",
                grounded_facts=None,
                suggestions=suggestions,
            )

        # Ground response using verified live weather
        temp = weather_context.get("temperature", 0.0)
        feels_like = weather_context.get("apparent_temperature", temp)
        desc = weather_context.get("weather_description", "Current condition")
        precip = weather_context.get("precipitation", 0.0)
        wind = weather_context.get("wind_speed", 0.0)
        humidity = weather_context.get("relative_humidity", 50.0)
        loc_name = weather_context.get("location_name") or f"coordinates ({weather_context.get('latitude', 0):.2f}, {weather_context.get('longitude', 0):.2f})"

        # Check for specific intents
        is_agri = any(k in query for k in ["crop", "kisan", "farm", "fertilizer", "spray", "fasal", "sheti", "शेती", "पीक", "फसल", "किसान"])
        is_travel = any(k in query for k in ["travel", "drive", "road", "trip", "highway", "yatra", "प्रवास", "यात्रा", "सफर"])
        is_rain = any(k in query for k in ["rain", "barish", "paus", "बारिश", "पाऊस", "वर्षा"])

        if is_agri:
            if lang == "hi":
                reply = (
                    f"{loc_name} में वर्तमान तापमान {temp}°C है और मौसम '{desc}' है। "
                    f"आर्द्रता {humidity}% और वर्षा {precip}mm है। "
                    f"कृषि सलाह: {'बारिश की संभावना के कारण कीटनाशक या खाद का छिड़काव अभी टालें।' if precip > 0.5 or 'बारिश' in desc else 'मौसम अनुकूल है। छिड़काव एवं सामान्य कृषि कार्य किए जा सकते हैं।'}"
                )
                suggestions = ["अगले 3 दिनों का पूर्वानुमान क्या है?", "सिंचाई कब करें?", "तेज हवा की चेतावनी"]
            elif lang == "mr":
                reply = (
                    f"{loc_name} येथे सध्याचे तापमान {temp}°C असून हवामान '{desc}' आहे. "
                    f"हवेतील आर्द्रता {humidity}% व पर्जन्यमान {precip}mm नोंदवले गेले आहे. "
                    f"शेती सल्ला: {'पावसाची शक्यता असल्याने कीटकनाशक फवारणी किंवा खत व्यवस्थापन पुढे ढकलावे.' if precip > 0.5 or 'पाऊस' in desc else 'हवामान अनुकूल आहे. फवारणी आणि शेतीची कामे करता येतील.'}"
                )
                suggestions = ["पुढील ३ दिवसांचा अंदाज काय?", "पिकांना पाणी कधी द्यावे?", "वादळी वाऱ्याची शक्यता आहे का?"]
            else:
                reply = (
                    f"In {loc_name}, the current temperature is {temp}°C with {desc}. "
                    f"Humidity is {humidity}% and precipitation is {precip}mm. "
                    f"Agri Advisory: {'Postpone chemical spraying and fertilizer application due to rainfall.' if precip > 0.5 or 'rain' in desc.lower() else 'Conditions are favorable for routine spraying and field operations.'}"
                )
                suggestions = ["Next 3 days outlook", "Best time for irrigation", "Wind hazard advisory"]

        elif is_travel:
            if lang == "hi":
                reply = (
                    f"{loc_name} के लिए यात्रा मौसम: वर्तमान तापमान {temp}°C है ('{desc}'), हवा की गति {wind} किमी/घंटा है। "
                    f"{'भारी बारिश या खराब मौसम के कारण सावधानी से वाहन चलाएं।' if precip > 2.0 or 'तूफान' in desc else 'सड़क मार्ग की स्थिति सामान्य और यात्रा के लिए सुरक्षित प्रतीत होती है।'}"
                )
                suggestions = ["रास्ते में कोहरा रहेगा क्या?", "कल का मौसम कैसा होगा?"]
            elif lang == "mr":
                reply = (
                    f"{loc_name} साठी प्रवास सल्ला: सध्या तापमान {temp}°C असून हवामान '{desc}' आहे, वाऱ्याचा वेग {wind} किमी/तास आहे. "
                    f"{'पावसामुळे रस्त्यांवर सावधगिरी बाळगावी.' if precip > 2.0 or 'वादळ' in desc else 'प्रवासासाठी हवामान अनुकूल आणि सुरक्षित आहे.'}"
                )
                suggestions = ["धुक्याची शक्यता आहे का?", "उद्याचे हवामान कसे राहील?"]
            else:
                reply = (
                    f"Travel advisory for {loc_name}: Currently {temp}°C with {desc}, and winds at {wind} km/h. "
                    f"{'Exercise caution while driving due to wet road conditions and reduced visibility.' if precip > 2.0 or 'rain' in desc.lower() else 'Weather conditions are stable and clear for travel.'}"
                )
                suggestions = ["Visibility and fog forecast", "Tomorrow's road weather"]

        elif is_rain:
            if lang == "hi":
                reply = (
                    f"{loc_name} में वर्तमान में '{desc}' है और वर्षा दर {precip} mm है। "
                    f"{'जी हां, इस समय बारिश हो रही है या होने की संभावना है। छाता साथ रखें!' if precip > 0 or 'बारिश' in desc else 'फिलहाल वर्षा नहीं हो रही है।'}"
                )
                suggestions = ["आज का अधिकतम तापमान?", "शाम को बारिश होगी क्या?"]
            elif lang == "mr":
                reply = (
                    f"{loc_name} येथे सद्यस्थिती '{desc}' असून पर्जन्यमान {precip} mm आहे. "
                    f"{'होय, सध्या पावसाची शक्यता किंवा हलका पाऊस सुरू आहे. छत्री सोबत ठेवा!' if precip > 0 or 'पाऊस' in desc else 'सध्या पाऊस नाही.'}"
                )
                suggestions = ["आजचे कमाल तापमान किती?", "संध्याकाळी पाऊस पडेल का?"]
            else:
                reply = (
                    f"In {loc_name}, current condition is '{desc}' with a precipitation rate of {precip} mm. "
                    f"{'Yes, rain is active or imminent. Please keep an umbrella handy!' if precip > 0 or 'rain' in desc.lower() else 'It is currently dry with no active rain.'}"
                )
                suggestions = ["Hourly forecast for today", "Will it rain this evening?"]

        else:
            if lang == "hi":
                reply = (
                    f"{loc_name} में वर्तमान तापमान {temp}°C (महसूस {feels_like}°C) है। "
                    f"आसमान की स्थिति '{desc}' है। आर्द्रता {humidity}% और हवा {wind} किमी/घंटा की गति से चल रही है।"
                )
                suggestions = ["किसानों के लिए सलाह", "यात्रा मौसम अपडेट", "7 दिनों का पूर्वानुमान"]
            elif lang == "mr":
                reply = (
                    f"{loc_name} मध्ये सध्याचे तापमान {temp}°C (जाणवणारे {feels_like}°C) आहे. "
                    f"हवामानाची स्थिती '{desc}' आहे. हवेतील आर्द्रता {humidity}% आणि वाऱ्याचा वेग {wind} किमी/तास आहे."
                )
                suggestions = ["शेतीविषयक सल्ला", "प्रवास हवामान सल्ला", "७ दिवसांचा अंदाज"]
            else:
                reply = (
                    f"The current temperature in {loc_name} is {temp}°C (feels like {feels_like}°C) with {desc}. "
                    f"Relative humidity is {humidity}% and wind speed is {wind} km/h."
                )
                suggestions = ["Agricultural advisory", "Travel conditions", "7-day forecast"]

        return ChatResponse(
            reply=reply,
            language=lang,
            model="WeatherGPT-GroundedCore (Safe)",
            grounded_facts={
                "temperature": temp,
                "apparent_temperature": feels_like,
                "description": desc,
                "precipitation": precip,
                "humidity": humidity,
                "wind_speed": wind,
                "location": loc_name,
            },
            suggestions=suggestions,
        )
