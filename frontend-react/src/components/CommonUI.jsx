import React from 'react';
import { X, Sparkles, Activity } from 'lucide-react';

export const getThemeColors = (theme) => {
  if (theme === 'dark') return {
    bg: 'bg-slate-950',
    panel: 'bg-slate-900/60',
    panelBorder: 'border-slate-800/50',
    textMain: 'text-slate-200',
    textMuted: 'text-slate-400',
    sidebar: 'bg-slate-950/80 border-slate-800',
    header: 'bg-slate-950/80 border-slate-800',
    input: 'bg-slate-900 border-slate-700 text-slate-200',
    inputBg: 'bg-slate-900'
  };
  return {
    bg: 'bg-[#f8f5f0]',
    panel: 'bg-white/80',
    panelBorder: 'border-stone-200',
    textMain: 'text-stone-900',
    textMuted: 'text-stone-500',
    sidebar: 'bg-[#efe9e1]/90 border-stone-200',
    header: 'bg-[#f8f5f0]/90 border-stone-200',
    input: 'bg-[#fcfaf7] border-stone-200 text-stone-900',
    inputBg: 'bg-[#fcfaf7]'
  };
};

export const Toast = ({ message, type, onClose }) => {
  const isSerendipity = type === 'serendipity';
  return (
    <div className={`pointer-events-auto flex w-full rounded-xl shadow-2xl ring-1 ring-black ring-opacity-5 animate-in slide-in-from-top-8 fade-in duration-700 ${isSerendipity ? 'bg-gradient-to-r from-amber-900/90 to-slate-900 border border-amber-500/50 shadow-[0_0_30px_rgba(251,191,36,0.25)] backdrop-blur-md' : 'bg-slate-800 border border-slate-700'}`}>
      <div className="flex-1 p-4">
        <div className="flex items-start">
          <div className="flex-shrink-0 pt-0.5">
            {isSerendipity ? <Sparkles className="h-5 w-5 text-amber-400 animate-pulse" /> : <Activity className="h-5 w-5 text-blue-400" />}
          </div>
          <div className="ml-3 flex-1">
            <p className={`text-sm font-medium ${isSerendipity ? 'text-amber-200' : 'text-slate-200'}`}>
              {isSerendipity ? 'Serendipity Realization' : 'System Notice'}
            </p>
            <p className="mt-1 text-sm text-slate-400">{message}</p>
          </div>
        </div>
      </div>
      <div className="flex border-l border-slate-700/50">
        <button onClick={onClose} className="p-4 text-slate-400 hover:text-slate-200 transition-colors"><X className="h-4 w-4" /></button>
      </div>
    </div>
  );
};
