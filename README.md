# PSUU - Parameter Selection Under Uncertainty

PSUU is a Python package designed to automate the process of parameter selection and optimization for simulation models under uncertainty, with a focus on cadCAD simulations.

## Overview

PSUU provides a framework for:
- Interfacing with simulation models via command-line interfaces
- Defining custom Key Performance Indicators (KPIs) for evaluation
- Exploring parameter spaces using various optimization algorithms
- Analyzing and visualizing results

## Key Features

- **Flexible Simulation Interface**: Connect to any CLI-based simulation model
- **Custom KPI Definitions**: Define your own metrics to optimize for your specific model
- **Multiple Optimization Strategies**: Choose from grid search, random search, Bayesian optimization, and more
- **Feedback Control**: Iterative optimization leveraging simulation results
- **Extensible Architecture**: Easily add new optimization algorithms or KPI calculations

## Installation

```bash
pip install psuu
```

## Quick Start

```python
from psuu import PsuuExperiment

# Define experiment
experiment = PsuuExperiment(
    simulation_command="python -m model"
)

# Define KPIs
def peak_metric(df):
    return df['metric_column'].max()

experiment.add_kpi("peak", peak_metric)

# Set parameter space
experiment.set_parameter_space({
    "beta": (0.1, 0.5),
    "gamma": (0.01, 0.1)
})

# Configure optimization
experiment.set_optimizer(
    method="bayesian",
    iterations=20
)

# Run optimization
results = experiment.run()

# Access results
best_params = results.best_parameters
```

## CLI Usage

```bash
# Initialize configuration
psuu init

# Define parameter space
psuu add-param --name "beta" --range 0.1 0.5

# Add KPI function
psuu add-kpi --name "peak" --column "metric_column" --operation "max"

# Run optimization
psuu run
```

## License

MIT
