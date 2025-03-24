#!/usr/bin/env python
"""
Example of using PSUU to optimize parameters for an SIR epidemic model.

This example assumes you have the cadcad-sandbox package installed
(https://github.com/yourusername/cadcad-sandbox).

To run this example:
1. Install the cadcad-sandbox package: `pip install git+https://github.com/yourusername/cadcad-sandbox.git`
2. Install the psuu package: `pip install -e .`
3. Run this script: `python examples/sir_optimization.py`
"""

import os
from psuu import PsuuExperiment
import pandas as pd


def peak_infections(df):
    """Calculate peak infections KPI."""
    return df["I"].max()


def total_infections(df):
    """Calculate total infections KPI."""
    # Sum the difference between initial S and final S
    initial_s = df.iloc[0]["S"]
    return initial_s - df.iloc[-1]["S"]


def epidemic_duration(df, threshold=1):
    """Calculate epidemic duration KPI."""
    # Find time from first to last infection above threshold
    above_threshold = df[df["I"] > threshold]
    if len(above_threshold) == 0:
        return 0
    return above_threshold.iloc[-1]["time"] - above_threshold.iloc[0]["time"]


def main():
    # Create output directory
    os.makedirs("results", exist_ok=True)
    
    # Create experiment
    experiment = PsuuExperiment(
        simulation_command="cadcad-sir",
        param_format="--{name} {value}",
        output_format="csv",
        working_dir=None,
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
        num_iterations=20,
        seed=42
    )
    
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
    
    # Try a different objective (minimize epidemic duration)
    print("\nRunning optimization for minimum epidemic duration...")
    
    experiment.set_optimizer(
        method="bayesian",
        objective_name="duration",
        maximize=False,
        num_iterations=20,
        n_initial_points=5,
        seed=42
    )
    
    # Run experiment
    results_duration = experiment.run(
        verbose=True,
        save_results="results/sir_optimization_duration"
    )
    
    # Print best results
    print("\nBest parameters to minimize epidemic duration:")
    print(f"Beta: {results_duration.best_parameters['beta']:.4f}")
    print(f"Gamma: {results_duration.best_parameters['gamma']:.4f}")
    print(f"Population: {results_duration.best_parameters['population']}")
    print(f"Peak infections: {results_duration.best_kpis['peak']:.2f}")
    print(f"Total infections: {results_duration.best_kpis['total']:.2f}")
    print(f"Epidemic duration: {results_duration.best_kpis['duration']:.2f}")


if __name__ == "__main__":
    main()
