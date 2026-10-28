# Requirements Specification: WeatherGPT

**SIH Problem Statement ID**: SIH26068  
**Document Status**: Baseline Specification  

---

## 1. Functional Requirements (FR)

### FR-01: Weather Data Ingestion & Forecasting
- **FR-01.1 Current Weather**: The system shall retrieve real-time temperature, apparent temperature ("feels like"), humidity, precipitation, wind speed/direction, atmospheric pressure, and UV index for any requested coordinates or resolved location.
- **FR-01.2 Hourly Forecast**: The system shall provide a continuous 24- to 48-hour hourly breakdown of temperature, precipitation probability, cloud cover, and wind velocity.
- **FR-01.3 Multi-Day Forecast**: The system shall offer a 7- to 14-day daily outlook with minimum/maximum temperatures, expected precipitation sum, and dominant weather conditions.
- **FR-01.4 Real-Data Enactment**: All weather metrics must originate from verified providers (e.g., Open-Meteo, IMD feeds, WeatherAPI). Synthetic or fabricated weather figures are strictly forbidden.

### FR-02: Location Search & Geocoding
- **FR-02.1 Search by Name**: Users shall be able to search for cities, towns, tehsils, and villages by name in English, Hindi, or Marathi.
- **FR-02.2 GPS Geolocation**: With explicit user permission, clients (Web and Android) shall capture device latitude and longitude and reverse-geocode to human-readable place names.
- **FR-02.3 Recent Searches**: Clients shall persist recent search locations locally for rapid recall.

### FR-03: Multilingual Conversational AI Assistant
- **FR-03.1 Trilingual Understanding & Generation**: The AI engine must accurately interpret questions and respond natively in:
  - English (`en`)
  - Hindi (`hi`)
  - Marathi (`mr`)
- **FR-03.2 Context-Grounded Prompting**: The conversational engine must accept structured meteorological JSON from the backend cache/fetch layer and formulate responses exclusively from that context.
- **FR-03.3 Guardrails**: The AI assistant shall not speculate on future disasters, contradict official alerts, or answer out-of-domain queries that could mislead users regarding atmospheric conditions.

### FR-04: Domain-Specific Advisory Modules
- **FR-04.1 Agriculture Weather Assistant**:
  - Evaluate rainfall probability over a 48-hour window before recommending pesticide/fertilizer spraying.
  - Assess soil moisture indicators and temperature extremes to advise on irrigation timing.
  - Detect impending cold waves, frost risks, or extreme heatwaves and deliver crop-safety advisories in Hindi and Marathi.
- **FR-04.2 Travel Weather Assistant**:
  - Deliver destination weather previews for planned travel dates.
  - Issue proactive warnings for poor visibility (dense fog), heavy monsoon downpours, waterlogging, or severe winds.
  - Suggest packing essentials (rain gear, warm clothing, hydration reminders).

### FR-05: Severe Weather Alerts & Safety Notifications
- **FR-05.1 Alert Ingestion**: The system shall parse and normalize severe weather warnings from recognized agencies (e.g., IMD, NDMA, State Disaster Management Authorities).
- **FR-05.2 Severity Classification**: Alerts must be categorized into standard tiers (e.g., Green/None, Yellow/Watch, Orange/Alert, Red/Warning).
- **FR-05.3 Actionable Guidance**: Each severe alert must accompany simple, clear safety instructions in the user's selected language.

### FR-06: Voice Interaction (Speech-to-Text & Text-to-Speech)
- **FR-06.1 Voice Input**: The web application (via browser Web Speech API) and the Android application (via native Android SpeechRecognizer) shall support voice dictation for user prompts in English, Hindi, and Marathi.
- **FR-06.2 Text-to-Speech (TTS)**: The system shall provide an audible playback of the AI's synthesized answer using speech synthesis engines.

### FR-07: Offline Caching & Resilience
- **FR-07.1 Backend Caching**: The FastAPI backend shall cache external weather responses in an SQLite / in-memory store for 15 minutes to minimize redundant third-party API calls and prevent rate limiting.
- **FR-07.2 Client Caching**: Web and Android clients shall cache the latest retrieved forecast locally (IndexedDB / Room DB) so that users can view recent conditions during network disconnects.

---

## 2. Non-Functional Requirements (NFR)

### NFR-01: Performance & Latency
- Weather API response time from backend cache shall not exceed 150 ms.
- Third-party weather retrieval fallback shall complete within 1.5 seconds.
- Conversational AI responses (end-to-end streaming/response) shall begin delivery within 2.5 seconds.

### NFR-02: Security & Privacy
- **No Secret Leakage**: No private API keys, database credentials, or internal tokens shall be exposed in the React frontend or Android client code.
- **CORS Protection**: Backend APIs shall enforce strict Cross-Origin Resource Sharing rules.
- **Data Minimization**: User queries and coordinates shall not be tied to personally identifiable profiles.

### NFR-03: Usability & Accessibility
- **Responsive Web Design**: The website must provide an optimized experience across mobile viewports (320px+), tablets, and desktop displays.
- **Accessible Android UI**: Jetpack Compose screens must comply with Material 3 accessibility guidelines, supporting dynamic text scaling and screen readers.
- **Intuitive Language Switching**: One-tap toggle between English, Hindi, and Marathi must instantly update UI strings and AI conversational context.

### NFR-04: Reliability & Maintainability
- Modular architecture with clean separation of concerns between data ingestion, AI processing, business logic, and presentation.
- Decoupled weather provider adapters allowing plug-and-play migration between weather data sources.
- Comprehensive automated unit and integration tests for backend endpoints and validation models.
