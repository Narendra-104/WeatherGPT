import React from 'react';
import { 
  Thermometer, Droplets, Wind, Gauge, CloudRain, Sun, Compass, Sunrise, Sunset, ShieldAlert, Sparkles, MapPin 
} from 'lucide-react';
import { translations } from '../i18n/translations';

export default function CurrentWeather({ weather, language, onOpenAI, onOpenLocationModal }) {
  const t = translations[language] || translations.en;

  if (!weather) return null;

  const getWeatherIcon = (code) => {
    // Rain or drizzle
    if ([51, 53, 55, 61, 63, 65, 80, 81, 82].includes(code) || (code >= 500 && code < 600)) {
      return <CloudRain className="w-16 h-16 text-sky-400 animate-bounce" />;
    }
    // Thunderstorm
    if ([95, 96, 99].includes(code) || (code >= 200 && code < 300)) {
      return <ShieldAlert className="w-16 h-16 text-amber-400 animate-pulse" />;
    }
    // Clear sky
    if (code === 0 || code === 800) {
      return <Sun className="w-16 h-16 text-amber-400 animate-spin-slow" />;
    }
    // Overcast/clouds
    return <Sun className="w-16 h-16 text-sky-300" />;
  };

  const formatTime = (isoString) => {
    if (!isoString) return '--:--';
    try {
      const d = new Date(isoString);
      return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } catch {
      return isoString;
    }
  };

  return (
    <div className="bg-gradient-to-br from-slate-800/90 via-slate-800/60 to-slate-900/90 rounded-3xl p-6 sm:p-8 border border-slate-700/80 shadow-2xl relative overflow-hidden">
      {/* Decorative background glow */}
      <div className="absolute -right-16 -top-16 w-64 h-64 bg-sky-500/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute -left-16 -bottom-16 w-64 h-64 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />

      {/* Top Bar: Location & Provider Info */}
      <div className="flex flex-wrap items-center justify-between gap-3 mb-6 relative z-10">
        <div>
          <div className="flex flex-wrap items-center gap-2">
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              {weather.location_name || `${weather.latitude.toFixed(2)}°, ${weather.longitude.toFixed(2)}°`}
            </h1>
            <button
              onClick={onOpenLocationModal}
              className="text-xs px-2.5 py-1 rounded-xl bg-sky-500/20 hover:bg-sky-500/30 text-sky-300 font-bold border border-sky-500/40 transition-colors flex items-center gap-1 shadow-sm"
              title="Change Location"
            >
              <MapPin className="w-3 h-3 text-sky-400" />
              <span>{language === 'hi' ? 'स्थान बदलें' : language === 'mr' ? 'स्थान बदला' : 'Change Location'}</span>
            </button>
            <span className="text-[11px] px-2 py-0.5 rounded-full bg-slate-700/60 text-slate-300 font-medium border border-slate-600/40">
              {weather.provider}
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            {t.today} • {new Date(weather.observation_time).toLocaleString([], { dateStyle: 'medium', timeStyle: 'short' })}
          </p>
        </div>

        <button
          onClick={onOpenAI}
          className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-sky-500/10 hover:bg-sky-500/20 text-sky-400 text-xs font-semibold border border-sky-500/30 transition-colors"
        >
          <Sparkles className="w-3.5 h-3.5" />
          <span>{t.askAI}</span>
        </button>
      </div>

      {/* Main Temperature & Condition Row */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-6 pb-8 border-b border-slate-700/60 relative z-10">
        <div className="flex items-center gap-6">
          <div className="p-3 bg-slate-700/40 rounded-2xl border border-slate-600/30 backdrop-blur-sm">
            {getWeatherIcon(weather.weather_code)}
          </div>
          <div>
            <div className="flex items-baseline">
              <span className="text-6xl sm:text-7xl font-extrabold text-white tracking-tighter">
                {Math.round(weather.temperature)}
              </span>
              <span className="text-3xl sm:text-4xl font-light text-sky-400 ml-1">°C</span>
            </div>
            <p className="text-lg font-semibold text-slate-200 mt-1 capitalize">
              {weather.weather_description}
            </p>
          </div>
        </div>

        {weather.apparent_temperature !== undefined && weather.apparent_temperature !== null && (
          <div className="bg-slate-700/30 rounded-2xl px-5 py-3 border border-slate-700/50 flex items-center gap-3">
            <Thermometer className="w-5 h-5 text-amber-400" />
            <div>
              <p className="text-xs text-slate-400">{t.feelsLike}</p>
              <p className="text-base font-bold text-white">{Math.round(weather.apparent_temperature)}°C</p>
            </div>
          </div>
        )}
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 sm:gap-4 mt-6 relative z-10">
        {/* Humidity */}
        <div className="bg-slate-800/60 p-3.5 rounded-2xl border border-slate-700/40 flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-400 mb-1">
            <span className="text-xs font-medium">{t.humidity}</span>
            <Droplets className="w-4 h-4 text-sky-400" />
          </div>
          <span className="text-lg font-bold text-white">
            {weather.relative_humidity !== null ? `${weather.relative_humidity}%` : '--'}
          </span>
        </div>

        {/* Wind Speed */}
        <div className="bg-slate-800/60 p-3.5 rounded-2xl border border-slate-700/40 flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-400 mb-1">
            <span className="text-xs font-medium">{t.wind}</span>
            <Wind className="w-4 h-4 text-teal-400" />
          </div>
          <span className="text-lg font-bold text-white">
            {weather.wind_speed !== null ? `${weather.wind_speed} km/h` : '--'}
          </span>
        </div>

        {/* Precipitation */}
        <div className="bg-slate-800/60 p-3.5 rounded-2xl border border-slate-700/40 flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-400 mb-1">
            <span className="text-xs font-medium">{t.precipitation}</span>
            <CloudRain className="w-4 h-4 text-indigo-400" />
          </div>
          <span className="text-lg font-bold text-white">
            {weather.precipitation !== null ? `${weather.precipitation} mm` : '0 mm'}
          </span>
        </div>

        {/* Atmospheric Pressure */}
        <div className="bg-slate-800/60 p-3.5 rounded-2xl border border-slate-700/40 flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-400 mb-1">
            <span className="text-xs font-medium">{t.pressure}</span>
            <Gauge className="w-4 h-4 text-violet-400" />
          </div>
          <span className="text-lg font-bold text-white">
            {weather.surface_pressure !== null ? `${Math.round(weather.surface_pressure)} hPa` : '--'}
          </span>
        </div>

        {/* Sunrise */}
        <div className="bg-slate-800/60 p-3.5 rounded-2xl border border-slate-700/40 flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-400 mb-1">
            <span className="text-xs font-medium">{t.sunrise}</span>
            <Sunrise className="w-4 h-4 text-amber-400" />
          </div>
          <span className="text-lg font-bold text-white">
            {formatTime(weather.sunrise)}
          </span>
        </div>

        {/* Sunset */}
        <div className="bg-slate-800/60 p-3.5 rounded-2xl border border-slate-700/40 flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-400 mb-1">
            <span className="text-xs font-medium">{t.sunset}</span>
            <Sunset className="w-4 h-4 text-orange-400" />
          </div>
          <span className="text-lg font-bold text-white">
            {formatTime(weather.sunset)}
          </span>
        </div>
      </div>
    </div>
  );
}
