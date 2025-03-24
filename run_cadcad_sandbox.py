#!/usr/bin/env python
"""
Example script to run cadcad-sandbox with PSUU.

This script demonstrates how to use PSUU to optimize parameters for cadcad-sandbox.
"""

import os
import sys
import pandas as pd
from psuu import PsuuExperiment

from psuu.custom_connectors.cadcad_connector import CadcadSimulationConnector
from psuu.custom_connectors.cadcad_connector import peak_infections, total_infections, epidemic_duration, calculate_r0


def main():
    """Run optimization for cadcad-sandbox."""
    print("PSUU - Cadcad-sandbox Parameter Optimization")
    print("=" * 50)
    
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
        "population": [1000, 5000],
    })

    # Configure optimizer
    experiment.set_optimizer(
        method="random",
        objective_name="peak",
        maximize=False,
        num_iterations=20
    )

    # Run optimization
    results = experiment.run(verbose=True, save_results="results/cadcad_sandbox_optimization")

    # Print results
    print("\nOptimization Results:")
    print(f"Best parameters: {results.best_parameters}")
    print(f"Best peak: {results.best_kpis['peak']:.2f}")
    print(f"Best total: {results.best_kpis['total']:.2f}")
    print(f"Best duration: {results.best_kpis['duration']:.2f}")
    print(f"Best r0: {results.best_kpis['r0']:.2f}")


if __name__ == "__main__":
    main()
