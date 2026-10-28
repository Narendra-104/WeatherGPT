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

        # Handle City Comparison if available in context
        comparison = weather_context.get("comparison") if weather_context else None
        if comparison:
            ca = comparison["city_a"]
            cb = comparison["city_b"]
            if lang == "hi":
                reply = (
                    f"मौसम तुलना ({ca['name']} बनाम {cb['name']}):\n"
                    f"• {ca['name']}: {ca['temp']}°C, {ca['desc']}, आर्द्रता {ca['humidity']}%, हवा {ca['wind']} किमी/घंटा।\n"
                    f"• {cb['name']}: {cb['temp']}°C, {cb['desc']}, आर्द्रता {cb['humidity']}%, हवा {cb['wind']} किमी/घंटा।\n"
                    f"निष्कर्ष: {ca['name'] if ca['temp'] > cb['temp'] else cb['name']} में तापमान अधिक है।"
                )
                suggestions = ["किस शहर में बारिश होगी?", "कल का पूर्वानुमान क्या है?"]
            elif lang == "mr":
                reply = (
                    f"हवामान तुलना ({ca['name']} विरुद्ध {cb['name']}):\n"
                    f"• {ca['name']}: {ca['temp']}°C, {ca['desc']}, आर्द्रता {ca['humidity']}%, वारा {ca['wind']} किमी/तास.\n"
                    f"• {cb['name']}: {cb['temp']}°C, {cb['desc']}, आर्द्रता {cb['humidity']}%, वारा {cb['wind']} किमी/तास.\n"
                    f"निष्कर्ष: {ca['name'] if ca['temp'] > cb['temp'] else cb['name']} येथे अधिक उष्णता जाणवत आहे."
                )
                suggestions = ["कोणत्या शहरात पाऊस पडेल?", "पुढील ५ दिवसांचा अंदाज?"]
            else:
                reply = (
                    f"Weather Comparison ({ca['name']} vs {cb['name']}):\n"
                    f"• {ca['name']}: {ca['temp']}°C with {ca['desc']}, humidity {ca['humidity']}%, wind {ca['wind']} km/h.\n"
                    f"• {cb['name']}: {cb['temp']}°C with {cb['desc']}, humidity {cb['humidity']}%, wind {cb['wind']} km/h.\n"
                    f"Summary: {ca['name'] if ca['temp'] > cb['temp'] else cb['name']} is currently warmer by {abs(ca['temp'] - cb['temp']):.1f}°C."
                )
                suggestions = ["Will it rain in either city?", "Show 5-day forecast comparison"]

            return ChatResponse(
                reply=reply,
                language=lang,
                model="WeatherGPT-GroundedCore (Safe)",
                grounded_facts=comparison,
                suggestions=suggestions,
            )

        # If no location or weather context is available
        if not weather_context or not weather_context.get("temperature"):
            if lang == "hi":
                reply = (
                    "कृपया अपने शहर या स्थान का नाम बताएं (जैसे: 'पुणे का मौसम' या 'मुंबई में बारिश होगी क्या?'), ताकि मैं सटीक मौसम जानकारी दे सकूँ।"
                )
                suggestions = ["दिल्ली का मौसम क्या है?", "मुंबई और पुणे के मौसम की तुलना करें", "किसानों के लिए सलाह"]
            elif lang == "mr":
                reply = (
                    "कृपया आपल्या शहराचे नाव सांगा (उदा: 'पुण्याचे हवामान' किंवा 'मुंबईत पाऊस पडेल का?'), जेणेकरून मी अचूक माहिती देऊ शकेन."
                )
                suggestions = ["पुण्याचे आजचे हवामान कसे आहे?", "शेतीसाठी आजचा सल्ला काय आहे?", "उद्या पाऊस पडेल का?"]
            else:
                reply = (
                    "Please specify a city or coordinates (e.g., 'What is the weather in Pune?' or 'Compare Pune and Mumbai') to retrieve verified weather intelligence."
                )
                suggestions = ["What is the weather in Pune?", "Will it rain tomorrow?", "Compare Pune and Mumbai", "What should I wear today?"]

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
        forecast_list = weather_context.get("forecast") or []

        # Intent detection
        is_tomorrow_rain = any(k in query for k in ["tomorrow", "कल", "उद्या"]) and any(k in query for k in ["rain", "barish", "paus", "बारिश", "पाऊस", "छाता", "umbrella"])
        is_five_days = any(k in query for k in ["five day", "5 day", "next 5", "5 दिवस", "५ दिवस", "५ दिन", "5 दिन", "week"])
        is_wear = any(k in query for k in ["wear", "clothing", "clothes", "outfit", "कपड़े", "काय घालावे", "कपडे"])
        is_outside = any(k in query for k in ["outside", "outdoor", "go out", "walk", "बाहर", "बाहेर", "फिरणे"])
        is_simple = any(k in query for k in ["simple", "easy", "सरल", "सोप्या", "समझाओ", "सांगा"])
        is_agri = any(k in query for k in ["crop", "kisan", "farm", "fertilizer", "spray", "fasal", "sheti", "शेती", "पीक", "फसल", "किसान"])
        is_travel = any(k in query for k in ["travel", "drive", "road", "trip", "highway", "yatra", "प्रवास", "यात्रा", "सफर"])
        is_rain = any(k in query for k in ["rain", "barish", "paus", "बारिश", "पाऊस", "वर्षा"])

        if is_tomorrow_rain:
            # Check tomorrow in forecast if available
            tmrw = forecast_list[1] if len(forecast_list) > 1 else (forecast_list[0] if forecast_list else None)
            if tmrw:
                tmrw_rain = tmrw.get("rain", 0.0) or 0.0
                tmrw_pop = tmrw.get("pop", 0) or 0
                tmrw_desc = tmrw.get("desc", desc)
                if lang == "hi":
                    reply = (
                        f"{loc_name} में कल का पूर्वानुमान: मौसम '{tmrw_desc}', अधिकतम {tmrw['temp_max']}°C, न्यूनतम {tmrw['temp_min']}°C। "
                        f"बारिश की संभावना {tmrw_pop}% ({tmrw_rain} mm) है। "
                        f"{'हाँ, कल बारिश होने की संभावना है, छाता साथ लेकर निकलें।' if tmrw_rain > 1.0 or tmrw_pop >= 50 or 'बारिश' in tmrw_desc else 'कल बारिश की संभावना काफी कम है।'}"
                    )
                elif lang == "mr":
                    reply = (
                        f"{loc_name} मध्ये उद्याचा हवामान अंदाज: '{tmrw_desc}', कमाल {tmrw['temp_max']}°C, किमान {tmrw['temp_min']}°C. "
                        f"पावसाची शक्यता {tmrw_pop}% ({tmrw_rain} mm) आहे. "
                        f"{'होय, उद्या पाऊस पडण्याची शक्यता जास्त आहे, छत्री सोबत ठेवा.' if tmrw_rain > 1.0 or tmrw_pop >= 50 or 'पाऊस' in tmrw_desc else 'उद्या पावसाची शक्यता फार कमी आहे.'}"
                    )
                else:
                    reply = (
                        f"Tomorrow's forecast for {loc_name}: {tmrw_desc} with a high of {tmrw['temp_max']}°C and low of {tmrw['temp_min']}°C. "
                        f"Precipitation probability is {tmrw_pop}% ({tmrw_rain} mm). "
                        f"{'Yes, rain is likely tomorrow. Keeping an umbrella with you is recommended.' if tmrw_rain > 1.0 or tmrw_pop >= 50 or 'rain' in tmrw_desc.lower() else 'Rain is unlikely tomorrow.'}"
                    )
            else:
                reply = f"Current rain rate in {loc_name} is {precip} mm ({desc}). Rain probability is moderate."
            suggestions = ["What should I wear tomorrow?", "Give me a 5-day summary"]

        elif is_five_days:
            if forecast_list:
                lines = []
                for d in forecast_list[:5]:
                    lines.append(f"• {d['date']}: {d['desc']}, {d['temp_min']}°C – {d['temp_max']}°C (Rain: {d['pop'] or 0}%)")
                summary_block = "\n".join(lines)
                if lang == "hi":
                    reply = f"{loc_name} के लिए आगामी 5 दिनों का मौसम सारांश:\n{summary_block}"
                elif lang == "mr":
                    reply = f"{loc_name} साठी पुढील ५ दिवसांचा हवामान सारांश:\n{summary_block}"
                else:
                    reply = f"5-day forecast summary for {loc_name}:\n{summary_block}"
            else:
                reply = f"In {loc_name}, expect temperatures hovering around {temp}°C with {desc}."
            suggestions = ["Will it rain tomorrow?", "What should I wear today?"]

        elif is_wear:
            if temp >= 32:
                advice_en = "Wear lightweight, breathable cotton clothes, sunglasses, and a sunhat. Keep hydrated."
                advice_hi = "हल्के और ढीले सूती कपड़े पहनें, धूप का चश्मा लगाएं और पानी की बोतल साथ रखें।"
                advice_mr = "हलके सुती कपडे वापरा, उन्हाचा चष्मा लावा आणि भरपूर पाणी सोबत ठेवा."
            elif temp <= 18:
                advice_en = "Wear a warm jacket, sweater, or layered clothing to stay comfortable in cool temperatures."
                advice_hi = "हल्की जैकेट, स्वेटर या गर्म कपड़े पहनें ताकि ठंड से बचाव हो सके।"
                advice_mr = "उबदार स्वेटर किंवा जॅकेट परिधान करा जेणेकरून थंडीपासून बचाव होईल."
            else:
                advice_en = "Comfortable everyday attire (t-shirt/shirt and jeans) is ideal. Carry an umbrella if rain threatens."
                advice_hi = "सामान्य आरामदायक कपड़े उपयुक्त हैं। बारिश का अंदेशा हो तो छाता रख लें।"
                advice_mr = "नेहमीचे आरामदायक कपडे उत्तम आहेत. पावसाची शक्यता असल्यास छत्री सोबत ठेवा."

            if precip > 0.5 or "rain" in desc.lower() or "पाऊस" in desc or "बारिश" in desc:
                advice_en += " Waterproof shoes and a raincoat/umbrella are strongly recommended today!"
                advice_hi += " साथ ही वाटरप्रूफ जूते और रेनकोट/छाता अवश्य रखें!"
                advice_mr += " सोबतच रेनकोट किंवा छत्री नक्की सोबत बाळगा!"

            if lang == "hi":
                reply = f"{loc_name} में वर्तमान तापमान {temp}°C ({desc}) है। पहनावा सलाह: {advice_hi}"
            elif lang == "mr":
                reply = f"{loc_name} मध्ये सध्या तापमान {temp}°C ({desc}) आहे. पोशाख सल्ला: {advice_mr}"
            else:
                reply = f"Current temperature in {loc_name} is {temp}°C with {desc}. Clothing Advice: {advice_en}"
            suggestions = ["Is it a good time to go outside?", "Will it rain tomorrow?"]

        elif is_outside:
            is_bad = precip > 2.0 or temp >= 40.0 or temp <= 10.0 or "तूफान" in desc or "thunderstorm" in desc.lower()
            if is_bad:
                rec_en = "It is NOT an optimal time for outdoor activities due to adverse weather conditions."
                rec_hi = "खराब मौसम या तेज धूप/बारिश के कारण इस समय बाहर जाना उचित नहीं है।"
                rec_mr = "प्रतिकूल हवामानामुळे किंवा पाऊस/उन्हामुळे सध्या बाहेर फिरणे टाळणे योग्य राहील."
            else:
                rec_en = "Weather is pleasant and safe for outdoor walks, exercise, and errands."
                rec_hi = "मौसम सुहावना और बाहर जाने के लिए बिल्कुल अनुकूल है।"
                rec_mr = "हवामान छान असून बाहेर फिरण्यासाठी किंवा कामासाठी उत्तम आहे."

            if lang == "hi":
                reply = f"{loc_name} में वर्तमान तापमान {temp}°C है ({desc})। {rec_hi}"
            elif lang == "mr":
                reply = f"{loc_name} येथे सद्य तापमान {temp}°C असून हवामान '{desc}' आहे. {rec_mr}"
            else:
                reply = f"Current condition in {loc_name} is {temp}°C with {desc}. Outdoor Advice: {rec_en}"
            suggestions = ["What should I wear today?", "Forecast for the next 5 days"]

        elif is_simple:
            if lang == "hi":
                reply = (
                    f"सरल शब्दों में: {loc_name} में आज का मौसम '{desc}' है। "
                    f"तापमान {temp}°C है, जो शरीर को {feels_like}°C जैसा लगता है। "
                    f"{'आज छाता लेकर निकलना समझदारी होगी।' if precip > 0.5 else 'मौसम सामान्य और शांत है।'}"
                )
            elif lang == "mr":
                reply = (
                    f"सोप्या भाषेत: {loc_name} येथे आजचे हवामान '{desc}' आहे. "
                    f"तापमान {temp}°C असून जाणवणारे तापमान {feels_like}°C आहे. "
                    f"{'पाऊस असल्याने छत्री सोबत ठेवा.' if precip > 0.5 else 'हवामान अगदी सामान्य आणि शांत आहे.'}"
                )
            else:
                reply = (
                    f"In simple words: {loc_name} is experiencing {desc} today. "
                    f"The temperature is {temp}°C (feels like {feels_like}°C). "
                    f"{'You should carry an umbrella today!' if precip > 0.5 else 'The atmosphere is fairly calm and comfortable.'}"
                )
            suggestions = ["What should I wear today?", "Will it rain tomorrow?"]

        elif is_agri:
            if lang == "hi":
                reply = (
                    f"{loc_name} में वर्तमान तापमान {temp}°C है और मौसम '{desc}' है। "
                    f"आर्द्रता {humidity}% और वर्षा {precip}mm है। "
                    f"कृषि सलाह: {'बारिश की संभावना के कारण कीटनाशक या खाद का छिड़काव अभी टालें।' if precip > 0.5 or 'बारिश' in desc else 'मौसम अनुकूल है। छिड़काव एवं सामान्य कृषि कार्य किए जा सकते हैं।'}"
                )
                suggestions = ["अगले 5 दिनों का पूर्वानुमान क्या है?", "सिंचाई कब करें?", "तेज हवा की चेतावनी"]
            elif lang == "mr":
                reply = (
                    f"{loc_name} येथे सध्याचे तापमान {temp}°C असून हवामान '{desc}' आहे. "
                    f"हवेतील आर्द्रता {humidity}% व पर्जन्यमान {precip}mm नोंदवले गेले आहे. "
                    f"शेती सल्ला: {'पावसाची शक्यता असल्याने कीटकनाशक फवारणी किंवा खत व्यवस्थापन पुढे ढकलावे.' if precip > 0.5 or 'पाऊस' in desc else 'हवामान अनुकूल आहे. फवारणी आणि शेतीची कामे करता येतील.'}"
                )
                suggestions = ["पुढील ५ दिवसांचा अंदाज काय?", "पिकांना पाणी कधी द्यावे?", "वादळी वाऱ्याची शक्यता आहे का?"]
            else:
                reply = (
                    f"In {loc_name}, the current temperature is {temp}°C with {desc}. "
                    f"Humidity is {humidity}% and precipitation is {precip}mm. "
                    f"Agri Advisory: {'Postpone chemical spraying and fertilizer application due to rainfall.' if precip > 0.5 or 'rain' in desc.lower() else 'Conditions are favorable for routine spraying and field operations.'}"
                )
                suggestions = ["Next 5 days outlook", "Best time for irrigation", "Wind hazard advisory"]

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
                suggestions = ["किसानों के लिए सलाह", "यात्रा मौसम अपडेट", "5 दिनों का पूर्वानुमान"]
            elif lang == "mr":
                reply = (
                    f"{loc_name} मध्ये सध्याचे तापमान {temp}°C (जाणवणारे {feels_like}°C) आहे. "
                    f"हवामानाची स्थिती '{desc}' आहे. हवेतील आर्द्रता {humidity}% आणि वाऱ्याचा वेग {wind} किमी/तास आहे."
                )
                suggestions = ["शेतीविषयक सल्ला", "प्रवास हवामान सल्ला", "५ दिवसांचा अंदाज"]
            else:
                reply = (
                    f"The current temperature in {loc_name} is {temp}°C (feels like {feels_like}°C) with {desc}. "
                    f"Relative humidity is {humidity}% and wind speed is {wind} km/h."
                )
                suggestions = ["Agricultural advisory", "Travel conditions", "5-day forecast"]

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
