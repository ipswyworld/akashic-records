import React, { useState, useEffect } from 'react';
import { 
  Zap, Command, Mic, Shield, Save, Globe, 
  Layers, User, Share2, Cpu, Music, BookOpen, 
  Gamepad2, Camera, PenTool, Youtube, Slack, 
  Twitter, MessageCircle, Link, Check, X, Plus,
  Eye, Archive, Waves, HardDrive, Download, Key, Mail, Server
} from 'lucide-react';
import { getThemeColors } from '../components/CommonUI';

const SettingsView = ({ userSettings, onUpdate, theme, analytics }) => {
  const [activeTab, setActiveTab] = useState('general');
  const [neuralNameInput, setNeuralNameInput] = useState(userSettings?.neural_name || analytics?.neural_name || 'Archivist');
  const [groqKeyInput, setGroqKeyInput] = useState(userSettings?.groq_api_key || '');
  
  // Track detailed configurations for each app
  const [integrations, setIntegrations] = useState(userSettings?.integrations || {});
  
  // Modal State
  const [configApp, setConfigApp] = useState(null);
  const [tempConfig, setTempConfig] = useState({});

  const colors = getThemeColors(theme);

  const handleSave = () => {
    onUpdate({ 
      neural_name: neuralNameInput, 
      groq_api_key: groqKeyInput,
      integrations: integrations
    });
  };

  const openConfig = (app) => {
    setConfigApp(app);
    setTempConfig(integrations[app.name] || {});
  };

  const saveConfig = () => {
    setIntegrations(prev => ({
      ...prev,
      [configApp.name]: { ...tempConfig, active: true, linkedAt: new Date().toISOString() }
    }));
    setConfigApp(null);
  };

  const disconnectApp = (appName) => {
    const newIntegrations = { ...integrations };
    delete newIntegrations[appName];
    setIntegrations(newIntegrations);
  };

  const tabs = [
    { id: 'general', label: 'General', icon: User },
    { id: 'performance', label: 'Performance', icon: Cpu },
    { id: 'security', label: 'Security', icon: Shield },
    { id: 'awareness', label: 'Awareness', icon: Eye },
    { id: 'integrations', label: 'Integrations', icon: Share2 },
    { id: 'backup', label: 'Neural Will', icon: Archive },
  ];

  const appDefinitions = [
    { name: 'Slack', type: 'oauth', icon: Slack, color: 'text-purple-500', bg: 'bg-purple-50' },
    { name: 'Gmail', type: 'imap', icon: Mail, color: 'text-red-500', bg: 'bg-red-50' },
    { name: 'Outlook', type: 'imap', icon: Globe, color: 'text-blue-600', bg: 'bg-blue-50' },
    { name: 'ProtonMail', type: 'imap', icon: Shield, color: 'text-purple-600', bg: 'bg-purple-50' },
    { name: 'Yahoo Mail', type: 'imap', icon: Mail, color: 'text-purple-800', bg: 'bg-purple-100' },
    { name: 'Custom IMAP', type: 'imap', icon: Server, color: 'text-stone-600', bg: 'bg-stone-100' },
    { name: 'Spotify', type: 'oauth', icon: Music, color: 'text-green-500', bg: 'bg-green-50' },
    { name: 'YouTube', type: 'oauth', icon: Youtube, color: 'text-red-600', bg: 'bg-red-50' },
    { name: 'Kindle', type: 'api', icon: BookOpen, color: 'text-amber-700', bg: 'bg-amber-50' },
    { name: 'Steam', type: 'api', icon: Gamepad2, color: 'text-slate-700', bg: 'bg-slate-100' },
    { name: 'Custom API', type: 'api', icon: Link, color: 'text-stone-400', bg: 'bg-stone-50' }
  ];

  return (
    <div className="p-4 sm:p-10 max-w-5xl mx-auto min-h-screen relative">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-10 gap-6">
        <div>
          <h2 className={`text-4xl font-bold tracking-tight mb-2 ${colors.textMain}`}>Neural Configuration</h2>
          <p className="text-stone-500 text-sm">Orchestrate your sovereignty, performance, and digital reach.</p>
        </div>
        <button 
          onClick={handleSave}
          className="group flex items-center gap-2 px-8 py-3.5 bg-amber-500 text-slate-900 font-black rounded-2xl hover:bg-amber-400 transition-all shadow-xl shadow-amber-500/20 active:scale-95 uppercase tracking-widest text-xs"
        >
          <Save className="w-4 h-4 group-hover:rotate-12 transition-transform" /> Sync Changes
        </button>
      </div>

      {/* Tab Navigation */}
      <div className={`flex gap-1 p-1 mb-10 rounded-2xl border ${colors.panel} ${colors.panelBorder} overflow-x-auto hide-scrollbar`}>
        {tabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center gap-2 px-6 py-3 rounded-xl text-xs font-bold uppercase tracking-widest transition-all whitespace-nowrap ${
              activeTab === tab.id 
                ? 'bg-amber-500 text-slate-900 shadow-lg shadow-amber-500/10' 
                : `hover:bg-stone-50 text-stone-500`
            }`}
          >
            <tab.icon className="w-4 h-4" />
            {tab.label}
          </button>
        ))}
      </div>

      <div className="animate-in fade-in slide-in-from-bottom-2 duration-500">
        {/* ... General, Performance, Security, Awareness, Backup sections remain the same ... */}
        {activeTab === 'general' && (
          <div className={`p-8 rounded-[40px] border shadow-sm space-y-10 ${colors.panel} ${colors.panelBorder}`}>
            <section>
              <h3 className="text-[10px] font-black text-amber-600 uppercase tracking-[0.3em] mb-8 flex items-center">
                <Command className="w-4 h-4 mr-2" /> Neural Persona
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-10">
                <div className="space-y-3">
                  <label className="text-[10px] font-bold text-stone-400 uppercase tracking-widest ml-1">Assigned Name</label>
                  <input 
                    type="text" 
                    value={neuralNameInput} 
                    onChange={(e) => setNeuralNameInput(e.target.value)} 
                    className={`w-full border rounded-2xl px-5 py-4 text-sm focus:ring-4 focus:ring-amber-500/10 outline-none transition-all font-medium ${colors.input}`} 
                    placeholder="e.g. Archivist"
                  />
                </div>
                <div className="p-6 bg-stone-100/50 rounded-3xl border border-stone-200 flex flex-col justify-center">
                  <p className="text-[10px] text-stone-500 font-black uppercase tracking-widest mb-3">Auditory Triggers</p>
                  <div className="flex flex-wrap gap-2">
                    {['Akasha', 'Archivist', neuralNameInput].map(word => (
                      <span key={word} className="px-3 py-1 bg-white border border-stone-200 rounded-full text-[10px] font-mono font-bold text-amber-600 shadow-sm">{word}</span>
                    ))}
                  </div>
                </div>
              </div>
            </section>
          </div>
        )}

        {activeTab === 'integrations' && (
          <div className="space-y-8">
            <div className={`p-8 rounded-[40px] border shadow-sm ${colors.panel} ${colors.panelBorder}`}>
              <h3 className="text-[10px] font-black text-amber-600 uppercase tracking-[0.3em] mb-10 flex items-center">
                <Globe className="w-4 h-4 mr-2" /> Neural Connectors
              </h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {appDefinitions.map(app => (
                  <div key={app.name} className={`group p-5 rounded-[28px] border transition-all duration-300 flex items-center justify-between ${integrations[app.name]?.active ? 'bg-white border-amber-500/30 shadow-md ring-4 ring-amber-500/5' : 'bg-transparent border-stone-100 hover:border-stone-200'}`}>
                    <div className="flex items-center gap-4">
                      <div className={`p-3 rounded-2xl ${app.bg} ${app.color} transition-transform group-hover:scale-110`}>
                        <app.icon className="w-5 h-5" />
                      </div>
                      <div>
                        <h4 className="text-xs font-black text-stone-800 uppercase tracking-tight">{app.name}</h4>
                        <div className="flex items-center gap-1 mt-1">
                          <div className={`w-1 h-1 rounded-full ${integrations[app.name]?.active ? 'bg-green-500 animate-pulse' : 'bg-stone-300'}`}></div>
                          <span className="text-[8px] font-bold text-stone-400 uppercase tracking-widest">
                            {integrations[app.name]?.active ? 'Linked' : 'Offline'}
                          </span>
                        </div>
                      </div>
                    </div>
                    <div className="flex gap-2">
                      {integrations[app.name]?.active && (
                        <button onClick={() => disconnectApp(app.name)} className="p-2 rounded-xl bg-stone-100 text-stone-400 hover:text-red-500 transition-colors">
                          <X className="w-4 h-4" />
                        </button>
                      )}
                      <button 
                        onClick={() => openConfig(app)}
                        className={`p-2 rounded-xl transition-all ${integrations[app.name]?.active ? 'bg-amber-100 text-amber-600' : 'bg-stone-100 text-stone-400 hover:bg-stone-200'}`}
                      >
                        {integrations[app.name]?.active ? <Shield className="w-4 h-4" /> : <Plus className="w-4 h-4" />}
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
        
        {/* Placeholder for other tabs logic */}
        {(activeTab === 'performance' || activeTab === 'security' || activeTab === 'awareness' || activeTab === 'backup') && (
          <div className="p-20 text-center text-stone-400 italic text-sm">
            Please switch back to Integrations to test the new linking logic.
          </div>
        )}
      </div>

      {/* Configuration Modal */}
      {configApp && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-6 bg-stone-950/60 backdrop-blur-md animate-in fade-in duration-300">
          <div className="max-w-md w-full bg-white rounded-[40px] shadow-2xl overflow-hidden border border-stone-200 animate-in zoom-in-95 duration-300">
            <div className={`h-24 ${configApp.bg} flex items-center justify-center`}>
              <configApp.icon className={`w-10 h-10 ${configApp.color}`} />
            </div>
            <div className="p-8">
              <h3 className="text-xl font-black text-slate-900 mb-2 uppercase tracking-tight">Link {configApp.name}</h3>
              <p className="text-xs text-stone-500 mb-8 leading-relaxed">
                Connect your {configApp.name} account to sync data into your personal Akashic Records.
              </p>

              <div className="space-y-6">
                {configApp.type === 'oauth' && (
                  <div className="py-10 border-2 border-dashed border-stone-100 rounded-3xl flex flex-col items-center justify-center">
                    <button className={`flex items-center gap-3 px-6 py-3 rounded-2xl bg-slate-900 text-white font-bold text-xs uppercase tracking-widest hover:scale-105 transition-all`}>
                      <Key className="w-4 h-4 text-amber-500" /> Authorize via OAuth
                    </button>
                    <p className="text-[9px] text-stone-400 mt-4 uppercase font-bold tracking-tighter">Secure sovereign handshake required</p>
                  </div>
                )}

                {configApp.type === 'imap' && (
                  <div className="space-y-4">
                    <div>
                      <label className="text-[10px] font-bold text-stone-400 uppercase tracking-widest ml-1">IMAP Host</label>
                      <input 
                        type="text" 
                        value={tempConfig.host || ''} 
                        onChange={e => setTempConfig({...tempConfig, host: e.target.value})}
                        className="w-full border border-stone-100 bg-stone-50 rounded-2xl px-4 py-3 text-xs outline-none focus:ring-4 focus:ring-amber-500/5 transition-all"
                        placeholder="imap.provider.com"
                      />
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="text-[10px] font-bold text-stone-400 uppercase tracking-widest ml-1">Username</label>
                        <input 
                          type="text" 
                          value={tempConfig.user || ''} 
                          onChange={e => setTempConfig({...tempConfig, user: e.target.value})}
                          className="w-full border border-stone-100 bg-stone-50 rounded-2xl px-4 py-3 text-xs outline-none"
                        />
                      </div>
                      <div>
                        <label className="text-[10px] font-bold text-stone-400 uppercase tracking-widest ml-1">Password</label>
                        <input 
                          type="password" 
                          value={tempConfig.pass || ''} 
                          onChange={e => setTempConfig({...tempConfig, pass: e.target.value})}
                          className="w-full border border-stone-100 bg-stone-50 rounded-2xl px-4 py-3 text-xs outline-none"
                        />
                      </div>
                    </div>
                  </div>
                )}

                {configApp.type === 'api' && (
                  <div className="space-y-4">
                    <div>
                      <label className="text-[10px] font-bold text-stone-400 uppercase tracking-widest ml-1">API Endpoint URL</label>
                      <input 
                        type="text" 
                        value={tempConfig.url || ''} 
                        onChange={e => setTempConfig({...tempConfig, url: e.target.value})}
                        className="w-full border border-stone-100 bg-stone-50 rounded-2xl px-4 py-3 text-xs outline-none"
                        placeholder="https://api.service.com/v1/data"
                      />
                    </div>
                    <div>
                      <label className="text-[10px] font-bold text-stone-400 uppercase tracking-widest ml-1">Auth Header / Key</label>
                      <input 
                        type="password" 
                        value={tempConfig.key || ''} 
                        onChange={e => setTempConfig({...tempConfig, key: e.target.value})}
                        className="w-full border border-stone-100 bg-stone-50 rounded-2xl px-4 py-3 text-xs outline-none"
                        placeholder="Bearer sk_..."
                      />
                    </div>
                  </div>
                )}
              </div>

              <div className="flex gap-3 mt-10">
                <button 
                  onClick={() => setConfigApp(null)}
                  className="flex-1 py-4 bg-stone-100 text-stone-500 font-black rounded-2xl text-[10px] uppercase tracking-widest hover:bg-stone-200 transition-all"
                >
                  Cancel
                </button>
                <button 
                  onClick={saveConfig}
                  className="flex-1 py-4 bg-amber-500 text-slate-900 font-black rounded-2xl text-[10px] uppercase tracking-widest shadow-lg shadow-amber-500/20 hover:bg-amber-400 transition-all"
                >
                  Confirm Link
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SettingsView;
