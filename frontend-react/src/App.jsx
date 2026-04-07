import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion'; // [OPTIMIZED]
import { 
  Bell, Mic, LayoutDashboard, Library, Network, Globe, Hammer,
  MessageSquare, Building2, Sun, Moon, PanelLeftClose, 
  PanelLeftOpen, Settings, Zap, Sparkles, BrainCircuit,
  Command, Search, Plus, Activity, Unlock, X, Check, AlertCircle, Paperclip, Send,
  Book, Landmark, Clock, GraduationCap
} from 'lucide-react';

const NeuralClock = () => {
  const [time, setTime] = React.useState(new Date());
  React.useEffect(() => {
    const timer = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);
  
  return (
    <div className="flex flex-col items-end">
      <div className="text-xs font-mono font-bold text-amber-500 tracking-wider">
        {time.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
      </div>
      <div className="text-[8px] font-black text-stone-500 uppercase tracking-[0.2em]">
        {time.toLocaleDateString([], { weekday: 'short', month: 'short', day: 'numeric' })}
      </div>
    </div>
  );
};
import gsap from 'gsap';

import { getThemeColors, Toast } from './components/CommonUI';
import { useAnalytics, useArtifacts, usePsychology, useUpdateSettings, useSettings } from './hooks/useAkasha';

// Modular Views
import DashboardView from './views/DashboardView';
import LibraryView from './views/LibraryView';
import ChatView from './views/ChatView';
import PalaceView from './views/PalaceView';
import DataHarvestView from './views/DataHarvestView';
import EgoView from './views/EgoView';
import ButlerView from './views/ButlerView';
import SettingsView from './views/SettingsView';
import GraphView from './views/GraphView';
import NetworkView from './views/NetworkView';
import ForgeView from './views/ForgeView';
import AuthView from './views/AuthView';
import DigitalLibrary from './views/DigitalLibrary';
import TutorView from './views/TutorView';
import ArcReactor from './components/ArcReactor';
import Orb from './components/Orb';
import { useVoice } from './hooks/useVoice';
import { logout } from './api';

class ErrorBoundary extends React.Component {
  constructor(props) { super(props); this.state = { hasError: false, error: null }; }
  static getDerivedStateFromError(error) { return { hasError: true, error }; }
  render() { 
    if (this.state.hasError) return <div className="min-h-screen bg-slate-950 flex items-center justify-center p-10 text-red-500 font-mono text-center">System Error: {this.state.error?.toString()}</div>; 
    return this.props.children; 
  }
}

export default function AkashaOS() {
  return (
    <ErrorBoundary>
      <AkashaOSContent />
    </ErrorBoundary>
  );
}

function AkashaOSContent() {
  const [isAuthenticated, setIsAuthenticated] = useState(true); // DORMANT MODE
  const [currentView, setCurrentView] = useState('dashboard');
  const [isSidebarOpen, setSidebarOpen] = useState(true);
  const [theme, setTheme] = useState('dark');
  const [toasts, setToasts] = useState([]);
  const { 
    isListening, 
    isPlaying, 
    startListening, 
    stopListening, 
    enqueueAudio, 
    stopAudio, 
    analyser 
  } = useVoice(
    (transcript) => {
      if (socketRef.current?.readyState === WebSocket.OPEN) {
        socketRef.current.send(JSON.stringify({ type: 'TRANSCRIPT', payload: transcript }));
      }
    },
    (err) => setToasts(prev => [{ id: Date.now(), type: 'system', message: err }, ...prev])
  );

  const [activeIntent, setActiveIntent] = useState(null);
  const [isActionActive, setIsActionActive] = useState(false);
  const [messages, setMessages] = useState([]);
  const [isSynthesizing, setIsSynthesizing] = useState(false);
  const socketRef = useRef(null);
  const bgRef = useRef(null);
  
  const colors = getThemeColors(theme);

  const { data: analytics, refetch: refetchAnalytics } = useAnalytics();
  const { data: artifacts, refetch: refetchArtifacts } = useArtifacts();
  const { data: psychology } = usePsychology();
  const { data: userSettings } = useSettings();
  const updateSettingsMutation = useUpdateSettings();

  const userName = psychology?.known_name || 'User';
  const userInitials = userName.substring(0, 2).toUpperCase();

  useEffect(() => {
    if (!isAuthenticated) return;
    if (messages.length === 0 && analytics?.neural_name) {
      setMessages([{ role: 'ai', content: `Greetings ${userName}. I am ${analytics.neural_name}. My neural pathways are initialized. How may I assist your synthesis today?` }]);
    }
  }, [analytics, userName, isAuthenticated]);

  useEffect(() => {
    if (!bgRef.current) return;
    const pulse = gsap.to(bgRef.current, {
      scale: isSynthesizing ? 1.2 : 1.0,
      opacity: isSynthesizing ? 0.3 : 0.1,
      duration: isSynthesizing ? 1.5 : 4,
      repeat: -1, yoyo: true, ease: 'sine.inOut'
    });
    return () => pulse.kill();
  }, [isSynthesizing]);

  const refreshData = () => { 
    refetchAnalytics?.();
    refetchArtifacts?.();
  };

  useEffect(() => {
    if (!isAuthenticated) return;
    const connectSocket = () => {
      try {
        const token = localStorage.getItem('akasha_token');
        const socket = new WebSocket(`ws://localhost:8001/akasha/sensory?token=${token}`);
        socketRef.current = socket;
        socket.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            if (data.event === 'SERENDIPITY_REALIZATION') {
              setToasts(prev => [...prev, { id: Date.now(), message: data.payload, type: 'serendipity' }]);
            }
            if (data.type === 'HUD_MORPH') {
              setActiveIntent(data.intent);
              if (data.intent === 'COMPLEX_REASONING') setCurrentView('graph');
              if (data.intent === 'SYSTEM_COMMAND') setCurrentView('butler');
              setTimeout(() => setActiveIntent(null), 5000);
            }
            if (data.type === 'WAKE_RESPONSE' || data.type === 'RESPONSE') { 
              setMessages(prev => [...prev, { role: 'ai', content: data.payload.answer, monologue: data.payload.monologue }]); 
              
              // --- Trigger Thought Trace ---
              if (data.payload.citations && data.payload.citations.length > 0) {
                setToasts(prev => [{ id: Date.now(), type: 'system', message: 'Thought Trace Active: Illuminating neural path...' }, ...prev]);
                // We'll pass the citations to the PalaceView if it's active
                // For now, we simulate the 'Glow' intent
                setActiveIntent('NEURAL_TRACE');
              }
              // -----------------------------

              setCurrentView('chat'); 
              if (data.audio) {
                enqueueAudio(data.audio);
              }
            }
            else if (data.type === 'OS_CONTROL') {
              const { view, action } = data.payload;
              setIsActionActive(true);
              setTimeout(() => setIsActionActive(false), 3000);
              if (view) {
                setCurrentView(view);
                setToasts(prev => [{ id: Date.now(), type: 'system', message: `Navigating to ${view}...` }, ...prev]);
              }
              if (action === 'toggle_theme') setTheme(theme === 'dark' ? 'light' : 'dark');
              if (data.message) {
                setMessages(prev => [...prev, { role: 'ai', content: data.message }]);
                if (data.audio) enqueueAudio(data.audio);
              }
            }
            else if (data.type === 'ACTION_COMPLETE') {
              setIsActionActive(true);
              setTimeout(() => setIsActionActive(false), 3000);
              setMessages(prev => [...prev, { role: 'ai', content: data.message }]);
              setCurrentView('butler');
              if (data.audio) enqueueAudio(data.audio);
              refreshData();
            }
            else if (data.event === 'NEW_ARTIFACT_INGESTED') { 
              refreshData(); 
              const newId = Date.now(); 
              setToasts(prev => [{ id: newId, type: 'system', message: `Indexed: ${data.title}` }, ...prev]); 
              setTimeout(() => setToasts(prev => prev.filter(t => t.id !== newId)), 5000); 
            }
          } catch (e) { console.error("WS error", e); }
        };
        socket.onclose = () => setTimeout(connectSocket, 5000);
      } catch (e) { console.error("WS connection fail", e); }
    };
    connectSocket();
    return () => socketRef.current?.close();
  }, [isAuthenticated, enqueueAudio]);

  if (!isAuthenticated) {
    return <AuthView onAuthSuccess={() => setIsAuthenticated(true)} />;
  }

  const NavItem = ({ icon: Icon, label, id }) => {
    const active = currentView === id;
    return (
      <button onClick={() => setCurrentView(id)} className={`w-full flex items-center px-3 py-3 rounded-xl mb-1 transition-all ${active ? (theme === 'dark' ? 'bg-amber-500/10 text-amber-500 border border-amber-500/20 shadow-sm' : 'bg-amber-500 text-white shadow-md') : `text-stone-500 hover:bg-stone-100 ${theme === 'dark' ? 'hover:bg-slate-800 text-slate-400 hover:text-slate-200' : ''}`}`}>
        <Icon className={`w-5 h-5 shrink-0 ${isSidebarOpen ? 'mr-3' : 'mx-auto'}`} />
        {isSidebarOpen && <span className="font-medium text-sm truncate">{label}</span>}
      </button>
    );
  };

  return (
    <div className={`flex h-screen w-full transition-colors duration-700 font-sans overflow-hidden relative ${colors.bg}`}>
      <div ref={bgRef} className="absolute inset-0 pointer-events-none z-0 overflow-hidden">
        <div className={`absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] rounded-full blur-[120px] ${theme === 'dark' ? 'bg-blue-500/20' : 'bg-amber-500/10'}`}></div>
      </div>

      <div className="fixed top-20 right-4 sm:top-24 sm:right-6 z-[60] flex flex-col gap-3 pointer-events-none items-end w-96">{toasts.map(t => <Toast key={t.id} message={t.message} type={t.type} onClose={() => setToasts(prev => prev.filter(x => x.id !== t.id))} />)}</div>
      
      <aside className={`hidden sm:flex flex-col border-r transition-all duration-300 z-20 shrink-0 backdrop-blur-xl ${colors.sidebar} ${isSidebarOpen ? 'w-64' : 'w-20'}`}>
        <div className="h-20 flex items-center px-4 border-b border-inherit shrink-0">
          <div className="w-10 h-10 bg-amber-500 rounded-xl flex items-center justify-center shrink-0 shadow-lg shadow-amber-500/20">
            <Command className="w-6 h-6 text-slate-900" />
          </div>
          {isSidebarOpen && (
            <div className="ml-3 flex flex-col overflow-hidden animate-in fade-in slide-in-from-left-2 duration-500">
              <span className={`text-xl font-bold tracking-tight leading-tight ${colors.textMain}`}>Akasha</span>
              <span className="text-[10px] uppercase font-bold tracking-widest text-amber-500 truncate">Universal Library</span>
            </div>
          )}
        </div>
        <div className="flex-1 py-4 px-3 overflow-y-auto hide-scrollbar">
          <NavItem icon={LayoutDashboard} label="Dashboard" id="dashboard" />
          <NavItem icon={Zap} label="Butler" id="butler" />
          <NavItem icon={Library} label="Deep Library" id="library" />
          <NavItem icon={Book} label="Neural Library" id="digital_library" />
          <NavItem icon={GraduationCap} label="Synaptic Tutor" id="tutor" />
          <NavItem icon={Network} label="Neural Graph" id="graph" />
          <NavItem icon={Globe} label="Sovereign Network" id="network" />
          <NavItem icon={Hammer} label="Neural Forge" id="forge" />
          <NavItem icon={MessageSquare} label="Archivist Chat" id="chat" />
          <NavItem icon={Building2} label="Memory Palace" id="palace" />
          <NavItem icon={Sparkles} label="Data Harvest" id="harvest" />
          <NavItem icon={BrainCircuit} label="Digital Ego" id="ego" />
        </div>
        <div className="p-4 border-t border-inherit space-y-2 shrink-0">
          <div className="flex items-center justify-between text-stone-500 mb-2 px-2">
            <div className="flex items-center">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-[10px] font-bold uppercase ${theme === 'dark' ? 'bg-slate-800 border-slate-700 text-slate-300' : 'bg-stone-200 border-stone-300 text-stone-600'} border`}>{userInitials}</div>
              {isSidebarOpen && <span className={`ml-2 text-xs font-medium truncate max-w-[80px] ${theme === 'dark' ? 'text-slate-400' : 'text-stone-500'}`}>{userName}</span>}
            </div>
            <div className="flex gap-1">
              <button onClick={() => setCurrentView('settings')} className="p-1.5 hover:bg-stone-100 rounded-lg transition-colors"><Settings className="w-4 h-4" /></button>
              <button onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')} className="p-1.5 hover:bg-stone-100 rounded-lg transition-colors">{theme === 'dark' ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}</button>
              <button onClick={logout} title="Logout" className="p-1.5 hover:bg-red-500/10 text-red-500 rounded-lg transition-colors"><X className="w-4 h-4" /></button>
            </div>
          </div>
          <button onClick={() => setSidebarOpen(!isSidebarOpen)} className={`w-full flex items-center ${isSidebarOpen ? 'justify-start px-2' : 'justify-center'} py-2.5 hover:bg-stone-100 rounded-lg transition-colors text-stone-500`}>{isSidebarOpen ? <><PanelLeftClose className="w-5 h-5 mr-2"/><span className="text-xs uppercase font-bold tracking-widest">Collapse</span></> : <PanelLeftOpen className="w-5 h-5"/>}</button>
        </div>
      </aside>

      <main className="flex-1 flex flex-col relative min-w-0 h-screen z-10 overflow-hidden">
        {/* HUD Overlay (Neural Interface Style) */}
        <div className={`absolute top-0 left-0 right-0 h-1 z-[70] transition-all duration-1000 ${isSynthesizing ? 'bg-amber-500 shadow-[0_0_15px_rgba(245,158,11,0.5)]' : 'bg-transparent'}`}></div>
        
        {activeIntent && (
          <div className="absolute top-24 left-1/2 -translate-x-1/2 z-[70] animate-in fade-in zoom-in duration-500">
            <div className={`px-6 py-2 rounded-full border border-blue-500/20 bg-slate-900/80 backdrop-blur-xl text-[10px] font-black uppercase tracking-[0.3em] text-blue-500 shadow-2xl flex items-center gap-3`}>
              <div className="w-1.5 h-1.5 rounded-full bg-blue-500 animate-pulse"></div>
              Intent Detected: {activeIntent.replace('_', ' ')}
            </div>
          </div>
        )}

        <header className={`h-16 border-b backdrop-blur-md flex items-center justify-between px-6 z-30 shrink-0 ${colors.header}`}>
          <div className="flex items-center text-sm font-medium text-stone-400 truncate">
            <span className="hidden sm:inline">Neural Core</span>
            <span className="hidden sm:inline mx-2 text-stone-200">/</span>
            <span className={`capitalize font-bold tracking-tight truncate ${colors.textMain}`}>{currentView}</span>
          </div>
          <div className="flex items-center gap-6">
            <NeuralClock />
            <button 
              onClick={() => setToasts([])} 
              className={`p-2 transition-colors relative ${toasts.length > 0 ? 'text-amber-500' : 'text-stone-400 hover:text-amber-500'}`}
            >
              <Bell className="w-5 h-5" />
              {toasts.length > 0 && (
                <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-blue-500 rounded-full border-2 border-inherit"></span>
              )}
            </button>
          </div>
        </header>
        <div className="flex-1 overflow-hidden relative flex flex-col perspective-1000">
          <AnimatePresence mode="wait">
            <motion.div
              key={currentView}
              initial={{ opacity: 0, z: -100, rotateX: 5 }}
              animate={{ opacity: 1, z: 0, rotateX: 0 }}
              exit={{ opacity: 0, z: 100, rotateX: -5 }}
              transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
              className="flex-1 overflow-y-auto h-full w-full"
            >
              {currentView === 'dashboard' && <DashboardView analytics={analytics} recentArtifacts={artifacts} onIngest={refreshData} theme={theme} setView={setCurrentView} />}
              {currentView === 'butler' && <ButlerView theme={theme} />}
              {currentView === 'library' && <LibraryView artifacts={artifacts || []} analytics={analytics} theme={theme} />}
              {currentView === 'digital_library' && <DigitalLibrary theme={theme} />}
              {currentView === 'tutor' && <TutorView theme={theme} />}
              {currentView === 'graph' && <GraphView theme={theme} />}
              {currentView === 'network' && <NetworkView theme={theme} />}
              {currentView === 'forge' && <ForgeView theme={theme} />}
              {currentView === 'chat' && <ChatView messages={messages} setMessages={setMessages} isSynthesizing={isSynthesizing} setIsSynthesizing={setIsSynthesizing} theme={theme} analytics={analytics} />}
              {currentView === 'palace' && <PalaceView analytics={analytics} theme={theme} />}
              {currentView === 'harvest' && <DataHarvestView theme={theme} onIngest={refreshData} />}
              {currentView === 'ego' && <EgoView theme={theme} />}
              {currentView === 'settings' && <SettingsView userSettings={userSettings} analytics={analytics} onUpdate={(s) => updateSettingsMutation.mutate({ settings: s, userId: 'system_user' })} theme={theme} />}
            </motion.div>
          </AnimatePresence>
        </div>
        <div className="absolute bottom-10 left-1/2 -translate-x-1/2 z-40 flex flex-col items-center">
          <div 
            className="w-48 h-48 cursor-pointer active:scale-95 transition-transform"
            onClick={() => isListening ? stopListening() : startListening()}
          >
            <Orb 
              state={isPlaying ? 'speaking' : (isSynthesizing ? 'thinking' : (isListening ? 'listening' : 'idle'))} 
              analyser={analyser} 
            />
          </div>
          <span className={`text-[10px] font-bold uppercase tracking-[0.2em] mt-3 transition-all duration-500 ${isListening ? 'text-amber-500 opacity-100' : 'text-stone-500 opacity-40'}`}>
            {isListening ? 'Sovereign Ears Active' : 'Neural Core Ready'}
          </span>
        </div>
      </main>
      <style dangerouslySetInnerHTML={{__html: `.custom-scrollbar::-webkit-scrollbar { width: 4px; height: 4px; } .custom-scrollbar::-webkit-scrollbar-thumb { background: #d6d3d1; border-radius: 10px; } .hide-scrollbar::-webkit-scrollbar { display: none; }`}} />
    </div>
  );
}
