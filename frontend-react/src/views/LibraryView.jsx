import React, { useMemo, useLayoutEffect, useRef } from 'react';
import { 
  Search, Library, Globe, Headphones, FileText, Building2, Sparkles
} from 'lucide-react';
import { gsap } from 'gsap';
import { getThemeColors } from '../components/CommonUI';

const LibraryView = ({ artifacts, analytics, theme }) => {
  const colors = getThemeColors(theme);
  const containerRef = useRef(null);

  useLayoutEffect(() => {
    if (!artifacts || artifacts.length === 0) return;
    const ctx = gsap.context(() => {
      gsap.from('.artifact-card', {
        scale: 0.9,
        opacity: 0,
        duration: 0.5,
        stagger: 0.05,
        ease: 'back.out(1.7)'
      });
    }, containerRef);
    return () => ctx.revert();
  }, [artifacts]);

  const groupedArtifacts = useMemo(() => {
    const groups = {};
    artifacts.forEach(art => {
      const date = new Date(art.timestamp).toLocaleDateString(undefined, { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
      });
      if (!groups[date]) groups[date] = [];
      groups[date].push(art);
    });
    return Object.entries(groups).sort((a, b) => {
      return new Date(b[1][0].timestamp) - new Date(a[1][0].timestamp);
    });
  }, [artifacts]);

  const getIcon = (type) => {
    switch(type) {
      case 'web_clip': return <Globe className="w-4 h-4 text-blue-500" />;
      case 'audio_transcript': return <Headphones className="w-4 h-4 text-purple-500" />;
      case 'academic_paper': return <FileText className="w-4 h-4 text-emerald-500" />;
      case 'dataset': return <Building2 className="w-4 h-4 text-amber-500" />;
      case 'synthetic_insight': return <Sparkles className="w-4 h-4 text-rose-500" />;
      default: return <FileText className="w-4 h-4 text-stone-400" />;
    }
  };

  return (
    <div ref={containerRef} className="p-4 sm:p-6 flex flex-col max-w-7xl mx-auto w-full animate-in fade-in duration-500">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-10">
        <div className="relative w-full sm:w-96 shrink-0">
          <Search className="w-5 h-5 absolute left-3 top-2.5 text-stone-400" />
          <input type="text" placeholder="Search knowledge base..." className={`w-full border rounded-xl py-2.5 pl-10 pr-4 focus:outline-none focus:ring-1 focus:ring-blue-500/50 transition-all text-sm ${colors.input}`} />
        </div>
        <div className="flex gap-2 overflow-x-auto pb-2 sm:pb-0 w-full sm:w-auto hide-scrollbar">
          {(analytics?.top_entities || ['General']).map(tag => (
            <button key={tag} className={`px-3 py-1 rounded-full border text-xs whitespace-nowrap transition-colors capitalize ${theme === 'dark' ? 'bg-slate-800 border-slate-700 text-slate-300 hover:border-amber-500/50' : 'bg-white border-stone-200 text-stone-600 hover:border-amber-500 hover:text-amber-600 shadow-sm'}`}>#{tag}</button>
          ))}
        </div>
      </div>

      <div className="space-y-12">
        {groupedArtifacts.length > 0 ? groupedArtifacts.map(([date, items]) => (
          <div key={date} className="animate-in slide-in-from-bottom-4 duration-700">
            <div className="flex items-center gap-4 mb-6">
              <div className={`px-4 py-1 rounded-full text-[10px] font-bold uppercase tracking-widest ${theme === 'dark' ? 'bg-slate-900 text-slate-500 border border-slate-800' : 'bg-stone-100 text-stone-400 border border-stone-200'}`}>
                {date}
              </div>
              <div className={`h-px flex-1 ${theme === 'dark' ? 'bg-slate-800/50' : 'bg-stone-200/50'}`}></div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
              {items.map(art => (
                <div key={art.id} className={`artifact-card group relative p-5 rounded-xl border transition-all cursor-pointer flex flex-col h-44 ${colors.panel} ${colors.panelBorder} ${theme === 'dark' ? 'hover:border-blue-500/30 shadow-[0_4px_20px_-10px_rgba(0,0,0,0.5)]' : 'hover:border-amber-500 shadow-sm hover:shadow-md'}`}>
                  <div className="flex justify-between items-start mb-3">
                    <div className="flex items-center gap-2 overflow-hidden w-full">
                      <div className={`p-1.5 rounded-md shrink-0 ${theme === 'dark' ? 'bg-slate-800' : 'bg-stone-50 border border-stone-100'}`}>{getIcon(art.artifact_type)}</div>
                      <h4 className={`font-medium text-sm sm:text-base truncate pr-2 ${colors.textMain}`}>{art.title}</h4>
                    </div>
                  </div>
                  <p className={`text-xs sm:text-sm line-clamp-3 mb-auto leading-relaxed ${colors.textMuted}`}>{art.summary}</p>
                  <div className="flex justify-between items-end mt-4">
                    <div className="flex gap-1.5 overflow-hidden pr-2">
                      {art.metadata_json?.entities?.slice(0, 2).map(tag => (
                        <span key={tag} className={`text-[9px] px-2 py-0.5 rounded border truncate ${theme === 'dark' ? 'text-slate-500 bg-slate-950 border-slate-800' : 'text-stone-500 bg-stone-50 border-stone-100'}`}>{tag}</span>
                      ))}
                    </div>
                    <span className="text-[10px] text-stone-400 font-mono whitespace-nowrap">{new Date(art.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )) : (
          <div className="text-center py-24 text-stone-400 border border-dashed border-stone-200 rounded-2xl bg-white/20 backdrop-blur-sm">
            <Library className="w-12 h-12 mx-auto mb-4 opacity-20" />
            <p className="text-lg font-light italic">Your deep library is currently empty.</p>
            <p className="text-xs mt-2 opacity-60">Begin your neural feeding to populate these vaults.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default LibraryView;
