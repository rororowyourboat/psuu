# PSUU Documentation

Welcome to the PSUU (Parameter Selection Under Uncertainty) documentation. This package provides a framework for automated parameter selection and optimization for simulation models under uncertainty.

## Contents

1. [Getting Started](getting_started.md)
2. [User Guide](user_guide.md)
3. [Advanced Usage](advanced_usage.md)
4. [Custom Simulation Connectors](custom_connectors.md)
5. [API Reference](api_reference.md)

## Overview

PSUU is designed to automate the process of finding optimal parameter sets for simulation models, particularly those with uncertainty in their outputs. The package provides a flexible framework that can interface with any command-line based simulation model.

### Key Features

- **Command-line Interface**: Run experiments from the terminal
- **Python API**: Programmatically set up and run optimization experiments
- **Multiple Optimization Algorithms**: Grid search, random search, Bayesian optimization
- **Custom KPI Definitions**: Define your own metrics to optimize
- **Extensible Architecture**: Easily add new optimization algorithms or KPI calculations

### Basic Workflow

1. Define the parameter space to explore
2. Configure KPI calculations
3. Select an optimization algorithm
4. Run the optimization
5. Analyze the results

## Installation

```bash
pip install psuu
```

Or for development:

```bash
git clone https://github.com/yourusername/psuu.git
cd psuu
pip install -e .
```

## Quick Example

```python
from psuu import PsuuExperiment

# Create experiment
experiment = PsuuExperiment(simulation_command="my_simulation")

# Define KPIs
experiment.add_kpi("score", column="score", operation="max")

# Set parameter space
experiment.set_parameter_space({
    "alpha": (0.1, 0.9),
    "beta": [1, 2, 3, 4, 5]
})

# Configure optimizer
experiment.set_optimizer(
    method="bayesian",
    objective_name="score",
    maximize=True
)

# Run optimization
results = experiment.run()

# Print best parameters
print(f"Best parameters: {results.best_parameters}")
print(f"Best score: {results.best_kpis['score']}")
```

## Next Steps

Explore the [Getting Started](getting_started.md) guide for a more detailed introduction to using PSUU.
