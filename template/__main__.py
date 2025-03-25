"""
Command-line interface for the model.

This module provides a CLI entry point for running the model, making it
compatible with PSUU's CLI integration approach.
"""

import argparse
import json
import os
import pandas as pd
import sys
from typing import Dict, Any

# Import the model class
from .model import SIRModel
from .params import ModelParameters, default_params
from psuu.results import SimulationResults


def parse_args() -> Dict[str, Any]:
    """
    Parse command-line arguments.
    
    Returns:
        Dictionary of parsed arguments
    """
    parser = argparse.ArgumentParser(description="Run the SIR epidemic model")
    
    # Define model parameters
    parser.add_argument("--beta", type=float, help="Infection rate parameter")
    parser.add_argument("--gamma", type=float, help="Recovery rate parameter")
    parser.add_argument("--population", type=int, help="Initial population size")
    parser.add_argument("--initial_infected", type=int, default=10, help="Initial infected population")
    
    # Simulation settings
    parser.add_argument("--timesteps", type=int, help="Number of simulation timesteps")
    parser.add_argument("--monte_carlo_runs", type=int, help="Number of Monte Carlo runs")
    
    # Output options
    parser.add_argument("--output", type=str, help="Base name for output files")
    parser.add_argument("--format", type=str, choices=["json", "csv"], default="json",
                        help="Output format (default: json)")
    parser.add_argument("--output_dir", type=str, default="data/simulations",
                        help="Directory for output files")
    
    args = parser.parse_args()
    return vars(args)


def main() -> None:
    """Main entry point for CLI."""
    # Parse arguments
    args = parse_args()
    
    # Extract parameters (filtering out None values)
    params = {}
    for param in ['beta', 'gamma', 'population', 'initial_infected']:
        if args.get(param) is not None:
            params[param] = args[param]
    
    # Extract simulation settings
    sim_settings = {}
    for setting in ['timesteps', 'monte_carlo_runs']:
        if args.get(setting) is not None:
            sim_settings[setting] = args[setting]
    
    # Create model instance
    model = SIRModel()
    
    # Run simulation
    results = model.run(params, **sim_settings)
    
    # Prepare output
    output_format = args.get("format", "json")
    output_name = args.get("output")
    output_dir = args.get("output_dir", "data/simulations")
    
    # Create output directory if it doesn't exist
    if output_name:
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate output filename
        output_base = os.path.join(output_dir, output_name)
        
        # Save results based on format
        if output_format == "json":
            # Save as JSON
            results_dict = results.to_dict()
            with open(f"{output_base}.json", "w") as f:
                json.dump(results_dict, f, indent=2)
            
            # Also save time series data to CSV
            results.time_series_data.to_csv(f"{output_base}_timeseries.csv", index=False)
            
            print(f"Results saved to {output_base}.json and {output_base}_timeseries.csv")
        else:
            # Save time series to CSV
            results.time_series_data.to_csv(f"{output_base}.csv", index=False)
            print(f"Results saved to {output_base}.csv")
    else:
        # If no output file specified, print to stdout in JSON format
        json_output = results.to_dict()
        print(json.dumps(json_output))


if __name__ == "__main__":
    main()
