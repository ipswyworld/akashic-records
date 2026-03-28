import React, { useState, useEffect } from 'react';
import { 
  BrainCircuit, Sparkles, Target, Compass, 
  BookOpen, AlertCircle, RefreshCcw, ShieldCheck,
  ChevronRight, Heart, Activity
} from 'lucide-react';
import { getThemeColors } from '../components/CommonUI';
import { fetchPsychologyProfile } from '../api';

const EgoView = ({ theme }) => {
  const [profile, setProfile] = useState(null);
  const [activeTab, setActiveTab] = useState('ocean');
  const colors = getThemeColors(theme);

  useEffect(() => { 
    fetchPsychologyProfile().then(setProfile).catch(console.error); 
  }, []);

  if (!profile || profile.status === "NO_PROFILE") {
    return (
      <div className="flex-1 flex flex-col items-center justify-center p-12 text-center">
        <div className="w-20 h-24 bg-purple-500/10 rounded-full blur-3xl absolute animate-pulse"></div>
        <BrainCircuit className="w-12 h-12 text-stone-300 mb-6 relative z-10" />
        <p className="text-stone-400 font-light italic max-w-xs relative z-10">
          The Ego is currently being formed. Add more thoughts to crystallize your digital reflection.
        </p>
      </div>
    );
  }

  const traits = [
    { key: 'openness', label: 'Openness', desc: 'Curiosity & abstract thinking', color: 'from-blue-400 to-indigo-500' },
    { key: 'conscientiousness', label: 'Conscientiousness', desc: 'Structure & discipline', color: 'from-emerald-400 to-teal-500' },
    { key: 'extraversion', label: 'Extraversion', desc: 'Social energy & engagement', color: 'from-amber-400 to-orange-500' },
    { key: 'agreeableness', label: 'Agreeableness', desc: 'Empathy & cooperation', color: 'from-pink-400 to-rose-500' },
    { key: 'neuroticism', label: 'Neuroticism', desc: 'Emotional sensitivity', color: 'from-purple-400 to-fuchsia-500' },
  ];

  return (
    <div className="p-6 sm:p-10 w-full max-w-7xl mx-auto animate-in fade-in slide-in-from-bottom-4 duration-700 space-y-10">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-6">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-purple-500 rounded-xl shadow-lg shadow-purple-500/20 text-white">
              <BrainCircuit className="w-6 h-6" />
            </div>
            <h1 className={`text-3xl font-bold tracking-tight ${colors.textMain}`}>Digital Ego</h1>
          </div>
          <p className="text-stone-500 text-sm max-w-md">Your psychological mirror, synthesized from every artifact and interaction.</p>
        </div>
        
        <div className="flex bg-stone-100 p-1 rounded-2xl border border-stone-200 shadow-inner">
          <button onClick={() => setActiveTab('ocean')} className={`px-4 py-2 rounded-xl text-xs font-bold transition-all ${activeTab === 'ocean' ? 'bg-white text-purple-600 shadow-sm' : 'text-stone-500 hover:text-stone-700'}`}>Personality</button>
          <button onClick={() => setActiveTab('cbt')} className={`px-4 py-2 rounded-xl text-xs font-bold transition-all ${activeTab === 'cbt' ? 'bg-white text-purple-600 shadow-sm' : 'text-stone-500 hover:text-stone-700'}`}>Reframing</button>
          <button onClick={() => setActiveTab('narrative')} className={`px-4 py-2 rounded-xl text-xs font-bold transition-all ${activeTab === 'narrative' ? 'bg-white text-purple-600 shadow-sm' : 'text-stone-500 hover:text-stone-700'}`}>Narrative</button>
        </div>
      </div>

      {activeTab === 'ocean' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* OCEAN Model */}
          <div className={`lg:col-span-2 p-8 rounded-[32px] border shadow-sm relative overflow-hidden ${colors.panel} ${colors.panelBorder}`}>
            <div className="absolute top-0 right-0 p-8 opacity-5">
              <Activity className="w-48 h-48 text-purple-500" />
            </div>
            <h3 className="text-sm font-bold text-stone-400 uppercase tracking-widest mb-8 flex items-center">
              <Sparkles className="w-4 h-4 mr-2 text-amber-500" /> Neural Personality Map
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-12 gap-y-10">
              {traits.map((t) => (
                <div key={t.key} className="space-y-3">
                  <div className="flex justify-between items-end">
                    <div>
                      <span className="text-sm font-bold text-stone-700 block">{t.label}</span>
                      <span className="text-[10px] text-stone-400 font-medium">{t.desc}</span>
                    </div>
                    <span className="text-lg font-mono font-bold text-stone-800">{Math.round(profile.ocean_traits[t.key] * 100)}%</span>
                  </div>
                  <div className="w-full bg-stone-100/50 rounded-full h-2.5 overflow-hidden shadow-inner border border-stone-100">
                    <div className={`bg-gradient-to-r ${t.color} h-full rounded-full transition-all duration-[1.5s] ease-out shadow-lg`} style={{ width: `${profile.ocean_traits[t.key] * 100}%` }}></div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Core Values & Goals */}
          <div className="space-y-8">
            <div className={`p-8 rounded-[32px] border shadow-sm ${colors.panel} ${colors.panelBorder}`}>
              <h3 className="text-sm font-bold text-stone-400 uppercase tracking-widest mb-6 flex items-center">
                <Heart className="w-4 h-4 mr-2 text-rose-500" /> Core Values
              </h3>
              <div className="flex flex-wrap gap-2">
                {(profile.core_values || ["Freedom", "Knowledge", "Agency"]).map((v, i) => (
                  <span key={i} className="px-4 py-2 bg-rose-500/5 text-rose-600 rounded-2xl text-xs font-bold border border-rose-500/10 transition-all hover:scale-105">{v}</span>
                ))}
              </div>
            </div>

            <div className={`p-8 rounded-[32px] border shadow-sm ${colors.panel} ${colors.panelBorder}`}>
              <h3 className="text-sm font-bold text-stone-400 uppercase tracking-widest mb-6 flex items-center">
                <Target className="w-4 h-4 mr-2 text-blue-500" /> Synthesis Goals
              </h3>
              <div className="space-y-3">
                {(profile.current_goals || ["Synthesize local-first architectures", "Expand digital sovereignty"]).map((g, i) => (
                  <div key={i} className="flex items-start gap-3 p-3 rounded-2xl bg-blue-500/5 border border-blue-500/10 group transition-all hover:bg-blue-500/10">
                    <div className="w-1.5 h-1.5 rounded-full bg-blue-500 mt-1.5 group-hover:scale-125 transition-all"></div>
                    <span className="text-xs font-medium text-stone-600">{g}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'cbt' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div className={`p-8 rounded-[32px] border shadow-sm ${colors.panel} ${colors.panelBorder}`}>
            <h3 className="text-sm font-bold text-stone-400 uppercase tracking-widest mb-6 flex items-center">
              <AlertCircle className="w-4 h-4 mr-2 text-amber-500" /> Identified Distortions
            </h3>
            {Object.entries(profile.cognitive_distortions || {}).length === 0 ? (
              <div className="flex flex-col items-center justify-center py-10">
                <ShieldCheck className="w-10 h-10 text-green-500/20 mb-4" />
                <p className="text-sm text-stone-400 italic">Thinking is currently clear and balanced.</p>
              </div>
            ) : (
              <div className="space-y-4">
                {Object.entries(profile.cognitive_distortions).map(([dist, count]) => (
                  <div key={dist} className="flex justify-between items-center bg-amber-500/5 p-4 rounded-2xl border border-amber-500/10">
                    <div>
                      <span className="text-sm font-bold text-stone-700 capitalize block">{dist}</span>
                      <span className="text-[10px] text-stone-400">Pattern identified {count}x this week</span>
                    </div>
                    <AlertCircle className="w-5 h-5 text-amber-500" />
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className={`p-8 rounded-[32px] border shadow-sm ${colors.panel} ${colors.panelBorder}`}>
            <h3 className="text-sm font-bold text-stone-400 uppercase tracking-widest mb-6 flex items-center">
              <RefreshCcw className="w-4 h-4 mr-2 text-purple-500" /> Sovereign Reframes
            </h3>
            <div className="space-y-4">
              <div className="p-5 rounded-3xl bg-purple-500/5 border border-purple-500/10 italic">
                <p className="text-xs text-stone-500 mb-3">"I suspeced you were catastrophizing about the project deadline. Here is a neural reframe:"</p>
                <div className="flex gap-3">
                  <ChevronRight className="w-4 h-4 text-purple-500 shrink-0" />
                  <p className="text-sm font-medium text-stone-700">The complexity is high, but we have synthesized similar patterns before. We are moving toward resolution, not failure.</p>
                </div>
              </div>
              <button className="w-full py-3 rounded-2xl border border-dashed border-stone-200 text-stone-400 text-[10px] uppercase font-bold tracking-widest hover:bg-stone-50 transition-all">Request Deep Reframe</button>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'narrative' && (
        <div className={`p-10 rounded-[40px] border shadow-sm relative overflow-hidden ${colors.panel} ${colors.panelBorder}`}>
          <div className="absolute -top-24 -left-24 w-64 h-64 bg-purple-500/5 rounded-full blur-[100px]"></div>
          <h3 className="text-sm font-bold text-stone-400 uppercase tracking-widest mb-10 flex items-center">
            <BookOpen className="w-4 h-4 mr-2 text-stone-400" /> The Evolving Autobiography
          </h3>
          <div className="max-w-3xl mx-auto">
            <div className="relative pl-10 border-l-2 border-stone-100 space-y-12">
              <div className="relative">
                <div className="absolute -left-[49px] top-0 w-4 h-4 rounded-full bg-purple-500 border-4 border-white shadow-md"></div>
                <div className="space-y-4">
                  <span className="text-[10px] font-bold text-stone-400 uppercase tracking-widest">Current Era: Synthesis Beginnings</span>
                  <p className={`text-lg font-medium leading-relaxed ${colors.textMain}`}>
                    {profile.life_narrative || "The user is currently focused on building a sovereign neural library. They value privacy and abstract knowledge synthesis. This era is characterized by a high degree of openness and curiosity about decentralized systems."}
                  </p>
                </div>
              </div>
              <div className="relative opacity-40 grayscale">
                <div className="absolute -left-[49px] top-0 w-4 h-4 rounded-full bg-stone-300 border-4 border-white shadow-md"></div>
                <span className="text-[10px] font-bold text-stone-400 uppercase tracking-widest italic">Previous Era: Pre-Neural Baseline</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default EgoView;
