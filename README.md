# WeatherGPT: AI-Powered Multilingual Weather Forecasting and Alert Assistant

[![SIH Problem Statement](https://img.shields.io/badge/SIH%20Problem%20Statement-SIH26068-blue.svg)](https://www.sih.gov.in/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/Frontend-React%20%2B%20Vite-61DAFB.svg?logo=react&logoColor=black)](https://react.dev/)
[![Android](https://img.shields.io/badge/Mobile-Android%20%28Jetpack%20Compose%29-3DDC84.svg?logo=android&logoColor=white)](https://developer.android.com/jetpack/compose)
[![Languages](https://img.shields.io/badge/Languages-English%20%7C%20Hindi%20%7C%20Marathi-orange.svg)](#multilingual-support)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

WeatherGPT is an intelligent, cross-platform weather intelligence and advisory system built for the Smart India Hackathon (Problem ID: **SIH26068**). It combines verified meteorological data with generative AI capabilities to deliver hyper-local, multilingual weather forecasts, severe weather warnings, and domain-specific advisories for agriculture and travel.

---

## 🌟 Key Features

1. **Current, Hourly & Multi-Day Weather Forecasts**
   - Live temperature, precipitation, humidity, wind velocity, UV index, and atmospheric pressure.
   - Granular hourly outlook for the next 24-48 hours.
   - Comprehensive 7 to 14-day extended outlook.

2. **Grounded Conversational AI Assistant**
   - Natural language interface strictly constrained to live meteorological observations and forecast models.
   - Prevents AI hallucinations—will never synthesize unverified forecasts or emergency alerts.

3. **True Multilingual Accessibility**
   - Native support for **English**, **Hindi (हिन्दी)**, and **Marathi (मराठी)** across text and audio interfaces.
   - Cultural and contextual domain terms adapted for rural and agricultural communities.

4. **Speech Interface (Voice-in / Voice-out)**
   - Voice-driven questioning via Web Speech API and Android SpeechRecognizer.
   - Text-to-speech (TTS) audio answers for accessibility and low-literacy users.

5. **Domain-Specific Weather Advisories**
   - **AgriWeather Assistance**: Crop-stage guidance, spray windows, sowing readiness, frost warnings, and soil-moisture indications.
   - **TravelWeather Assistance**: Route advisories, storm hazards, visibility warnings, and luggage/clothing recommendations.

6. **Severe Weather & Official Alerts**
   - Dissemination of standardized Common Alerting Protocol (CAP) feeds and meteorological warnings (e.g., IMD alerts).
   - High-visibility safety notices with recommended mitigation steps.

7. **Offline-First Resilience**
   - Local caching (SQLite backend, IndexedDB on web, Room Database on Android) to review recent forecasts without active internet connectivity.

---

## 🏗️ Architecture Overview

The system is designed around a single shared backend that serves both web and native mobile clients, ensuring data consistency and centralized AI governance.

```
                              ┌─────────────────────────────────────┐
                              │            Client Apps              │
                              ├──────────────────┬──────────────────┤
                              │  React.js + Vite │ Android (Kotlin) │
                              │     Website      │  Jetpack Compose │
                              └─────────┬────────┴─────────┬────────┘
                                        │                  │
                                        │    REST / JSON   │
                                        ▼                  ▼
                              ┌─────────────────────────────────────┐
                              │        FastAPI Shared Backend       │
                              ├─────────────────────────────────────┤
                              │  - REST API Routing & Auth          │
                              │  - Localization & i18n Controller   │
                              │  - Domain Advisory Engines          │
                              │    (AgriGPT & TravelGPT)            │
                              │  - Caching & Persistence (SQLite)   │
                              └─────────┬──────────────────┬────────┘
                                        │                  │
               ┌────────────────────────┴────────┐         │
               ▼                                 ▼         ▼
┌──────────────────────────────┐ ┌──────────────────────────────────┐
│ Verified Weather Data APIs   │ │ AI Language Model API            │
│ (Open-Meteo, IMD Feeds, etc.)│ │ (Context-Grounded Weather LLM)   │
└──────────────────────────────┘ └──────────────────────────────────┘
```

---

## 📂 Project Structure

```
WeatherGPT/
├── .env.example              # Environment variables template
├── .gitignore                # Global git ignore configuration
├── README.md                 # Primary project overview and instructions
├── docs/                     # Architectural and design documentation
│   ├── project_overview.md   # SIH problem statement and mission details
│   ├── requirements.md       # Functional and non-functional specifications
│   ├── system_architecture.md# Technical system design and data flow
│   └── development_roadmap.md# Phased development strategy and milestones
├── backend/                  # Shared Python FastAPI application
├── website/                  # React.js + Vite responsive web frontend
├── android/                  # Native Android app (Kotlin + Jetpack Compose)
├── shared/                   # Shared schemas, localization strings, and assets
└── deployment/               # Cloud deployment scripts, Dockerfiles, and CI/CD
```

---

## 🚀 Technology Stack

| Layer | Technologies |
|---|---|
| **Website** | React 18, Vite, JavaScript / TypeScript, Tailwind CSS, Web Speech API |
| **Android Application** | Kotlin, Jetpack Compose, Material 3, Retrofit, Room DB, Android STT/TTS |
| **Backend API** | Python 3.10+, FastAPI, Uvicorn, Pydantic v2, HTTPX |
| **Data & Caching** | SQLite, SQLAlchemy / aiosqlite, In-memory TTL cache |
| **Weather Providers** | Open-Meteo (real-time meteorological data), IMD Alert Feeds |
| **AI / LLM Engine** | Google Gemini API / OpenAI API with strict context injection |
| **Deployment** | Vercel (Website), Render / Railway / Cloud Run (FastAPI Backend) |

---

## 🛡️ Security & Responsible AI Standards

- **Zero Secret Exposure**: API keys and tokens are stored in server-side environment variables and never transmitted to frontend clients.
- **Strict Anti-Hallucination Guardrails**: Prompts explicitly constrain the LLM to verified weather JSON payloads. It cannot generate speculative forecasts or invent official warnings.
- **Input Sanitization**: All incoming queries are sanitized and validated against standard Pydantic schemas.
- **Privacy by Design**: Location searches are handled without tracking or collecting unnecessary personal identifiable information (PII).

---

## 📋 Implementation Roadmap

- [x] **Phase 1**: Initial Project Structure, Specifications & Documentation
- [ ] **Phase 2**: FastAPI Backend Core & Meteorological Data Integration
- [ ] **Phase 3**: Conversational AI Engine & Multilingual Pipeline (EN/HI/MR)
- [ ] **Phase 4**: Responsive Web Client (React + Vite + Voice I/O)
- [ ] **Phase 5**: Native Android Application (Kotlin + Jetpack Compose)
- [ ] **Phase 6**: Comprehensive Testing, Offline Caching & End-to-End Validation
- [ ] **Phase 7**: Production Deployment (Vercel & Python Cloud Host)

For in-depth architectural and development details, consult the [docs/](docs/) directory.

---

## 👥 Authors & Acknowledgments

- **Team**: WeatherGPT
- **SIH Problem Statement**: SIH26068
- **Repository**: [https://github.com/Narendra-104/WeatherGPT.git](https://github.com/Narendra-104/WeatherGPT.git)
