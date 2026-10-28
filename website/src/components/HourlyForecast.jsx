import React from 'react';
import { Clock, CloudRain, Sun, Cloud } from 'lucide-react';
import { translations } from '../i18n/translations';

export default function HourlyForecast({ hourly, language }) {
  const t = translations[language] || translations.en;

  if (!hourly || hourly.length === 0) return null;

  const formatHour = (timeStr) => {
    try {
      const d = new Date(timeStr);
      return d.toLocaleTimeString([], { hour: 'numeric', hour12: true });
    } catch {
      return timeStr.split('T')[1] || timeStr;
    }
  };

  const getIcon = (code) => {
    if ([51, 53, 55, 61, 63, 65, 80, 81, 82].includes(code) || (code >= 500 && code < 600)) {
      return <CloudRain className="w-6 h-6 text-sky-400" />;
    }
    if (code === 0 || code === 800) {
      return <Sun className="w-6 h-6 text-amber-400" />;
    }
    return <Cloud className="w-6 h-6 text-slate-300" />;
  };

  return (
    <div className="bg-slate-800/60 rounded-3xl p-6 border border-slate-700/80 backdrop-blur-sm">
      <div className="flex items-center gap-2 mb-4 text-slate-200">
        <Clock className="w-4 h-4 text-sky-400" />
        <h2 className="text-base font-bold tracking-tight">{t.hourlyForecast}</h2>
      </div>

      <div className="flex gap-4 overflow-x-auto pb-3 pt-1 scrollbar-thin">
        {hourly.slice(0, 24).map((item, idx) => (
          <div
            key={idx}
            className="flex flex-col items-center justify-between min-w-[85px] p-3 rounded-2xl bg-slate-800/80 hover:bg-slate-750 border border-slate-700/60 transition-all hover:scale-105 shrink-0"
          >
            <span className="text-xs font-medium text-slate-400 mb-2">
              {idx === 0 ? t.today : formatHour(item.time)}
            </span>

            <div className="my-1">{getIcon(item.weather_code)}</div>

            <span className="text-base font-extrabold text-white mt-2">
              {Math.round(item.temperature)}°
            </span>

            {item.precipitation_probability !== null && item.precipitation_probability > 0 ? (
              <span className="text-[11px] font-semibold text-sky-400 mt-1 flex items-center gap-0.5">
                <CloudRain className="w-2.5 h-2.5" />
                {Math.round(item.precipitation_probability)}%
              </span>
            ) : (
              <span className="text-[11px] text-slate-500 mt-1">--</span>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
