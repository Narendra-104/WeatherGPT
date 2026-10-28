import React from 'react';
import { MapPin, Star } from 'lucide-react';
import { translations } from '../i18n/translations';

const DEFAULT_CITIES = [
  { name: 'Pune', lat: 18.5204, lon: 73.8567 },
  { name: 'Mumbai', lat: 19.0760, lon: 72.8777 },
  { name: 'Delhi', lat: 28.6139, lon: 77.2090 },
  { name: 'Bengaluru', lat: 12.9716, lon: 77.5946 },
  { name: 'Nagpur', lat: 21.1458, lon: 79.0882 },
  { name: 'Nashik', lat: 19.9975, lon: 73.7898 },
];

export default function SavedLocations({ currentCity, onSelectCity, onOpenLocationModal, language }) {
  const t = translations[language] || translations.en;

  return (
    <div className="flex items-center gap-2 overflow-x-auto py-2 scrollbar-none">
      <div className="flex items-center gap-1.5 text-xs text-slate-400 font-semibold uppercase tracking-wider shrink-0 mr-1">
        <Star className="w-3.5 h-3.5 text-amber-400 fill-amber-400" />
        <span>{t.savedCities}:</span>
      </div>

      {DEFAULT_CITIES.map((c) => {
        const isActive = currentCity?.name?.toLowerCase() === c.name.toLowerCase();
        return (
          <button
            key={c.name}
            onClick={() => onSelectCity({ name: c.name, latitude: c.lat, longitude: c.lon })}
            className={`px-3 py-1 rounded-full text-xs font-semibold whitespace-nowrap transition-all border ${
              isActive
                ? 'bg-sky-500/20 text-sky-300 border-sky-500/50 shadow-sm'
                : 'bg-slate-800/80 hover:bg-slate-700/80 text-slate-300 border-slate-700'
            }`}
          >
            {c.name}
          </button>
        );
      })}

      <button
        onClick={onOpenLocationModal}
        className="px-3 py-1 rounded-full text-xs font-bold whitespace-nowrap bg-sky-500/10 hover:bg-sky-500/20 text-sky-400 border border-sky-500/30 flex items-center gap-1 transition-all shrink-0"
      >
        <MapPin className="w-3 h-3" />
        <span>{language === 'hi' ? '+ अन्य स्थान' : language === 'mr' ? '+ इतर शहरे' : '+ More Locations'}</span>
      </button>
    </div>
  );
}
