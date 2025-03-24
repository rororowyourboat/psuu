"""
Command Line Interface Module

This module provides a command-line interface for the PSUU package.
"""

import os
import sys
import time
import json
import yaml
import click
from typing import Dict, Any, List, Optional, Tuple, Union

from .experiment import PsuuExperiment
from .optimizers import AVAILABLE_OPTIMIZERS
from .version import __version__


CONFIG_FILENAME = "psuu_config.yaml"


@click.group()
@click.version_option(version=__version__)
def cli():
    """
    PSUU - Parameter Selection Under Uncertainty
    
    A framework for simulation parameter optimization.
    """
    pass


@cli.command()
@click.option(
    "--output-dir", "-o",
    default=".",
    help="Directory to store configuration file"
)
def init(output_dir: str):
    """
    Initialize a new PSUU configuration file.
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Create default configuration
    config = {
        "simulation": {
            "command": "python -m model",
            "param_format": "--{name} {value}",
            "output_format": "csv",
            "output_file": "results.csv",
            "working_dir": None,
        },
        "parameters": {},
        "kpis": {},
        "optimizer": {
            "method": "random",
            "objective": None,
            "maximize": True,
            "iterations": 20,
        }
    }
    
    # Write configuration file
    config_path = os.path.join(output_dir, CONFIG_FILENAME)
    with open(config_path, "w") as f:
        yaml.dump(config, f, default_flow_style=False)
    
    click.echo(f"Created configuration file: {config_path}")
    click.echo("You can now add parameters and KPIs.")


@cli.command("add-param")
@click.option("--name", "-n", required=True, help="Parameter name")
@click.option("--range", "-r", nargs=2, type=float, help="Parameter range (min max)")
@click.option("--values", "-v", multiple=True, help="Discrete parameter values")
@click.option("--config", "-c", default=CONFIG_FILENAME, help="Configuration file")
def add_param(name: str, range: Optional[Tuple[float, float]], values: List[str], config: str):
    """
    Add a parameter to the configuration.
    """
    # Load configuration
    try:
        with open(config, "r") as f:
            cfg = yaml.safe_load(f)
    except FileNotFoundError:
        click.echo(f"Configuration file not found: {config}")
        click.echo("Run 'psuu init' first to create a configuration file.")
        sys.exit(1)
    
    # Add parameter
    if range:
        cfg["parameters"][name] = list(range)
    elif values:
        cfg["parameters"][name] = list(values)
    else:
        click.echo("Must specify either range or values for the parameter.")
        sys.exit(1)
    
    # Write updated configuration
    with open(config, "w") as f:
        yaml.dump(cfg, f, default_flow_style=False)
    
    click.echo(f"Added parameter '{name}' to configuration.")


@cli.command("add-kpi")
@click.option("--name", "-n", required=True, help="KPI name")
@click.option("--column", "-c", help="DataFrame column for simple KPI")
@click.option("--operation", "-o", help="Operation for simple KPI")
@click.option("--filter", "-f", help="Optional filter condition")
@click.option("--custom", is_flag=True, help="Flag for custom KPI function")
@click.option("--module", "-m", help="Python module with custom KPI function")
@click.option("--function", "-func", help="Function name in the module")
@click.option("--config", default=CONFIG_FILENAME, help="Configuration file")
def add_kpi(
    name: str,
    column: Optional[str],
    operation: Optional[str],
    filter: Optional[str],
    custom: bool,
    module: Optional[str],
    function: Optional[str],
    config: str,
):
    """
    Add a KPI to the configuration.
    """
    # Load configuration
    try:
        with open(config, "r") as f:
            cfg = yaml.safe_load(f)
    except FileNotFoundError:
        click.echo(f"Configuration file not found: {config}")
        click.echo("Run 'psuu init' first to create a configuration file.")
        sys.exit(1)
    
    # Add KPI
    if custom:
        if not module or not function:
            click.echo("Custom KPI requires both module and function.")
            sys.exit(1)
        
        cfg["kpis"][name] = {
            "type": "custom",
            "module": module,
            "function": function,
        }
    else:
        if not column or not operation:
            click.echo("Simple KPI requires both column and operation.")
            sys.exit(1)
        
        cfg["kpis"][name] = {
            "column": column,
            "operation": operation,
        }
        
        if filter:
            cfg["kpis"][name]["filter"] = filter
    
    # Write updated configuration
    with open(config, "w") as f:
        yaml.dump(cfg, f, default_flow_style=False)
    
    click.echo(f"Added KPI '{name}' to configuration.")


@cli.command("set-optimizer")
@click.option(
    "--method", "-m",
    type=click.Choice(list(AVAILABLE_OPTIMIZERS.keys())),
    default="random",
    help="Optimization method"
)
@click.option("--objective", "-o", help="KPI to optimize")
@click.option("--maximize/--minimize", default=True, help="Whether to maximize or minimize")
@click.option("--iterations", "-i", type=int, default=20, help="Number of iterations")
@click.option("--num-points", type=int, default=5, help="Points per dimension for grid search")
@click.option("--n-initial-points", type=int, default=10, help="Initial points for Bayesian")
@click.option("--seed", type=int, help="Random seed")
@click.option("--config", default=CONFIG_FILENAME, help="Configuration file")
def set_optimizer(
    method: str,
    objective: Optional[str],
    maximize: bool,
    iterations: int,
    num_points: int,
    n_initial_points: int,
    seed: Optional[int],
    config: str,
):
    """
    Configure the optimizer.
    """
    # Load configuration
    try:
        with open(config, "r") as f:
            cfg = yaml.safe_load(f)
    except FileNotFoundError:
        click.echo(f"Configuration file not found: {config}")
        click.echo("Run 'psuu init' first to create a configuration file.")
        sys.exit(1)
    
    # Update optimizer configuration
    cfg["optimizer"]["method"] = method
    cfg["optimizer"]["maximize"] = maximize
    
    if objective:
        cfg["optimizer"]["objective"] = objective
    
    # Method-specific settings
    if method == "grid":
        cfg["optimizer"]["num_points"] = num_points
    elif method == "random":
        cfg["optimizer"]["num_iterations"] = iterations
        if seed is not None:
            cfg["optimizer"]["seed"] = seed
    elif method == "bayesian":
        cfg["optimizer"]["num_iterations"] = iterations
        cfg["optimizer"]["n_initial_points"] = n_initial_points
        if seed is not None:
            cfg["optimizer"]["seed"] = seed
    
    # Write updated configuration
    with open(config, "w") as f:
        yaml.dump(cfg, f, default_flow_style=False)
    
    click.echo(f"Updated optimizer configuration.")


@cli.command()
@click.option("--config", "-c", default=CONFIG_FILENAME, help="Configuration file")
@click.option("--verbose/--quiet", default=True, help="Show progress information")
@click.option(
    "--output", "-o",
    default="psuu_results",
    help="Base filename for output files"
)
def run(config: str, verbose: bool, output: str):
    """
    Run a parameter optimization experiment.
    """
    # Load configuration
    try:
        with open(config, "r") as f:
            cfg = yaml.safe_load(f)
    except FileNotFoundError:
        click.echo(f"Configuration file not found: {config}")
        click.echo("Run 'psuu init' first to create a configuration file.")
        sys.exit(1)
    
    # Check configuration
    if not cfg["parameters"]:
        click.echo("No parameters defined. Use 'psuu add-param' to add parameters.")
        sys.exit(1)
    
    if not cfg["kpis"]:
        click.echo("No KPIs defined. Use 'psuu add-kpi' to add KPIs.")
        sys.exit(1)
    
    if not cfg["optimizer"]["objective"]:
        click.echo("No objective KPI set. Use 'psuu set-optimizer --objective KPI_NAME'.")
        sys.exit(1)
    
    # Create experiment
    experiment = PsuuExperiment(
        simulation_command=cfg["simulation"]["command"],
        param_format=cfg["simulation"]["param_format"],
        output_format=cfg["simulation"]["output_format"],
        output_file=cfg["simulation"]["output_file"],
        working_dir=cfg["simulation"]["working_dir"],
    )
    
    # Add KPIs
    for name, kpi_config in cfg["kpis"].items():
        if kpi_config.get("type") == "custom":
            # Import custom KPI function
            try:
                import importlib
                module = importlib.import_module(kpi_config["module"])
                function = getattr(module, kpi_config["function"])
                experiment.add_kpi(name=name, function=function)
            except (ImportError, AttributeError) as e:
                click.echo(f"Error loading custom KPI function: {e}")
                sys.exit(1)
        else:
            # Simple KPI
            experiment.add_kpi(
                name=name,
                column=kpi_config["column"],
                operation=kpi_config["operation"],
                filter_condition=kpi_config.get("filter")
            )
    
    # Set parameter space
    parameter_space = {}
    for name, values in cfg["parameters"].items():
        if len(values) == 2 and all(isinstance(v, (int, float)) for v in values):
            # Continuous parameter
            parameter_space[name] = (values[0], values[1])
        else:
            # Discrete parameter
            parameter_space[name] = values
    
    experiment.set_parameter_space(parameter_space)
    
    # Configure optimizer
    optimizer_args = {}
    if cfg["optimizer"]["method"] == "grid":
        if "num_points" in cfg["optimizer"]:
            optimizer_args["num_points"] = cfg["optimizer"]["num_points"]
    elif cfg["optimizer"]["method"] == "random":
        if "num_iterations" in cfg["optimizer"]:
            optimizer_args["num_iterations"] = cfg["optimizer"]["num_iterations"]
        if "seed" in cfg["optimizer"]:
            optimizer_args["seed"] = cfg["optimizer"]["seed"]
    elif cfg["optimizer"]["method"] == "bayesian":
        if "num_iterations" in cfg["optimizer"]:
            optimizer_args["num_iterations"] = cfg["optimizer"]["num_iterations"]
        if "n_initial_points" in cfg["optimizer"]:
            optimizer_args["n_initial_points"] = cfg["optimizer"]["n_initial_points"]
        if "seed" in cfg["optimizer"]:
            optimizer_args["seed"] = cfg["optimizer"]["seed"]
    
    experiment.set_optimizer(
        method=cfg["optimizer"]["method"],
        objective_name=cfg["optimizer"]["objective"],
        maximize=cfg["optimizer"]["maximize"],
        **optimizer_args
    )
    
    # Run experiment
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    output_path = f"{output}_{timestamp}"
    
    click.echo(f"Starting optimization experiment...")
    
    try:
        results = experiment.run(verbose=verbose, save_results=output_path)
        
        click.echo(f"\nOptimization completed successfully.")
        click.echo(f"Best parameters: {results.best_parameters}")
        click.echo(f"Best {cfg['optimizer']['objective']}: {results.best_kpis[cfg['optimizer']['objective']]}")
        click.echo(f"Results saved to: {output_path}.<csv|json|yaml>")
    
    except Exception as e:
        click.echo(f"Error running experiment: {e}")
        sys.exit(1)


def main():
    """Main entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
