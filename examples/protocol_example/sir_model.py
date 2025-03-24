"""
SIR Model Example.

This module provides an example of a SIR model that implements
the CadcadModelProtocol.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple, Optional, Union, Callable

# Import the PSUU protocol
from psuu.protocols import CadcadModelProtocol
from psuu.results import SimulationResults


class SIRModel(CadcadModelProtocol):
    """
    SIR epidemic model implementing the CadcadModelProtocol.
    
    This class demonstrates how to implement the protocol for a
    simple epidemiological model.
    """
    
    VERSION = "0.1.0"
    
    def __init__(self, timesteps: int = 100, samples: int = 1):
        """
        Initialize the SIR model.
        
        Args:
            timesteps: Number of timesteps to simulate
            samples: Number of Monte Carlo samples
        """
        self.timesteps = timesteps
        self.samples = samples
        
        # Default parameters
        self.default_params = {
            "beta": 0.3,         # Transmission rate
            "gamma": 0.05,       # Recovery rate
            "population": 1000,  # Total population
            "initial_infected": 5 # Initial number of infected
        }
    
    def run(self, params: Dict[str, Any], **kwargs) -> SimulationResults:
        """
        Run the SIR model simulation.
        
        Args:
            params: Dictionary of parameter values
            **kwargs: Additional simulation options
                - timesteps: Override default timesteps
                - samples: Override default samples
        
        Returns:
            SimulationResults object with simulation results
        """
        # Merge default parameters with provided parameters
        run_params = self.default_params.copy()
        run_params.update(params)
        
        # Get simulation options
        timesteps = kwargs.get('timesteps', self.timesteps)
        samples = kwargs.get('samples', self.samples)
        
        # Validate parameters
        is_valid, error_msg = self.validate_parameters(run_params)
        if not is_valid:
            raise ValueError(error_msg)
        
        # Run simulation for each sample
        all_results = []
        
        for sample in range(samples):
            # Initial state
            population = run_params["population"]
            initial_infected = run_params["initial_infected"]
            
            S = population - initial_infected
            I = initial_infected
            R = 0
            
            # Arrays to store results
            S_values = [S]
            I_values = [I]
            R_values = [R]
            time_values = [0]
            
            # Run simulation
            for t in range(1, timesteps + 1):
                # SIR model equations
                beta = run_params["beta"]
                gamma = run_params["gamma"]
                
                new_infections = beta * S * I / population
                new_recoveries = gamma * I
                
                S -= new_infections
                I += new_infections - new_recoveries
                R += new_recoveries
                
                # Store results
                S_values.append(S)
                I_values.append(I)
                R_values.append(R)
                time_values.append(t)
            
            # Create DataFrame for this sample
            sample_df = pd.DataFrame({
                'timestep': time_values,
                'S': S_values,
                'I': I_values,
                'R': R_values,
                'run': sample
            })
            
            all_results.append(sample_df)
        
        # Combine all samples
        combined_df = pd.concat(all_results, ignore_index=True)
        
        # Calculate KPIs
        kpis = self._calculate_kpis(combined_df, run_params)
        
        # Create metadata
        metadata = {
            "model": "SIR",
            "timesteps": timesteps,
            "samples": samples,
            "version": self.VERSION
        }
        
        # Return results
        return SimulationResults(
            time_series_data=combined_df,
            kpis=kpis,
            metadata=metadata,
            parameters=run_params
        )
    
    def get_parameter_space(self) -> Dict[str, Union[List, Tuple, Dict]]:
        """
        Return the parameter space definition.
        
        Returns:
            Dictionary mapping parameter names to their valid ranges/values
        """
        return {
            "beta": {
                "type": "continuous",
                "range": (0.1, 0.5),
                "description": "Transmission rate (contact rate * transmission probability)"
            },
            "gamma": {
                "type": "continuous",
                "range": (0.01, 0.1),
                "description": "Recovery rate (1 / infectious period)"
            },
            "population": {
                "type": "discrete",
                "range": [1000, 5000, 10000],
                "description": "Total population"
            },
            "initial_infected": {
                "type": "continuous",
                "range": (1, 100),
                "description": "Initial number of infected individuals",
                "required": True
            }
        }
    
    def get_kpi_definitions(self) -> Dict[str, Union[Callable, Dict]]:
        """
        Return KPI calculation functions.
        
        Returns:
            Dictionary mapping KPI names to their calculation functions
        """
        return {
            "peak_infections": {
                "function": self.peak_infections,
                "description": "Maximum number of infections at any time",
                "tags": ["epidemic", "critical"]
            },
            "total_infections": {
                "function": self.total_infections,
                "description": "Total number of people infected over the course of the epidemic",
                "tags": ["epidemic", "cumulative"]
            },
            "epidemic_duration": {
                "function": self.epidemic_duration,
                "description": "Number of days until infections drop below 1% of peak",
                "tags": ["epidemic", "temporal"]
            },
            "r0": {
                "function": self.calculate_r0,
                "description": "Basic reproduction number",
                "tags": ["epidemic", "transmission"]
            }
        }
    
    def get_cadcad_config(self) -> Dict[str, Any]:
        """
        Get cadCAD configuration.
        
        Returns:
            Dictionary with cadCAD configuration
        """
        # This is a simplified version since we're not using actual cadCAD
        return {
            "timesteps": self.timesteps,
            "samples": self.samples,
            "model_type": "SIR"
        }
    
    def _calculate_kpis(self, df: pd.DataFrame, params: Dict[str, Any]) -> Dict[str, float]:
        """
        Calculate all KPIs from simulation results.
        
        Args:
            df: DataFrame with simulation results
            params: Parameters used for simulation
            
        Returns:
            Dictionary of KPI values
        """
        kpis = {}
        
        # Calculate each KPI
        kpis["peak_infections"] = self.peak_infections(df)
        kpis["total_infections"] = self.total_infections(df)
        kpis["epidemic_duration"] = self.epidemic_duration(df)
        kpis["r0"] = self.calculate_r0(df, params.get("beta", 0.3), params.get("gamma", 0.05))
        
        return kpis
    
    # KPI calculation functions
    
    @staticmethod
    def peak_infections(df: pd.DataFrame) -> float:
        """
        Calculate peak infections KPI.
        
        Args:
            df: DataFrame with simulation results
            
        Returns:
            Peak number of infections
        """
        return df['I'].max()
    
    @staticmethod
    def total_infections(df: pd.DataFrame) -> float:
        """
        Calculate total infections KPI.
        
        Args:
            df: DataFrame with simulation results
            
        Returns:
            Total number of infections (final R value)
        """
        # Get the last timestep for each run
        last_timesteps = df.groupby('run')['timestep'].max()
        final_states = df[df['timestep'].isin(last_timesteps.values)]
        
        # Return the average final R value across all runs
        return final_states['R'].mean()
    
    @staticmethod
    def epidemic_duration(df: pd.DataFrame) -> float:
        """
        Calculate epidemic duration KPI.
        
        Args:
            df: DataFrame with simulation results
            
        Returns:
            Duration of the epidemic in timesteps
        """
        # Calculate peak for each run
        peaks = df.groupby('run')['I'].max()
        
        durations = []
        for run in df['run'].unique():
            run_df = df[df['run'] == run].sort_values('timestep')
            peak = peaks[run]
            threshold = peak * 0.01  # 1% of peak
            
            # Find when infections drop below threshold after peak
            peak_time = run_df[run_df['I'] == peak]['timestep'].iloc[0]
            post_peak = run_df[run_df['timestep'] >= peak_time]
            
            end_points = post_peak[post_peak['I'] <= threshold]
            if not end_points.empty:
                end_time = end_points['timestep'].iloc[0]
                durations.append(end_time)
            else:
                # If never drops below threshold, use max timestep
                durations.append(run_df['timestep'].max())
        
        return np.mean(durations) if durations else 0
    
    @staticmethod
    def calculate_r0(df: pd.DataFrame, beta: Optional[float] = None, gamma: Optional[float] = None) -> float:
        """
        Calculate basic reproduction number (R0).
        
        Args:
            df: DataFrame with simulation results
            beta: Transmission rate (if not provided, estimated from data)
            gamma: Recovery rate (if not provided, estimated from data)
            
        Returns:
            R0 value
        """
        # Simple calculation if rates are provided
        if beta is not None and gamma is not None:
            return beta / gamma
        
        # Otherwise, estimate from data (simplified)
        early_growth_rate = 0
        try:
            # Use early part of epidemic for estimation
            for run in df['run'].unique():
                run_df = df[(df['run'] == run) & (df['timestep'] <= 10)].copy()
                if len(run_df) > 1:
                    run_df['growth_rate'] = run_df['I'].pct_change()
                    early_growth_rate += run_df['growth_rate'].mean()
            
            early_growth_rate /= len(df['run'].unique())
            
            # Convert growth rate to R0 using standard formula
            return 1 + early_growth_rate * 5  # Assuming average infectious period of 5 days
        except:
            return 0  # Default if calculation fails
