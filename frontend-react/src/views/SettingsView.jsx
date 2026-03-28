import React, { useState } from 'react';
import { Zap, Command, Mic, Shield, Save } from 'lucide-react';
import { getThemeColors } from '../components/CommonUI';

const SettingsView = ({ userSettings, onUpdate, theme, analytics }) => {
  const [neuralNameInput, setNeuralNameInput] = useState(userSettings?.neural_name || analytics?.neural_name || 'Archivist');
  const [groqKeyInput, setGroqKeyInput] = useState(userSettings?.groq_api_key || '');
  const colors = getThemeColors(theme);

  const handleSave = () => {
    onUpdate({ 
      neural_name: neuralNameInput, 
      groq_api_key: groqKeyInput 
    });
  };

  return (
    <div className="p-6 sm:p-10 max-w-3xl mx-auto space-y-10 animate-in slide-in-from-bottom-4 duration-700">
      <div className="flex justify-between items-end">
        <div>
          <h2 className={`text-3xl font-bold tracking-tight mb-2 ${colors.textMain}`}>System Configuration</h2>
          <p className="text-stone-500 text-sm">Fine-tune your Neural Core's identity, performance, and security.</p>
        </div>
        <button 
          onClick={handleSave}
          className="flex items-center gap-2 px-6 py-3 bg-amber-500 text-slate-900 font-bold rounded-2xl hover:bg-amber-600 transition-all shadow-lg shadow-amber-500/20 active:scale-95"
        >
          <Save className="w-4 h-4" /> Save Changes
        </button>
      </div>

      <div className={`grid grid-cols-1 md:grid-cols-2 gap-8`}>
        <div className={`p-8 rounded-[32px] border shadow-sm space-y-8 ${colors.panel} ${colors.panelBorder}`}>
          <div>
            <h3 className="text-xs font-bold text-amber-600 uppercase tracking-[0.2em] mb-6 flex items-center">
              <Command className="w-4 h-4 mr-2" /> Neural Identity
            </h3>
            <div className="space-y-6">
              <div className="space-y-2">
                <label className="text-[10px] font-bold text-stone-400 uppercase tracking-widest">Primary Assistant Name</label>
                <input 
                  type="text" 
                  value={neuralNameInput} 
                  onChange={(e) => setNeuralNameInput(e.target.value)} 
                  className={`w-full border rounded-xl p-3.5 text-sm focus:ring-2 focus:ring-amber-500/20 outline-none transition-all ${colors.input}`} 
                  placeholder="e.g. Archivist"
                />
              </div>
              <div className="p-4 bg-stone-100/50 rounded-2xl border border-stone-200">
                <p className="text-[10px] text-stone-500 font-bold uppercase tracking-widest mb-1">Global Triggers</p>
                <p className="text-[10px] text-stone-400 leading-relaxed italic">The core always responds to: <span className="text-amber-600 font-mono">Akasha, Jarvis, {neuralNameInput}</span>.</p>
              </div>
            </div>
          </div>
        </div>

        <div className={`p-8 rounded-[32px] border shadow-sm space-y-8 ${colors.panel} ${colors.panelBorder}`}>
          <div>
            <h3 className="text-xs font-bold text-blue-500 uppercase tracking-[0.2em] mb-6 flex items-center">
              <Zap className="w-4 h-4 mr-2" /> Performance Engine
            </h3>
            <div className="space-y-6">
              <div className={`flex items-center justify-between p-5 rounded-2xl border transition-all duration-500 ${userSettings?.turbo_mode ? 'bg-amber-500/5 border-amber-500/20' : 'bg-stone-50 border-stone-100'}`}>
                <div>
                  <div className={`text-sm font-black uppercase tracking-tight flex items-center ${userSettings?.turbo_mode ? 'text-amber-600' : 'text-stone-800'}`}>
                    Neural Turbo
                  </div>
                  <div className="text-[9px] text-stone-500 font-medium uppercase mt-1">Sub-second synthesis via Groq.</div>
                </div>
                <button 
                  onClick={() => onUpdate({ turbo_mode: !userSettings?.turbo_mode })} 
                  className={`w-12 h-6 rounded-full transition-all relative ${userSettings?.turbo_mode ? 'bg-amber-500' : 'bg-stone-300'}`}
                >
                  <div className={`absolute top-1 w-4 h-4 bg-white rounded-full shadow-sm transition-all ${userSettings?.turbo_mode ? 'left-7' : 'left-1'}`}></div>
                </button>
              </div>
              <div className="space-y-2">
                <label className="text-[10px] font-bold text-stone-400 uppercase tracking-widest">Groq Cloud API Key</label>
                <input 
                  type="password" 
                  value={groqKeyInput} 
                  onChange={(e) => setGroqKeyInput(e.target.value)} 
                  className={`w-full border rounded-xl p-3.5 text-sm focus:ring-2 focus:ring-amber-500/20 outline-none transition-all ${colors.input}`} 
                  placeholder="gsk_..." 
                />
              </div>
            </div>
          </div>
        </div>

        <div className={`md:col-span-2 p-8 rounded-[32px] border shadow-sm ${colors.panel} ${colors.panelBorder} flex items-center justify-between`}>
          <div className="flex items-center gap-4">
            <div className="p-3 bg-green-500/10 rounded-2xl border border-green-500/20">
              <Shield className="w-6 h-6 text-green-600" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-stone-800">Biometric Vocal Lock</h3>
              <p className="text-xs text-stone-500">Only respond to your specific voice frequency.</p>
            </div>
          </div>
          <button onClick={() => onUpdate({ voice_verification_enabled: !userSettings?.voice_verification_enabled })} className={`w-14 h-7 rounded-full transition-all relative ${userSettings?.voice_verification_enabled ? 'bg-green-500' : 'bg-stone-300'}`}>
            <div className={`absolute top-1 w-5 h-5 bg-white rounded-full shadow-sm transition-all ${userSettings?.voice_verification_enabled ? 'left-8' : 'left-1'}`}></div>
          </button>
        </div>
      </div>
    </div>
  );
};

export default SettingsView;
