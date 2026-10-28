import React, { useState, useEffect } from 'react';
import { 
  X, MapPin, Search, Navigation, Compass, Globe, Check, Loader2, Sparkles 
} from 'lucide-react';
import { api } from '../api/client';
import { translations } from '../i18n/translations';

const POPULAR_LOCATIONS = [
  {
    category: { en: "Maharashtra", hi: "महाराष्ट्र", mr: "महाराष्ट्र" },
    cities: [
      { name: "Pune", state: "Maharashtra", lat: 18.5204, lon: 73.8567 },
      { name: "Mumbai", state: "Maharashtra", lat: 19.0760, lon: 72.8777 },
      { name: "Nagpur", state: "Maharashtra", lat: 21.1458, lon: 79.0882 },
      { name: "Nashik", state: "Maharashtra", lat: 19.9975, lon: 73.7898 },
      { name: "Chhatrapati Sambhajinagar", state: "Maharashtra", lat: 19.8762, lon: 75.3433 },
      { name: "Kolhapur", state: "Maharashtra", lat: 16.7050, lon: 74.2433 },
      { name: "Solapur", state: "Maharashtra", lat: 17.6599, lon: 75.9064 },
      { name: "Amravati", state: "Maharashtra", lat: 20.9374, lon: 77.7796 },
    ]
  },
  {
    category: { en: "Major Metros", hi: "प्रमुख महानगर", mr: "प्रमुख शहरे" },
    cities: [
      { name: "New Delhi", state: "Delhi", lat: 28.6139, lon: 77.2090 },
      { name: "Bengaluru", state: "Karnataka", lat: 12.9716, lon: 77.5946 },
      { name: "Hyderabad", state: "Telangana", lat: 17.3850, lon: 78.4867 },
      { name: "Chennai", state: "Tamil Nadu", lat: 13.0827, lon: 80.2707 },
      { name: "Kolkata", state: "West Bengal", lat: 22.5726, lon: 88.3639 },
      { name: "Ahmedabad", state: "Gujarat", lat: 23.0225, lon: 72.5714 },
    ]
  },
  {
    category: { en: "North & Central", hi: "उत्तर एवं मध्य भारत", mr: "उत्तर व मध्य भारत" },
    cities: [
      { name: "Jaipur", state: "Rajasthan", lat: 26.9124, lon: 75.7873 },
      { name: "Lucknow", state: "Uttar Pradesh", lat: 26.8467, lon: 80.9462 },
      { name: "Chandigarh", state: "Punjab/Haryana", lat: 30.7333, lon: 76.7794 },
      { name: "Bhopal", state: "Madhya Pradesh", lat: 23.2599, lon: 77.4126 },
      { name: "Indore", state: "Madhya Pradesh", lat: 22.7196, lon: 75.8577 },
      { name: "Dehradun", state: "Uttarakhand", lat: 30.3165, lon: 78.0322 },
    ]
  },
  {
    category: { en: "South & East", hi: "दक्षिण एवं पूर्वी भारत", mr: "दक्षिण व पूर्व भारत" },
    cities: [
      { name: "Kochi", state: "Kerala", lat: 9.9312, lon: 76.2673 },
      { name: "Visakhapatnam", state: "Andhra Pradesh", lat: 17.6868, lon: 83.2185 },
      { name: "Bhubaneswar", state: "Odisha", lat: 20.2961, lon: 85.8245 },
      { name: "Guwahati", state: "Assam", lat: 26.1445, lon: 91.7362 },
      { name: "Patna", state: "Bihar", lat: 25.5941, lon: 85.1376 },
    ]
  }
];

export default function LocationModal({ isOpen, onClose, currentCity, onSelectCity, onUseGPS, language }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [activeTab, setActiveTab] = useState('popular'); // 'popular', 'search', 'custom'
  const [customLat, setCustomLat] = useState('');
  const [customLon, setCustomLon] = useState('');
  const [customName, setCustomName] = useState('');

  const t = translations[language] || translations.en;

  // Search autocomplete with debounce
  useEffect(() => {
    if (!searchTerm || searchTerm.trim().length < 2) {
      setSearchResults([]);
      setIsSearching(false);
      return;
    }

    setIsSearching(true);
    const timer = setTimeout(async () => {
      try {
        const results = await api.searchLocations(searchTerm, language, 6);
        setSearchResults(results);
      } catch (err) {
        console.error('Search failed:', err);
      } finally {
        setIsSearching(false);
      }
    }, 350);

    return () => clearTimeout(timer);
  }, [searchTerm, language]);

  if (!isOpen) return null;

  const handleSelect = (cityObj) => {
    onSelectCity({
      name: cityObj.name,
      latitude: cityObj.lat || cityObj.latitude,
      longitude: cityObj.lon || cityObj.longitude,
      country: cityObj.country,
      admin1: cityObj.admin1 || cityObj.state,
    });
    onClose();
  };

  const handleApplyCoordinates = (e) => {
    e.preventDefault();
    const lat = parseFloat(customLat);
    const lon = parseFloat(customLon);
    if (isNaN(lat) || isNaN(lon) || lat < -90 || lat > 90 || lon < -180 || lon > 180) {
      alert("Please enter valid latitude (-90 to 90) and longitude (-180 to 180).");
      return;
    }
    onSelectCity({
      name: customName.trim() || `${lat.toFixed(2)}°, ${lon.toFixed(2)}°`,
      latitude: lat,
      longitude: lon,
    });
    onClose();
  };

  const getCategoryTitle = (cat) => {
    return cat[language] || cat.en;
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-fadeIn">
      <div 
        className="bg-slate-900 border border-slate-700 rounded-3xl w-full max-w-2xl max-h-[90vh] flex flex-col shadow-2xl overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Modal Header */}
        <div className="px-6 py-5 border-b border-slate-800 flex items-center justify-between bg-slate-900/90">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-sky-500/10 border border-sky-500/30 flex items-center justify-center text-sky-400">
              <MapPin className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-white">
                {language === 'hi' ? 'स्थान चुनें' : language === 'mr' ? 'स्थान निवडा' : 'Select Location'}
              </h2>
              <p className="text-xs text-slate-400">
                {language === 'hi' ? 'सटीक मौसम देखने के लिए कोई शहर या जिला चुनें' : language === 'mr' ? 'थेट हवामान पाहण्यासाठी शहर किंवा जिल्हा निवडा' : 'Choose a city or enter coordinates for live weather'}
              </p>
            </div>
          </div>
          <button 
            onClick={onClose}
            className="p-2 text-slate-400 hover:text-white rounded-xl hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Search Bar & GPS Trigger */}
        <div className="p-6 border-b border-slate-800/80 space-y-3 bg-slate-900/50">
          <div className="relative">
            <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder={language === 'hi' ? 'शहर का नाम खोजें (उदा: पुणे, मुंबई, नासिक)...' : language === 'mr' ? 'शहर शोधा (उदा: पुणे, मुंबई, नाशिक)...' : 'Search any city or district name...'}
              className="w-full bg-slate-800/90 border border-slate-700/80 text-sm rounded-2xl pl-10 pr-10 py-3 text-slate-100 placeholder:text-slate-500 focus:outline-none focus:border-sky-500 focus:ring-2 focus:ring-sky-500/20 transition-all"
              autoFocus
            />
            {isSearching && (
              <Loader2 className="absolute right-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-sky-400 animate-spin" />
            )}
            {searchTerm && !isSearching && (
              <button
                onClick={() => setSearchTerm('')}
                className="absolute right-3.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-white"
              >
                <X className="w-4 h-4" />
              </button>
            )}
          </div>

          <div className="flex items-center justify-between gap-3 pt-1">
            <button
              onClick={() => {
                onUseGPS();
                onClose();
              }}
              className="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-sky-500/20 to-indigo-500/20 hover:from-sky-500/30 hover:to-indigo-500/30 border border-sky-500/40 text-sky-300 text-xs font-bold transition-all"
            >
              <Navigation className="w-4 h-4 text-sky-400 animate-pulse" />
              <span>{t.useCurrentLocation}</span>
            </button>

            <div className="flex rounded-xl bg-slate-800/80 p-1 border border-slate-700/80 text-xs font-medium">
              <button
                onClick={() => setActiveTab('popular')}
                className={`px-3 py-1.5 rounded-lg transition-all ${activeTab === 'popular' ? 'bg-sky-500 text-white shadow' : 'text-slate-400 hover:text-slate-200'}`}
              >
                {language === 'hi' ? 'लोकप्रिय शहर' : language === 'mr' ? 'लोकप्रिय शहरे' : 'Popular'}
              </button>
              <button
                onClick={() => setActiveTab('custom')}
                className={`px-3 py-1.5 rounded-lg transition-all ${activeTab === 'custom' ? 'bg-sky-500 text-white shadow' : 'text-slate-400 hover:text-slate-200'}`}
              >
                {language === 'hi' ? 'निर्देशांक (GPS)' : language === 'mr' ? 'अक्षांश/रेखांश' : 'Coordinates'}
              </button>
            </div>
          </div>
        </div>

        {/* Modal Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {/* Autocomplete Search Results */}
          {searchTerm.trim().length >= 2 ? (
            <div className="space-y-2">
              <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                {language === 'hi' ? 'खोज परिणाम' : language === 'mr' ? 'शोध निकाल' : 'Search Results'} ({searchResults.length})
              </h3>
              {isSearching ? (
                <div className="py-8 text-center text-sm text-slate-400 flex items-center justify-center gap-2">
                  <Loader2 className="w-5 h-5 animate-spin text-sky-400" />
                  <span>Searching locations...</span>
                </div>
              ) : searchResults.length > 0 ? (
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  {searchResults.map((loc, idx) => (
                    <button
                      key={idx}
                      onClick={() => handleSelect(loc)}
                      className="p-3 text-left bg-slate-800/60 hover:bg-slate-800 border border-slate-700/60 hover:border-sky-500/50 rounded-2xl transition-all flex items-center justify-between group"
                    >
                      <div className="flex items-center gap-2.5">
                        <MapPin className="w-4 h-4 text-sky-400 group-hover:scale-110 transition-transform" />
                        <div>
                          <div className="text-sm font-semibold text-slate-200">{loc.name}</div>
                          <div className="text-xs text-slate-400">{loc.admin1 ? `${loc.admin1}, ` : ''}{loc.country}</div>
                        </div>
                      </div>
                      <span className="text-[11px] text-slate-500 font-mono">
                        {loc.latitude.toFixed(2)}°, {loc.longitude.toFixed(2)}°
                      </span>
                    </button>
                  ))}
                </div>
              ) : (
                <div className="py-8 text-center text-sm text-slate-400">
                  No matching cities found. Try searching for a different district or spelling.
                </div>
              )}
            </div>
          ) : activeTab === 'custom' ? (
            /* Custom Coordinates Form */
            <form onSubmit={handleApplyCoordinates} className="space-y-4 max-w-md mx-auto py-2">
              <div className="p-4 rounded-2xl bg-sky-950/30 border border-sky-800/40 text-xs text-sky-200 flex items-center gap-2.5">
                <Compass className="w-5 h-5 text-sky-400 shrink-0" />
                <span>Enter exact geographic decimal coordinates for custom micro-climate weather data.</span>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1.5">Location Name (Optional)</label>
                <input
                  type="text"
                  value={customName}
                  onChange={(e) => setCustomName(e.target.value)}
                  placeholder="e.g. My Farm / Home Town"
                  className="w-full bg-slate-800/90 border border-slate-700 rounded-xl px-3.5 py-2.5 text-sm text-slate-100 placeholder:text-slate-500 focus:outline-none focus:border-sky-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1.5">Latitude (-90 to 90)</label>
                  <input
                    type="number"
                    step="any"
                    required
                    value={customLat}
                    onChange={(e) => setCustomLat(e.target.value)}
                    placeholder="18.5204"
                    className="w-full bg-slate-800/90 border border-slate-700 rounded-xl px-3.5 py-2.5 text-sm text-slate-100 placeholder:text-slate-500 focus:outline-none focus:border-sky-500 font-mono"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1.5">Longitude (-180 to 180)</label>
                  <input
                    type="number"
                    step="any"
                    required
                    value={customLon}
                    onChange={(e) => setCustomLon(e.target.value)}
                    placeholder="73.8567"
                    className="w-full bg-slate-800/90 border border-slate-700 rounded-xl px-3.5 py-2.5 text-sm text-slate-100 placeholder:text-slate-500 focus:outline-none focus:border-sky-500 font-mono"
                  />
                </div>
              </div>

              <button
                type="submit"
                className="w-full py-3 rounded-xl bg-sky-500 hover:bg-sky-400 text-white font-bold text-sm shadow-lg shadow-sky-500/20 transition-all mt-4"
              >
                Apply Coordinates & View Weather
              </button>
            </form>
          ) : (
            /* Popular Categorized Cities Grid */
            <div className="space-y-6">
              {POPULAR_LOCATIONS.map((group, gIdx) => (
                <div key={gIdx} className="space-y-2.5">
                  <div className="flex items-center gap-2">
                    <span className="w-1.5 h-3.5 rounded-full bg-sky-400" />
                    <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider">
                      {getCategoryTitle(group.category)}
                    </h3>
                  </div>

                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                    {group.cities.map((city, cIdx) => {
                      const isCurrent = currentCity?.name?.toLowerCase() === city.name.toLowerCase();
                      return (
                        <button
                          key={cIdx}
                          onClick={() => handleSelect(city)}
                          className={`px-3.5 py-2.5 rounded-xl text-left border transition-all flex items-center justify-between ${
                            isCurrent
                              ? 'bg-sky-500/20 border-sky-500/60 text-sky-300 shadow-sm'
                              : 'bg-slate-800/60 hover:bg-slate-800 border-slate-700/60 hover:border-slate-600 text-slate-200'
                          }`}
                        >
                          <div>
                            <div className="text-xs font-semibold">{city.name}</div>
                            <div className="text-[10px] text-slate-400">{city.state}</div>
                          </div>
                          {isCurrent && <Check className="w-3.5 h-3.5 text-sky-400 shrink-0" />}
                        </button>
                      );
                    })}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
