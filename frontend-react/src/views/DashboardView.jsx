import React, { useState, useMemo, useLayoutEffect, useRef, useEffect } from 'react';
import { 
  Zap, Plus, Activity, UploadCloud, Globe, Unlock, Sparkles, TrendingUp, Cpu
} from 'lucide-react';
import gsap from 'gsap';
import { ingestUrl, fetchEvolutionAnalytics } from '../api';
import { getThemeColors } from '../components/CommonUI';

const DashboardView = ({ analytics, recentArtifacts, onIngest, theme, setView }) => {
  const [ingestUrlInput, setIngestUrlInput] = useState('');
  const [isIngesting, setIsIngesting] = useState(false);
  const [evolutionData, setEvolutionData] = useState(null);
  const colors = getThemeColors(theme);
  const containerRef = useRef(null);

  useEffect(() => {
    fetchEvolutionAnalytics().then(setEvolutionData).catch(console.error);
  }, []);

  useLayoutEffect(() => {
    const ctx = gsap.context(() => {
      gsap.from('.dashboard-card', { y: 20, opacity: 0, duration: 0.8, stagger: 0.1, ease: 'power3.out', clearProps: 'all' });
    }, containerRef);
    return () => ctx.revert();
  }, [analytics]);

  const handleIngestClick = async () => {
    if (!ingestUrlInput) return;
    setIsIngesting(true);
    try { await ingestUrl(ingestUrlInput); setIngestUrlInput(''); onIngest(); } catch (err) { console.error(err); } finally { setIsIngesting(false); }
  };

  const heatmapData = useMemo(() => Array.from({ length: 28 * 7 }, (_, i) => (i % 7 === 0 && (analytics?.total_count || 0) > 0) ? Math.min(Math.floor((analytics?.total_count || 0) / 10), 3) : 0), [analytics]);

  return (
    <div ref={containerRef} className="p-4 sm:p-6 space-y-6 sm:space-y-8 animate-in fade-in duration-500 max-w-7xl mx-auto w-full">
      <div className={`dashboard-card p-6 sm:p-8 rounded-2xl ${colors.panel} border ${colors.panelBorder} backdrop-blur-xl relative overflow-hidden group shadow-sm`}>
        <div className="absolute -inset-1 bg-gradient-to-r from-amber-500/10 to-blue-500/10 blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-1000"></div>
        <div className="relative z-10">
          <h1 className={`text-2xl sm:text-3xl font-light mb-2 ${colors.textMain}`}><span className="text-amber-500 font-semibold tracking-wide">{analytics?.neural_name || 'Archivist'}</span> is Online.</h1>
          <p className={`${colors.textMuted} max-w-xl mb-6 leading-relaxed text-sm sm:text-base`}>System nominal. {analytics?.total_count || 0} neural artifacts indexed. Evolution Status: <span className="text-blue-500 font-mono font-bold">{evolutionData?.evolution_status || 'INITIALIZING'}</span>. Awaiting cognitive input.</p>
          <div className="flex flex-wrap gap-3 sm:gap-4">
            <button onClick={() => setView('chat')} className="px-4 sm:px-5 py-2.5 bg-amber-500/10 text-amber-600 border border-amber-500/30 rounded-lg hover:bg-amber-500/20 transition-all flex items-center shadow-sm text-sm font-medium"><Zap className="w-4 h-4 mr-2" /> Ask AI</button>
            <button onClick={() => setView('library')} className={`px-4 sm:px-5 py-2.5 rounded-lg border flex items-center text-sm font-medium transition-all ${theme === 'dark' ? 'bg-slate-800 text-slate-200 border-slate-700 hover:bg-slate-700' : 'bg-white text-stone-700 border-stone-200 hover:bg-stone-50 shadow-sm'}`}><Plus className="w-4 h-4 mr-2" /> Add Record</button>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          {/* Neural Evolution Card */}
          <div className={`dashboard-card p-5 sm:p-6 rounded-2xl ${colors.panel} border ${colors.panelBorder} shadow-sm overflow-hidden relative`}>
            <div className="absolute top-0 right-0 p-6 opacity-5">
              <Sparkles className="w-24 h-24 text-amber-500" />
            </div>
            <h3 className={`text-xs sm:text-sm font-semibold ${colors.textMuted} uppercase tracking-wider mb-6 flex items-center`}><TrendingUp className="w-4 h-4 mr-2 text-amber-500" /> Neural Evolution</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div>
                <span className="text-[10px] font-bold text-stone-400 uppercase tracking-widest block mb-4">Fitness Trends</span>
                <div className="flex items-end gap-1 h-20">
                  {evolutionData?.performance_history.length > 0 ? evolutionData.performance_history.slice(-15).map((p, i) => (
                    <div key={i} className="flex-1 group relative">
                      <div 
                        className={`w-full rounded-t-sm transition-all duration-500 ${p.fitness > 0.8 ? 'bg-green-500' : p.fitness > 0.5 ? 'bg-amber-500' : 'bg-rose-500'}`}
                        style={{ height: `${p.fitness * 100}%` }}
                      ></div>
                      <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 hidden group-hover:block z-20">
                        <div className="bg-slate-900 text-white text-[8px] py-1 px-2 rounded whitespace-nowrap shadow-xl">
                          {p.agent}: {(p.fitness * 100).toFixed(0)}%
                        </div>
                      </div>
                    </div>
                  )) : (
                    <div className="flex-1 flex items-center justify-center border border-dashed border-stone-200 rounded-lg h-full">
                      <span className="text-[10px] text-stone-400 italic">Gathering evolution metrics...</span>
                    </div>
                  )}
                </div>
              </div>

              <div>
                <span className="text-[10px] font-bold text-stone-400 uppercase tracking-widest block mb-4">Forged Skills</span>
                <div className="space-y-3">
                  {evolutionData?.forged_skills.length > 0 ? evolutionData.forged_skills.map((s, i) => (
                    <div key={i} className={`p-2.5 rounded-xl border ${theme === 'dark' ? 'bg-slate-800/50 border-slate-700' : 'bg-stone-50 border-stone-100'} flex items-center gap-3`}>
                      <div className="p-1.5 bg-amber-500/10 text-amber-600 rounded-lg"><Cpu className="w-3 h-3" /></div>
                      <div className="min-w-0">
                        <div className="text-[10px] font-bold truncate">{s.name}</div>
                        <div className="text-[8px] text-stone-400 truncate">{s.desc}</div>
                      </div>
                      <div className="ml-auto text-[8px] font-mono font-bold text-amber-500">x{s.count}</div>
                    </div>
                  )) : (
                    <div className="p-4 border border-dashed border-stone-200 rounded-xl text-center">
                      <span className="text-[10px] text-stone-400 italic">No skills forged yet.</span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>

          <div className={`dashboard-card p-5 sm:p-6 rounded-2xl ${colors.panel} border ${colors.panelBorder} shadow-sm`}>
            <h3 className={`text-xs sm:text-sm font-semibold ${colors.textMuted} uppercase tracking-wider mb-4 flex items-center`}><Activity className="w-4 h-4 mr-2 text-blue-500" /> Cognitive Heatmap</h3>
            <div className="flex flex-wrap gap-1.5 opacity-80">
              {heatmapData.map((val, i) => (
                <div key={i} className={`w-2.5 h-2.5 sm:w-3 sm:h-3 rounded-[2px] ${val === 0 ? (theme === 'dark' ? 'bg-slate-800/50' : 'bg-stone-100') : val === 1 ? 'bg-blue-400/40' : val === 2 ? 'bg-blue-500/60' : 'bg-amber-500/80 shadow-sm'}`} />
              ))}
            </div>
          </div>

          <div className={`dashboard-card p-5 sm:p-6 rounded-2xl ${colors.panel} border ${colors.panelBorder} shadow-sm`}>
            <h3 className={`text-xs sm:text-sm font-semibold ${colors.textMuted} uppercase tracking-wider mb-4`}>Recent Alterations</h3>
            <div className="space-y-4 relative before:absolute before:inset-0 before:ml-2 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-stone-200 before:to-transparent">
              {(recentArtifacts || []).slice(0, 5).length > 0 ? (recentArtifacts || []).slice(0, 5).map((art, i) => (
                <div key={art.id} className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group">
                  <div className={`flex items-center justify-center w-5 h-5 rounded-full border bg-white group-hover:border-amber-500 shadow-sm shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2 transition-all z-10 ${theme === 'dark' ? 'border-slate-700 bg-slate-900' : 'border-stone-200'}`}><div className="w-1.5 h-1.5 bg-amber-500 rounded-full"></div></div>
                  <div className={`w-[calc(100%-2.5rem)] md:w-[calc(50%-1.25rem)] p-4 rounded-xl border ${colors.panelBorder} ${theme === 'dark' ? 'bg-slate-800/30 hover:bg-slate-800/60' : 'bg-white hover:bg-stone-50 shadow-sm'} transition-colors`}>
                    <div className="flex items-center justify-between mb-1"><span className={`text-sm font-medium ${colors.textMain} truncate pr-2`}>{art.title}</span><span className="text-[10px] sm:text-xs text-stone-400 shrink-0">{new Date(art.timestamp).toLocaleDateString()}</span></div>
                    <p className={`text-xs ${colors.textMuted} truncate`}>{art.summary || 'Indexing...'}</p>
                  </div>
                </div>
              )) : <div className="text-center p-8 text-stone-400 italic">No neural artifacts detected yet.</div>}
            </div>
          </div>
        </div>

        <div className="space-y-6">
          <div className={`dashboard-card p-5 sm:p-6 rounded-2xl ${colors.panel} border ${colors.panelBorder} shadow-sm`}>
            <div className="flex justify-between items-center mb-6">
              <h3 className={`text-xs sm:text-sm font-semibold ${colors.textMuted} uppercase tracking-wider`}>System Integrity</h3>
              <button className="text-stone-400 hover:text-amber-500 transition-colors"><Unlock className="w-4 h-4" /></button>
            </div>
            <div className="space-y-4">
              <div className="flex justify-between items-center"><span className={`${colors.textMuted} text-sm`}>Neural Sync</span><span className="text-green-500 text-sm flex items-center font-medium"><div className="w-2 h-2 rounded-full bg-green-500 mr-2 animate-pulse"></div> Live</span></div>
              <div className="flex justify-between items-center"><span className={`${colors.textMuted} text-sm`}>Total Nodes</span><span className={`${colors.textMain} text-sm font-mono`}>{analytics?.total_count || 0}</span></div>
              <div className="flex justify-between items-center"><span className={`${colors.textMuted} text-sm`}>API Latency</span><span className={`${colors.textMain} text-sm font-mono`}>{analytics?.latency || 24}ms</span></div>
              <div className="pt-4 border-t border-stone-100">
                <div className="w-full bg-stone-100 rounded-full h-1.5 mb-1 overflow-hidden"><div className="bg-gradient-to-r from-blue-500 to-amber-400 h-1.5 rounded-full w-[12%]"></div></div>
                <div className="flex justify-between text-[10px] text-stone-400"><span>Storage Capacity</span><span>{Math.round((analytics?.total_count || 0) / 10)}%</span></div>
              </div>
            </div>
          </div>

          <div className={`dashboard-card p-5 sm:p-6 rounded-2xl ${colors.panel} border ${colors.panelBorder} shadow-sm`}>
            <h3 className={`text-xs sm:text-sm font-semibold ${colors.textMuted} uppercase tracking-wider mb-4`}>Fast Ingestion</h3>
            <div className="space-y-3">
              <div className="relative">
                <Globe className="w-4 h-4 absolute left-3 top-3 text-stone-400" />
                <input type="text" value={ingestUrlInput} onChange={(e) => setIngestUrlInput(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && handleIngestClick()} placeholder="Paste URL to clip..." className={`w-full rounded-lg py-2.5 pl-9 pr-3 text-sm focus:outline-none focus:ring-1 focus:ring-amber-500/20 transition-all ${colors.input}`} />
              </div>
              <button onClick={handleIngestClick} disabled={isIngesting || !ingestUrlInput} className={`w-full border border-dashed rounded-lg p-4 text-center transition-all flex flex-col items-center justify-center text-stone-400 hover:text-amber-600 hover:border-amber-500/50 hover:bg-amber-50/50 ${theme === 'dark' ? 'border-slate-700' : 'border-stone-200'}`}>
                {isIngesting ? <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-amber-500 mb-2"></div> : <UploadCloud className="w-6 h-6 mb-2" />}
                <span className="text-xs font-medium">{isIngesting ? 'Ingesting...' : 'Click to Upload'}</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardView;
