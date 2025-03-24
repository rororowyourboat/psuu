#!/usr/bin/env python
"""
Example of using PSUU to optimize parameters for the cadcad-sandbox SIR model.

This example demonstrates how to use PSUU to find optimal parameter values
for minimizing peak infections in an SIR epidemic model.
"""

import os
import sys
import pandas as pd
import numpy as np
from psuu import PsuuExperiment


def peak_infections(df: pd.DataFrame) -> float:
    """Calculate peak infections KPI from simulation output."""
    return df['I'].max()


def total_infections(df: pd.DataFrame) -> float:
    """Calculate total infections KPI from simulation output."""
    # Sum the difference between initial S and final S
    initial_s = df.loc[df['timestep'] == 0, 'S'].iloc[0]
    final_s = df.loc[df['timestep'] == df['timestep'].max(), 'S'].iloc[0]
    return initial_s - final_s


def epidemic_duration(df: pd.DataFrame, threshold: float = 1.0) -> float:
    """Calculate epidemic duration KPI from simulation output."""
    # Find time from first to last infection above threshold
    above_threshold = df[df['I'] > threshold]
    if len(above_threshold) <= 1:
        return 0.0
    else:
        first_time = above_threshold['timestep'].min()
        last_time = above_threshold['timestep'].max()
        return last_time - first_time


def main():
    """Run optimization experiments for the SIR model."""
    print("PSUU - Parameter Optimization for cadcad-sandbox SIR Model")
    print("=========================================================")
    
    # Create output directory
    os.makedirs("results", exist_ok=True)
    
    # Create experiment
    experiment = PsuuExperiment(
        simulation_command="python -m model",
        param_format="--{name} {value}",
        output_format="csv",
        working_dir="/home/e4roh/projects/cadcad-sandbox"
    )
    
    # Add KPIs
    experiment.add_kpi("peak", function=peak_infections)
    experiment.add_kpi("total", function=total_infections)
    experiment.add_kpi("duration", function=epidemic_duration)
    
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
        num_iterations=10,           # Small number for quick demonstration
        seed=42
    )
    
    print("\nRunning optimization to minimize peak infections...")
    
    # Run experiment
    results = experiment.run(
        verbose=True,
        save_results="results/sir_optimization"
    )
    
    # Print best results
    print("\nBest parameters to minimize peak infections:")
    print(f"Beta: {results.best_parameters['beta']:.4f}")
    print(f"Gamma: {results.best_parameters['gamma']:.4f}")
    print(f"Population: {results.best_parameters['population']}")
    print(f"Peak infections: {results.best_kpis['peak']:.2f}")
    print(f"Total infections: {results.best_kpis['total']:.2f}")
    print(f"Epidemic duration: {results.best_kpis['duration']:.2f}")
    
    # Try grid search with a narrower parameter space
    print("\nRunning grid search in a narrow parameter space...")
    
    # Narrow parameter space around the best found values
    best_beta = results.best_parameters['beta']
    best_gamma = results.best_parameters['gamma']
    
    # Create a narrow window around best values
    beta_min = max(0.1, best_beta - 0.05)
    beta_max = min(0.5, best_beta + 0.05)
    gamma_min = max(0.01, best_gamma - 0.01)
    gamma_max = min(0.1, best_gamma + 0.01)
    
    experiment.set_parameter_space({
        "beta": (beta_min, beta_max),
        "gamma": (gamma_min, gamma_max),
        "population": [results.best_parameters['population']]  # Use the best population
    })
    
    experiment.set_optimizer(
        method="grid",
        objective_name="peak",
        maximize=False,
        num_points=5  # 5x5 grid for beta and gamma
    )
    
    # Run grid search
    results_grid = experiment.run(
        verbose=True,
        save_results="results/sir_optimization_grid"
    )
    
    # Print refined results
    print("\nRefined parameters from grid search:")
    print(f"Beta: {results_grid.best_parameters['beta']:.4f}")
    print(f"Gamma: {results_grid.best_parameters['gamma']:.4f}")
    print(f"Population: {results_grid.best_parameters['population']}")
    print(f"Peak infections: {results_grid.best_kpis['peak']:.2f}")
    print(f"Total infections: {results_grid.best_kpis['total']:.2f}")
    print(f"Epidemic duration: {results_grid.best_kpis['duration']:.2f}")
    
    # Calculate R0 (basic reproduction number)
    r0 = results_grid.best_parameters['beta'] / results_grid.best_parameters['gamma']
    print(f"Basic reproduction number (R0): {r0:.2f}")
    
    print("\nOptimization complete! Results saved to 'results/' directory.")


if __name__ == "__main__":
    main()
