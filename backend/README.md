# WeatherGPT Backend (FastAPI)

Shared high-performance Python FastAPI backend for **WeatherGPT (SIH26068)**.
Serves real-time weather observations, multi-day forecasts, geocoding, severe weather warnings, and context-grounded multilingual conversational AI for both the responsive web application and native Android mobile application.

---

## ⛅ Supported Meteorological Providers

WeatherGPT supports hot-swappable meteorological providers via an extensible adapter pattern:

1. **Open-Meteo (`WEATHER_PROVIDER=open_meteo`)**:
   - Default provider.
   - Requires **no external API key**.
   - Supports global coordinates, granular hourly forecasts, and extended 7 to 14-day forecasts.

2. **OpenWeather (`WEATHER_PROVIDER=openweather`)**:
   - Industry-standard weather service powered by the OpenWeather API (data/2.5 and geo/1.0).
   - Requires a valid `WEATHER_API_KEY`.
   - Supports live weather, 5-day / 3-hour forecasts, and multilingual location geocoding.

---

## 🛠️ Local Configuration Guide

### Step 1: Create your local `.env` file

Navigate to the `backend/` directory and copy the template:

```bash
cp backend/.env.example backend/.env
```

### Step 2: Configure OpenWeather

Open `backend/.env` in your editor and configure the provider settings:

```env
WEATHER_PROVIDER=openweather
WEATHER_API_KEY=YOUR_OPENWEATHER_API_KEY
OPENWEATHER_BASE_URL=https://api.openweathermap.org
```

> [!IMPORTANT]
> Replace `YOUR_OPENWEATHER_API_KEY` with your actual OpenWeather API key.
> **Never commit your actual `.env` file into Git version control.** The file is strictly ignored by `.gitignore`.

### Step 3: Switch Back to Open-Meteo (Optional)

If you wish to switch back to Open-Meteo without an API key, simply set:

```env
WEATHER_PROVIDER=open_meteo
```

### Step 4: Restart the Backend

Environment changes are read upon startup. Whenever you modify `backend/.env`, **you must restart the backend server** for the new configuration to take effect:

```bash
uvicorn backend.app.main:app --reload --port 8000
```

---

## 🚀 Running the Automated Test Suite

Run the full automated test suite (including OpenWeather mock tests and Open-Meteo live integration):

```bash
python -m pytest backend/tests -v
```

---

## 📋 API Endpoints Reference

Interactive documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/health` | Diagnostic status & active provider check |
| `GET` | `/api/v1/weather/current` | Live weather observation (`lat`, `lon`, `language`) |
| `GET` | `/api/v1/weather/forecast` | Hourly breakdown & multi-day forecast (`days=1..14`) |
| `GET` | `/api/v1/locations/search` | Location search & coordinate geocoding |
| `POST` | `/api/v1/chat` | Multilingual conversational weather assistant |
| `GET` | `/api/v1/alerts` | Verified severe weather alerts & advisories |
