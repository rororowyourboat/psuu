"""
Main model class implementing the PSUU CadcadModelProtocol.

This module provides the main model class that implements the CadcadModelProtocol
interface for seamless integration with PSUU.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple, Optional, Union, Callable
from dataclasses import dataclass, field
import json

# Import cadCAD components
from cadCAD.configuration import Experiment
from cadCAD.configuration.utils import config_sim
from cadCAD.engine import ExecutionMode, ExecutionContext, Executor

# Import PSUU components
from psuu.protocols.cadcad_protocol import CadcadModelProtocol
from psuu.results import SimulationResults

# Import local modules
from .params import ModelParameters, default_params


# Define State Update functions
def p_sir(params, substep, state_history, state):
    """
    Update function for SIR dynamics.
    """
    # Try to get beta and gamma with defaults
    beta = params.get('beta', 0.3)
    gamma = params.get('gamma', 0.05)
    
    # Get current state values
    S = state['susceptible']
    I = state['infected']
    R = state['recovered']
    N = S + I + R
    
    # Calculate new infections
    if I == 0 or N == 0:
        new_infections = 0
    else:
        new_infections = beta * S * I / N
        
    # Calculate new recoveries
    new_recoveries = gamma * I
    
    return {'new_infections': new_infections, 'new_recoveries': new_recoveries}


def s_susceptible(params, substep, state_history, state, signal):
    """
    State update function for susceptible population.
    """
    S = state['susceptible']
    new_infections = signal['new_infections']
    return ('susceptible', S - new_infections)


def s_infected(params, substep, state_history, state, signal):
    """
    State update function for infected population.
    """
    I = state['infected']
    new_infections = signal['new_infections']
    new_recoveries = signal['new_recoveries']
    return ('infected', I + new_infections - new_recoveries)


def s_recovered(params, substep, state_history, state, signal):
    """
    State update function for recovered population.
    """
    R = state['recovered']
    new_recoveries = signal['new_recoveries']
    return ('recovered', R + new_recoveries)


def s_timestep(params, substep, state_history, state, signal):
    """
    State update function for timestep.
    """
    timestep = state['timestep']
    return ('timestep', timestep + 1)


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
        
        # Define model blocks for cadCAD
        self.partial_state_update_blocks = [
            {
                'policies': {
                    'sir_policy': p_sir
                },
                'variables': {
                    'susceptible': s_susceptible,
                    'infected': s_infected,
                    'recovered': s_recovered,
                    'timestep': s_timestep
                }
            }
        ]
    
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
        return {
            "peak_infected": self._calculate_peak_infected,
            "total_infected": self._calculate_total_infected,
            "epidemic_duration": self._calculate_epidemic_duration,
            "r0": lambda df=None, params=None: params['beta'] / params['gamma'] if params else 0
        }
    
    def _calculate_peak_infected(self, df):
        """Calculate peak infected from cadCAD output DataFrame."""
        # Extract the state dictionaries from the first row
        states = []
        for i in range(df.shape[1]):
            # Get the dictionary from position 0, column i
            if isinstance(df.iloc[0, i], dict) and 'infected' in df.iloc[0, i]:
                states.append(df.iloc[0, i])
        
        # Calculate peak infected
        peak = max(state['infected'] for state in states) if states else 0
        return peak
    
    def _calculate_total_infected(self, df):
        """Calculate total infected from cadCAD output DataFrame."""
        # Extract the state dictionaries from the first row
        states = []
        for i in range(df.shape[1]):
            # Get the dictionary from position 0, column i
            if isinstance(df.iloc[0, i], dict) and 'susceptible' in df.iloc[0, i]:
                states.append(df.iloc[0, i])
        
        # Calculate total infected (initial susceptible - final susceptible)
        if states:
            initial_susceptible = states[0]['susceptible']
            final_susceptible = states[-1]['susceptible']
            return initial_susceptible - final_susceptible
        return 0
    
    def _calculate_epidemic_duration(self, df):
        """Calculate epidemic duration from cadCAD output DataFrame."""
        # Extract the state dictionaries from the first row
        states = []
        for i in range(df.shape[1]):
            # Get the dictionary from position 0, column i
            if isinstance(df.iloc[0, i], dict) and 'infected' in df.iloc[0, i]:
                states.append(df.iloc[0, i])
        
        # Calculate duration (timesteps with infected > 0)
        if states:
            infected_states = [state['infected'] > 1 for state in states]
            return sum(infected_states)
        return 0
    
    def get_initial_state(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Define the initial state of the system.
        
        Args:
            params: Optional parameters to use (defaults to self.params)
            
        Returns:
            Dictionary of initial state variables
        """
        params = params or self.params.to_dict()
        population = params.get('population', 1000)
        initial_infected = params.get('initial_infected', 10)
        
        return {
            'susceptible': population - initial_infected,
            'infected': initial_infected,
            'recovered': 0,
            'timestep': 0
        }
    
    def get_cadcad_config(self) -> Dict[str, Any]:
        """
        Get cadCAD configuration details.
        
        Returns:
            Dictionary with cadCAD configuration
        """
        return {
            "N": self.monte_carlo_runs,  # number of monte carlo runs
            "T": self.timesteps,  # timesteps
            "blocks": self.partial_state_update_blocks  # model blocks
        }
    
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
            
        # Get initial state
        initial_state = self.get_initial_state(params)
        
        # Define simulation config
        sim_config = config_sim({
            'T': range(self.timesteps),
            'N': self.monte_carlo_runs,
            'M': {
                'simulation_id': range(1),  # Fixed to avoid M list length error
            },
        })
        
        # Create experiment
        exp = Experiment()
        
        # Make sure params are properly formatted
        sim_params = {
            'beta': params.get('beta', 0.3),
            'gamma': params.get('gamma', 0.05),
            'population': params.get('population', 1000),
            'initial_infected': params.get('initial_infected', 10)
        }
        
        exp.append_configs(
            initial_state=initial_state,
            partial_state_update_blocks=self.partial_state_update_blocks,
            sim_configs=sim_config,
            env_processes={},
            params=sim_params  # Use formatted params
        )
        
        # Execute experiment
        exec_context = ExecutionContext(ExecutionMode.single_proc)
        executor = Executor(exec_context=exec_context, configs=exp.configs)
        
        # Handle the return format (in some versions it returns a tuple, in others just the result)
        try:
            raw_result = executor.execute()
            # If we get here, it's just the raw result
        except ValueError:
            # If there's a ValueError about too many values to unpack,
            # try unpacking as a tuple
            raw_result = executor.execute()[0]
        
        # Convert to DataFrame
        df = pd.DataFrame(raw_result)
        
        # Extract timestep data into a more usable format
        # We need to transform the cadCAD output format to our expected format
        transformed_data = []
        
        # Extract the states from the first row
        states = []
        for i in range(df.shape[1]):
            # Get the dictionary from position 0, column i
            if isinstance(df.iloc[0, i], dict) and 'susceptible' in df.iloc[0, i]:
                state_dict = df.iloc[0, i].copy()
                state_dict['run'] = 0  # Run ID
                states.append(state_dict)
        
        # Create a standard DataFrame
        if states:
            transformed_df = pd.DataFrame(states)
        else:
            # Create an empty DataFrame with expected columns
            transformed_df = pd.DataFrame(columns=['susceptible', 'infected', 'recovered', 'timestep', 'run'])
        
        # Add run parameters as columns
        for param_name, param_value in params.items():
            transformed_df[f"param_{param_name}"] = param_value
        
        # Calculate KPIs
        kpi_definitions = self.get_kpi_definitions()
        kpis = {}
        for name, func in kpi_definitions.items():
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
            time_series_data=transformed_df,
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
