import React, { useState } from 'react';
import { Zap } from 'lucide-react';
import { getThemeColors } from '../components/CommonUI';

const SettingsView = ({ userSettings, onUpdate, theme, analytics }) => {
  const [neuralNameInput, setNeuralNameInput] = useState(userSettings?.neural_name || analytics?.neural_name || 'Archivist');
  const [groqKeyInput, setGroqKeyInput] = useState(userSettings?.groq_api_key || '');
  const colors = getThemeColors(theme);
  return (
    <div className="p-6 max-w-2xl mx-auto space-y-8 animate-in slide-in-from-bottom-4 duration-500">
      <h2 className={`text-2xl font-light ${colors.textMain}`}>System Configuration</h2>
      <div className={`p-6 rounded-2xl border shadow-sm space-y-6 ${colors.panel} ${colors.panelBorder}`}>
        
        <div className="space-y-4">
          <h3 className="text-xs font-bold text-amber-600 uppercase tracking-widest">Performance & Speed</h3>
          <div className={`flex items-center justify-between p-5 rounded-xl border transition-all duration-500 shadow-sm ${userSettings?.turbo_mode ? 'bg-amber-500/10 border-amber-500/30' : 'bg-stone-50 border-stone-100'}`}>
            <div>
              <div className={`text-sm font-black italic uppercase tracking-tight flex items-center ${userSettings?.turbo_mode ? 'text-amber-600' : 'text-stone-800'}`}>
                <Zap className={`w-4 h-4 mr-2 ${userSettings?.turbo_mode ? 'text-amber-500 fill-amber-500' : 'text-stone-400'}`}/> 
                Neural Turbo Ignition
              </div>
              <div className="text-[10px] text-stone-500 font-bold uppercase tracking-tighter">Sub-second synthesis via Groq Cloud.</div>
            </div>
            <button 
              onClick={() => onUpdate({ turbo_mode: !userSettings?.turbo_mode })} 
              className={`px-4 py-2 rounded-lg font-black uppercase tracking-widest text-[10px] transition-all duration-300 ${userSettings?.turbo_mode ? 'bg-amber-500 text-white shadow-lg shadow-amber-500/40' : 'bg-black text-amber-500 hover:bg-stone-900'}`}
            >
              {userSettings?.turbo_mode ? 'Engaged' : 'Ignite'}
            </button>
          </div>
          <div className="space-y-2">
            <label className="text-[10px] font-semibold text-stone-400 uppercase">Groq API Key</label>
            <input type="password" value={groqKeyInput} onChange={(e) => setGroqKeyInput(e.target.value)} className={`w-full border rounded-lg p-3 focus:ring-2 focus:ring-amber-500/20 outline-none transition-all ${colors.input}`} placeholder="gsk_..." />
          </div>
        </div>

        <div className="flex items-center justify-between p-4 bg-stone-50 rounded-xl border border-stone-100 shadow-sm">
          <div>
            <div className="text-sm text-stone-800 font-medium">Voice Verification</div>
            <div className="text-[10px] text-stone-500">Enable biometric vocal lock.</div>
          </div>
          <button onClick={() => onUpdate({ voice_verification_enabled: !userSettings?.voice_verification_enabled })} className={`w-12 h-6 rounded-full transition-all relative ${userSettings?.voice_verification_enabled ? 'bg-amber-500' : 'bg-stone-300'}`}>
            <div className={`absolute top-1 w-4 h-4 bg-white rounded-full shadow-sm transition-all ${userSettings?.voice_verification_enabled ? 'left-7' : 'left-1'}`}></div>
          </button>
        </div>
        <button onClick={() => onUpdate({ neural_name: neuralNameInput, groq_api_key: groqKeyInput })} className="w-full py-4 bg-amber-500 text-white font-black uppercase tracking-widest rounded-xl hover:bg-amber-600 transition-all shadow-lg shadow-amber-500/20 active:scale-95">Save Neural Identity</button>
      </div>
    </div>
  );
};

export default SettingsView;
