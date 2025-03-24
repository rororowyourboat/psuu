"""
CadCAD Simulation Connector for PSUU.

This module provides a custom connector for cadCAD-based simulation models.
"""

import os
import tempfile
import subprocess
import json
import pandas as pd
import numpy as np
from typing import Dict, Any
import time

from psuu.simulation_connector import SimulationConnector


class CadcadSimulationConnector(SimulationConnector):
    """
    Custom simulation connector for cadcad-sandbox that handles its specific output format.
    """
    
    def run_simulation(self, parameters: Dict[str, Any]) -> pd.DataFrame:
        """
        Run the simulation with the given parameters and return results.
        
        Args:
            parameters: Dictionary of parameter names and values
            
        Returns:
            DataFrame containing simulation results
        """
        # Convert any numpy types to native Python types
        cleaned_params = {}
        for key, value in parameters.items():
            if isinstance(value, np.integer):
                cleaned_params[key] = int(value)
            elif isinstance(value, np.floating):
                cleaned_params[key] = float(value)
            else:
                cleaned_params[key] = value
        
        cmd = self._build_command(cleaned_params)
        timestamp = time.strftime("%Y_%m_%d_%H_%M_%S")
        output_name = f"psuu_run_{timestamp}"
        
        # Add output parameter to command
        cmd = f"{cmd} --output {output_name}"
        
        # Run simulation
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                check=True,
                cwd=self.working_dir,
                env=os.environ.copy(),
                capture_output=True,
                text=True
            )
            
            # Find the latest simulation output files
            sim_dir = os.path.join(self.working_dir, "data", "simulations")
            files = [f for f in os.listdir(sim_dir) if f.endswith('.json') and output_name in f]
            
            if not files:
                raise FileNotFoundError(f"No output files found with name {output_name}")
            
            # Get the latest KPI file
            kpi_file = sorted(files)[-1]
            
            # Load KPI data
            with open(os.path.join(sim_dir, kpi_file), 'r') as f:
                kpi_data = json.load(f)
            
            # Convert KPI data to DataFrame for compatibility with our KPI functions
            # Create a synthetic DataFrame with just the KPI values
            peak = kpi_data['peak_infections']['mean']
            total = kpi_data['total_infections']['mean']
            duration = kpi_data['epidemic_duration']['mean']
            r0 = kpi_data['r0']['mean']
            
            df = pd.DataFrame({
                'timestep': [0],
                'I': [peak],         # Using peak as I value
                'S': [1000 - total], # Estimating S from total infections
                'R': [total],        # Using total as R value
                'duration': [duration],
                'r0': [r0]
            })
            
            return df
            
        except subprocess.CalledProcessError as e:
            print(f"Simulation failed with error: {e}")
            print(f"Stdout: {e.stdout}")
            print(f"Stderr: {e.stderr}")
            # Return empty DataFrame with expected columns
            return pd.DataFrame(columns=['timestep', 'I', 'S', 'R', 'duration', 'r0'])


# Custom KPI Functions

def peak_infections(df: pd.DataFrame) -> float:
    """Calculate peak infections KPI from simulation output."""
    # Since we're using the synthetic DataFrame, I is directly the peak
    return df['I'].iloc[0]


def total_infections(df: pd.DataFrame) -> float:
    """Calculate total infections KPI from simulation output."""
    # In our synthetic DataFrame, R is the total infections
    return df['R'].iloc[0]


def epidemic_duration(df: pd.DataFrame) -> float:
    """Calculate epidemic duration KPI from simulation output."""
    # In our synthetic DataFrame, duration is directly available
    return df['duration'].iloc[0]


def calculate_r0(df: pd.DataFrame) -> float:
    """Calculate basic reproduction number."""
    # In our synthetic DataFrame, r0 is directly available
    return df['r0'].iloc[0]
