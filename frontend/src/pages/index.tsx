import React, { useState } from 'react';
import { useRouter } from 'next/router';
import Layout from '@/components/Layout';
import { usePsuu } from '@/contexts/PsuuContext';
import api, { ModelConnection } from '@/api';

export default function ModelConnectionPage() {
  const router = useRouter();
  const { state, dispatch } = usePsuu();
  const [loading, setLoading] = useState(false);
  const [connectionType, setConnectionType] = useState<'protocol' | 'cli'>('protocol');
  
  // Form state
  const [protocolForm, setProtocolForm] = useState({
    moduleClass: '',
    protocol: 'cadcad',
  });
  
  const [cliForm, setCliForm] = useState({
    command: '',
    paramFormat: '--{name} {value}',
    outputFormat: 'json',
    workingDir: '',
  });
  
  const handleProtocolChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setProtocolForm(prev => ({ ...prev, [name]: value }));
  };
  
  const handleCliChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setCliForm(prev => ({ ...prev, [name]: value }));
  };
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      // Create connection object based on type
      const connection: ModelConnection = {
        type: connectionType,
        details: connectionType === 'protocol' 
          ? { moduleClass: protocolForm.moduleClass, protocol: protocolForm.protocol }
          : { 
              command: cliForm.command, 
              paramFormat: cliForm.paramFormat, 
              outputFormat: cliForm.outputFormat, 
              workingDir: cliForm.workingDir || undefined 
            }
      };
      
      // Test connection
      const result = await api.testConnection(connection);
      
      if (result.success) {
        // Update context
        dispatch({ type: 'SET_MODEL_CONNECTION', payload: connection });
        dispatch({ 
          type: 'SET_CONNECTION_STATUS', 
          payload: { isConnected: true } 
        });
        
        // Try to fetch parameter space
        try {
          const parameters = await api.getParameterSpace();
          dispatch({ type: 'SET_PARAMETERS', payload: parameters });
        } catch (error) {
          console.error('Failed to fetch parameters:', error);
        }
        
        // Try to fetch KPIs
        try {
          const kpis = await api.getAvailableKPIs();
          dispatch({ type: 'SET_KPIS', payload: kpis });
        } catch (error) {
          console.error('Failed to fetch KPIs:', error);
        }
        
        // Set active step
        dispatch({ type: 'SET_ACTIVE_STEP', payload: 'parameters' });
        
        // Navigate to parameters page
        router.push('/parameters');
      } else {
        dispatch({ 
          type: 'SET_CONNECTION_STATUS', 
          payload: { 
            isConnected: false, 
            error: result.message || 'Connection failed' 
          } 
        });
      }
    } catch (error) {
      dispatch({ 
        type: 'SET_CONNECTION_STATUS', 
        payload: { 
          isConnected: false, 
          error: error instanceof Error ? error.message : 'Connection failed' 
        } 
      });
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <Layout>
      <div className="max-w-2xl mx-auto">
        <h1 className="text-2xl font-bold mb-6">Model Connection</h1>
        
        <div className="mb-6">
          <div className="p-4 border rounded bg-white">
            <div className="mb-4">
              <label className="block text-sm font-medium mb-2">Connection Type</label>
              <div className="flex space-x-4">
                <button 
                  type="button"
                  className={`px-4 py-2 rounded ${connectionType === 'protocol' ? 'bg-blue-500 text-white' : 'bg-gray-200'}`}
                  onClick={() => setConnectionType('protocol')}
                >
                  Protocol Integration
                </button>
                <button 
                  type="button"
                  className={`px-4 py-2 rounded ${connectionType === 'cli' ? 'bg-blue-500 text-white' : 'bg-gray-200'}`}
                  onClick={() => setConnectionType('cli')}
                >
                  CLI Integration
                </button>
              </div>
            </div>
            
            <form onSubmit={handleSubmit}>
              {connectionType === 'protocol' ? (
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium mb-1">Model Class</label>
                    <input
                      type="text"
                      name="moduleClass"
                      value={protocolForm.moduleClass}
                      onChange={handleProtocolChange}
                      placeholder="e.g. template.model.SIRModel"
                      className="w-full p-2 border rounded"
                      required
                    />
                    <p className="text-xs text-gray-500 mt-1">
                      Full import path to your model class that implements ModelProtocol
                    </p>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium mb-1">Model Protocol</label>
                    <select
                      name="protocol"
                      value={protocolForm.protocol}
                      onChange={handleProtocolChange}
                      className="w-full p-2 border rounded"
                    >
                      <option value="cadcad">cadCAD Protocol</option>
                      <option value="generic">Generic Protocol</option>
                    </select>
                  </div>
                </div>
              ) : (
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium mb-1">Command</label>
                    <input
                      type="text"
                      name="command"
                      value={cliForm.command}
                      onChange={handleCliChange}
                      placeholder="e.g. python -m model"
                      className="w-full p-2 border rounded"
                      required
                    />
                    <p className="text-xs text-gray-500 mt-1">
                      Command to run the simulation model
                    </p>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium mb-1">Parameter Format</label>
                    <input
                      type="text"
                      name="paramFormat"
                      value={cliForm.paramFormat}
                      onChange={handleCliChange}
                      placeholder="--{name} {value}"
                      className="w-full p-2 border rounded"
                      required
                    />
                    <p className="text-xs text-gray-500 mt-1">
                      Format for passing parameters (use {"{name}"} and {"{value}"} placeholders)
                    </p>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium mb-1">Output Format</label>
                    <select
                      name="outputFormat"
                      value={cliForm.outputFormat}
                      onChange={handleCliChange}
                      className="w-full p-2 border rounded"
                    >
                      <option value="json">JSON</option>
                      <option value="csv">CSV</option>
                    </select>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium mb-1">Working Directory</label>
                    <input
                      type="text"
                      name="workingDir"
                      value={cliForm.workingDir}
                      onChange={handleCliChange}
                      placeholder="(Optional) e.g. /path/to/model"
                      className="w-full p-2 border rounded"
                    />
                  </div>
                </div>
              )}
              
              {state.connectionError && (
                <div className="mt-4 p-3 bg-red-100 border border-red-300 text-red-700 rounded">
                  {state.connectionError}
                </div>
              )}
              
              <div className="mt-6 flex justify-end">
                <button
                  type="submit"
                  className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
                  disabled={loading}
                >
                  {loading ? 'Testing Connection...' : 'Connect to Model'}
                </button>
              </div>
            </form>
          </div>
          
          <div className="bg-blue-50 border border-blue-200 p-4 rounded mt-6">
            <h3 className="text-lg font-medium mb-2">Using the Model Connection</h3>
            <div className="text-sm">
              <p className="mb-2">
                <strong>Protocol Integration:</strong> For direct integration with Python models that implement the PSUU ModelProtocol. 
                This is recommended for new models or when you have control over the model code.
              </p>
              <p>
                <strong>CLI Integration:</strong> For integration with models via command-line interfaces. 
                This is useful for existing models or when you don't want to modify the original model code.
              </p>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}
