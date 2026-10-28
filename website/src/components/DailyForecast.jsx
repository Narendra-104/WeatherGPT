import React from 'react';
import { Calendar, CloudRain, Sun, Cloud } from 'lucide-react';
import { translations } from '../i18n/translations';

export default function DailyForecast({ daily, language }) {
  const t = translations[language] || translations.en;

  if (!daily || daily.length === 0) return null;

  const formatDate = (dateStr) => {
    try {
      const d = new Date(dateStr);
      return d.toLocaleDateString(language === 'hi' ? 'hi-IN' : language === 'mr' ? 'mr-IN' : 'en-US', {
        weekday: 'short',
        month: 'short',
        day: 'numeric',
      });
    } catch {
      return dateStr;
    }
  };

  const getIcon = (code) => {
    if ([51, 53, 55, 61, 63, 65, 80, 81, 82].includes(code) || (code >= 500 && code < 600)) {
      return <CloudRain className="w-5 h-5 text-sky-400" />;
    }
    if (code === 0 || code === 800) {
      return <Sun className="w-5 h-5 text-amber-400" />;
    }
    return <Cloud className="w-5 h-5 text-slate-300" />;
  };

  return (
    <div className="bg-slate-800/60 rounded-3xl p-6 border border-slate-700/80 backdrop-blur-sm">
      <div className="flex items-center gap-2 mb-4 text-slate-200">
        <Calendar className="w-4 h-4 text-indigo-400" />
        <h2 className="text-base font-bold tracking-tight">{t.sevenDayForecast}</h2>
      </div>

      <div className="divide-y divide-slate-700/50">
        {daily.map((item, idx) => (
          <div
            key={idx}
            className="py-3.5 first:pt-0 last:pb-0 flex items-center justify-between gap-4 text-sm hover:bg-slate-700/20 px-2 rounded-xl transition-colors"
          >
            {/* Day and Date */}
            <div className="w-32 shrink-0">
              <p className="font-semibold text-slate-200">
                {idx === 0 ? t.today : formatDate(item.date)}
              </p>
              <p className="text-xs text-slate-400 capitalize truncate">
                {item.weather_description}
              </p>
            </div>

            {/* Icon & Rain Probability */}
            <div className="flex items-center gap-2 shrink-0 w-20">
              {getIcon(item.weather_code)}
              {item.precipitation_probability_max !== null && item.precipitation_probability_max > 0 ? (
                <span className="text-xs text-sky-400 font-medium">
                  {Math.round(item.precipitation_probability_max)}%
                </span>
              ) : (
                <span className="text-xs text-slate-500">0%</span>
              )}
            </div>

            {/* Min & Max Temp Bar */}
            <div className="flex items-center gap-3 flex-1 justify-end max-w-xs">
              <span className="text-xs font-semibold text-slate-400 w-8 text-right">
                {Math.round(item.temperature_min)}°
              </span>
              <div className="h-1.5 flex-1 bg-slate-700 rounded-full overflow-hidden relative">
                <div 
                  className="h-full bg-gradient-to-r from-sky-400 to-amber-400 rounded-full"
                  style={{ width: '100%' }}
                />
              </div>
              <span className="text-xs font-bold text-white w-8 text-right">
                {Math.round(item.temperature_max)}°
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
