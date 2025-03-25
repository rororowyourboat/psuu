import React, { useState } from 'react';
import { useRouter } from 'next/router';
import Layout from '@/components/Layout';
import { usePsuu } from '@/contexts/PsuuContext';
import api, { OptimizationConfig } from '@/api';

export default function OptimizationPage() {
  const router = useRouter();
  const { state, dispatch } = usePsuu();
  const [loading, setLoading] = useState(false);
  
  // Optimization config state
  const [config, setConfig] = useState<OptimizationConfig>({
    method: 'bayesian',
    iterations: 20,
    initialPoints: 5,
    seed: 42
  });
  
  // Handle config change
  const handleConfigChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setConfig(prev => ({
      ...prev,
      [name]: name === 'method' ? value : Number(value)
    }));
  };
  
  // Start optimization
  const handleStartOptimization = async () => {
    setLoading(true);
    
    try {
      // Configure optimization
      await api.configureOptimization(config);
      
      // Start optimization job
      const { jobId } = await api.startOptimization();
      
      // Update state
      dispatch({
        type: 'SET_JOB_STATUS',
        payload: {
          jobId,
          status: 'running',
          progress: 0,
          message: 'Optimization started'
        }
      });
      
      // Set active step
      dispatch({ type: 'SET_ACTIVE_STEP', payload: 'results' });
      
      // Navigate to results page
      router.push('/results');
    } catch (error) {
      alert('Failed to start optimization');
      console.error('Failed to start optimization:', error);
    } finally {
      setLoading(false);
    }
  };
  
  // Ensure prerequisites are met
  if (!state.isConnected || state.parameters.length === 0 || state.kpis.length === 0) {
    if (typeof window !== 'undefined') {
      router.push(state.kpis.length === 0 ? '/kpis' : state.parameters.length === 0 ? '/parameters' : '/');
    }
    return null;
  }
  
  // Get objective KPI
  const objectiveKPI = state.kpis.find(kpi => kpi.isObjective);
  
  return (
    <Layout>
      <div className="max-w-4xl mx-auto">
        <h1 className="text-2xl font-bold mb-6">Optimization Configuration</h1>
        
        {/* Selected Parameters & KPIs Summary */}
        <div className="bg-white border rounded p-4 mb-6">
          <h2 className="text-lg font-medium mb-4">Configuration Summary</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="font-medium mb-2">Parameters</h3>
              <ul className="text-sm">
                {state.parameters.map(param => (
                  <li key={param.name} className="mb-1">
                    {param.name}: {param.type === 'continuous' 
                      ? `${param.min} to ${param.max}`
                      : param.values?.join(', ')}
                  </li>
                ))}
              </ul>
            </div>
            
            <div>
              <h3 className="font-medium mb-2">Objective</h3>
              {objectiveKPI ? (
                <p className="text-sm">
                  {objectiveKPI.name} ({objectiveKPI.maximize ? 'Maximize' : 'Minimize'})
                </p>
              ) : (
                <p className="text-sm text-red-500">
                  No objective selected. Please select a KPI objective.
                </p>
              )}
            </div>
          </div>
        </div>
        
        {/* Optimization Settings */}
        <div className="bg-white border rounded p-4 mb-6">
          <h2 className="text-lg font-medium mb-4">Optimization Settings</h2>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1">Method</label>
              <select
                name="method"
                value={config.method}
                onChange={handleConfigChange}
                className="w-full p-2 border rounded"
              >
                <option value="grid">Grid Search</option>
                <option value="random">Random Search</option>
                <option value="bayesian">Bayesian Optimization</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-1">Number of Iterations</label>
              <input
                type="number"
                name="iterations"
                value={config.iterations}
                onChange={handleConfigChange}
                min={1}
                className="w-full p-2 border rounded"
              />
            </div>
            
            {config.method === 'bayesian' && (
              <div>
                <label className="block text-sm font-medium mb-1">Initial Random Points</label>
                <input
                  type="number"
                  name="initialPoints"
                  value={config.initialPoints}
                  onChange={handleConfigChange}
                  min={1}
                  className="w-full p-2 border rounded"
                />
              </div>
            )}
            
            <div>
              <label className="block text-sm font-medium mb-1">Random Seed</label>
              <input
                type="number"
                name="seed"
                value={config.seed}
                onChange={handleConfigChange}
                className="w-full p-2 border rounded"
              />
            </div>
          </div>
        </div>
        
        {/* Actions */}
        <div className="flex justify-end space-x-4">
          <button
            type="button"
            onClick={() => router.push('/kpis')}
            className="px-4 py-2 border rounded"
          >
            Back to KPIs
          </button>
          
          <button
            type="button"
            onClick={handleStartOptimization}
            disabled={!objectiveKPI || loading}
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
          >
            {loading ? 'Starting...' : 'Start Optimization'}
          </button>
        </div>
      </div>
    </Layout>
  );
}
