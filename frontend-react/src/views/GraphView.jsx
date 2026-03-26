import React, { useState, useEffect } from 'react';
import { Network } from 'lucide-react';
import ForceGraph3D from 'react-force-graph-3d';
import { getThemeColors } from '../components/CommonUI';
import { fetchGraphTopology } from '../api';

const GraphView = ({ theme }) => {
  const [topology, setTopology] = useState(null);
  const [graphData, setGraphData] = useState({ nodes: [], links: [] });
  const [isLoading, setIsLoading] = useState(true);

  const fetchVisualData = async () => {
    try {
      const top = await fetchGraphTopology();
      setTopology(top);
      
      const response = await fetch('http://localhost:8001/analytics/graph/visual');
      const data = await response.json();
      
      if (data.nodes && data.nodes.length > 0) {
        // Add color based on node val or name
        const processedNodes = data.nodes.map(n => ({
          ...n,
          nodeColor: n.id.includes('EGO') ? '#fbbf24' : '#3b82f6'
        }));
        setGraphData({ nodes: processedNodes, links: data.links || [] });
      } else {
        // Fallback for empty graph but still show topology counts
        setGraphData({ nodes: [], links: [] });
      }
    } catch (err) {
      console.error("Neural Graph Error:", err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchVisualData();
    const interval = setInterval(fetchVisualData, 10000); // Poll every 10s
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="relative w-full h-full animate-in fade-in duration-1000 flex-1 overflow-hidden">
      <div className="absolute inset-0 z-0 bg-slate-900 flex items-center justify-center">
        {/* <ForceGraph3D 
          graphData={graphData} 
          nodeLabel="name" 
          nodeColor="nodeColor" 
          nodeRelSize={6} 
          linkColor={() => theme === 'dark' ? 'rgba(59, 130, 246, 0.2)' : 'rgba(120, 113, 108, 0.2)'} 
          backgroundColor={theme === 'dark' ? '#020617' : '#f8f5f0'} 
          enableNodeDrag={false} 
          showNavInfo={false} 
        /> */}
        <p className="text-slate-500 font-mono text-sm italic">Neural Graph Engine [Standby Mode]</p>
      </div>
      
      {isLoading && (
        <div className="absolute inset-0 flex items-center justify-center bg-black/5 backdrop-blur-sm z-20">
          <div className="flex flex-col items-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-amber-500 mb-4"></div>
            <p className="text-amber-500 font-medium animate-pulse">Mapping Neural Territory...</p>
          </div>
        </div>
      )}

      <div className={`absolute top-4 left-4 sm:top-6 sm:left-6 pointer-events-none z-10 p-4 rounded-xl border backdrop-blur shadow-sm ${theme === 'dark' ? 'bg-slate-900/40 border-slate-800' : 'bg-white/60 border-stone-200'}`}>
        <h2 className={`text-lg sm:text-xl font-light tracking-wider mb-2 flex items-center ${theme === 'dark' ? 'text-slate-200' : 'text-stone-800'}`}><Network className="w-5 h-5 mr-2 text-amber-500" /> Neural Topology</h2>
        <div className="space-y-2 mt-4">
          <div className="flex justify-between items-center text-xs"><span className="text-stone-500 mr-4">Real Nodes</span><span className="text-amber-600 font-mono bg-stone-100 px-2 py-0.5 rounded shadow-sm">{topology?.node_count || 0}</span></div>
          <div className="flex justify-between items-center text-xs"><span className="text-stone-500">Synapses</span><span className="text-blue-600 font-mono bg-stone-100 px-2 py-0.5 rounded shadow-sm">{topology?.edge_count || 0}</span></div>
        </div>
        {graphData.nodes.length === 0 && !isLoading && (
          <p className="mt-4 text-[10px] text-amber-600 italic">Feed the Archivist to generate neural connections.</p>
        )}
      </div>
    </div>
  );
};

export default GraphView;
