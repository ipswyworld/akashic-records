import React, { useState, useEffect } from 'react';
import { Zap } from 'lucide-react';
import { getThemeColors } from '../components/CommonUI';
import { fetchActionHistory, runActionGoal } from '../api';

const ButlerView = ({ theme }) => {
  const [goal, setGoal] = useState('');
  const [isRunning, setIsRunning] = useState(false);
  const [history, setHistory] = useState([]);
  const colors = getThemeColors(theme);

  const refreshHistory = () => fetchActionHistory().then(setHistory).catch(console.error);
  useEffect(() => { refreshHistory(); }, []);

  const handleRun = async () => {
    if (!goal.trim()) return;
    setIsRunning(true);
    try {
      await runActionGoal(goal);
      setGoal('');
      refreshHistory();
    } catch (err) { console.error(err); } finally { setIsRunning(false); }
  };

  return (
    <div className="p-4 sm:p-6 w-full max-w-4xl mx-auto animate-in fade-in duration-500 space-y-8">
      <div className="mb-6">
        <h2 className={`text-xl sm:text-2xl font-light flex items-center ${colors.textMain}`}>
          <Zap className="w-5 h-5 sm:w-6 sm:h-6 mr-3 text-amber-500" /> Executive Butler
        </h2>
        <p className="text-stone-500 text-sm mt-1">Autonomous tool execution and real-world interventions.</p>
      </div>

      <div className={`p-6 rounded-2xl border shadow-sm ${colors.panel} ${colors.panelBorder}`}>
        <div className="flex gap-2">
          <input 
            type="text" 
            value={goal} 
            onChange={(e) => setGoal(e.target.value)}
            placeholder="Set a goal for the Butler (e.g., 'Organize my recent downloads')"
            className={`flex-1 p-3 rounded-xl border focus:outline-none focus:ring-2 focus:ring-amber-500/20 transition-all ${colors.input}`}
          />
          <button 
            onClick={handleRun} 
            disabled={!goal.trim() || isRunning}
            className={`px-6 py-2 rounded-xl font-bold transition-all ${goal.trim() && !isRunning ? 'bg-amber-500 text-white shadow-lg' : 'bg-stone-200 text-stone-400'}`}
          >
            {isRunning ? 'Acting...' : 'Execute'}
          </button>
        </div>
      </div>

      <div className="space-y-4">
        <h3 className={`text-sm font-semibold uppercase tracking-wider ${colors.textMuted}`}>Action History</h3>
        <div className="space-y-3">
          {history.length > 0 ? history.map((action, i) => (
            <div key={i} className={`p-4 rounded-xl border ${colors.panel} ${colors.panelBorder} shadow-sm`}>
              <div className="flex justify-between items-start mb-2">
                <div className="flex items-center gap-2">
                  <span className="px-2 py-0.5 bg-amber-500/10 text-amber-600 text-[10px] font-bold rounded uppercase">{action.tool}</span>
                  <span className={`text-xs font-medium ${colors.textMain}`}>{action.agent}</span>
                </div>
                <span className="text-[10px] text-stone-400">{new Date(action.timestamp).toLocaleString()}</span>
              </div>
              <p className={`text-xs ${colors.textMuted} font-mono bg-stone-50 p-2 rounded border border-stone-100`}>Result: {action.result}</p>
            </div>
          )) : <p className="text-center p-8 text-stone-400 italic">No actions executed yet.</p>}
        </div>
      </div>
    </div>
  );
};

export default ButlerView;
