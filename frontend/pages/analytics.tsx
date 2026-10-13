import { useState, useEffect } from 'react';
import axios from 'axios';
import { BarChart3, RefreshCw, Download, FileText } from 'lucide-react';

const API_URL = 'http://localhost:5000';

interface DetectionLog {
  id: string;
  timestamp: string;
  mode: string;
  type: string;
  filename?: string;
  total_objects: number;
  status?: string;
  compliance_score?: number;
  person_count?: number;
  detected_ppe?: any;
  class_counts?: any;
}

export default function AnalyticsPage() {
  const [mode, setMode] = useState<'ppe' | 'normal'>('ppe');
  const [logs, setLogs] = useState<DetectionLog[]>([]);
  const [summary, setSummary] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      console.log(`Fetching analytics for mode: ${mode}`);
      const response = await axios.get(`${API_URL}/analytics?mode=${mode}`);
      console.log('Response:', response.data);
      
      setLogs(response.data.records || []);
      setSummary(response.data.summary || {});
      
      console.log(`Loaded ${response.data.records?.length || 0} records`);
    } catch (err: any) {
      console.error('Error:', err);
      setError(err.message || 'Failed to fetch analytics');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [mode]);

  const exportCSV = async (recordId: string) => {
    try {
      const response = await axios.get(`${API_URL}/export/csv/${recordId}`, {
        responseType: 'blob'
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `detection_${recordId}.csv`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error('CSV export error:', error);
      alert('Failed to export CSV');
    }
  };

  const exportPDF = async (recordId: string) => {
    try {
      const response = await axios.get(`${API_URL}/export/pdf/${recordId}`, {
        responseType: 'blob'
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `detection_${recordId}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error('PDF export error:', error);
      alert('Failed to export PDF');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-white p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center space-x-4">
            <BarChart3 className="w-10 h-10" />
            <div>
              <h1 className="text-4xl font-light">Analytics Dashboard</h1>
              <p className="text-slate-400">Detection history from database</p>
            </div>
          </div>
          
          <button
            onClick={fetchData}
            disabled={loading}
            className="flex items-center space-x-2 px-6 py-3 bg-blue-600 hover:bg-blue-700 rounded-xl transition-all disabled:opacity-50"
          >
            <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
        </div>

        {/* Mode Selector */}
        <div className="flex space-x-4 mb-8">
          <button
            onClick={() => setMode('ppe')}
            className={`px-6 py-3 rounded-xl font-medium transition-all ${
              mode === 'ppe'
                ? 'bg-white text-slate-900'
                : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
            }`}
          >
            PPE Detection
          </button>
          <button
            onClick={() => setMode('normal')}
            className={`px-6 py-3 rounded-xl font-medium transition-all ${
              mode === 'normal'
                ? 'bg-white text-slate-900'
                : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
            }`}
          >
            Normal Detection
          </button>
        </div>

        {/* Error */}
        {error && (
          <div className="bg-red-900/30 border border-red-500/50 rounded-xl p-4 mb-8">
            <p className="text-red-300">Error: {error}</p>
          </div>
        )}

        {/* Summary */}
        {summary && (
          <div className="grid grid-cols-4 gap-6 mb-8">
            <div className="bg-slate-800/50 rounded-xl p-6">
              <p className="text-slate-400 text-sm">Total Detections</p>
              <p className="text-4xl font-light mt-2">{summary.total_detections || 0}</p>
            </div>
            <div className="bg-slate-800/50 rounded-xl p-6">
              <p className="text-slate-400 text-sm">Images</p>
              <p className="text-4xl font-light mt-2">{summary.image_count || 0}</p>
            </div>
            <div className="bg-slate-800/50 rounded-xl p-6">
              <p className="text-slate-400 text-sm">Videos</p>
              <p className="text-4xl font-light mt-2">{summary.video_count || 0}</p>
            </div>
            <div className="bg-slate-800/50 rounded-xl p-6">
              <p className="text-slate-400 text-sm">Live</p>
              <p className="text-4xl font-light mt-2">{summary.live_count || 0}</p>
            </div>
          </div>
        )}

        {/* Table */}
        <div className="bg-slate-800/50 rounded-xl overflow-hidden">
          <div className="p-6 border-b border-slate-700">
            <h2 className="text-2xl font-light">Detection Logs</h2>
            <p className="text-slate-400 text-sm mt-1">{logs.length} records found</p>
          </div>

          {loading ? (
            <div className="p-12 text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto"></div>
              <p className="text-slate-400 mt-4">Loading...</p>
            </div>
          ) : logs.length === 0 ? (
            <div className="p-12 text-center text-slate-500">
              <p>No detection logs found</p>
              <p className="text-sm mt-2">Upload some images to see logs here</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-slate-900/70">
                  <tr>
                    <th className="px-6 py-4 text-left text-xs font-medium text-slate-400 uppercase">Timestamp</th>
                    <th className="px-6 py-4 text-left text-xs font-medium text-slate-400 uppercase">Filename</th>
                    <th className="px-6 py-4 text-left text-xs font-medium text-slate-400 uppercase">Type</th>
                    <th className="px-6 py-4 text-left text-xs font-medium text-slate-400 uppercase">Objects</th>
                    {mode === 'ppe' && (
                      <>
                        <th className="px-6 py-4 text-left text-xs font-medium text-slate-400 uppercase">Status</th>
                        <th className="px-6 py-4 text-left text-xs font-medium text-slate-400 uppercase">Score</th>
                      </>
                    )}
                    <th className="px-6 py-4 text-left text-xs font-medium text-slate-400 uppercase">Export</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-700">
                  {logs.map((log) => (
                    <tr key={log.id} className="hover:bg-slate-700/30">
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        {new Date(log.timestamp).toLocaleString()}
                      </td>
                      <td className="px-6 py-4 text-sm">{log.filename || 'N/A'}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">{log.type}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">{log.total_objects}</td>
                      {mode === 'ppe' && (
                        <>
                          <td className="px-6 py-4 whitespace-nowrap text-sm">
                            <span className={`px-3 py-1 rounded-full text-xs ${
                              log.status === 'SAFE'
                                ? 'bg-emerald-900/30 text-emerald-300'
                                : 'bg-red-900/30 text-red-300'
                            }`}>
                              {log.status}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm">{log.compliance_score}%</td>
                        </>
                      )}
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex space-x-2">
                          <button
                            onClick={() => exportCSV(log.id)}
                            className="p-2 bg-emerald-600/20 hover:bg-emerald-600/30 rounded-lg transition-all"
                          >
                            <FileText className="w-4 h-4 text-emerald-400" />
                          </button>
                          <button
                            onClick={() => exportPDF(log.id)}
                            className="p-2 bg-red-600/20 hover:bg-red-600/30 rounded-lg transition-all"
                          >
                            <Download className="w-4 h-4 text-red-400" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
