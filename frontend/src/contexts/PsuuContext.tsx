import React, { createContext, useContext, useReducer, ReactNode } from 'react';
import { 
  ModelConnection, 
  Parameter, 
  KPI, 
  OptimizationConfig,
  OptimizationResult
} from '@/api';

// State definition
interface PsuuState {
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

// Initial state
const initialState: PsuuState = {
  modelConnection: null,
  isConnected: false,
  connectionError: null,
  
  parameters: [],
  
  kpis: [],
  
  optimizationConfig: null,
  currentJob: {
    jobId: null,
    status: 'pending',
    progress: 0,
    message: null,
  },
  optimizationResults: null,
  
  activeStep: 'connection',
  isLoading: false,
};

// Action types
type Action =
  | { type: 'SET_MODEL_CONNECTION'; payload: ModelConnection }
  | { type: 'SET_CONNECTION_STATUS'; payload: { isConnected: boolean; error?: string | null } }
  | { type: 'SET_PARAMETERS'; payload: Parameter[] }
  | { type: 'ADD_PARAMETER'; payload: Parameter }
  | { type: 'UPDATE_PARAMETER'; payload: { index: number; parameter: Parameter } }
  | { type: 'REMOVE_PARAMETER'; payload: number }
  | { type: 'SET_KPIS'; payload: KPI[] }
  | { type: 'ADD_KPI'; payload: KPI }
  | { type: 'UPDATE_KPI'; payload: { index: number; kpi: KPI } }
  | { type: 'REMOVE_KPI'; payload: number }
  | { type: 'SET_OPTIMIZATION_CONFIG'; payload: OptimizationConfig }
  | { type: 'SET_JOB_STATUS'; payload: { jobId: string; status: string; progress: number; message?: string } }
  | { type: 'SET_OPTIMIZATION_RESULTS'; payload: OptimizationResult }
  | { type: 'SET_ACTIVE_STEP'; payload: PsuuState['activeStep'] }
  | { type: 'SET_LOADING'; payload: boolean };

// Reducer
function psuuReducer(state: PsuuState, action: Action): PsuuState {
  switch (action.type) {
    case 'SET_MODEL_CONNECTION':
      return {
        ...state,
        modelConnection: action.payload,
      };
      
    case 'SET_CONNECTION_STATUS':
      return {
        ...state,
        isConnected: action.payload.isConnected,
        connectionError: action.payload.error || null,
      };
      
    case 'SET_PARAMETERS':
      return {
        ...state,
        parameters: action.payload,
      };
      
    case 'ADD_PARAMETER':
      return {
        ...state,
        parameters: [...state.parameters, action.payload],
      };
      
    case 'UPDATE_PARAMETER':
      return {
        ...state,
        parameters: state.parameters.map((param, index) => 
          index === action.payload.index ? action.payload.parameter : param
        ),
      };
      
    case 'REMOVE_PARAMETER':
      return {
        ...state,
        parameters: state.parameters.filter((_, index) => index !== action.payload),
      };
      
    case 'SET_KPIS':
      return {
        ...state,
        kpis: action.payload,
      };
      
    case 'ADD_KPI':
      return {
        ...state,
        kpis: [...state.kpis, action.payload],
      };
      
    case 'UPDATE_KPI':
      return {
        ...state,
        kpis: state.kpis.map((kpi, index) => 
          index === action.payload.index ? action.payload.kpi : kpi
        ),
      };
      
    case 'REMOVE_KPI':
      return {
        ...state,
        kpis: state.kpis.filter((_, index) => index !== action.payload),
      };
      
    case 'SET_OPTIMIZATION_CONFIG':
      return {
        ...state,
        optimizationConfig: action.payload,
      };
      
    case 'SET_JOB_STATUS':
      return {
        ...state,
        currentJob: {
          jobId: action.payload.jobId,
          status: action.payload.status as any,
          progress: action.payload.progress,
          message: action.payload.message || null,
        },
      };
      
    case 'SET_OPTIMIZATION_RESULTS':
      return {
        ...state,
        optimizationResults: action.payload,
      };
      
    case 'SET_ACTIVE_STEP':
      return {
        ...state,
        activeStep: action.payload,
      };
      
    case 'SET_LOADING':
      return {
        ...state,
        isLoading: action.payload,
      };
      
    default:
      return state;
  }
}

// Context
interface PsuuContextType {
  state: PsuuState;
  dispatch: React.Dispatch<Action>;
}

const PsuuContext = createContext<PsuuContextType | undefined>(undefined);

// Provider component
interface PsuuProviderProps {
  children: ReactNode;
}

export function PsuuProvider({ children }: PsuuProviderProps) {
  const [state, dispatch] = useReducer(psuuReducer, initialState);

  const value = { state, dispatch };
  
  return <PsuuContext.Provider value={value}>{children}</PsuuContext.Provider>;
}

// Hook for using the PSUU context
export function usePsuu() {
  const context = useContext(PsuuContext);
  
  if (context === undefined) {
    throw new Error('usePsuu must be used within a PsuuProvider');
  }
  
  return context;
}
