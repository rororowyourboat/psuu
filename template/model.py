"""
Main model class implementing the PSUU CadcadModelProtocol.

This module provides the main model class that implements the CadcadModelProtocol
interface for seamless integration with PSUU.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple, Optional, Union, Callable
from dataclasses import dataclass, field

# Import cadCAD components
from cadCAD.configuration import Configuration
from cadCAD.configuration.utils import config_sim
from cadCAD.engine import ExecutionMode, ExecutionContext, Executor

# Import PSUU components
from psuu.protocols.cadcad_protocol import CadcadModelProtocol
from psuu.results import SimulationResults

# Import local modules
from .params import ModelParameters, default_params
from .core_logic import get_state_update_functions, get_initial_state
from .kpi import get_all_kpis


class SIRModel(CadcadModelProtocol):
    """
    SIR epidemic model implementing the PSUU CadcadModelProtocol.
    
    This class provides a complete implementation of an SIR epidemic model
    that integrates with PSUU for parameter optimization.
    """
    
    # Model version
    VERSION = "0.1.0"
    
    def __init__(self, params: Optional[ModelParameters] = None):
        """
        Initialize the model with parameters.
        
        Args:
            params: Model parameters (defaults to default_params if None)
        """
        self.params = params or default_params
        self.timesteps = 100
        self.monte_carlo_runs = 1
        self.kpi_functions = get_all_kpis()
    
    def get_parameter_space(self) -> Dict[str, Union[List, Tuple, Dict]]:
        """
        Return the parameter space definition.
        
        Returns:
            Dictionary mapping parameter names to their ranges or options
        """
        return self.params.parameter_space
    
    def get_kpi_definitions(self) -> Dict[str, Callable]:
        """
        Return KPI calculation functions.
        
        Returns:
            Dictionary mapping KPI names to functions that compute them
        """
        return self.kpi_functions
    
    def get_initial_state(self) -> Dict[str, Any]:
        """
        Define the initial state of the system.
        
        Returns:
            Dictionary of initial state variables
        """
        return get_initial_state(self.params.to_dict())
    
    def get_cadcad_config(self) -> Dict[str, Any]:
        """
        Get cadCAD configuration details.
        
        Returns:
            Dictionary with cadCAD configuration
        """
        return {
            "N": self.monte_carlo_runs,  # number of monte carlo runs
            "T": range(self.timesteps),  # timesteps
            "M": {}  # simulation methods (empty for default)
        }
    
    def _build_cadcad_config(self, params_dict: Dict[str, Any]) -> Configuration:
        """
        Build cadCAD configuration object.
        
        Args:
            params_dict: Dictionary of parameter values
            
        Returns:
            cadCAD Configuration object
        """
        # Get initial state
        initial_state = get_initial_state(params_dict)
        
        # Get state update functions
        state_update_functions = get_state_update_functions()
        
        # Define policy and state update blocks
        psubs = [{}]  # Empty policy function - we're using only state updates
        
        # State update blocks - one for each function
        subs = [
            {
                'policies': {},
                'variables': {
                    k: s_function for k, s_function in 
                    zip(initial_state.keys(), state_update_functions)
                }
            }
        ]
        
        # Build config
        config = config_sim({
            'T': range(self.timesteps),
            'N': self.monte_carlo_runs,
            'M': {},
        })
        
        # Create system configuration
        return Configuration(
            initial_state=initial_state,
            partial_state_update_blocks=subs,
            sim_config=config,
            params=params_dict
        )
    
    def run(self, params: Dict[str, Any], **kwargs) -> SimulationResults:
        """
        Run cadCAD simulation with given parameters.
        
        Args:
            params: Dictionary of parameter values
            **kwargs: Additional run options
                - timesteps: Number of timesteps (default: self.timesteps)
                - monte_carlo_runs: Number of Monte Carlo runs (default: self.monte_carlo_runs)
            
        Returns:
            SimulationResults object with time series data and KPIs
        """
        # Update simulation settings from kwargs
        if 'timesteps' in kwargs:
            self.timesteps = kwargs['timesteps']
        if 'monte_carlo_runs' in kwargs:
            self.monte_carlo_runs = kwargs['monte_carlo_runs']
        
        # Build configuration
        config = self._build_cadcad_config(params)
        
        # Create and run executor
        exec_context = ExecutionContext(ExecutionMode.SINGLE_PROCESS)
        executor = Executor(exec_context=exec_context, configs=config)
        
        # Run simulation
        raw_result, _ = executor.execute()
        
        # Convert to DataFrame
        df = pd.DataFrame(raw_result)
        
        # Add run parameters as columns
        for param_name, param_value in params.items():
            df[f"param_{param_name}"] = param_value
        
        # Calculate KPIs
        kpis = {}
        for name, func in self.kpi_functions.items():
            # Special case for r0 which depends on parameters
            if name == 'r0':
                kpis[name] = func(df, params)
            else:
                kpis[name] = func(df)
        
        # Create metadata
        metadata = {
            "model_version": self.VERSION,
            "timesteps": self.timesteps,
            "monte_carlo_runs": self.monte_carlo_runs,
            "simulation_time": pd.Timestamp.now().isoformat()
        }
        
        # Return standardized SimulationResults object
        return SimulationResults(
            time_series_data=df,
            kpis=kpis,
            metadata=metadata,
            parameters=params
        )
    
    def validate_params(self, params: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validate simulation parameters.
        
        Args:
            params: Dictionary of parameter values to validate
            
        Returns:
            Tuple of (is_valid, error_message_if_any)
        """
        # Run base validation from ModelProtocol
        is_valid, error_msg = super().validate_parameters(params)
        if not is_valid:
            return is_valid, error_msg
        
        # Add model-specific validation
        try:
            # Ensure R0 > 0 for epidemic simulation
            beta = params.get('beta', self.params.beta)
            gamma = params.get('gamma', self.params.gamma)
            
            if gamma <= 0:
                return False, f"Invalid gamma value: {gamma}. Must be greater than 0."
                
            r0 = beta / gamma
            
            if r0 <= 0:
                return False, f"Invalid R0 value: {r0}. Must be greater than 0."
                
            # All checks passed
            return True, None
            
        except Exception as e:
            return False, f"Parameter validation error: {str(e)}"
