// API client for PSUU backend

// Default API base URL
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000/api';

// Types for API requests and responses
export interface ModelConnection {
  type: 'protocol' | 'cli';
  details: {
    // For protocol connection
    moduleClass?: string;
    protocol?: string;
    
    // For CLI connection
    command?: string;
    paramFormat?: string;
    outputFormat?: string;
    workingDir?: string;
  };
}

export interface Parameter {
  name: string;
  type: 'continuous' | 'integer' | 'categorical';
  min?: number;
  max?: number;
  values?: any[];
  description?: string;
}

export interface KPI {
  name: string;
  column?: string;
  operation?: string;
  function?: string;
  isObjective?: boolean;
  maximize?: boolean;
  description?: string;
}

export interface OptimizationConfig {
  method: 'grid' | 'random' | 'bayesian';
  iterations?: number;
  initialPoints?: number;
  populationSize?: number;
  generations?: number;
  seed?: number;
}

export interface OptimizationResult {
  bestParameters: Record<string, any>;
  bestKPIs: Record<string, number>;
  iterations: number;
  elapsedTime: number;
  allResults?: any[];
}

// API client functions
async function fetchWithErrorHandling(endpoint: string, options: RequestInit = {}) {
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.message || `API error: ${response.status} ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('API request failed:', error);
    throw error;
  }
}

// API endpoints
export const api = {
  // Model connection
  testConnection: async (connection: ModelConnection): Promise<{ success: boolean; message: string }> => {
    return fetchWithErrorHandling('/models/test-connection', {
      method: 'POST',
      body: JSON.stringify(connection),
    });
  },

  // Parameter space
  getParameterSpace: async (): Promise<Parameter[]> => {
    return fetchWithErrorHandling('/parameters');
  },

  setParameterSpace: async (parameters: Parameter[]): Promise<{ success: boolean }> => {
    return fetchWithErrorHandling('/parameters', {
      method: 'POST',
      body: JSON.stringify({ parameters }),
    });
  },

  // KPIs
  getAvailableKPIs: async (): Promise<KPI[]> => {
    return fetchWithErrorHandling('/kpis');
  },

  setKPIs: async (kpis: KPI[]): Promise<{ success: boolean }> => {
    return fetchWithErrorHandling('/kpis', {
      method: 'POST',
      body: JSON.stringify({ kpis }),
    });
  },

  // Optimization
  configureOptimization: async (config: OptimizationConfig): Promise<{ success: boolean }> => {
    return fetchWithErrorHandling('/optimization/configure', {
      method: 'POST',
      body: JSON.stringify(config),
    });
  },

  startOptimization: async (): Promise<{ jobId: string }> => {
    return fetchWithErrorHandling('/optimization/start', {
      method: 'POST',
    });
  },

  getOptimizationStatus: async (jobId: string): Promise<{ 
    status: 'pending' | 'running' | 'completed' | 'failed';
    progress: number;
    message?: string;
    result?: OptimizationResult;
  }> => {
    return fetchWithErrorHandling(`/optimization/status/${jobId}`);
  },

  getOptimizationResults: async (jobId: string): Promise<OptimizationResult> => {
    return fetchWithErrorHandling(`/optimization/results/${jobId}`);
  },

  // Run a single simulation with specific parameters
  runSimulation: async (parameters: Record<string, any>): Promise<any> => {
    return fetchWithErrorHandling('/simulation/run', {
      method: 'POST',
      body: JSON.stringify({ parameters }),
    });
  },
};

export default api;
