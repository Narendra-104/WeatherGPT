import React, { useState, useEffect, useRef } from 'react';
import { 
  CloudSun, Search, MapPin, Globe, Sparkles, Scale, Heart, Navigation, Loader2 
} from 'lucide-react';
import { api } from '../api/client';
import { translations } from '../i18n/translations';

export default function Header({ 
  currentCity, 
  onSelectCity, 
  onUseLocation, 
  language, 
  onLanguageChange,
  onOpenChat,
  onOpenCompare,
  isLoadingLocation 
}) {
  const [query, setQuery] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [showDropdown, setShowDropdown] = useState(false);
  const dropdownRef = useRef(null);

  const t = translations[language] || translations.en;

  useEffect(() => {
    if (!query || query.trim().length < 2) {
      setSuggestions([]);
      setShowDropdown(false);
      return;
    }

    const timer = setTimeout(async () => {
      try {
        setIsSearching(true);
        const results = await api.searchLocations(query, language, 5);
        setSuggestions(results);
        setShowDropdown(results.length > 0);
      } catch (err) {
        console.error('Search error:', err);
      } finally {
        setIsSearching(false);
      }
    }, 300);

    return () => clearTimeout(timer);
  }, [query, language]);

  // Click outside to close dropdown
  useEffect(() => {
    function handleClickOutside(event) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setShowDropdown(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSelect = (item) => {
    onSelectCity({
      name: item.name,
      latitude: item.latitude,
      longitude: item.longitude,
      country: item.country,
      admin1: item.admin1
    });
    setQuery('');
    setShowDropdown(false);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && query.trim()) {
      if (suggestions.length > 0) {
        handleSelect(suggestions[0]);
      } else {
        onSelectCity({ name: query.trim() });
        setQuery('');
        setShowDropdown(false);
      }
    }
  };

  return (
    <header className="sticky top-0 z-40 backdrop-blur-md bg-slate-900/80 border-b border-slate-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between gap-4">
        
        {/* Brand */}
        <div className="flex items-center gap-3 cursor-pointer shrink-0" onClick={() => onSelectCity({ name: 'Pune' })}>
          <div className="h-11 w-11 rounded-2xl bg-gradient-to-tr from-sky-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-sky-500/20 text-white">
            <CloudSun className="w-6 h-6 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xl font-extrabold tracking-tight bg-gradient-to-r from-sky-400 to-indigo-400 bg-clip-text text-transparent">
                WeatherGPT
              </span>
              <span className="text-[10px] font-bold px-1.5 py-0.5 rounded-full bg-sky-500/20 text-sky-400 border border-sky-500/30">
                SIH26068
              </span>
            </div>
            <p className="text-xs text-slate-400 hidden sm:block">
              {t.tagline}
            </p>
          </div>
        </div>

        {/* Search Bar */}
        <div className="relative flex-1 max-w-md" ref={dropdownRef}>
          <div className="relative">
            <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={t.searchPlaceholder}
              className="w-full bg-slate-800/80 hover:bg-slate-800 focus:bg-slate-800 text-sm rounded-xl pl-10 pr-10 py-2.5 border border-slate-700/80 focus:border-sky-500 focus:outline-none focus:ring-2 focus:ring-sky-500/20 transition-all text-slate-100 placeholder:text-slate-500"
            />
            {isSearching ? (
              <Loader2 className="absolute right-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-sky-400 animate-spin" />
            ) : (
              <button
                type="button"
                onClick={onUseLocation}
                title={t.useCurrentLocation}
                disabled={isLoadingLocation}
                className="absolute right-2.5 top-1/2 -translate-y-1/2 p-1 text-slate-400 hover:text-sky-400 rounded-lg hover:bg-slate-700/50 transition-colors"
              >
                {isLoadingLocation ? (
                  <Loader2 className="w-4 h-4 animate-spin text-sky-400" />
                ) : (
                  <Navigation className="w-4 h-4" />
                )}
              </button>
            )}
          </div>

          {/* Autocomplete Dropdown */}
          {showDropdown && suggestions.length > 0 && (
            <div className="absolute left-0 right-0 mt-2 bg-slate-800 border border-slate-700 rounded-xl shadow-2xl overflow-hidden z-50 divide-y divide-slate-700/50">
              {suggestions.map((item, idx) => (
                <button
                  key={idx}
                  onClick={() => handleSelect(item)}
                  className="w-full px-4 py-3 text-left hover:bg-slate-700/60 transition-colors flex items-center justify-between text-sm"
                >
                  <div className="flex items-center gap-2.5">
                    <MapPin className="w-4 h-4 text-sky-400 shrink-0" />
                    <span className="font-medium text-slate-200">{item.name}</span>
                    {item.admin1 && <span className="text-xs text-slate-400">({item.admin1})</span>}
                  </div>
                  {item.country && (
                    <span className="text-xs px-2 py-0.5 rounded bg-slate-700 text-slate-300">
                      {item.country}
                    </span>
                  )}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Actions & Language Selector */}
        <div className="flex items-center gap-2">
          {/* Compare Button */}
          <button
            onClick={onOpenCompare}
            className="hidden md:flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition-colors"
            title={t.compareCities}
          >
            <Scale className="w-4 h-4 text-indigo-400" />
            <span>{t.compareCities}</span>
          </button>

          {/* AI Assistant Button */}
          <button
            onClick={onOpenChat}
            className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-bold bg-gradient-to-r from-sky-500 to-indigo-600 hover:from-sky-400 hover:to-indigo-500 text-white shadow-md shadow-sky-500/20 transition-all hover:scale-105"
          >
            <Sparkles className="w-4 h-4" />
            <span className="hidden sm:inline">{t.askAI}</span>
          </button>

          {/* Language Switcher */}
          <div className="flex items-center bg-slate-800/90 rounded-xl p-1 border border-slate-700/80">
            <Globe className="w-3.5 h-3.5 text-slate-400 ml-1.5 mr-1" />
            {[
              { code: 'en', label: 'EN' },
              { code: 'hi', label: 'हिं' },
              { code: 'mr', label: 'मरा' },
            ].map((lang) => (
              <button
                key={lang.code}
                onClick={() => onLanguageChange(lang.code)}
                className={`px-2 py-1 text-xs rounded-lg font-semibold transition-all ${
                  language === lang.code
                    ? 'bg-sky-500 text-white shadow-sm'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                {lang.label}
              </button>
            ))}
          </div>
        </div>

      </div>
    </header>
  );
}
