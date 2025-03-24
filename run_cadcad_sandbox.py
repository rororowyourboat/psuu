#!/usr/bin/env python
"""
Example script to run cadcad-sandbox with PSUU.

This script demonstrates how to use PSUU to optimize parameters for cadcad-sandbox.
"""

import os
import sys
import json
import pandas as pd
import numpy as np
from typing import Any
from psuu import PsuuExperiment

from psuu.custom_connectors.cadcad_connector import CadcadSimulationConnector
from psuu.custom_connectors.cadcad_connector import peak_infections, total_infections, epidemic_duration, calculate_r0


# Custom JSON encoder to handle NumPy types
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)


def convert_numpy_types(obj: Any) -> Any:
    """Convert NumPy types to native Python types."""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {k: convert_numpy_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    else:
        return obj


def main():
    """Run optimization for cadcad-sandbox."""
    print("PSUU - Cadcad-sandbox Parameter Optimization")
    print("=" * 50)
    
    # Create output directory
    os.makedirs("results", exist_ok=True)
    
    # Create experiment
    experiment = PsuuExperiment(
        simulation_command="python -m model",
        param_format="--{name} {value}",
        output_format="json",
        working_dir="cadcad-sandbox"
    )
    
    # Replace default connector with custom connector
    experiment.simulation_connector = CadcadSimulationConnector(
        command="python -m model",
        param_format="--{name} {value}",
        working_dir="cadcad-sandbox"
    )
    
    # Add KPIs
    experiment.add_kpi("peak", function=peak_infections)
    experiment.add_kpi("total", function=total_infections)
    experiment.add_kpi("duration", function=epidemic_duration)
    experiment.add_kpi("r0", function=calculate_r0)

    # Set parameter space
    experiment.set_parameter_space({
        "beta": (0.1, 0.5),
        "gamma": (0.01, 0.1),
        "population": [1000, 5000],  # List of two integers for the range
    })

    # Configure optimizer
    experiment.set_optimizer(
        method="random",
        objective_name="peak",
        maximize=False,
        num_iterations=20
    )

    # Run optimization but don't save results automatically
    results = experiment.run(verbose=True, save_results=None)
    
    # Manually save results with proper type conversion
    results_file = "results/cadcad_sandbox_optimization.json"
    
    # Convert the results data to Python native types
    results_data = {
        "iterations": results.iterations,
        "elapsed_time": results.elapsed_time,
        "best_parameters": convert_numpy_types(results.best_parameters),
        "best_kpis": convert_numpy_types(results.best_kpis),
        "summary": convert_numpy_types(results.summary),
    }
    
    # Save to JSON
    with open(results_file, "w") as f:
        json.dump(results_data, f, indent=2, cls=NumpyEncoder)

    # Print results
    print("\nOptimization Results:")
    print(f"Best parameters: {convert_numpy_types(results.best_parameters)}")
    print(f"Best peak: {convert_numpy_types(results.best_kpis['peak']):.2f}")
    print(f"Best total: {convert_numpy_types(results.best_kpis['total']):.2f}")
    print(f"Best duration: {convert_numpy_types(results.best_kpis['duration']):.2f}")
    print(f"Best r0: {convert_numpy_types(results.best_kpis['r0']):.2f}")
    print(f"\nResults saved to {results_file}")


if __name__ == "__main__":
    main()
