import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Activity, Brain, Database, Zap, Clock, 
  BarChart3, RefreshCw, AlertCircle, CheckCircle2,
  Cpu, Layers, HardDrive, Search
} from 'lucide-react';

const TrainingView = ({ theme }) => {
  const [status, setStatus] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isRetraining, setIsRetraining] = useState(false);
  const [error, setError] = useState(null);

  const fetchStatus = async () => {
    try {
      const response = await fetch('http://localhost:8001/analytics/training/status', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('akasha_token')}`
        }
      });
      if (!response.ok) throw new Error('Neural core connection failed');
      const data = await response.json();
      setStatus(data);
      setError(null);
    } catch (err) {
      console.error("Dashboard Fetch Error:", err);
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRetrain = async () => {
    setIsRetraining(true);
    try {
      const response = await fetch('http://localhost:8001/user/training/retrain', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('akasha_token')}`
        },
        body: JSON.stringify({ all_artifacts: true })
      });
      if (!response.ok) throw new Error('Failed to initiate retraining');
      // Success - status will update via interval
    } catch (err) {
      setError("Failed to initiate retraining. Is the backend restarted?");
    } finally {
      setIsRetraining(false);
    }
  };

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 5000); // Faster refresh for training
    return () => clearInterval(interval);
  }, []);

  if (isLoading && !status) return <div className="flex h-full items-center justify-center"><Zap className="w-8 h-8 text-amber-500 animate-pulse" /></div>;

  return (
    <div className="flex flex-col h-full bg-stone-50 p-6 overflow-hidden custom-scrollbar">
      <header className="mb-8 flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-serif text-stone-800">Neural Dashboard</h1>
          <p className="text-stone-500 font-sans italic">Transparency in the silicon ego: Oversight of all training and ingestion.</p>
        </div>
        
        <div className="flex items-center gap-4">
          <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-[10px] font-bold uppercase tracking-wider border shadow-sm ${error ? 'bg-red-50 text-red-500 border-red-100' : 'bg-green-50 text-green-600 border-green-100'}`}>
            <div className={`w-1.5 h-1.5 rounded-full ${error ? 'bg-red-500 animate-pulse' : 'bg-green-500'}`} />
            {error ? 'Neural Core Offline' : 'Neural Core Online'}
          </div>

          <button 
            onClick={handleRetrain}
            disabled={isRetraining}
            className={`flex items-center gap-2 px-5 py-2.5 rounded-2xl border transition-all font-sans text-sm font-bold shadow-sm
              ${isRetraining 
                ? 'bg-stone-100 text-stone-400 border-stone-200 cursor-not-allowed' 
                : 'bg-stone-800 text-white border-stone-800 hover:bg-stone-700 active:scale-95'}`}
          >
            {isRetraining ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Brain className="w-4 h-4" />}
            {isRetraining ? 'Neural Recalibration...' : 'Retrain Library'}
          </button>
          
          <div className="bg-white px-4 py-2 rounded-2xl border border-stone-200 shadow-sm flex items-center gap-3">
            <div className="flex flex-col items-end">
              <span className="text-[10px] font-bold text-stone-400 uppercase tracking-widest">Core Status</span>
              <span className="text-sm font-mono font-bold text-green-500">{isRetraining ? 'RETRAINING' : 'OPTIMIZING'}</span>
            </div>
            <RefreshCw className={`w-5 h-5 text-amber-500 ${isRetraining ? 'animate-spin' : 'animate-spin-slow'}`} />
          </div>
        </div>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        <StatusCard 
          icon={Database} 
          title="Data Harvest" 
          value={status?.recent_data_ingested?.length || 0} 
          subtitle="Recent Artifacts" 
          color="blue"
        />
        <StatusCard 
          icon={Brain} 
          title="Agent Fitness" 
          value={status?.agent_performance?.length > 0 ? `${Math.round(status.agent_performance[0].fitness * 100)}%` : '0%'} 
          subtitle="Avg Success Rate" 
          color="amber"
        />
        <StatusCard 
          icon={Activity} 
          title="Neural Latency" 
          value={status?.agent_performance?.length > 0 ? `${status.agent_performance[0].latency}ms` : '0ms'} 
          subtitle="Inference Speed" 
          color="purple"
        />
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-8 flex-1 overflow-hidden">
        {/* Ingestion Stream */}
        <section className="flex flex-col bg-white rounded-3xl border border-stone-200 shadow-sm overflow-hidden">
          <div className="p-6 border-b border-stone-100 flex justify-between items-center">
            <h2 className="text-lg font-bold text-stone-800 flex items-center gap-2">
              <Layers className="w-5 h-5 text-blue-500" />
              Ingestion Stream
            </h2>
            <span className="text-[10px] font-bold text-stone-400 uppercase tracking-widest">Dataset Monitoring</span>
          </div>
          <div className="flex-1 overflow-y-auto p-6 space-y-4 custom-scrollbar">
            {status?.recent_data_ingested?.map((event, i) => (
              <IngestionItem key={i} event={event} />
            ))}
            {(!status?.recent_data_ingested || status.recent_data_ingested.length === 0) && (
              <div className="text-center py-20 text-stone-300 italic">No recent ingestion data detected. Click 'Retrain' to see activity.</div>
            )}
          </div>
        </section>

        {/* Agent Performance */}
        <section className="flex flex-col bg-white rounded-3xl border border-stone-200 shadow-sm overflow-hidden">
          <div className="p-6 border-b border-stone-100 flex justify-between items-center">
            <h2 className="text-lg font-bold text-stone-800 flex items-center gap-2">
              <Cpu className="w-5 h-5 text-amber-500" />
              Agent Evolution
            </h2>
            <span className="text-[10px] font-bold text-stone-400 uppercase tracking-widest">Fitness Metrics</span>
          </div>
          <div className="flex-1 overflow-y-auto p-6 space-y-4 custom-scrollbar">
            {status?.agent_performance?.map((perf, i) => (
              <AgentPerformanceItem key={i} perf={perf} />
            ))}
            {(!status?.agent_performance || status.agent_performance.length === 0) && (
              <div className="text-center py-20 text-stone-300 italic">Neural agents are currently dormant.</div>
            )}
          </div>
        </section>
      </div>
    </div>
  );
};

const StatusCard = ({ icon: Icon, title, value, subtitle, color }) => {
  const colors = {
    blue: 'text-blue-500 bg-blue-50',
    amber: 'text-amber-500 bg-amber-50',
    purple: 'text-purple-500 bg-purple-50'
  };
  return (
    <div className="bg-white p-6 rounded-3xl border border-stone-200 shadow-sm flex items-center gap-5">
      <div className={`w-14 h-14 rounded-2xl flex items-center justify-center ${colors[color]}`}>
        <Icon className="w-7 h-7" />
      </div>
      <div>
        <h3 className="text-stone-400 text-[10px] font-bold uppercase tracking-widest">{title}</h3>
        <div className="text-2xl font-mono font-bold text-stone-800">{value}</div>
        <div className="text-[10px] text-stone-400 font-medium">{subtitle}</div>
      </div>
    </div>
  );
};

const IngestionItem = ({ event }) => {
  const isError = event.payload?.status === 'ERROR';
  const isTrainingStart = event.type === 'TRAINING_STARTED';
  
  if (isTrainingStart) {
    return (
      <div className="flex gap-4 p-4 rounded-2xl bg-amber-50/50 border border-amber-100 hover:border-amber-200 transition-all group">
        <div className="w-10 h-10 rounded-xl flex items-center justify-center shrink-0 bg-white text-amber-500 shadow-sm">
          <Activity className="w-5 h-5" />
        </div>
        <div className="flex-1 overflow-hidden">
          <div className="flex justify-between items-start">
            <h4 className="text-sm font-bold text-stone-800 truncate">Training Cycle Initiated</h4>
            <span className="text-[10px] font-mono text-stone-400">{new Date(event.timestamp).toLocaleTimeString()}</span>
          </div>
          <p className="text-xs text-stone-600 mt-1">
            Agent <span className="font-bold text-amber-600">{event.payload?.agent}</span> specializing on <span className="italic">"{event.payload?.dataset}"</span> ({event.payload?.file_count} files).
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex gap-4 p-4 rounded-2xl bg-stone-50 border border-stone-100 hover:border-blue-200 transition-all group">
      <div className={`w-10 h-10 rounded-xl flex items-center justify-center shrink-0 ${isError ? 'bg-red-50 text-red-500' : 'bg-white text-blue-500 shadow-sm'}`}>
        {isError ? <AlertCircle className="w-5 h-5" /> : <HardDrive className="w-5 h-5" />}
      </div>
      <div className="flex-1 overflow-hidden">
        <div className="flex justify-between items-start">
          <h4 className="text-sm font-bold text-stone-800 truncate">{event.payload?.filename || 'System Artifact'}</h4>
          <span className="text-[10px] font-mono text-stone-400">{new Date(event.timestamp).toLocaleTimeString()}</span>
        </div>
        <p className="text-xs text-stone-500 truncate mt-1">
          {event.payload?.detail || 'Analyzing semantic structures...'}
        </p>
        <div className="mt-2 flex items-center gap-3">
          <div className="flex-1 h-1 bg-stone-200 rounded-full overflow-hidden">
            <div 
              className={`h-full transition-all duration-500 ${isError ? 'bg-red-500' : 'bg-blue-500'}`} 
              style={{ width: event.payload?.status === 'SUCCESS' ? '100%' : (event.payload?.count ? '60%' : '10%') }}
            ></div>
          </div>
          <span className={`text-[10px] font-bold ${isError ? 'text-red-500' : 'text-blue-500'}`}>
            {event.payload?.status || 'INGESTING'}
          </span>
        </div>
      </div>
    </div>
  );
};

const AgentPerformanceItem = ({ perf }) => {
  return (
    <div className="flex gap-4 p-4 rounded-2xl bg-stone-50 border border-stone-100 hover:border-amber-200 transition-all">
      <div className="w-10 h-10 bg-white rounded-xl flex items-center justify-center shrink-0 shadow-sm text-amber-500">
        <Brain className="w-5 h-5" />
      </div>
      <div className="flex-1">
        <div className="flex justify-between items-start">
          <h4 className="text-sm font-bold text-stone-800">{perf.agent}</h4>
          <span className="text-[10px] font-mono text-stone-400">{perf.task}</span>
        </div>
        <div className="flex items-center gap-4 mt-2">
          <div className="flex flex-col">
            <span className="text-[9px] text-stone-400 font-bold uppercase">Fitness</span>
            <span className="text-xs font-mono font-bold text-stone-700">{Math.round(perf.fitness * 100)}%</span>
          </div>
          <div className="flex flex-col">
            <span className="text-[9px] text-stone-400 font-bold uppercase">Latency</span>
            <span className="text-xs font-mono font-bold text-stone-700">{perf.latency}ms</span>
          </div>
          <div className="flex-1 flex justify-end">
            {perf.fitness > 0.8 ? (
              <CheckCircle2 className="w-4 h-4 text-green-500" />
            ) : (
              <Zap className="w-4 h-4 text-amber-400 animate-pulse" />
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default TrainingView;
