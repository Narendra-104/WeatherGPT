import React, { useState } from 'react';
import { X, Scale, ArrowRight, Loader2, Thermometer, Droplets, Wind, CloudRain } from 'lucide-react';
import { api } from '../api/client';
import { translations } from '../i18n/translations';

export default function CityComparison({ isOpen, onClose, language }) {
  const t = translations[language] || translations.en;

  const [cityA, setCityA] = useState('Pune');
  const [cityB, setCityB] = useState('Mumbai');
  const [weatherA, setWeatherA] = useState(null);
  const [weatherB, setWeatherB] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleCompare = async () => {
    if (!cityA.trim() || !cityB.trim()) return;

    setIsLoading(true);
    setError(null);

    try {
      const [resA, resB] = await Promise.all([
        api.getCurrentWeather({ city: cityA.trim(), language }),
        api.getCurrentWeather({ city: cityB.trim(), language }),
      ]);
      setWeatherA(resA);
      setWeatherB(resB);
    } catch (err) {
      setError(err.message || 'Failed to compare cities.');
    } finally {
      setIsLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/70 backdrop-blur-sm animate-fade-in">
      <div className="bg-slate-900 border border-slate-800 rounded-3xl max-w-2xl w-full p-6 shadow-2xl relative overflow-hidden">
        
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-slate-800">
          <div className="flex items-center gap-2.5">
            <div className="p-2 bg-indigo-500/20 text-indigo-400 rounded-xl">
              <Scale className="w-5 h-5" />
            </div>
            <h2 className="text-lg font-bold text-white">{t.compareCities}</h2>
          </div>
          <button onClick={onClose} className="p-2 text-slate-400 hover:text-white rounded-xl">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Inputs */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mt-5">
          <div>
            <label className="text-xs font-semibold text-slate-400 mb-1 block">{t.cityA}</label>
            <input
              type="text"
              value={cityA}
              onChange={(e) => setCityA(e.target.value)}
              className="w-full bg-slate-800 text-white text-sm rounded-xl px-4 py-2.5 border border-slate-700 focus:outline-none focus:border-indigo-500"
            />
          </div>
          <div>
            <label className="text-xs font-semibold text-slate-400 mb-1 block">{t.cityB}</label>
            <input
              type="text"
              value={cityB}
              onChange={(e) => setCityB(e.target.value)}
              className="w-full bg-slate-800 text-white text-sm rounded-xl px-4 py-2.5 border border-slate-700 focus:outline-none focus:border-indigo-500"
            />
          </div>
        </div>

        <button
          onClick={handleCompare}
          disabled={isLoading}
          className="mt-4 w-full py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-sm rounded-xl flex items-center justify-center gap-2 shadow-lg shadow-indigo-600/20 transition-all"
        >
          {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Scale className="w-4 h-4" />}
          <span>{t.compareButton}</span>
        </button>

        {error && (
          <p className="mt-4 text-xs text-rose-400 bg-rose-950/40 border border-rose-800 p-3 rounded-xl">
            {error}
          </p>
        )}

        {/* Comparison Result Cards */}
        {weatherA && weatherB && (
          <div className="grid grid-cols-2 gap-4 mt-6">
            {[weatherA, weatherB].map((item, idx) => (
              <div key={idx} className="bg-slate-800/80 p-4 rounded-2xl border border-slate-700/60">
                <h3 className="font-bold text-base text-white">{item.location_name}</h3>
                <p className="text-xs text-slate-400 capitalize">{item.weather_description}</p>
                <div className="text-3xl font-extrabold text-white my-2">
                  {Math.round(item.temperature)}°C
                </div>

                <div className="space-y-1.5 text-xs text-slate-300 pt-2 border-t border-slate-700/50">
                  <div className="flex justify-between">
                    <span>{t.feelsLike}:</span>
                    <span className="font-semibold">{Math.round(item.apparent_temperature)}°C</span>
                  </div>
                  <div className="flex justify-between">
                    <span>{t.humidity}:</span>
                    <span className="font-semibold">{item.relative_humidity}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span>{t.wind}:</span>
                    <span className="font-semibold">{item.wind_speed} km/h</span>
                  </div>
                  <div className="flex justify-between">
                    <span>{t.precipitation}:</span>
                    <span className="font-semibold">{item.precipitation} mm</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

      </div>
    </div>
  );
}
