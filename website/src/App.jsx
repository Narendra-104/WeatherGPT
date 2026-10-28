import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import CurrentWeather from './components/CurrentWeather';
import HourlyForecast from './components/HourlyForecast';
import DailyForecast from './components/DailyForecast';
import AlertBanner from './components/AlertBanner';
import SavedLocations from './components/SavedLocations';
import AIChatModal from './components/AIChatModal';
import CityComparison from './components/CityComparison';
import { api } from './api/client';
import { translations } from './i18n/translations';
import { Loader2, AlertCircle, RefreshCw } from 'lucide-react';

export default function App() {
  const [language, setLanguage] = useState(() => localStorage.getItem('weathergpt_lang') || 'en');
  const [currentCity, setCurrentCity] = useState({
    name: 'Pune',
    latitude: 18.5204,
    longitude: 73.8567,
  });

  const [weather, setWeather] = useState(null);
  const [forecast, setForecast] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isLoadingLocation, setIsLoadingLocation] = useState(false);

  // Modals state
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [isCompareOpen, setIsCompareOpen] = useState(false);

  const t = translations[language] || translations.en;

  const handleLanguageChange = (newLang) => {
    setLanguage(newLang);
    localStorage.setItem('weathergpt_lang', newLang);
  };

  const fetchWeatherData = async (targetCity = currentCity) => {
    setIsLoading(true);
    setError(null);

    try {
      // 1. Fetch current weather
      const weatherData = await api.getCurrentWeather({
        city: targetCity.name,
        latitude: targetCity.latitude,
        longitude: targetCity.longitude,
        language,
      });
      setWeather(weatherData);

      // 2. Fetch forecast & alerts in parallel using resolved coordinates
      const [forecastData, alertsData] = await Promise.all([
        api.getForecast({
          latitude: weatherData.latitude,
          longitude: weatherData.longitude,
          days: 7,
          language,
        }),
        api.getAlerts({
          latitude: weatherData.latitude,
          longitude: weatherData.longitude,
          language,
        }),
      ]);

      setForecast(forecastData);
      setAlerts(alertsData);
    } catch (err) {
      console.error('Weather fetch error:', err);
      setError(err.message || t.errorLoading);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchWeatherData(currentCity);
  }, [currentCity, language]);

  // Handle GPS location request
  const handleUseCurrentLocation = () => {
    if (!navigator.geolocation) {
      alert('Geolocation is not supported by your browser.');
      return;
    }

    setIsLoadingLocation(true);
    navigator.geolocation.getCurrentPosition(
      (position) => {
        setIsLoadingLocation(false);
        const coords = {
          name: '',
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
        };
        setCurrentCity(coords);
      },
      (err) => {
        setIsLoadingLocation(false);
        console.warn('Geolocation denied:', err);
        alert(t.locationPermissionDenied);
      },
      { timeout: 10000 }
    );
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col justify-between selection:bg-sky-500 selection:text-white">
      
      {/* Top Header */}
      <Header
        currentCity={currentCity}
        onSelectCity={(city) => setCurrentCity(city)}
        onUseLocation={handleUseCurrentLocation}
        language={language}
        onLanguageChange={handleLanguageChange}
        onOpenChat={() => setIsChatOpen(true)}
        onOpenCompare={() => setIsCompareOpen(true)}
        isLoadingLocation={isLoadingLocation}
      />

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
        
        {/* Quick Access Saved Cities */}
        <SavedLocations
          currentCity={currentCity}
          onSelectCity={(city) => setCurrentCity(city)}
          language={language}
        />

        {/* Loading Spinner */}
        {isLoading && (
          <div className="py-20 flex flex-col items-center justify-center gap-3">
            <Loader2 className="w-10 h-10 text-sky-400 animate-spin" />
            <p className="text-sm font-medium text-slate-400 animate-pulse">{t.loadingWeather}</p>
          </div>
        )}

        {/* Error State */}
        {!isLoading && error && (
          <div className="bg-rose-950/40 border border-rose-800/60 rounded-3xl p-8 text-center max-w-md mx-auto space-y-4">
            <AlertCircle className="w-12 h-12 text-rose-400 mx-auto" />
            <p className="text-sm text-rose-200">{error}</p>
            <button
              onClick={() => fetchWeatherData(currentCity)}
              className="px-4 py-2 bg-rose-600 hover:bg-rose-500 text-white rounded-xl text-xs font-bold flex items-center gap-2 mx-auto transition-colors"
            >
              <RefreshCw className="w-4 h-4" />
              <span>{t.retry}</span>
            </button>
          </div>
        )}

        {/* Weather Dashboard View */}
        {!isLoading && !error && weather && (
          <>
            {/* Severe Alerts */}
            <AlertBanner alerts={alerts} language={language} />

            {/* Current Weather Card */}
            <CurrentWeather 
              weather={weather} 
              language={language} 
              onOpenAI={() => setIsChatOpen(true)} 
            />

            {/* Hourly & Daily Forecasts */}
            {forecast && (
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-2 space-y-6">
                  <HourlyForecast hourly={forecast.hourly} language={language} />
                </div>
                <div className="lg:col-span-1">
                  <DailyForecast daily={forecast.daily} language={language} />
                </div>
              </div>
            )}
          </>
        )}

      </main>

      {/* Footer */}
      <footer className="border-t border-slate-900 bg-slate-950/80 py-6 mt-12 text-center text-xs text-slate-500">
        <p>{t.poweredBy}</p>
        <p className="mt-1">
          WeatherGPT — AI-Powered Multilingual Weather & Alert Assistant
        </p>
      </footer>

      {/* AI Assistant Modal */}
      <AIChatModal
        isOpen={isChatOpen}
        onClose={() => setIsChatOpen(false)}
        weather={weather}
        language={language}
      />

      {/* City Comparison Modal */}
      <CityComparison
        isOpen={isCompareOpen}
        onClose={() => setIsCompareOpen(false)}
        language={language}
      />

    </div>
  );
}
