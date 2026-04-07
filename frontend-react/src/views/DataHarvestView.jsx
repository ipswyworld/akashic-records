import React, { useState, useEffect } from 'react';
import { Sparkles, UploadCloud, Zap, AlertCircle, Check } from 'lucide-react';
import { getThemeColors } from '../components/CommonUI';

const DataHarvestView = ({ theme, onIngest }) => {
  const [files, setFiles] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(null);
  const [progress, setProgress] = useState({});
  const colors = getThemeColors(theme);

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8001/akasha/sensory');
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.event === 'INGESTION_PROGRESS') {
        setProgress(prev => ({
          ...prev,
          [data.filename]: { status: data.status, detail: data.detail, count: data.count }
        }));
        if (data.status === 'SUCCESS' || data.status === 'ERROR') {
          onIngest();
        }
      }
    };
    return () => ws.close();
  }, [onIngest]);

  const handleFileChange = (e) => {
    setFiles(Array.from(e.target.files));
    setUploadStatus(null);
    setProgress({});
  };

  const handleUpload = async () => {
    if (files.length === 0) return;
    setIsUploading(true);
    setUploadStatus(`Queuing ${files.length} dataset(s)...`);
    
    const formData = new FormData();
    files.forEach(f => {
      formData.append('file', f);
    });
    formData.append('user_id', 'system_user');

    try {
      const response = await fetch('http://localhost:8001/ingest/dataset', {
        method: 'POST',
        body: formData,
      });
      const data = await response.json();
      
      if (response.ok && data.status === 'BATCH_QUEUED') {
        setUploadStatus(`Success: ${data.message}`);
        setFiles([]);
      } else {
        const errorDetail = typeof data.detail === 'object' ? JSON.stringify(data.detail) : data.detail;
        setUploadStatus(`Error: ${errorDetail || 'Upload failed'}`);
      }
    } catch (err) {
      setUploadStatus(`Error: Neural core connection failed.`);
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="p-4 sm:p-6 w-full max-w-4xl mx-auto animate-in fade-in duration-500 space-y-8">
      <div className="mb-6">
        <h2 className={`text-xl sm:text-2xl font-light flex items-center ${colors.textMain}`}>
          <Sparkles className="w-5 h-5 sm:w-6 sm:h-6 mr-3 text-amber-500" /> Neural Feeding: Data Harvest
        </h2>
        <p className="text-stone-500 text-sm mt-1">Upload multiple CSV, JSON, PDF, Excel, or Word datasets simultaneously. They will be processed in the background.</p>
      </div>

      <div className={`p-8 rounded-2xl border-2 border-dashed flex flex-col items-center justify-center transition-all ${theme === 'dark' ? 'border-slate-800 bg-slate-900/40' : 'border-stone-200 bg-white/50'} ${files.length > 0 ? 'border-amber-500 bg-amber-500/5' : ''}`}>
        <UploadCloud className={`w-12 h-12 mb-4 ${files.length > 0 ? 'text-amber-500' : 'text-stone-300'}`} />
        <p className={`text-sm mb-4 ${colors.textMuted}`}>
          {files.length > 0 ? `Selected ${files.length} file(s): ${files.map(f => f.name).join(', ')}` : 'Drop datasets here or click to browse'}
        </p>
        <input type="file" onChange={handleFileChange} className="hidden" id="dataset-upload" accept=".csv,.json,.pdf,.xlsx,.xls,.docx" multiple />

        <label htmlFor="dataset-upload" className={`px-6 py-2 rounded-lg cursor-pointer text-sm font-medium transition-all ${theme === 'dark' ? 'bg-slate-800 text-slate-200 hover:bg-slate-700' : 'bg-white border border-stone-200 text-stone-700 hover:bg-stone-50 shadow-sm'}`}>
          Select Files
        </label>
      </div>

      <div className="flex flex-col items-center gap-4">
        <button 
          onClick={handleUpload} 
          disabled={files.length === 0 || isUploading}
          className={`px-8 py-3 rounded-xl font-bold transition-all flex items-center gap-2 ${files.length > 0 && !isUploading ? 'bg-amber-500 text-white shadow-lg shadow-amber-500/20 hover:bg-amber-600 scale-105' : 'bg-stone-200 text-stone-400 cursor-not-allowed'}`}
        >
          {isUploading ? <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div> : <Zap className="w-4 h-4" />}
          {isUploading ? 'Queuing...' : 'Feed the Archivist'}
        </button>
        {uploadStatus && (
          <p className={`text-sm font-medium flex items-center gap-2 animate-in fade-in ${uploadStatus.startsWith('Error') ? 'text-red-500' : 'text-amber-600'}`}>
            {uploadStatus.startsWith('Error') ? <AlertCircle className="w-4 h-4" /> : <Check className="w-4 h-4" />}
            {uploadStatus}
          </p>
        )}
      </div>

      {Object.keys(progress).length > 0 && (
        <div className={`mt-8 p-4 rounded-xl border ${theme === 'dark' ? 'bg-slate-900/60 border-slate-800' : 'bg-stone-50 border-stone-100'}`}>
          <h3 className={`text-sm font-semibold mb-4 ${colors.textMain}`}>Live Neural Progress</h3>
          <div className="space-y-3">
            {Object.entries(progress).map(([filename, info]) => (
              <div key={filename} className="flex items-center justify-between text-xs sm:text-sm">
                <span className={`truncate max-w-[200px] ${colors.textMain}`}>{filename}</span>
                <div className="flex items-center gap-2">
                  {info.status === 'PROCESSING' && <div className="animate-spin rounded-full h-3 w-3 border-2 border-amber-500 border-t-transparent"></div>}
                  {info.status === 'SUCCESS' && <Check className="w-4 h-4 text-green-500" />}
                  {info.status === 'ERROR' && <AlertCircle className="w-4 h-4 text-red-500" />}
                  <span className={
                    info.status === 'SUCCESS' ? 'text-green-500' : 
                    info.status === 'ERROR' ? 'text-red-500' : 
                    'text-amber-500'
                  }>
                    {info.status} {info.count ? `(${info.count} items)` : ''}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default DataHarvestView;
