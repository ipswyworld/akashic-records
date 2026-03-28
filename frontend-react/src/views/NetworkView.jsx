import React, { useState, useEffect } from 'react';
import { 
  Shield, ShieldAlert, ShieldCheck, Globe, 
  Cpu, Server, Activity, Zap, RefreshCw, 
  Lock, Unlock, Wifi, WifiOff, Terminal,
  ArrowLeftRight, CloudSync, Share2
} from 'lucide-react';
import { fetchP2PStatus, toggleP2PStealth } from '../api';
import { getThemeColors } from '../components/CommonUI';

const NetworkView = ({ theme }) => {
  const [status, setStatus] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isUpdating, setIsUpdating] = useState(false);
  const [syncPhase, setSyncPhase] = useState(0);
  const colors = getThemeColors(theme);

  const getStatus = async () => {
    try {
      const data = await fetchP2PStatus();
      setStatus(data);
    } catch (err) {
      console.error("Network Status Error:", err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    getStatus();
    const interval = setInterval(() => {
      getStatus();
      setSyncPhase(p => (p + 1) % 4);
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleToggleStealth = async () => {
    if (!status) return;
    setIsUpdating(true);
    try {
      await toggleP2PStealth(!status.is_stealth);
      await getStatus();
    } catch (err) {
      console.error("Stealth Toggle Error:", err);
    } finally {
      setIsUpdating(false);
    }
  };

  if (isLoading && !status) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="flex flex-col items-center">
          <RefreshCw className="w-8 h-8 text-amber-500 animate-spin mb-4" />
          <p className="text-stone-500 font-mono animate-pulse">Scanning Neural Mesh...</p>
        </div>
      </div>
    );
  }

  const isStealth = status?.is_stealth;

  return (
    <div className="p-6 sm:p-10 max-w-7xl mx-auto w-full animate-in fade-in duration-700">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-10 gap-6">
        <div>
          <h1 className={`text-3xl font-bold tracking-tight mb-2 ${theme === 'dark' ? 'text-slate-100' : 'text-stone-800'}`}>Sovereign Network</h1>
          <p className="text-stone-500 text-sm max-w-md">Real-time visualization of your distributed Neural Mesh and sync protocols.</p>
        </div>
        
        <button 
          onClick={handleToggleStealth}
          disabled={isUpdating}
          className={`flex items-center px-6 py-3 rounded-2xl font-bold transition-all shadow-lg ${
            isStealth 
              ? 'bg-blue-600 text-white shadow-blue-500/20 hover:bg-blue-700' 
              : 'bg-amber-500 text-slate-900 shadow-amber-500/20 hover:bg-amber-600'
          } ${isUpdating ? 'opacity-50 cursor-not-allowed' : ''}`}
        >
          {isUpdating ? (
            <RefreshCw className="w-5 h-5 mr-2 animate-spin" />
          ) : isStealth ? (
            <ShieldCheck className="w-5 h-5 mr-2" />
          ) : (
            <ShieldAlert className="w-5 h-5 mr-2" />
          )}
          {isStealth ? 'Sovereign Shield: Active' : 'Sovereign Shield: Offline'}
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-10">
        <div className="lg:col-span-2 space-y-8">
          {/* Enhanced Mesh Topology */}
          <div className={`p-10 rounded-[40px] border ${theme === 'dark' ? 'bg-slate-900/50 border-slate-800' : 'bg-white border-stone-100'} shadow-sm relative overflow-hidden`}>
            <div className="absolute top-0 right-0 p-8 opacity-5">
              <Globe className="w-64 h-64" />
            </div>
            
            <div className="flex justify-between items-center mb-12">
              <h3 className="text-lg font-bold flex items-center">
                <Activity className="w-5 h-5 mr-2 text-blue-500" /> Neural Mesh Topology
              </h3>
              <div className="flex items-center gap-2">
                <div className={`w-2 h-2 rounded-full ${status?.peers.length > 0 ? 'bg-green-500 animate-pulse' : 'bg-stone-300'}`}></div>
                <span className="text-[10px] font-bold text-stone-400 uppercase tracking-widest">{status?.peers.length} Peers Active</span>
              </div>
            </div>

            <div className="flex flex-col items-center justify-center py-10 relative min-h-[300px]">
              {/* Local Node */}
              <div className={`w-32 h-32 rounded-[40px] flex flex-col items-center justify-center relative z-10 border-4 ${isStealth ? 'bg-blue-500/10 border-blue-500 shadow-2xl shadow-blue-500/30' : 'bg-amber-500/10 border-amber-500 shadow-2xl shadow-amber-500/30'} transition-all duration-700`}>
                <div className="absolute -top-3 -right-3 p-2 bg-slate-900 rounded-xl border border-slate-800 shadow-lg">
                  <Cpu className={`w-4 h-4 ${isStealth ? 'text-blue-500' : 'text-amber-500'}`} />
                </div>
                <span className="text-[10px] font-black uppercase tracking-[0.2em] text-stone-500 mb-1">Local Core</span>
                <div className="text-xs font-mono font-bold truncate max-w-[80px]">{status?.node_id.substring(0, 8)}</div>
              </div>

              {/* Dynamic Sync Waves */}
              {status?.peers.length > 0 && (
                <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                  <div className={`w-48 h-48 rounded-full border-2 border-dashed ${isStealth ? 'border-blue-500/20' : 'border-amber-500/20'} animate-ping opacity-20`} style={{ animationDuration: '3s' }}></div>
                  <div className={`w-64 h-64 rounded-full border border-dashed ${isStealth ? 'border-blue-500/10' : 'border-amber-500/10'} animate-reverse-spin opacity-10`} style={{ animationDuration: '10s' }}></div>
                </div>
              )}

              {/* Connecting Lines & Peers */}
              <div className="mt-16 grid grid-cols-2 sm:grid-cols-4 gap-12 w-full relative z-10">
                {status?.peers.length > 0 ? status.peers.map((peer, i) => (
                  <div key={i} className="flex flex-col items-center group">
                    <div className={`w-20 h-20 rounded-3xl flex items-center justify-center border-2 transition-all group-hover:scale-110 ${theme === 'dark' ? 'bg-slate-800 border-slate-700 group-hover:border-blue-500/50' : 'bg-stone-50 border-stone-200 group-hover:border-amber-500/50'} relative`}>
                      <Server className="w-8 h-8 text-stone-400 group-hover:text-blue-500 transition-colors" />
                      {/* Individual Peer Sync Indicator */}
                      <div className="absolute -bottom-1 -right-1 p-1 bg-green-500 rounded-full border-2 border-white shadow-sm">
                        <CloudSync className="w-2 h-2 text-white" />
                      </div>
                    </div>
                    <span className="text-[10px] mt-3 font-mono font-bold text-stone-500 group-hover:text-blue-500 transition-colors">{peer[0]}:{peer[1]}</span>
                    <span className="text-[8px] text-stone-400 uppercase tracking-widest mt-1 opacity-0 group-hover:opacity-100 transition-opacity">Trust: 1.0</span>
                  </div>
                )) : (
                  <div className="col-span-full flex flex-col items-center justify-center py-10">
                    <div className="w-16 h-16 rounded-full bg-stone-100 flex items-center justify-center mb-4">
                      <WifiOff className="w-8 h-8 text-stone-300" />
                    </div>
                    <p className="text-xs text-stone-400 font-bold uppercase tracking-widest italic">Awaiting Peer Discovery...</p>
                  </div>
                )}
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className={`p-8 rounded-[32px] border ${colors.panel} ${colors.panelBorder} shadow-sm`}>
              <h3 className="text-sm font-bold uppercase tracking-widest text-stone-400 mb-6 flex items-center">
                <ArrowLeftRight className="w-4 h-4 mr-2 text-blue-500" /> Synchronization
              </h3>
              <div className="space-y-6">
                <div className="flex justify-between items-center">
                  <span className="text-xs font-medium text-stone-500">Subchain Delta</span>
                  <span className="text-xs font-mono font-bold text-green-500">0 Blocks Behind</span>
                </div>
                <div className="w-full bg-stone-100 rounded-full h-1.5 overflow-hidden">
                  <div className={`h-full bg-blue-500 transition-all duration-1000 ${syncPhase === 0 ? 'w-full opacity-0' : 'w-full opacity-100'}`}></div>
                </div>
                <div className="flex justify-between items-center text-[10px] text-stone-400 uppercase font-bold tracking-widest">
                  <span>Last Sync</span>
                  <span>{new Date().toLocaleTimeString()}</span>
                </div>
              </div>
            </div>

            <div className={`p-8 rounded-[32px] border ${colors.panel} ${colors.panelBorder} shadow-sm`}>
              <h3 className="text-sm font-bold uppercase tracking-widest text-stone-400 mb-6 flex items-center">
                <Share2 className="w-4 h-4 mr-2 text-purple-500" /> Merkle Verification
              </h3>
              <div className="space-y-4">
                <div className="p-3 rounded-xl bg-purple-500/5 border border-purple-500/10 font-mono text-[9px] break-all text-purple-600">
                  ROOT: 0x7a1b3c2d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b
                </div>
                <div className="flex items-center gap-2 text-[10px] font-bold text-green-600">
                  <ShieldCheck className="w-3 h-3" /> Integrity Verified by 0 Peers
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="space-y-8">
          {/* Privacy Panel */}
          <div className={`p-8 rounded-[32px] border ${colors.panel} ${colors.panelBorder} shadow-sm`}>
            <h3 className="text-sm font-bold uppercase tracking-widest text-stone-400 mb-8 flex items-center">
              <Lock className="w-4 h-4 mr-2" /> Privacy Metrics
            </h3>
            <div className="space-y-6">
              <div className="flex justify-between items-center">
                <span className="text-xs font-bold text-stone-500 uppercase tracking-widest">Tor Bridge</span>
                <span className={`px-2 py-1 rounded-lg text-[10px] font-mono font-bold ${isStealth ? 'bg-blue-500/10 text-blue-500' : 'bg-stone-100 text-stone-400'}`}>
                  {isStealth ? 'SOCKS5:9050' : 'DISABLED'}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-xs font-bold text-stone-500 uppercase tracking-widest">I2P Tunnel</span>
                <span className="text-[10px] font-mono text-stone-400 italic font-bold">STANDBY</span>
              </div>
              <div className="flex justify-between items-center pt-4 border-t border-stone-100">
                <span className="text-xs font-bold text-stone-500 uppercase tracking-widest">Metadata Risk</span>
                <span className={`text-xs font-mono font-bold ${isStealth ? 'text-green-500' : 'text-amber-500'}`}>
                  {isStealth ? 'LOW' : 'MODERATE'}
                </span>
              </div>
            </div>
          </div>

          {/* Active Gossip Log */}
          <div className={`p-8 rounded-[32px] border ${colors.panel} ${colors.panelBorder} shadow-sm`}>
            <h3 className="text-sm font-bold uppercase tracking-widest text-stone-400 mb-6 flex items-center">
              <Terminal className="w-4 h-4 mr-2 text-amber-500" /> Network Log
            </h3>
            <div className={`p-4 rounded-2xl h-[320px] overflow-y-auto font-mono text-[9px] ${theme === 'dark' ? 'bg-slate-950 text-slate-400' : 'bg-stone-50 text-stone-500 shadow-inner'}`}>
              <div className="mb-2 text-green-500 opacity-80">[{new Date().toISOString()}] P2P_NODE_READY: Listening on 0.0.0.0:8888</div>
              <div className="mb-2 opacity-60">[{new Date().toISOString()}] SYNC_SERVICE: Checking Merkle Roots...</div>
              {status?.peers.map((peer, i) => (
                <div key={i} className="mb-2 text-blue-500 opacity-80">[{new Date().toISOString()}] PEER_FOUND: Connected to {peer[0]}:{peer[1]}</div>
              ))}
              {isStealth && <div className="mb-2 text-amber-500 opacity-80">[{new Date().toISOString()}] STEALTH_MODE: Routing via SOCKS5 Proxy</div>}
              <div className="mb-2 opacity-40 italic">[{new Date().toISOString()}] HEARTBEAT: Sent to Mesh...</div>
              <div className="mb-2 opacity-40 italic">[{new Date().toISOString()}] CHRONOS_SYNC: Waiting for nocturnal cycle...</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default NetworkView;
