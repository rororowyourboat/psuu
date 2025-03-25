"""
Command-line interface for the model.

This module provides a CLI entry point for running the model, making it
compatible with PSUU's CLI integration approach.
"""

import json
import os
import pandas as pd
import sys
from typing import Dict, Any
from datetime import datetime

# Try to use click if available, otherwise use argparse
try:
    import click
    
    @click.command()
    @click.option('--beta', type=float, help='Infection rate parameter')
    @click.option('--gamma', type=float, help='Recovery rate parameter')
    @click.option('--population', type=int, help='Initial population size')
    @click.option('--initial_infected', type=int, default=10, help='Initial infected population')
    @click.option('--timesteps', type=int, default=100, help='Number of simulation timesteps')
    @click.option('--monte_carlo_runs', type=int, default=1, help='Number of Monte Carlo runs')
    @click.option('--output', type=str, help='Base name for output files')
    @click.option('--format', type=click.Choice(['json', 'csv']), default='json', help='Output format')
    @click.option('--output_dir', type=str, default='data/simulations', help='Directory for output files')
    def main(beta, gamma, population, initial_infected, timesteps, monte_carlo_runs, output, format, output_dir):
        """Run the SIR epidemic model."""
        # Extract parameters (filtering out None values)
        params = {}
        for param, value in [('beta', beta), ('gamma', gamma), ('population', population), 
                             ('initial_infected', initial_infected)]:
            if value is not None:
                params[param] = value
        
        # Extract simulation settings
        sim_settings = {}
        for setting, value in [('timesteps', timesteps), ('monte_carlo_runs', monte_carlo_runs)]:
            if value is not None:
                sim_settings[setting] = value
        
        # Import here to avoid circular imports
        from .model import SIRModel
        
        # Create model instance
        model = SIRModel()
        
        # Run simulation
        click.echo("Running simulation...")
        results = model.run(params, **sim_settings)
        
        # Prepare output
        if output:
            os.makedirs(output_dir, exist_ok=True)
            
            # Generate output filename
            timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
            output_base = os.path.join(output_dir, f"{output}-{timestamp}")
            
            # Save results based on format
            if format == 'json':
                # Convert to dictionary and serialize to JSON
                results_dict = {
                    "time_series": results.time_series_data.to_dict(orient='records') if not results.time_series_data.empty else [],
                    "kpis": results.kpis,
                    "metadata": results.metadata,
                    "parameters": results.parameters
                }
                
                with open(f"{output_base}.json", "w") as f:
                    json.dump(results_dict, f, indent=2)
                
                # Also save time series data to CSV
                if not results.time_series_data.empty:
                    results.time_series_data.to_csv(f"{output_base}_timeseries.csv", index=False)
                    click.echo(f"Results saved to {output_base}.json and {output_base}_timeseries.csv")
                else:
                    click.echo(f"Results saved to {output_base}.json (no time series data)")
            else:
                # Save time series to CSV
                if not results.time_series_data.empty:
                    results.time_series_data.to_csv(f"{output_base}.csv", index=False)
                    click.echo(f"Results saved to {output_base}.csv")
                else:
                    click.echo("No time series data to save")
        else:
            # If no output file specified, print to stdout
            click.echo("\nSimulation Results:")
            for kpi_name, kpi_value in results.kpis.items():
                click.echo(f"{kpi_name}: {kpi_value}")

except ImportError:
    # Fallback to argparse if click is not available
    import argparse
    
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
        
        # Import here to avoid circular imports
        from .model import SIRModel
        
        # Create model instance
        model = SIRModel()
        
        # Run simulation
        print("Running simulation...")
        results = model.run(params, **sim_settings)
        
        # Prepare output
        output_format = args.get("format", "json")
        output_name = args.get("output")
        output_dir = args.get("output_dir", "data/simulations")
        
        # Create output directory if it doesn't exist
        if output_name:
            os.makedirs(output_dir, exist_ok=True)
            
            # Generate output filename
            timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
            output_base = os.path.join(output_dir, f"{output_name}-{timestamp}")
            
            # Save results based on format
            if output_format == "json":
                # Convert to dictionary and serialize to JSON
                results_dict = {
                    "time_series": results.time_series_data.to_dict(orient='records') if not results.time_series_data.empty else [],
                    "kpis": results.kpis,
                    "metadata": results.metadata,
                    "parameters": results.parameters
                }
                
                with open(f"{output_base}.json", "w") as f:
                    json.dump(results_dict, f, indent=2)
                
                # Also save time series data to CSV
                if not results.time_series_data.empty:
                    results.time_series_data.to_csv(f"{output_base}_timeseries.csv", index=False)
                    print(f"Results saved to {output_base}.json and {output_base}_timeseries.csv")
                else:
                    print(f"Results saved to {output_base}.json (no time series data)")
            else:
                # Save time series to CSV
                if not results.time_series_data.empty:
                    results.time_series_data.to_csv(f"{output_base}.csv", index=False)
                    print(f"Results saved to {output_base}.csv")
                else:
                    print("No time series data to save")
        else:
            # If no output file specified, print to stdout
            print("\nSimulation Results:")
            for kpi_name, kpi_value in results.kpis.items():
                print(f"{kpi_name}: {kpi_value}")


if __name__ == "__main__":
    main()
