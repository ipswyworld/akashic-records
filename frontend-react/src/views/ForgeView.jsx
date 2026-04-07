import React, { useState, useEffect } from 'react';
import { 
  Sparkles, Hammer, Cpu, Zap, AlertCircle, Check, 
  Terminal, Code, RefreshCw, Layers, Bug, Info
} from 'lucide-react';
import { triggerMutation, fetchNeuralSkills } from '../api';
import { getThemeColors } from '../components/CommonUI';

const ForgeView = ({ theme }) => {
  const [skills, setSkills] = useState([]);
  const [filePath, setFilePath] = useState('backend/librarians.py');
  const [instruction, setInstruction] = useState('');
  const [isForging, setIsForging] = useState(false);
  const [status, setStatus] = useState(null);
  
  // --- Phase 2: Macro Recording State ---
  const [isRecording, setIsRecording] = useState(false);
  const [recordGoal, setRecordGoal] = useState('');
  // --------------------------------------

  const colors = getThemeColors(theme);

  const getSkills = async () => {
    try {
      const data = await fetchNeuralSkills();
      setSkills(data);
    } catch (err) { console.error(err); }
  };

  useEffect(() => { getSkills(); }, []);

  const handleForge = async () => {
    if (!instruction) return;
    setIsForging(true);
    setStatus({ type: 'info', message: 'Initiating Darwinian Mutation loop...' });
    try {
      const res = await triggerMutation(filePath, instruction);
      if (res.status === 'SUCCESS') {
        setStatus({ type: 'success', message: res.message });
        getSkills();
      } else {
        setStatus({ type: 'error', message: res.message });
      }
    } catch (err) {
      setStatus({ type: 'error', message: 'Forge failure: Connection lost.' });
    } finally {
      setIsForging(false);
    }
  };

  // --- Phase 2: Macro Recording Logic ---
  const toggleRecording = async () => {
    if (!isRecording) {
      // Start Recording
      try {
        const res = await fetch('http://localhost:8001/forge/record/start', {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${localStorage.getItem('akasha_token')}` }
        });
        if (res.ok) {
          setIsRecording(true);
          setStatus({ type: 'info', message: 'Neural Recording ACTIVE. Perform tasks now.' });
        }
      } catch (err) { console.error(err); }
    } else {
      // Stop Recording
      setIsForging(true);
      setStatus({ type: 'info', message: 'Distilling neural steps into code...' });
      try {
        const res = await fetch('http://localhost:8001/forge/record/stop', {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${localStorage.getItem('akasha_token')}` }
        });
        const data = await res.json();
        if (data.status === 'SUCCESS') {
          setIsRecording(false);
          setStatus({ type: 'success', message: `Successfully forged skill: ${data.skill.name}` });
          getSkills();
        } else {
          setStatus({ type: 'error', message: data.message });
        }
      } catch (err) { console.error(err); } finally { setIsForging(false); }
    }
  };
  // --------------------------------------

  return (
    <div className="p-6 sm:p-10 max-w-7xl mx-auto w-full animate-in fade-in duration-700">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-10 gap-6">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-amber-500 rounded-xl shadow-lg shadow-amber-500/20 text-slate-900">
              <Hammer className="w-6 h-6" />
            </div>
            <h1 className={`text-3xl font-bold tracking-tight ${theme === 'dark' ? 'text-slate-100' : 'text-stone-800'}`}>Neural Forge</h1>
          </div>
          <p className="text-stone-500 text-sm max-w-md">Evolve Akasha's source code through Darwinian mutation or record macros.</p>
        </div>

        {/* --- Macro Recorder Widget --- */}
        <div className={`p-4 rounded-2xl border ${colors.panel} ${colors.panelBorder} flex items-center gap-4 shadow-sm`}>
          <div className="flex flex-col">
            <span className="text-[10px] font-bold text-stone-400 uppercase tracking-widest">Macro Recorder</span>
            <span className={`text-[8px] font-bold ${isRecording ? 'text-rose-500 animate-pulse' : 'text-stone-400'}`}>
              {isRecording ? 'RECORDING ACTIVE' : 'SYSTEM IDLE'}
            </span>
          </div>
          <button 
            onClick={toggleRecording}
            className={`p-3 rounded-full transition-all ${isRecording ? 'bg-rose-500 text-white shadow-lg shadow-rose-500/20' : 'bg-stone-100 text-stone-400'}`}
          >
            {isRecording ? <Zap className="w-4 h-4" /> : <Layers className="w-4 h-4" />}
          </button>
        </div>
        {/* ---------------------------- */}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-10">
        <div className="lg:col-span-2 space-y-8">
          {/* Mutation Console */}
          <div className={`p-8 rounded-[32px] border ${colors.panel} ${colors.panelBorder} shadow-sm relative overflow-hidden`}>
            <div className="absolute top-0 right-0 p-8 opacity-5">
              <Cpu className="w-48 h-48 text-amber-500" />
            </div>
            
            <h3 className="text-sm font-bold text-stone-400 uppercase tracking-widest mb-8 flex items-center">
              <Terminal className="w-4 h-4 mr-2 text-amber-500" /> Mutation Console
            </h3>

            <div className="space-y-6 relative z-10">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="text-[10px] uppercase font-bold text-stone-500 block mb-2 tracking-widest">Target Core File</label>
                  <select 
                    value={filePath} 
                    onChange={(e) => setFilePath(e.target.value)}
                    className={`w-full p-3 rounded-xl border font-mono text-xs ${colors.input}`}
                  >
                    <option value="backend/librarians.py">librarians.py (The Brain)</option>
                    <option value="backend/ai_engine.py">ai_engine.py (Neural Core)</option>
                    <option value="backend/action_engine.py">action_engine.py (Hands)</option>
                    <option value="backend/main.py">main.py (System Entry)</option>
                  </select>
                </div>
                <div>
                  <label className="text-[10px] uppercase font-bold text-stone-500 block mb-2 tracking-widest">Evolution Strategy</label>
                  <div className={`p-3 rounded-xl border bg-amber-500/5 border-amber-500/20 text-amber-600 text-[10px] font-bold flex items-center`}>
                    <Sparkles className="w-3 h-3 mr-2" /> DARWINIAN_SELECTION_V3 (ACTIVE)
                  </div>
                </div>
              </div>

              <div>
                <label className="text-[10px] uppercase font-bold text-stone-500 block mb-2 tracking-widest">Evolution Instruction</label>
                <textarea 
                  value={instruction}
                  onChange={(e) => setInstruction(e.target.value)}
                  placeholder="e.g., 'Make the Head Archivist more efficient at routing tasks' or 'Add a new sub-agent for financial data analysis'..."
                  className={`w-full p-4 rounded-2xl border min-h-[120px] text-sm focus:ring-2 focus:ring-amber-500/20 outline-none transition-all ${colors.input}`}
                />
              </div>

              {status && (
                <div className={`p-4 rounded-2xl flex items-start gap-3 animate-in slide-in-from-left-2 duration-300 ${
                  status.type === 'success' ? 'bg-green-500/10 text-green-600 border border-green-500/20' : 
                  status.type === 'error' ? 'bg-rose-500/10 text-rose-600 border border-rose-500/20' : 
                  'bg-blue-500/10 text-blue-600 border border-blue-500/20'
                }`}>
                  {status.type === 'success' ? <Check className="w-4 h-4 mt-0.5" /> : 
                   status.type === 'error' ? <AlertCircle className="w-4 h-4 mt-0.5" /> : 
                   <RefreshCw className="w-4 h-4 mt-0.5 animate-spin" />}
                  <span className="text-xs font-medium">{status.message}</span>
                </div>
              )}

              <button 
                onClick={handleForge}
                disabled={isForging || !instruction}
                className={`w-full py-4 bg-amber-500 hover:bg-amber-600 text-slate-900 font-bold rounded-2xl flex items-center justify-center transition-all shadow-lg shadow-amber-500/10 disabled:opacity-50 active:scale-[0.98]`}
              >
                {isForging ? (
                  <>
                    <RefreshCw className="w-5 h-5 mr-2 animate-spin" />
                    Simulating Population...
                  </>
                ) : (
                  <>
                    <Zap className="w-5 h-5 mr-2" />
                    Forge Mutation
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Evolution Stats */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className={`p-6 rounded-3xl border ${colors.panel} ${colors.panelBorder} shadow-sm`}>
              <div className="flex items-center gap-3 mb-4">
                <Layers className="w-4 h-4 text-blue-500" />
                <span className="text-[10px] font-bold text-stone-400 uppercase tracking-widest">Ghost Branch</span>
              </div>
              <div className="text-2xl font-mono font-bold">READY</div>
              <div className="text-[10px] text-stone-500 mt-1 italic">Sandboxed sandbox initialized.</div>
            </div>
            <div className={`p-6 rounded-3xl border ${colors.panel} ${colors.panelBorder} shadow-sm`}>
              <div className="flex items-center gap-3 mb-4">
                <Bug className="w-4 h-4 text-rose-500" />
                <span className="text-[10px] font-bold text-stone-400 uppercase tracking-widest">Selection Bias</span>
              </div>
              <div className="text-2xl font-mono font-bold text-green-500">OPTIMAL</div>
              <div className="text-[10px] text-stone-500 mt-1 italic">Fitness weight: 0.85 Accuracy.</div>
            </div>
            <div className={`p-6 rounded-3xl border ${colors.panel} ${colors.panelBorder} shadow-sm`}>
              <div className="flex items-center gap-3 mb-4">
                <Info className="w-4 h-4 text-amber-500" />
                <span className="text-[10px] font-bold text-stone-400 uppercase tracking-widest">Mutations Run</span>
              </div>
              <div className="text-2xl font-mono font-bold">14</div>
              <div className="text-[10px] text-stone-500 mt-1 italic">Total system evolutions.</div>
            </div>
          </div>
        </div>

        <div className="space-y-8">
          {/* Skill Library */}
          <div className={`p-8 rounded-[32px] border ${colors.panel} ${colors.panelBorder} shadow-sm min-h-full`}>
            <h3 className="text-sm font-bold text-stone-400 uppercase tracking-widest mb-8 flex items-center">
              <Code className="w-4 h-4 mr-2 text-purple-500" /> Neural Skill Store
            </h3>
            
            <div className="space-y-4">
              {skills.length > 0 ? skills.map((skill, i) => (
                <div key={skill.id} className={`p-4 rounded-2xl border group transition-all hover:border-amber-500/50 ${theme === 'dark' ? 'bg-slate-800/30 border-slate-700' : 'bg-stone-50 border-stone-100'}`}>
                  <div className="flex justify-between items-start mb-2">
                    <span className="text-xs font-bold font-mono text-amber-600">{skill.name}</span>
                    <span className="px-2 py-0.5 bg-amber-500/10 text-amber-600 rounded-full text-[8px] font-bold uppercase tracking-widest">FORGED</span>
                  </div>
                  <p className="text-[10px] text-stone-500 mb-4 line-clamp-2">{skill.description}</p>
                  <div className="flex items-center justify-between">
                    <span className="text-[8px] font-mono text-stone-400">Success: {skill.success_count}x</span>
                    <button className="text-[10px] font-bold text-blue-500 hover:text-blue-600 flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                      View Source <Code className="w-3 h-3" />
                    </button>
                  </div>
                </div>
              )) : (
                <div className="flex flex-col items-center justify-center py-20 text-center opacity-40">
                  <Cpu className="w-10 h-10 mb-4 text-stone-300" />
                  <p className="text-xs italic text-stone-400 max-w-[120px]">Awaiting the first forged capability.</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ForgeView;
