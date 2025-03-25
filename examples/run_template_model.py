#!/usr/bin/env python
"""
Example script that demonstrates using the template model with PSUU.

This script shows how to use both Protocol and CLI integration approaches
with the template SIR model.
"""

import os
import sys
import argparse
from typing import Dict, Any

# Add parent directory to sys.path to allow importing PSUU
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from psuu import PsuuExperiment
from psuu.config import configure_experiment_from_yaml
from template.model import SIRModel


def protocol_integration(args):
    """
    Run optimization using Protocol integration.
    
    Args:
        args: Command-line arguments
    """
    print("Running optimization with Protocol integration...")
    
    # Create model instance
    model = SIRModel()
    
    # Create experiment with model protocol integration
    experiment = PsuuExperiment(model=model)
    
    # Configure optimizer
    experiment.set_optimizer(
        method=args.method,
        objective_name="peak_infected",
        maximize=False,
        num_iterations=args.iterations
    )
    
    # Run optimization
    results = experiment.run(verbose=True, save_results=args.output)
    
    # Print results
    print("\nOptimization Results (Protocol):")
    print(f"Best parameters: {results.best_parameters}")
    print(f"Best KPIs: {results.best_kpis}")


def cli_integration(args):
    """
    Run optimization using CLI integration.
    
    Args:
        args: Command-line arguments
    """
    print("Running optimization with CLI integration...")
    
    # Define experiment with CLI integration
    experiment = PsuuExperiment(
        simulation_command="python -m template",
        param_format="--{name} {value}",
        output_format="json"
    )
    
    # Define KPIs
    experiment.add_kpi("peak_infected", column="peak_infected")
    experiment.add_kpi("total_infected", column="total_infected")
    experiment.add_kpi("epidemic_duration", column="epidemic_duration")
    experiment.add_kpi("r0", column="r0")
    
    # Set parameter space
    experiment.set_parameter_space({
        "beta": (0.1, 0.5),
        "gamma": (0.01, 0.1)
    })
    
    # Configure optimization
    experiment.set_optimizer(
        method=args.method,
        objective_name="peak_infected",
        maximize=False,
        num_iterations=args.iterations
    )
    
    # Run optimization
    results = experiment.run(verbose=True, save_results=args.output)
    
    # Print results
    print("\nOptimization Results (CLI):")
    print(f"Best parameters: {results.best_parameters}")
    print(f"Best KPIs: {results.best_kpis}")


def yaml_integration(args):
    """
    Run optimization using YAML configuration.
    
    Args:
        args: Command-line arguments
    """
    print("Running optimization with YAML configuration...")
    
    # Path to YAML configuration
    config_path = os.path.join(os.path.dirname(__file__), "..", "template", "sir_config.yaml")
    
    # Load configuration and create experiment
    experiment = configure_experiment_from_yaml(config_path)
    
    # Override optimizer settings if specified
    if args.method or args.iterations:
        experiment.set_optimizer(
            method=args.method or "bayesian",
            objective_name="peak_infected",
            maximize=False,
            num_iterations=args.iterations or 30
        )
    
    # Run optimization
    results = experiment.run(verbose=True, save_results=args.output)
    
    # Print results
    print("\nOptimization Results (YAML):")
    print(f"Best parameters: {results.best_parameters}")
    print(f"Best KPIs: {results.best_kpis}")


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Run template model optimization")
    
    # Integration mode
    parser.add_argument("--mode", choices=["protocol", "cli", "yaml"], default="protocol",
                       help="Integration mode (default: protocol)")
    
    # Optimization settings
    parser.add_argument("--method", choices=["random", "grid", "bayesian"], default="random",
                       help="Optimization method (default: random)")
    parser.add_argument("--iterations", type=int, default=10,
                       help="Number of iterations (default: 10)")
    
    # Output settings
    parser.add_argument("--output", type=str, default=None,
                       help="Path to save results (default: None)")
    
    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_args()
    
    # Create output directory if specified
    if args.output:
        os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    
    # Run optimization based on specified mode
    if args.mode == "protocol":
        protocol_integration(args)
    elif args.mode == "cli":
        cli_integration(args)
    elif args.mode == "yaml":
        yaml_integration(args)
    else:
        print(f"Unknown mode: {args.mode}")
        sys.exit(1)


if __name__ == "__main__":
    main()
