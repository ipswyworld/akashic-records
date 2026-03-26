import React, { useState, useEffect } from 'react';
import { BrainCircuit } from 'lucide-react';
import { getThemeColors } from '../components/CommonUI';
import { fetchPsychologyProfile } from '../api';

const EgoView = ({ theme }) => {
  const [profile, setProfile] = useState(null);
  const colors = getThemeColors(theme);
  useEffect(() => { fetchPsychologyProfile().then(setProfile).catch(console.error); }, []);
  if (!profile || profile.status === "NO_PROFILE") return <div className="p-12 text-center text-stone-400 font-light italic">The Ego is currently being formed. Add more thoughts to crystallize your digital reflection.</div>;
  return (
    <div className="p-4 sm:p-6 w-full max-w-5xl mx-auto animate-in fade-in duration-500 space-y-6">
      <div className="mb-6">
        <h2 className={`text-xl sm:text-2xl font-light flex items-center ${colors.textMain}`}>
          <BrainCircuit className="w-5 h-5 sm:w-6 sm:h-6 mr-3 text-purple-500" /> The Digital Ego
        </h2>
        <p className="text-stone-500 text-sm mt-1">A learned psychological mirror based on your cognitive history.</p>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className={`p-6 rounded-2xl border shadow-sm ${colors.panel} ${colors.panelBorder}`}>
          <h3 className="text-xs font-semibold text-stone-400 uppercase tracking-wider mb-6">OCEAN Personality Model</h3>
          <div className="space-y-5">
            {Object.entries(profile.ocean_traits).map(([trait, score]) => (
              <div key={trait}>
                <div className="flex justify-between text-xs text-stone-600 mb-1.5 capitalize font-medium">
                  <span>{trait}</span>
                  <span>{Math.round(score * 100)}%</span>
                </div>
                <div className="w-full bg-stone-100 rounded-full h-1.5 shadow-inner">
                  <div className="bg-gradient-to-r from-purple-400 to-purple-600 h-1.5 rounded-full transition-all duration-1000" style={{ width: `${score * 100}%` }}></div>
                </div>
              </div>
            ))}
          </div>
        </div>
        <div className={`p-6 rounded-2xl border shadow-sm ${colors.panel} ${colors.panelBorder}`}>
          <h3 className="text-xs font-semibold text-stone-400 uppercase tracking-wider mb-4">Cognitive Tracking</h3>
          {Object.entries(profile.cognitive_distortions || {}).length === 0 ? (
            <p className="text-sm text-stone-400 italic">Thinking is clear. No distortions detected.</p>
          ) : (
            <ul className="space-y-3">
              {Object.entries(profile.cognitive_distortions).map(([dist, count]) => (
                <li key={dist} className="flex justify-between items-center bg-stone-50 p-3 rounded-lg border border-stone-100 shadow-sm">
                  <span className="text-sm text-stone-700 capitalize">{dist}</span>
                  <span className="text-[10px] font-mono text-amber-600 bg-amber-50 px-2 py-1 rounded border border-amber-100">Found {count}x</span>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
};

export default EgoView;
