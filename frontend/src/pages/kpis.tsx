import React, { useState } from 'react';
import { useRouter } from 'next/router';
import Layout from '@/components/Layout';
import { usePsuu } from '@/contexts/PsuuContext';
import api, { KPI } from '@/api';

export default function KPIsPage() {
  const router = useRouter();
  const { state, dispatch } = usePsuu();
  const [loading, setLoading] = useState(false);
  
  // New KPI form
  const [newKPI, setNewKPI] = useState<KPI>({
    name: '',
    column: '',
    operation: 'max',
    isObjective: false,
    maximize: true
  });
  
  // KPI being edited
  const [editIndex, setEditIndex] = useState<number | null>(null);
  
  // Handle KPI change
  const handleKPIChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value, type } = e.target;
    
    // Handle checkbox
    if (type === 'checkbox') {
      const checked = (e.target as HTMLInputElement).checked;
      setNewKPI(prev => ({
        ...prev,
        [name]: checked
      }));
    } else {
      setNewKPI(prev => ({
        ...prev,
        [name]: value
      }));
    }
  };
  
  // Add or update KPI
  const handleAddKPI = async () => {
    // Validation
    if (!newKPI.name) {
      alert('KPI name is required');
      return;
    }
    
    if (!newKPI.column && !newKPI.function) {
      alert('Either column or custom function is required');
      return;
    }
    
    // If editing, update KPI
    if (editIndex !== null) {
      dispatch({
        type: 'UPDATE_KPI',
        payload: {
          index: editIndex,
          kpi: newKPI
        }
      });
      
      setEditIndex(null);
    } else {
      // Add new KPI
      dispatch({
        type: 'ADD_KPI',
        payload: newKPI
      });
    }
    
    // Reset form
    setNewKPI({
      name: '',
      column: '',
      operation: 'max',
      isObjective: false,
      maximize: true
    });
  };
  
  // Edit KPI
  const handleEditKPI = (index: number) => {
    setEditIndex(index);
    setNewKPI(state.kpis[index]);
  };
  
  // Remove KPI
  const handleRemoveKPI = (index: number) => {
    if (confirm('Are you sure you want to remove this KPI?')) {
      dispatch({
        type: 'REMOVE_KPI',
        payload: index
      });
    }
  };
  
  // Set objective KPI
  const handleSetObjective = (index: number) => {
    // Update all KPIs to remove objective flag
    const updatedKPIs = state.kpis.map((kpi, i) => ({
      ...kpi,
      isObjective: i === index
    }));
    
    dispatch({ type: 'SET_KPIS', payload: updatedKPIs });
  };
  
  // Save KPIs and go to next step
  const handleSaveKPIs = async () => {
    if (state.kpis.length === 0) {
      alert('Please add at least one KPI');
      return;
    }
    
    // Check if an objective is selected
    const hasObjective = state.kpis.some(kpi => kpi.isObjective);
    if (!hasObjective) {
      alert('Please select at least one KPI as an objective');
      return;
    }
    
    setLoading(true);
    
    try {
      await api.setKPIs(state.kpis);
      
      // Set active step
      dispatch({ type: 'SET_ACTIVE_STEP', payload: 'optimization' });
      
      // Navigate to optimization page
      router.push('/optimization');
    } catch (error) {
      alert('Failed to save KPIs');
      console.error('Failed to save KPIs:', error);
    } finally {
      setLoading(false);
    }
  };
  
  // Ensure parameters are configured
  if (!state.isConnected || state.parameters.length === 0) {
    if (typeof window !== 'undefined') {
      router.push(state.isConnected ? '/parameters' : '/');
    }
    return null;
  }
  
  return (
    <Layout>
      <div className="max-w-4xl mx-auto">
        <h1 className="text-2xl font-bold mb-6">Key Performance Indicators (KPIs)</h1>
        
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <div className="bg-white border rounded p-4 mb-6">
              <h2 className="text-lg font-medium mb-4">Defined KPIs</h2>
              
              {state.kpis.length === 0 ? (
                <div className="p-4 bg-gray-50 border rounded text-center">
                  No KPIs defined yet. Add KPIs using the form.
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="bg-gray-50">
                        <th className="py-2 px-3 text-left">Name</th>
                        <th className="py-2 px-3 text-left">Type</th>
                        <th className="py-2 px-3 text-left">Details</th>
                        <th className="py-2 px-3 text-left">Objective</th>
                        <th className="py-2 px-3 text-left">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {state.kpis.map((kpi, index) => (
                        <tr key={index} className="border-t">
                          <td className="py-2 px-3">{kpi.name}</td>
                          <td className="py-2 px-3">
                            {kpi.function ? 'Custom' : 'Simple'}
                          </td>
                          <td className="py-2 px-3">
                            {kpi.function 
                              ? `Function: ${kpi.function}`
                              : `${kpi.column} (${kpi.operation})`
                            }
                          </td>
                          <td className="py-2 px-3">
                            {kpi.isObjective ? (
                              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                                {kpi.maximize ? 'Maximize' : 'Minimize'}
                              </span>
                            ) : (
                              <button
                                onClick={() => handleSetObjective(index)}
                                className="text-xs underline text-blue-500"
                              >
                                Set as objective
                              </button>
                            )}
                          </td>
                          <td className="py-2 px-3">
                            <div className="flex space-x-2">
                              <button
                                onClick={() => handleEditKPI(index)}
                                className="text-blue-500 hover:text-blue-700"
                              >
                                Edit
                              </button>
                              <button
                                onClick={() => handleRemoveKPI(index)}
                                className="text-red-500 hover:text-red-700"
                              >
                                Remove
                              </button>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
              
              <div className="mt-6 flex justify-end">
                <button
                  onClick={handleSaveKPIs}
                  className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
                  disabled={state.kpis.length === 0 || loading}
                >
                  {loading ? 'Saving...' : 'Save and Continue'}
                </button>
              </div>
            </div>
          </div>
          
          <div>
            <div className="bg-white border rounded p-4 sticky top-4">
              <h2 className="text-lg font-medium mb-4">
                {editIndex !== null ? 'Edit KPI' : 'Add KPI'}
              </h2>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Name</label>
                  <input
                    type="text"
                    name="name"
                    value={newKPI.name}
                    onChange={handleKPIChange}
                    className="w-full p-2 border rounded"
                    placeholder="e.g., Average Temperature"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium mb-1">Type</label>
                  <select
                    name="type"
                    value={newKPI.function ? 'custom' : 'simple'}
                    onChange={(e) => {
                      if (e.target.value === 'custom') {
                        setNewKPI(prev => ({
                          ...prev,
                          column: '',
                          operation: '',
                          function: 'def calculate(df):\n    return '
                        }));
                      } else {
                        setNewKPI(prev => ({
                          ...prev,
                          function: undefined,
                          column: '',
                          operation: 'max'
                        }));
                      }
                    }}
                    className="w-full p-2 border rounded"
                  >
                    <option value="simple">Simple (Column Operation)</option>
                    <option value="custom">Custom (Python Function)</option>
                  </select>
                </div>
                
                {newKPI.function ? (
                  <div>
                    <label className="block text-sm font-medium mb-1">Custom Function</label>
                    <textarea
                      name="function"
                      value={newKPI.function}
                      onChange={handleKPIChange}
                      className="w-full p-2 border rounded font-mono text-sm"
                      rows={6}
                      placeholder="def calculate(df):&#10;    return df['column'].mean()"
                    />
                    <p className="text-xs text-gray-500 mt-1">
                      Write a Python function that takes a pandas DataFrame and returns a single numeric value
                    </p>
                  </div>
                ) : (
                  <>
                    <div>
                      <label className="block text-sm font-medium mb-1">Column</label>
                      <input
                        type="text"
                        name="column"
                        value={newKPI.column}
                        onChange={handleKPIChange}
                        className="w-full p-2 border rounded"
                        placeholder="e.g., temperature"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium mb-1">Operation</label>
                      <select
                        name="operation"
                        value={newKPI.operation}
                        onChange={handleKPIChange}
                        className="w-full p-2 border rounded"
                      >
                        <option value="max">Maximum</option>
                        <option value="min">Minimum</option>
                        <option value="mean">Mean</option>
                        <option value="sum">Sum</option>
                        <option value="std">Standard Deviation</option>
                        <option value="final">Final Value</option>
                      </select>
                    </div>
                  </>
                )}
                
                <div className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    name="isObjective"
                    checked={newKPI.isObjective}
                    onChange={handleKPIChange}
                    className="rounded border-gray-300"
                  />
                  <label className="text-sm">Use as optimization objective</label>
                </div>
                
                {newKPI.isObjective && (
                  <div className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      name="maximize"
                      checked={newKPI.maximize}
                      onChange={handleKPIChange}
                      className="rounded border-gray-300"
                    />
                    <label className="text-sm">Maximize objective</label>
                  </div>
                )}
                
                <div>
                  <label className="block text-sm font-medium mb-1">Description (optional)</label>
                  <textarea
                    name="description"
                    value={newKPI.description || ''}
                    onChange={handleKPIChange}
                    className="w-full p-2 border rounded"
                    rows={2}
                  />
                </div>
                
                <div className="flex justify-end space-x-2">
                  {editIndex !== null && (
                    <button
                      type="button"
                      onClick={() => {
                        setEditIndex(null);
                        setNewKPI({
                          name: '',
                          column: '',
                          operation: 'max',
                          isObjective: false,
                          maximize: true
                        });
                      }}
                      className="px-4 py-2 border rounded"
                    >
                      Cancel
                    </button>
                  )}
                  
                  <button
                    type="button"
                    onClick={handleAddKPI}
                    className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
                  >
                    {editIndex !== null ? 'Update KPI' : 'Add KPI'}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}
