#!/usr/bin/env python
"""
Example of using PSUU to optimize parameters for the cadcad-sandbox SIR model.

This example demonstrates how to use PSUU to find optimal parameter values
for minimizing peak infections in an SIR epidemic model.

This version uses a custom SimulationConnector to work with the cadcad-sandbox output format.
"""

import os
import sys
import tempfile
import subprocess
import json
import pandas as pd
import numpy as np
from typing import Dict, Any
import time

from psuu import PsuuExperiment
from psuu.simulation_connector import SimulationConnector
from psuu.experiment import ExperimentResults


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
        
        # Create temporary directory for output
        with tempfile.TemporaryDirectory() as temp_dir:
            # Set PYTHONPATH to include cadcad-sandbox directory
            env = os.environ.copy()
            if "PYTHONPATH" in env:
                env["PYTHONPATH"] = f"{self.working_dir}:{env['PYTHONPATH']}"
            else:
                env["PYTHONPATH"] = self.working_dir
            
            # Run simulation
            try:
                result = subprocess.run(
                    cmd,
                    shell=True,
                    check=True,
                    cwd=self.working_dir,
                    env=env,
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
                # Create a simple DataFrame with the necessary columns
                peak = kpi_data['peak_infections']['mean']
                total = kpi_data['total_infections']['mean']
                duration = kpi_data['epidemic_duration']['mean']
                r0 = kpi_data['r0']['mean']
                
                # Create a synthetic DataFrame with just the KPI values
                # This is a workaround since we don't have direct access to the simulation data
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


# Utility function to convert NumPy types to Python types
def convert_numpy_types(obj):
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, dict):
        return {k: convert_numpy_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    else:
        return obj


def main():
    """Run optimization experiments for the SIR model."""
    print("PSUU - Parameter Optimization for cadcad-sandbox SIR Model")
    print("=========================================================")
    
    # Create output directory
    os.makedirs("results", exist_ok=True)
    
    # Create experiment with custom simulation connector
    experiment = PsuuExperiment(
        simulation_command="python -m model",
        param_format="--{name} {value}",
        output_format="json",  # Not really used but needed for initialization
        working_dir="/home/e4roh/projects/cadcad-sandbox"
    )
    
    # Replace the default simulation connector with our custom one
    experiment.simulation_connector = CadcadSimulationConnector(
        command="python -m model",
        param_format="--{name} {value}",
        working_dir="/home/e4roh/projects/cadcad-sandbox"
    )
    
    # Add KPIs
    experiment.add_kpi("peak", function=peak_infections)
    experiment.add_kpi("total", function=total_infections)
    experiment.add_kpi("duration", function=epidemic_duration)
    experiment.add_kpi("r0", function=calculate_r0)
    
    # Set parameter space
    experiment.set_parameter_space({
        "beta": (0.1, 0.5),         # Transmission rate range
        "gamma": (0.01, 0.1),       # Recovery rate range
        "population": [1000, 5000]  # Population size options
    })
    
    # Configure optimizer
    experiment.set_optimizer(
        method="random",
        objective_name="peak",
        maximize=False,              # We want to minimize peak infections
        num_iterations=5,            # Small number for quick demonstration
        seed=42
    )
    
    print("\nRunning optimization to minimize peak infections...")
    
    # Run experiment
    results = experiment.run(verbose=True, save_results=None)  # Disable automatic saving
    
    # Manually save the results with proper type conversion
    results_file = "results/sir_optimization.json"
    
    # Convert the results data to Python native types
    results_data = {
        "iterations": results.iterations,
        "elapsed_time": results.elapsed_time,
        "best_parameters": convert_numpy_types(results.best_parameters),
        "best_kpis": convert_numpy_types(results.best_kpis),
        "summary": convert_numpy_types(results.summary),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Save to JSON
    with open(results_file, "w") as f:
        json.dump(results_data, f, indent=2)
    
    # Print best results
    print("\nBest parameters to minimize peak infections:")
    print(f"Beta: {convert_numpy_types(results.best_parameters['beta']):.4f}")
    print(f"Gamma: {convert_numpy_types(results.best_parameters['gamma']):.4f}")
    print(f"Population: {convert_numpy_types(results.best_parameters['population'])}")
    print(f"Peak infections: {convert_numpy_types(results.best_kpis['peak']):.2f}")
    print(f"Total infections: {convert_numpy_types(results.best_kpis['total']):.2f}")
    print(f"Epidemic duration: {convert_numpy_types(results.best_kpis['duration']):.2f}")
    print(f"Basic reproduction number (R0): {convert_numpy_types(results.best_kpis['r0']):.2f}")
    
    print(f"\nOptimization complete! Results saved to '{results_file}'")
    
    # Also try bayesian optimization if available
    try:
        # Try a more focused optimization with Bayesian method
        print("\nRunning Bayesian optimization for more precise results...")
        
        # Set a narrower parameter space based on best results
        beta_best = convert_numpy_types(results.best_parameters['beta'])
        gamma_best = convert_numpy_types(results.best_parameters['gamma'])
        pop_best = convert_numpy_types(results.best_parameters['population'])
        
        experiment.set_parameter_space({
            "beta": (max(0.05, beta_best - 0.05), min(0.5, beta_best + 0.05)),
            "gamma": (max(0.01, gamma_best - 0.02), min(0.15, gamma_best + 0.02)),
            "population": [pop_best]
        })
        
        # Configure Bayesian optimizer
        experiment.set_optimizer(
            method="bayesian",
            objective_name="peak",
            maximize=False,
            num_iterations=5,
            n_initial_points=2,
            seed=42
        )
        
        # Run experiment
        bayesian_results = experiment.run(verbose=True, save_results=None)
        
        # Save results
        bayesian_file = "results/sir_optimization_bayesian.json"
        bayesian_data = {
            "iterations": bayesian_results.iterations,
            "elapsed_time": bayesian_results.elapsed_time,
            "best_parameters": convert_numpy_types(bayesian_results.best_parameters),
            "best_kpis": convert_numpy_types(bayesian_results.best_kpis),
            "summary": convert_numpy_types(bayesian_results.summary),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        with open(bayesian_file, "w") as f:
            json.dump(bayesian_data, f, indent=2)
        
        # Print refined results
        print("\nRefined parameters from Bayesian optimization:")
        print(f"Beta: {convert_numpy_types(bayesian_results.best_parameters['beta']):.4f}")
        print(f"Gamma: {convert_numpy_types(bayesian_results.best_parameters['gamma']):.4f}")
        print(f"Population: {convert_numpy_types(bayesian_results.best_parameters['population'])}")
        print(f"Peak infections: {convert_numpy_types(bayesian_results.best_kpis['peak']):.2f}")
        print(f"Total infections: {convert_numpy_types(bayesian_results.best_kpis['total']):.2f}")
        print(f"Epidemic duration: {convert_numpy_types(bayesian_results.best_kpis['duration']):.2f}")
        print(f"Basic reproduction number (R0): {convert_numpy_types(bayesian_results.best_kpis['r0']):.2f}")
        
        print(f"\nBayesian optimization complete! Results saved to '{bayesian_file}'")
        
    except ImportError as e:
        print("\nBayesian optimization not available:", e)
        print("To use Bayesian optimization, install the 'scikit-optimize' package:")
        print("  uv pip install scikit-optimize")


if __name__ == "__main__":
    main()
