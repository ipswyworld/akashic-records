import React, { useState, useEffect } from 'react';
import { Library, Sparkles, Search, ChevronRight, ChevronLeft, Maximize2, X } from 'lucide-react';
import { getThemeColors } from '../components/CommonUI';

const DigitalLibrary = ({ theme }) => {
  const [artifacts, setArtifacts] = useState([]);
  const [selectedBook, setSelectedBook] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [isFullScreen, setIsFullScreen] = useState(false);
  const colors = getThemeColors(theme);

  useEffect(() => {
    fetch('http://localhost:8001/artifacts', {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('akasha_token')}` }
    })
      .then(res => res.json())
      .then(data => {
        setArtifacts(Array.isArray(data) ? data : []);
        setIsLoading(false);
      })
      .catch(err => {
        console.error("Library Fetch Error:", err);
        setIsLoading(false);
      });
  }, []);

  const filteredArtifacts = artifacts.filter(a => 
    (a.title || '').toLowerCase().includes(searchTerm.toLowerCase()) || 
    (a.content || '').toLowerCase().includes(searchTerm.toLowerCase())
  );

  const categories = [...new Set(filteredArtifacts.map(a => a.artifact_type || 'uncategorized'))];

  const scrollShelf = (id, direction) => {
    const shelf = document.getElementById(`shelf-${id}`);
    if (shelf) {
      const scrollAmount = direction === 'left' ? -500 : 500;
      shelf.scrollBy({ left: scrollAmount, behavior: 'smooth' });
    }
  };

  const getBookColor = (type) => {
    switch (type) {
      case 'research_report': return 'from-blue-700 to-blue-900 border-blue-400';
      case 'memory': return 'from-amber-700 to-amber-900 border-amber-400';
      case 'web_clip': return 'from-emerald-700 to-emerald-900 border-emerald-400';
      case 'financial': return 'from-purple-700 to-purple-900 border-purple-400';
      case 'behavioral_insight': return 'from-rose-700 to-rose-900 border-rose-400';
      case 'journal_reflection': return 'from-indigo-700 to-indigo-900 border-indigo-400';
      case 'news_article': return 'from-cyan-700 to-cyan-900 border-cyan-400';
      case 'dataset': return 'from-teal-700 to-teal-900 border-teal-400';
      case 'synthetic_insight': return 'from-fuchsia-700 to-fuchsia-900 border-fuchsia-400';
      default: return 'from-stone-700 to-stone-900 border-stone-400';
    }
  };

  return (
    <div className="p-10 max-w-7xl mx-auto w-full min-h-screen bg-stone-950/50">
      {/* Header */}
      <div className="flex justify-between items-end mb-16 border-b border-stone-800 pb-8">
        <div>
          <h1 className={`text-5xl font-serif mb-3 flex items-center gap-6 ${colors.textMain}`}>
            <Library className="w-12 h-12 text-amber-500" /> Neural Library
          </h1>
          <p className="text-stone-500 font-mono text-xs uppercase tracking-[0.3em]">The Private Akashic Records</p>
        </div>
        <div className="relative">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-stone-600" />
          <input 
            type="text" 
            placeholder="Search the vault..." 
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-12 pr-6 py-3 rounded-2xl border border-stone-800 bg-stone-900/50 text-white focus:outline-none focus:border-amber-500 w-80 transition-all"
          />
        </div>
      </div>

      {/* Shelves Container */}
      <div className="space-y-24">
        {isLoading && (
          <div className="text-center py-20">
            <div className="animate-spin w-10 h-10 border-4 border-amber-500 border-t-transparent rounded-full mx-auto mb-4"></div>
            <p className="text-stone-500 font-mono text-sm">Consulting the Head Archivist...</p>
          </div>
        )}

        {categories.length === 0 && !isLoading && (
          <div className="text-stone-600 text-center py-32 border-2 border-dashed border-stone-900 rounded-3xl">
            <p className="font-serif italic text-xl">"The silence of an empty library is the birth of a new idea."</p>
            <p className="mt-4 font-mono text-xs uppercase tracking-widest">No volumes found</p>
          </div>
        )}

        {categories.map(cat => {
          const catBooks = filteredArtifacts.filter(a => (a.artifact_type || 'uncategorized') === cat);
          return (
            <div key={cat} className="relative group">
              <div className="flex justify-between items-center mb-8 px-2">
                <h3 className="text-xs font-bold text-stone-400 uppercase tracking-[0.25em] flex items-center gap-3">
                  <Sparkles className="w-4 h-4 text-amber-500" /> 
                  <span className="text-stone-200">{cat ? cat.replace('_', ' ') : 'General'}</span>
                  <span className="px-2.5 py-0.5 bg-amber-500/10 text-amber-500 rounded-full border border-amber-500/20">{catBooks.length}</span>
                </h3>
                <div className="flex gap-3 opacity-0 group-hover:opacity-100 transition-all">
                  <button onClick={() => scrollShelf(cat, 'left')} className="p-2 bg-stone-900 hover:bg-amber-500 hover:text-black rounded-full text-stone-400 transition-colors shadow-lg"><ChevronLeft className="w-5 h-5"/></button>
                  <button onClick={() => scrollShelf(cat, 'right')} className="p-2 bg-stone-900 hover:bg-amber-500 hover:text-black rounded-full text-stone-400 transition-colors shadow-lg"><ChevronRight className="w-5 h-5"/></button>
                </div>
              </div>
              
              <div className="relative">
                {/* The Physical Shelf */}
                <div 
                  id={`shelf-${cat}`}
                  className="relative h-72 border-b-[12px] border-stone-900 flex items-end px-10 gap-2 overflow-x-auto scrollbar-hide pb-1"
                  style={{ perspective: '1200px' }}
                >
                  {catBooks.map((art, i) => (
                    <div 
                      key={art.id}
                      onClick={() => setSelectedBook(art)}
                      className={`
                        book-spine flex-shrink-0 relative w-14 h-56 
                        bg-gradient-to-br ${getBookColor(cat)} 
                        cursor-pointer transition-all duration-300
                        hover:-translate-y-8 hover:scale-105 active:scale-95
                        shadow-[5px_0_15px_rgba(0,0,0,0.5)] border-l-2
                        flex flex-col items-center justify-center
                      `}
                      style={{ 
                        transformStyle: 'preserve-3d',
                        transform: `rotateY(${i % 2 === 0 ? '-6deg' : '6deg'})`
                      }}
                    >
                      {/* Spine Texture */}
                      <div className="absolute inset-0 bg-white/5 opacity-50"></div>
                      <div className="absolute inset-y-0 left-1 w-[1px] bg-black/20"></div>
                      <div className="absolute inset-y-0 right-1 w-[1px] bg-black/20"></div>
                      
                      {/* Title on Spine */}
                      <div className="h-48 flex items-center justify-center overflow-hidden pointer-events-none">
                        <span 
                          className="text-[10px] font-bold text-white/90 uppercase tracking-tighter whitespace-nowrap origin-center -rotate-90 block w-48 text-center px-4 overflow-hidden text-ellipsis"
                        >
                          {art.title}
                        </span>
                      </div>

                      {/* Gold Gilded Bands */}
                      <div className="absolute top-4 left-0 right-0 h-0.5 bg-amber-400/40"></div>
                      <div className="absolute bottom-4 left-0 right-0 h-0.5 bg-amber-400/40"></div>
                    </div>
                  ))}
                </div>
                {/* Shelf Shadow */}
                <div className="h-12 w-full bg-gradient-to-b from-black/60 to-transparent pointer-events-none -mt-1"></div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Reading Overlay */}
      {selectedBook && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 md:p-12 bg-stone-950/90 backdrop-blur-xl animate-in fade-in duration-300">
          <div className={`${isFullScreen ? 'w-full h-full' : 'max-w-4xl h-[85vh]'} w-full bg-stone-900 border border-stone-800 rounded-[2.5rem] overflow-hidden shadow-[0_0_100px_rgba(0,0,0,0.8)] animate-in zoom-in-95 duration-300 flex flex-col transition-all relative`}>
            
            {/* Header */}
            <div className={`h-3 shrink-0 bg-gradient-to-r ${getBookColor(selectedBook.artifact_type)}`}></div>
            
            <div className="p-8 md:p-12 flex flex-col flex-1 overflow-hidden">
              <div className="flex justify-between items-start mb-10 shrink-0">
                <div className="max-w-[80%]">
                  <h2 className="text-3xl md:text-4xl font-serif font-bold text-white mb-4 leading-tight">{selectedBook.title}</h2>
                  <div className="flex gap-3">
                    <span className="px-3 py-1 bg-amber-500/10 text-amber-500 text-[10px] font-mono font-bold uppercase tracking-widest rounded-full border border-amber-500/20">
                      {selectedBook.artifact_type ? selectedBook.artifact_type.replace('_', ' ') : 'General'}
                    </span>
                    <span className="px-3 py-1 bg-stone-800 text-stone-400 text-[10px] font-mono rounded-full uppercase tracking-widest">
                      Volume #{selectedBook.id.substring(0, 6)}
                    </span>
                  </div>
                </div>
                <div className="flex gap-3">
                  <button 
                    onClick={() => setIsFullScreen(!isFullScreen)}
                    className="p-3 bg-stone-800 rounded-2xl hover:bg-amber-500 hover:text-black text-stone-400 transition-all shadow-lg"
                    title="Toggle Reading Mode"
                  >
                    <Maximize2 className="w-6 h-6" />
                  </button>
                  <button 
                    onClick={() => { setSelectedBook(null); setIsFullScreen(false); }}
                    className="p-3 bg-stone-800 rounded-2xl hover:bg-rose-500 hover:text-white text-stone-400 transition-all shadow-lg"
                    title="Close"
                  >
                    <X className="w-6 h-6" />
                  </button>
                </div>
              </div>
              
              {/* Content Area */}
              <div className="flex-1 overflow-y-auto pr-6 custom-scrollbar">
                <div className="prose prose-lg prose-invert max-w-none">
                  {selectedBook.summary && (
                    <div className="mb-10 p-8 bg-amber-500/5 border-l-4 border-amber-500 rounded-r-2xl italic text-amber-200/80 leading-relaxed shadow-inner font-serif text-lg">
                      {selectedBook.summary}
                    </div>
                  )}
                  <div className="text-stone-300 leading-relaxed whitespace-pre-wrap font-serif text-xl selection:bg-amber-500/30">
                    {selectedBook.content || "This volume's physical text is encrypted or missing."}
                  </div>
                </div>
              </div>
              
              {/* Footer */}
              <div className="mt-8 pt-8 border-t border-stone-800 flex justify-between items-center shrink-0">
                <div className="flex flex-col">
                  <span className="text-[10px] text-stone-600 uppercase tracking-widest font-mono mb-1">Indexed On</span>
                  <span className="text-sm text-stone-400 font-mono">{new Date(selectedBook.timestamp).toLocaleString()}</span>
                </div>
                <div className="flex items-center gap-4">
                  <span className="text-stone-600 font-serif italic text-sm">Archivist Certified Synthesis</span>
                  <div className="w-8 h-8 rounded-full bg-amber-500/20 flex items-center justify-center border border-amber-500/30">
                    <Library className="w-4 h-4 text-amber-500" />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Global CSS for scrollbars */}
      <style dangerouslySetInnerHTML={{ __html: `
        .scrollbar-hide::-webkit-scrollbar { display: none; }
        .scrollbar-hide { -ms-overflow-style: none; scrollbar-width: none; }
        .custom-scrollbar::-webkit-scrollbar { width: 6px; }
        .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
        .custom-scrollbar::-webkit-scrollbar-thumb { background: #292524; border-radius: 10px; }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover { background: #44403c; }
      `}} />
    </div>
  );
};

export default DigitalLibrary;
