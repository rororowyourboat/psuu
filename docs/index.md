# PSUU Documentation

Welcome to the PSUU (Parameter Selection Under Uncertainty) documentation. This package provides a framework for automated parameter selection and optimization for simulation models under uncertainty.

## Contents

1. [Getting Started](getting_started.md)
2. [Model Protocol Interface](model_protocol.md)
3. [Configuration-Based Integration](configuration.md)
4. [Simulation Connectors](custom_connectors.md)
5. [Robust Error Handling](error_handling.md)
6. [Model Cloning and Management](model_cloning.md)
7. [API Reference](api_reference.md)

## Overview

PSUU is designed to automate the process of finding optimal parameter sets for simulation models, particularly those with uncertainty in their outputs. The package provides a flexible framework that can interface with any command-line based simulation model or directly with Python-based models through our protocol interface.

### Key Features

- **Standardized Model Protocol**: Define a consistent interface for model integration
- **Flexible Simulation Interface**: Connect to any CLI-based or Python-based simulation model
- **Configuration-Based Integration**: Integration through YAML or JSON configuration files
- **Custom KPI Definitions**: Define your own metrics to optimize for your specific model
- **Multiple Optimization Strategies**: Choose from grid search, random search, Bayesian optimization, and more
- **Robust Error Handling**: Improved error handling and parameter validation
- **Standardized Results Format**: Unified format for simulation results
- **Command-line Interface**: Run experiments from the terminal
- **Python API**: Programmatically set up and run optimization experiments
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

For additional features:
```bash
# For Bayesian optimization support
pip install "psuu[bayesian]"

# For visualization features
pip install "psuu[visualization]"

# For cadCAD integration
pip install "psuu[cadcad]"

# For development
pip install "psuu[dev]"
```

## Quick Example: Python API

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

## Quick Example: Protocol Interface

```python
from psuu import CadcadModelProtocol, SimulationResults

class MyModel(CadcadModelProtocol):
    def run(self, params, **kwargs):
        # Implement model logic
        results_df = self._run_simulation(params)
        
        # Return standardized results
        return SimulationResults(
            time_series_data=results_df,
            kpis={"score": results_df['score'].max()},
            metadata={"model_version": "1.0.0"},
            parameters=params
        )
    
    def get_parameter_space(self):
        return {
            "alpha": (0.1, 0.9),
            "beta": [1, 2, 3, 4, 5]
        }
    
    def get_kpi_definitions(self):
        return {
            "score": lambda df: df['score'].max()
        }

# Use the model
model = MyModel()
results = model.run({"alpha": 0.5, "beta": 3})
```

## Quick Example: Configuration-Based Integration

```yaml
# config.yaml
model:
  type: "cadcad"
  module: "my_model"
  entry_point: "MyModel"
  
parameters:
  alpha: [0.1, 0.9]
  beta: [1, 2, 3, 4, 5]
  
kpis:
  score:
    function: "calculate_score"
    description: "Performance score"
  
optimization:
  method: "bayesian"
  objective: "score"
  maximize: true
  iterations: 30
```

```python
from psuu import PsuuConfig

# Load configuration
config = PsuuConfig("config.yaml")

# Load model
model = config.load_model()

# Run optimization with the model
# ...
```

## Next Steps

Explore the [Getting Started](getting_started.md) guide for a more detailed introduction to using PSUU.
