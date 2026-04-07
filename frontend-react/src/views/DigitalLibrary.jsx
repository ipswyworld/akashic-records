import React, { useState, useEffect, useRef } from 'react';
import { Book, Library, Sparkles, Search, ChevronRight, ChevronLeft } from 'lucide-react';
import { getThemeColors } from '../components/CommonUI';
import gsap from 'gsap';

const DigitalLibrary = ({ theme }) => {
  const [artifacts, setArtifacts] = useState([]);
  const [selectedBook, setSelectedBook] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const shelfRef = useRef(null);
  const colors = getThemeColors(theme);

  useEffect(() => {
    fetch('http://localhost:8001/artifacts', {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('akasha_token')}` }
    })
      .then(res => res.json())
      .then(data => {
        setArtifacts(data);
        setIsLoading(false);
      });
  }, []);

  useEffect(() => {
    if (!isLoading && shelfRef.current) {
      gsap.from('.book-spine', {
        y: 50,
        opacity: 0,
        stagger: 0.05,
        duration: 0.8,
        ease: 'power4.out'
      });
    }
  }, [isLoading]);

  const categories = [...new Set(artifacts.map(a => a.artifact_type))];

  const getBookColor = (type) => {
    switch (type) {
      case 'research_report': return 'bg-blue-600';
      case 'memory': return 'bg-amber-600';
      case 'web_clip': return 'bg-emerald-600';
      case 'financial': return 'bg-purple-600';
      default: return 'bg-stone-600';
    }
  };

  return (
    <div className="p-10 max-w-7xl mx-auto w-full min-h-screen">
      <div className="flex justify-between items-end mb-12">
        <div>
          <h1 className={`text-4xl font-bold mb-2 flex items-center gap-4 ${colors.textMain}`}>
            <Library className="w-10 h-10 text-amber-500" /> Neural Library
          </h1>
          <p className="text-stone-500 font-mono text-xs uppercase tracking-widest">Digital Progress Vault</p>
        </div>
        <div className="flex gap-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-stone-500" />
            <input 
              type="text" 
              placeholder="Search Volume..." 
              className={`pl-10 pr-4 py-2 rounded-xl border bg-transparent text-sm ${colors.panelBorder}`}
            />
          </div>
        </div>
      </div>

      <div className="space-y-16">
        {categories.map(cat => (
          <div key={cat} className="relative">
            <h3 className="text-[10px] font-bold text-stone-400 uppercase tracking-[0.2em] mb-6 flex items-center gap-2">
              <Sparkles className="w-3 h-3 text-amber-500" /> {cat.replace('_', ' ')}
            </h3>
            
            {/* The 3D Shelf */}
            <div 
              ref={shelfRef}
              className={`relative h-64 border-b-8 border-stone-800 flex items-end px-4 gap-1.5 overflow-x-auto scrollbar-hide`}
              style={{ perspective: '1000px' }}
            >
              {artifacts.filter(a => a.artifact_type === cat).map((art, i) => (
                <div 
                  key={art.id}
                  onClick={() => setSelectedBook(art)}
                  className={`book-spine relative w-12 h-48 ${getBookColor(cat)} cursor-pointer transition-all hover:-translate-y-4 hover:brightness-110 shadow-lg`}
                  style={{ 
                    transformStyle: 'preserve-3d',
                    transform: `rotateY(${i % 2 === 0 ? '-5deg' : '5deg'})`
                  }}
                >
                  <div className="absolute inset-0 bg-black/20"></div>
                  <div className="absolute inset-y-0 left-0 w-1 bg-white/10"></div>
                  <div className="h-full flex items-center justify-center">
                    <span 
                      className="text-[9px] font-bold text-white/90 uppercase tracking-tighter whitespace-nowrap origin-center -rotate-90 block w-full text-center px-4 overflow-hidden text-ellipsis"
                    >
                      {art.title}
                    </span>
                  </div>
                  {/* Gold Gilded Edge */}
                  <div className="absolute top-0 left-0 right-0 h-1 bg-amber-400/50"></div>
                </div>
              ))}
            </div>
            {/* Shelf Wood Detail */}
            <div className="h-2 w-full bg-stone-900 mt-0 shadow-2xl"></div>
          </div>
        ))}
      </div>

      {/* Book Detail Overlay */}
      {selectedBook && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-6 bg-black/80 backdrop-blur-sm animate-in fade-in duration-300">
          <div className={`max-w-2xl w-full bg-stone-900 border border-stone-800 rounded-3xl overflow-hidden shadow-2xl animate-in zoom-in-95 duration-300`}>
            <div className={`h-2 ${getBookColor(selectedBook.artifact_type)}`}></div>
            <div className="p-8">
              <div className="flex justify-between items-start mb-6">
                <div>
                  <h2 className="text-2xl font-bold text-white mb-2">{selectedBook.title}</h2>
                  <span className="text-[10px] font-bold text-amber-500 uppercase tracking-widest">{selectedBook.artifact_type}</span>
                </div>
                <button 
                  onClick={() => setSelectedBook(null)}
                  className="p-2 rounded-full hover:bg-stone-800 text-stone-400"
                >
                  <ChevronLeft className="w-5 h-5" />
                </button>
              </div>
              
              <div className="prose prose-invert max-h-[60vh] overflow-y-auto pr-4 text-stone-300 text-sm leading-relaxed scrollbar-thin scrollbar-thumb-stone-700">
                {selectedBook.summary || selectedBook.content}
              </div>
              
              <div className="mt-8 pt-6 border-t border-stone-800 flex justify-between items-center">
                <span className="text-[10px] text-stone-500 font-mono">{new Date(selectedBook.timestamp).toLocaleDateString()}</span>
                <button className="flex items-center gap-2 text-amber-500 text-xs font-bold hover:translate-x-1 transition-transform">
                  Open Volume <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DigitalLibrary;
