/**
 * WeatherGPT API Client
 * Centralized interface for communicating with the shared FastAPI backend.
 */

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

async function request(endpoint, options = {}) {
  const url = `${BASE_URL.replace(/\/$/, '')}/${endpoint.replace(/^\//, '')}`;
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  try {
    const res = await fetch(url, config);
    const data = await res.json();
    if (!res.ok || data.success === false) {
      throw new Error(data.message || data.error || `HTTP ${res.status}`);
    }
    return data.data;
  } catch (err) {
    console.error(`API Error [${endpoint}]:`, err);
    throw err;
  }
}

export const api = {
  // Current weather by city OR coordinates
  async getCurrentWeather({ city, latitude, longitude, language = 'en' }) {
    const params = new URLSearchParams({ language });
    if (latitude !== undefined && latitude !== null && longitude !== undefined && longitude !== null) {
      params.append('latitude', latitude);
      params.append('longitude', longitude);
    } else if (city) {
      params.append('city', city);
    }
    return request(`weather/current?${params.toString()}`);
  },

  // Forecast breakdown (hourly & daily)
  async getForecast({ latitude, longitude, days = 7, language = 'en' }) {
    const params = new URLSearchParams({
      latitude,
      longitude,
      days,
      language,
    });
    return request(`weather/forecast?${params.toString()}`);
  },

  // Geocoding location search
  async searchLocations(query, language = 'en', count = 5) {
    if (!query || query.trim().length < 2) return [];
    const params = new URLSearchParams({
      q: query.trim(),
      language,
      count,
    });
    const res = await request(`locations/search?${params.toString()}`);
    return res.results || [];
  },

  // Severe weather alerts
  async getAlerts({ latitude, longitude, language = 'en' }) {
    const params = new URLSearchParams({
      latitude,
      longitude,
      language,
    });
    const res = await request(`alerts?${params.toString()}`);
    return res.alerts || [];
  },

  // Conversational Weather Assistant
  async sendChatMessage({ message, language = 'en', latitude, longitude, location_name }) {
    const payload = {
      message,
      language,
      latitude: latitude ?? null,
      longitude: longitude ?? null,
      location_name: location_name ?? null,
    };
    return request('chat', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  // Health check
  async getHealth() {
    return request('health');
  },
};
