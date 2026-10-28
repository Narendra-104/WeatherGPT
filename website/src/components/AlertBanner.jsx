import React from 'react';
import { AlertTriangle, CheckCircle2, ShieldAlert } from 'lucide-react';
import { translations } from '../i18n/translations';

export default function AlertBanner({ alerts, language }) {
  const t = translations[language] || translations.en;

  if (!alerts || alerts.length === 0) {
    return (
      <div className="bg-emerald-950/30 border border-emerald-800/40 rounded-2xl p-4 flex items-center gap-3 text-emerald-300">
        <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0" />
        <p className="text-xs sm:text-sm font-medium">{t.noAlerts}</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {alerts.map((alert, idx) => (
        <div
          key={idx}
          className="bg-amber-950/40 border border-amber-600/50 rounded-2xl p-4.5 text-amber-200 shadow-lg relative overflow-hidden"
        >
          <div className="flex items-start gap-3.5">
            <div className="p-2 bg-amber-500/20 rounded-xl text-amber-400 shrink-0 mt-0.5">
              <ShieldAlert className="w-5 h-5 animate-pulse" />
            </div>
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-1">
                <span className="text-xs uppercase font-extrabold px-2 py-0.5 rounded-md bg-amber-500/30 text-amber-300 border border-amber-500/40">
                  {alert.severity}
                </span>
                <span className="text-xs text-amber-300/80">• {alert.source}</span>
              </div>
              <h3 className="text-base font-bold text-white tracking-tight">
                {alert.title}
              </h3>
              <p className="text-xs text-amber-200/90 mt-1 leading-relaxed">
                {alert.description}
              </p>

              {alert.instruction && (
                <div className="mt-2.5 p-2.5 bg-amber-900/40 rounded-xl border border-amber-700/50 text-xs text-amber-100 flex items-start gap-2">
                  <span className="font-bold shrink-0">{t.safetyInstruction}:</span>
                  <span>{alert.instruction}</span>
                </div>
              )}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
