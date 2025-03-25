import React, { useState } from 'react';
import { useRouter } from 'next/router';
import Layout from '@/components/Layout';
import { usePsuu } from '@/contexts/PsuuContext';
import api, { Parameter } from '@/api';

export default function ParametersPage() {
  const router = useRouter();
  const { state, dispatch } = usePsuu();
  const [loading, setLoading] = useState(false);
  
  // New parameter form
  const [newParameter, setNewParameter] = useState<Parameter>({
    name: '',
    type: 'continuous',
    min: 0,
    max: 1
  });
  
  // Parameter being edited
  const [editIndex, setEditIndex] = useState<number | null>(null);
  
  // Handle parameter type change
  const handleTypeChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const type = e.target.value as Parameter['type'];
    
    // Set defaults based on type
    if (type === 'continuous' || type === 'integer') {
      setNewParameter(prev => ({
        ...prev,
        type,
        min: 0,
        max: type === 'integer' ? 10 : 1,
        values: undefined
      }));
    } else if (type === 'categorical') {
      setNewParameter(prev => ({
        ...prev,
        type,
        values: [],
        min: undefined,
        max: undefined
      }));
    }
  };
  
  // Handle parameter change
  const handleParameterChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    
    // Handle numeric conversions
    if (name === 'min' || name === 'max') {
      setNewParameter(prev => ({
        ...prev,
        [name]: parseFloat(value)
      }));
    } else {
      setNewParameter(prev => ({
        ...prev,
        [name]: value
      }));
    }
  };
  
  // Handle categorical values change
  const handleValuesChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const valuesText = e.target.value;
    
    // Parse comma-separated values
    try {
      // Split and trim values, then JSON.parse each value
      const values = valuesText.split(',')
        .map(v => v.trim())
        .filter(v => v) // Remove empty strings
        .map(v => {
          try {
            return JSON.parse(v);
          } catch {
            return v; // If JSON parsing fails, use the string value
          }
        });
      
      setNewParameter(prev => ({
        ...prev,
        values
      }));
    } catch (error) {
      console.error('Failed to parse values:', error);
    }
  };
  
  // Add or update parameter
  const handleAddParameter = async () => {
    // Validation
    if (!newParameter.name) {
      alert('Parameter name is required');
      return;
    }
    
    if (
      (newParameter.type === 'continuous' || newParameter.type === 'integer') &&
      (newParameter.min === undefined || newParameter.max === undefined || newParameter.min >= newParameter.max)
    ) {
      alert('Min must be less than max');
      return;
    }
    
    if (newParameter.type === 'categorical' && (!newParameter.values || newParameter.values.length === 0)) {
      alert('Categorical parameter must have at least one value');
      return;
    }
    
    // If editing, update parameter
    if (editIndex !== null) {
      dispatch({
        type: 'UPDATE_PARAMETER',
        payload: {
          index: editIndex,
          parameter: newParameter
        }
      });
      
      setEditIndex(null);
    } else {
      // Add new parameter
      dispatch({
        type: 'ADD_PARAMETER',
        payload: newParameter
      });
    }
    
    // Reset form
    setNewParameter({
      name: '',
      type: 'continuous',
      min: 0,
      max: 1
    });
  };
  
  // Edit parameter
  const handleEditParameter = (index: number) => {
    setEditIndex(index);
    setNewParameter(state.parameters[index]);
  };
  
  // Remove parameter
  const handleRemoveParameter = (index: number) => {
    if (confirm('Are you sure you want to remove this parameter?')) {
      dispatch({
        type: 'REMOVE_PARAMETER',
        payload: index
      });
    }
  };
  
  // Save parameters and go to next step
  const handleSaveParameters = async () => {
    if (state.parameters.length === 0) {
      alert('Please add at least one parameter');
      return;
    }
    
    setLoading(true);
    
    try {
      await api.setParameterSpace(state.parameters);
      
      // Set active step
      dispatch({ type: 'SET_ACTIVE_STEP', payload: 'kpis' });
      
      // Navigate to KPIs page
      router.push('/kpis');
    } catch (error) {
      alert('Failed to save parameters');
      console.error('Failed to save parameters:', error);
    } finally {
      setLoading(false);
    }
  };
  
  // Ensure connection is established
  if (!state.isConnected) {
    if (typeof window !== 'undefined') {
      router.push('/');
    }
    return null;
  }
  
  return (
    <Layout>
      <div className="max-w-4xl mx-auto">
        <h1 className="text-2xl font-bold mb-6">Parameter Configuration</h1>
        
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <div className="bg-white border rounded p-4 mb-6">
              <h2 className="text-lg font-medium mb-4">Parameter Space</h2>
              
              {state.parameters.length === 0 ? (
                <div className="p-4 bg-gray-50 border rounded text-center">
                  No parameters defined yet. Add parameters using the form.
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="bg-gray-50">
                        <th className="py-2 px-3 text-left">Name</th>
                        <th className="py-2 px-3 text-left">Type</th>
                        <th className="py-2 px-3 text-left">Range/Values</th>
                        <th className="py-2 px-3 text-left">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {state.parameters.map((param, index) => (
                        <tr key={index} className="border-t">
                          <td className="py-2 px-3">{param.name}</td>
                          <td className="py-2 px-3">{param.type}</td>
                          <td className="py-2 px-3">
                            {param.type === 'categorical' 
                              ? (param.values?.join(', ') || '')
                              : `${param.min} to ${param.max}`
                            }
                          </td>
                          <td className="py-2 px-3">
                            <div className="flex space-x-2">
                              <button
                                onClick={() => handleEditParameter(index)}
                                className="text-blue-500 hover:text-blue-700"
                              >
                                Edit
                              </button>
                              <button
                                onClick={() => handleRemoveParameter(index)}
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
                  onClick={handleSaveParameters}
                  className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
                  disabled={state.parameters.length === 0 || loading}
                >
                  {loading ? 'Saving...' : 'Save and Continue'}
                </button>
              </div>
            </div>
          </div>
          
          <div>
            <div className="bg-white border rounded p-4 sticky top-4">
              <h2 className="text-lg font-medium mb-4">
                {editIndex !== null ? 'Edit Parameter' : 'Add Parameter'}
              </h2>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Name</label>
                  <input
                    type="text"
                    name="name"
                    value={newParameter.name}
                    onChange={handleParameterChange}
                    className="w-full p-2 border rounded"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium mb-1">Type</label>
                  <select
                    name="type"
                    value={newParameter.type}
                    onChange={handleTypeChange}
                    className="w-full p-2 border rounded"
                  >
                    <option value="continuous">Continuous</option>
                    <option value="integer">Integer</option>
                    <option value="categorical">Categorical</option>
                  </select>
                </div>
                
                {(newParameter.type === 'continuous' || newParameter.type === 'integer') && (
                  <>
                    <div>
                      <label className="block text-sm font-medium mb-1">Minimum</label>
                      <input
                        type={newParameter.type === 'integer' ? 'number' : 'text'}
                        name="min"
                        value={newParameter.min}
                        onChange={handleParameterChange}
                        step={newParameter.type === 'integer' ? 1 : 'any'}
                        className="w-full p-2 border rounded"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium mb-1">Maximum</label>
                      <input
                        type={newParameter.type === 'integer' ? 'number' : 'text'}
                        name="max"
                        value={newParameter.max}
                        onChange={handleParameterChange}
                        step={newParameter.type === 'integer' ? 1 : 'any'}
                        className="w-full p-2 border rounded"
                      />
                    </div>
                  </>
                )}
                
                {newParameter.type === 'categorical' && (
                  <div>
                    <label className="block text-sm font-medium mb-1">Values (comma-separated)</label>
                    <textarea
                      name="values"
                      value={newParameter.values?.join(', ') || ''}
                      onChange={handleValuesChange}
                      className="w-full p-2 border rounded"
                      rows={4}
                    />
                    <p className="text-xs text-gray-500 mt-1">
                      Enter comma-separated values. Use JSON format for non-string values (e.g., true, 42).
                    </p>
                  </div>
                )}
                
                <div>
                  <label className="block text-sm font-medium mb-1">Description (optional)</label>
                  <textarea
                    name="description"
                    value={newParameter.description || ''}
                    onChange={handleParameterChange}
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
                        setNewParameter({
                          name: '',
                          type: 'continuous',
                          min: 0,
                          max: 1
                        });
                      }}
                      className="px-4 py-2 border rounded"
                    >
                      Cancel
                    </button>
                  )}
                  
                  <button
                    type="button"
                    onClick={handleAddParameter}
                    className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
                  >
                    {editIndex !== null ? 'Update Parameter' : 'Add Parameter'}
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
