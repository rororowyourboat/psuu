import React, { useEffect, useState, useRef } from 'react';
import { useRouter } from 'next/router';
import Layout from '@/components/Layout';
import { usePsuu } from '@/contexts/PsuuContext';
import api, { OptimizationResult } from '@/api';

export default function ResultsPage() {
  const router = useRouter();
  const { state } = usePsuu();
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<OptimizationResult | null>(null);
  
  // Stream updates state
  const [updates, setUpdates] = useState<any[]>([]);
  const eventSourceRef = useRef<EventSource | null>(null);
  
  useEffect(() => {
    // Clean up previous EventSource
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }
    
    // Start streaming if we have a job ID
    if (state.currentJob.jobId) {
      setLoading(true);
      
      // Connect to SSE stream
      const eventSource = new EventSource('http://localhost:5000/api/optimization/stream');
      eventSourceRef.current = eventSource;
      
      // Handle stream events
      eventSource.onmessage = (event) => {
        const data = JSON.parse(event.data);
        
        switch (data.type) {
          case 'step':
            setUpdates(prev => [...prev, data]);
            break;
            
          case 'complete':
            setResults(data.result);
            setLoading(false);
            eventSource.close();
            break;
            
          case 'error':
            alert('Optimization error: ' + data.message);
            setLoading(false);
            eventSource.close();
            break;
        }
      };
      
      eventSource.onerror = () => {
        setLoading(false);
        eventSource.close();
        alert('Stream connection error');
      };
      
      // Cleanup on unmount
      return () => {
        eventSource.close();
      };
    }
  }, [state.currentJob.jobId]);
  
  // Ensure prerequisites are met
  if (!state.isConnected || state.parameters.length === 0 || state.kpis.length === 0) {
    if (typeof window !== 'undefined') {
      router.push(state.kpis.length === 0 ? '/kpis' : state.parameters.length === 0 ? '/parameters' : '/');
    }
    return null;
  }
  
  return (
    <Layout>
      <div className="max-w-4xl mx-auto">
        <h1 className="text-2xl font-bold mb-6">Optimization Results</h1>
        
        {/* Stream Updates */}
        <div className="bg-white border rounded p-4 mb-6">
          <h2 className="text-lg font-medium mb-4">Optimization Progress</h2>
          <div className="h-64 overflow-auto font-mono text-sm bg-slate-50 p-4 rounded">
            {updates.length === 0 && loading ? (
              <div className="text-slate-500">Waiting for updates...</div>
            ) : (
              updates.map((update, index) => (
                <div key={index} className="mb-4">
                  <div className="text-slate-500"># Step {update.step}</div>
                  <div className="text-slate-700">{update.command}</div>
                  <div className="mt-1 text-sm">
                    <span className="text-slate-500">Results:</span>
                    <pre className="mt-1 text-xs">
                      {JSON.stringify(update.result, null, 2)}
                    </pre>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
        
        {/* Final Results */}
        {results && (
          <div className="space-y-6">
            {/* Best Parameters */}
            <div className="bg-white border rounded p-4">
              <h2 className="text-lg font-medium mb-4">Best Parameters</h2>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                {Object.entries(results.bestParameters).map(([name, value]) => (
                  <div key={name} className="p-3 bg-slate-50 rounded">
                    <div className="text-sm text-slate-500">{name}</div>
                    <div className="font-medium">{value}</div>
                  </div>
                ))}
              </div>
            </div>
            
            {/* Best KPIs */}
            <div className="bg-white border rounded p-4">
              <h2 className="text-lg font-medium mb-4">Performance Metrics</h2>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                {Object.entries(results.bestKPIs).map(([name, value]) => (
                  <div key={name} className="p-3 bg-slate-50 rounded">
                    <div className="text-sm text-slate-500">{name}</div>
                    <div className="font-medium">
                      {typeof value === 'number' ? value.toFixed(2) : value}
                    </div>
                  </div>
                ))}
              </div>
            </div>
            
            {/* Summary */}
            <div className="bg-white border rounded p-4">
              <h2 className="text-lg font-medium mb-4">Optimization Summary</h2>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <div className="text-sm text-slate-500">Total Iterations</div>
                  <div className="font-medium">{results.iterations}</div>
                </div>
                <div>
                  <div className="text-sm text-slate-500">Time Elapsed</div>
                  <div className="font-medium">
                    {results.elapsedTime.toFixed(1)} seconds
                  </div>
                </div>
              </div>
            </div>
            
            {/* Actions */}
            <div className="flex justify-end space-x-4">
              <button
                type="button"
                onClick={() => router.push('/optimization')}
                className="px-4 py-2 border rounded hover:bg-slate-50"
              >
                New Optimization
              </button>
            </div>
          </div>
        )}
        
        {!results && !loading && (
          <div className="bg-white border rounded p-8 text-center">
            <p className="text-slate-600">No optimization results available.</p>
            <button
              type="button"
              onClick={() => router.push('/optimization')}
              className="mt-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
            >
              Start New Optimization
            </button>
          </div>
        )}
      </div>
    </Layout>
  );
}
