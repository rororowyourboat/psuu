import React from 'react';
import Layout from '@/components/Layout';

export default function ApiDocsPage() {
  return (
    <Layout>
      <div className="max-w-4xl mx-auto">
        <h1 className="text-2xl font-bold mb-6">PSUU API Documentation</h1>
        
        {/* Backend API */}
        <section className="mb-12">
          <h2 className="text-xl font-semibold mb-4">Backend API</h2>
          
          {/* Model Connection */}
          <div className="bg-white border rounded-lg p-6 mb-6">
            <h3 className="text-lg font-medium mb-3">Model Connection</h3>
            <div className="space-y-4">
              <div>
                <div className="flex items-center space-x-2">
                  <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-sm">POST</span>
                  <code className="text-sm">/api/models/test-connection</code>
                </div>
                <p className="mt-2 text-sm text-slate-600">Test connection to simulation model.</p>
                <div className="mt-2">
                  <h4 className="text-sm font-medium mb-1">Request Body:</h4>
                  <pre className="bg-slate-50 p-3 rounded text-xs">
{`{
  "type": "protocol" | "cli",
  "details": {
    // For protocol connection
    "moduleClass"?: string,
    "protocol"?: string,
    
    // For CLI connection
    "command"?: string,
    "paramFormat"?: string,
    "outputFormat"?: string,
    "workingDir"?: string
  }
}`}
                  </pre>
                </div>
              </div>
            </div>
          </div>
          
          {/* Parameters */}
          <div className="bg-white border rounded-lg p-6 mb-6">
            <h3 className="text-lg font-medium mb-3">Parameters</h3>
            <div className="space-y-4">
              <div>
                <div className="flex items-center space-x-2">
                  <span className="px-2 py-1 bg-green-100 text-green-700 rounded text-sm">GET</span>
                  <code className="text-sm">/api/parameters</code>
                </div>
                <p className="mt-2 text-sm text-slate-600">Get model parameter space definition.</p>
                <div className="mt-2">
                  <h4 className="text-sm font-medium mb-1">Response:</h4>
                  <pre className="bg-slate-50 p-3 rounded text-xs">
{`[{
  "name": string,
  "type": "continuous" | "integer" | "categorical",
  "min"?: number,
  "max"?: number,
  "values"?: any[],
  "description"?: string
}]`}
                  </pre>
                </div>
              </div>
              
              <div>
                <div className="flex items-center space-x-2">
                  <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-sm">POST</span>
                  <code className="text-sm">/api/parameters</code>
                </div>
                <p className="mt-2 text-sm text-slate-600">Update parameter space configuration.</p>
              </div>
            </div>
          </div>
          
          {/* KPIs */}
          <div className="bg-white border rounded-lg p-6 mb-6">
            <h3 className="text-lg font-medium mb-3">KPIs</h3>
            <div className="space-y-4">
              <div>
                <div className="flex items-center space-x-2">
                  <span className="px-2 py-1 bg-green-100 text-green-700 rounded text-sm">GET</span>
                  <code className="text-sm">/api/kpis</code>
                </div>
                <p className="mt-2 text-sm text-slate-600">Get available KPI definitions.</p>
                <div className="mt-2">
                  <h4 className="text-sm font-medium mb-1">Response:</h4>
                  <pre className="bg-slate-50 p-3 rounded text-xs">
{`[{
  "name": string,
  "type": "custom",
  "isObjective": boolean,
  "maximize": boolean
}]`}
                  </pre>
                </div>
              </div>
            </div>
          </div>
          
          {/* Optimization */}
          <div className="bg-white border rounded-lg p-6">
            <h3 className="text-lg font-medium mb-3">Optimization</h3>
            <div className="space-y-4">
              <div>
                <div className="flex items-center space-x-2">
                  <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-sm">POST</span>
                  <code className="text-sm">/api/optimization/configure</code>
                </div>
                <p className="mt-2 text-sm text-slate-600">Configure optimization settings.</p>
                <div className="mt-2">
                  <h4 className="text-sm font-medium mb-1">Request Body:</h4>
                  <pre className="bg-slate-50 p-3 rounded text-xs">
{`{
  "method": "grid" | "random" | "bayesian",
  "iterations"?: number,
  "initialPoints"?: number,
  "seed"?: number
}`}
                  </pre>
                </div>
              </div>
              
              <div>
                <div className="flex items-center space-x-2">
                  <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-sm">POST</span>
                  <code className="text-sm">/api/optimization/start</code>
                </div>
                <p className="mt-2 text-sm text-slate-600">Start optimization process.</p>
              </div>
              
              <div>
                <div className="flex items-center space-x-2">
                  <span className="px-2 py-1 bg-green-100 text-green-700 rounded text-sm">GET</span>
                  <code className="text-sm">/api/optimization/stream</code>
                </div>
                <p className="mt-2 text-sm text-slate-600">Stream optimization updates (Server-Sent Events).</p>
                <div className="mt-2">
                  <h4 className="text-sm font-medium mb-1">Stream Events:</h4>
                  <pre className="bg-slate-50 p-3 rounded text-xs">
{`// Step Update
{
  "type": "step",
  "step": number,
  "command": string,
  "result": {
    "parameters": Record<string, any>,
    "kpis": Record<string, number>
  }
}

// Completion
{
  "type": "complete",
  "result": {
    "bestParameters": Record<string, any>,
    "bestKPIs": Record<string, number>,
    "iterations": number,
    "elapsedTime": number
  }
}

// Error
{
  "type": "error",
  "message": string
}`}
                  </pre>
                </div>
              </div>
            </div>
          </div>
        </section>
        
        {/* Frontend State Management */}
        <section className="mb-12">
          <h2 className="text-xl font-semibold mb-4">Frontend State Types</h2>
          
          <div className="bg-white border rounded-lg p-6">
            <h3 className="text-lg font-medium mb-3">PSUU Context State</h3>
            <pre className="bg-slate-50 p-3 rounded text-xs overflow-auto">
{`interface PsuuState {
  // Connection
  modelConnection: ModelConnection | null;
  isConnected: boolean;
  connectionError: string | null;
  
  // Parameters
  parameters: Parameter[];
  
  // KPIs
  kpis: KPI[];
  
  // Optimization
  optimizationConfig: OptimizationConfig | null;
  currentJob: {
    jobId: string | null;
    status: 'pending' | 'running' | 'completed' | 'failed';
    progress: number;
    message: string | null;
  };
  optimizationResults: OptimizationResult | null;
  
  // UI state
  activeStep: 'connection' | 'parameters' | 'kpis' | 'optimization' | 'results';
  isLoading: boolean;
}

// Available Context Actions
type Action =
  | { type: 'SET_MODEL_CONNECTION'; payload: ModelConnection }
  | { type: 'SET_CONNECTION_STATUS'; payload: { isConnected: boolean; error?: string } }
  | { type: 'SET_PARAMETERS'; payload: Parameter[] }
  | { type: 'SET_KPIS'; payload: KPI[] }
  | { type: 'SET_OPTIMIZATION_CONFIG'; payload: OptimizationConfig }
  | { type: 'SET_JOB_STATUS'; payload: JobStatus }
  | { type: 'SET_OPTIMIZATION_RESULTS'; payload: OptimizationResult }
  | { type: 'SET_ACTIVE_STEP'; payload: PsuuState['activeStep'] }
  | { type: 'SET_LOADING'; payload: boolean };`}
            </pre>
          </div>
        </section>
      </div>
    </Layout>
  );
}
