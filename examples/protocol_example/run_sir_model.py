#!/usr/bin/env python
"""
Example script demonstrating the use of the new PSUU protocol interface.

This script shows how to use the config-based integration and
standardized protocol interface with a simple SIR model.
"""

import os
import sys
import argparse
from typing import Dict, Any

# Add project root to path if needed
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from psuu import (
    PsuuExperiment, 
    PsuuConfig, 
    SimulationResults,
    ParameterValidator,
    ConfigurationError
)

# Import our SIR model
from examples.protocol_example.sir_model import SIRModel


def direct_model_usage():
    """Example of using the SIR model directly with the protocol interface."""
    print("\n=== Direct Model Usage ===")
    
    # Initialize model
    model = SIRModel(timesteps=100, samples=3)
    
    # Run with specific parameters
    params = {
        "beta": 0.3,
        "gamma": 0.05,
        "population": 1000,
        "initial_infected": 5
    }
    
    # Run simulation and get results
    results = model.run(params)
    
    # Access time series data
    print(f"Time series data shape: {results.time_series_data.shape}")
    
    # Access KPIs
    print("\nKPI Results:")
    for kpi_name, kpi_value in results.kpis.items():
        print(f"  {kpi_name}: {kpi_value:.2f}")
    
    # Save results
    output_dir = "results/protocol_example/direct"
    os.makedirs(output_dir, exist_ok=True)
    saved_files = results.save(f"{output_dir}/sir_simulation", formats=["csv", "json"])
    
    print("\nResults saved to:")
    for fmt, path in saved_files.items():
        print(f"  {fmt}: {path}")


def config_based_usage():
    """Example of using the config-based integration."""
    print("\n=== Config-Based Usage ===")
    
    config_path = os.path.join(os.path.dirname(__file__), "sir_config.yaml")
    
    # Load configuration
    try:
        config = PsuuConfig(config_path)
    except ConfigurationError as e:
        print(f"Error loading configuration: {e}")
        return
    
    # Validate configuration
    is_valid, errors = config.validate()
    if not is_valid:
        print("Configuration errors:")
        for error in errors:
            print(f"  {error}")
        return
    
    # Load model
    try:
        model = config.load_model()
        print(f"Loaded model: {model.__class__.__name__}")
    except Exception as e:
        print(f"Error loading model: {e}")
        return
    
    # Get parameter space
    param_space = model.get_parameter_space()
    print("\nParameter space:")
    for param, spec in param_space.items():
        if isinstance(spec, dict) and 'description' in spec:
            print(f"  {param}: {spec['description']}")
        else:
            print(f"  {param}")
    
    # Get KPI definitions
    kpi_defs = model.get_kpi_definitions()
    print("\nKPI definitions:")
    for kpi, spec in kpi_defs.items():
        if isinstance(spec, dict) and 'description' in spec:
            print(f"  {kpi}: {spec['description']}")
        else:
            print(f"  {kpi}")
    
    # Run model with parameters from config
    opt_config = config.get_optimization_config()
    params = {
        "beta": 0.3,
        "gamma": 0.05,
        "population": 1000,
        "initial_infected": 5
    }
    
    results = model.run(params)
    
    # Print results
    print("\nSingle run results:")
    for kpi_name, kpi_value in results.kpis.items():
        print(f"  {kpi_name}: {kpi_value:.2f}")
    
    output_dir = config.get_output_config().get('directory', 'results/protocol_example/config')
    os.makedirs(output_dir, exist_ok=True)
    saved_files = results.save(f"{output_dir}/sir_config_run", formats=["csv", "json"])
    
    print("\nResults saved to:")
    for fmt, path in saved_files.items():
        print(f"  {fmt}: {path}")


def optimization_example():
    """Example of using optimization with the protocol interface."""
    print("\n=== Optimization Example ===")
    
    # Initialize model
    model = SIRModel(timesteps=100, samples=1)
    
    # Create experiment
    experiment = PsuuExperiment()
    
    # Create a model adapter function
    def model_adapter(params):
        """Adapter function to run the model and return a DataFrame."""
        results = model.run(params)
        return results.to_dataframe()
    
    # Set up the experiment to use the adapter function
    experiment.simulation_connector.run_simulation = model_adapter
    
    # Add KPIs from model
    kpi_defs = model.get_kpi_definitions()
    for kpi_name, kpi_def in kpi_defs.items():
        if isinstance(kpi_def, dict) and 'function' in kpi_def:
            experiment.add_kpi(kpi_name, function=kpi_def['function'])
        else:
            experiment.add_kpi(kpi_name, function=kpi_def)
    
    # Set parameter space from model
    experiment.set_parameter_space(model.get_parameter_space())
    
    # Configure optimizer
    experiment.set_optimizer(
        method="random",  # Using random for speed, could use bayesian
        objective_name="peak_infections",
        maximize=False,
        num_iterations=5  # Small number for demonstration
    )
    
    # Run optimization
    print("\nRunning optimization...")
    results = experiment.run(
        max_iterations=5,
        verbose=True,
        save_results="results/protocol_example/optimization/sir_opt"
    )
    
    # Print optimization results
    print("\nOptimization Results:")
    print(f"Best parameters: {results.best_parameters}")
    print("\nBest KPIs:")
    for kpi_name, kpi_value in results.best_kpis.items():
        print(f"  {kpi_name}: {kpi_value:.2f}")


def main():
    """Main function to run the examples."""
    parser = argparse.ArgumentParser(description="Run SIR model examples")
    parser.add_argument('--direct', action='store_true', help='Run direct model usage example')
    parser.add_argument('--config', action='store_true', help='Run config-based usage example')
    parser.add_argument('--optimize', action='store_true', help='Run optimization example')
    parser.add_argument('--all', action='store_true', help='Run all examples')
    
    args = parser.parse_args()
    
    # Default to running all examples if no arguments provided
    if not (args.direct or args.config or args.optimize or args.all):
        args.all = True
    
    if args.direct or args.all:
        direct_model_usage()
    
    if args.config or args.all:
        config_based_usage()
    
    if args.optimize or args.all:
        optimization_example()


if __name__ == "__main__":
    main()
