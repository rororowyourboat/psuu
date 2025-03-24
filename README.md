# PSUU - Parameter Selection Under Uncertainty

PSUU is a Python package designed to automate the process of parameter selection and optimization for simulation models under uncertainty, with a focus on cadCAD simulations.

## Overview

PSUU provides a framework for:
- Interfacing with simulation models via command-line interfaces or direct Python API
- Defining custom Key Performance Indicators (KPIs) for evaluation
- Exploring parameter spaces using various optimization algorithms
- Analyzing and visualizing results
- Standardized model protocol interface for seamless integration

## Key Features

- **Flexible Simulation Interface**: Connect to any CLI-based or Python-based simulation model
- **Standard Model Protocol**: Define a consistent interface for model integration
- **Custom KPI Definitions**: Define your own metrics to optimize for your specific model
- **Multiple Optimization Strategies**: Choose from grid search, random search, Bayesian optimization, and more
- **Feedback Control**: Iterative optimization leveraging simulation results
- **Extensible Architecture**: Easily add new optimization algorithms or KPI calculations
- **Configuration-Based Integration**: Integration through YAML or JSON configuration files
- **Robust Error Handling**: Improved error handling and parameter validation
- **Standardized Results Format**: Unified format for simulation results

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

## Using the Model Protocol

```python
from psuu import CadcadModelProtocol, SimulationResults

class MyModel(CadcadModelProtocol):
    def run(self, params, **kwargs):
        # Implement model logic
        results_df = self._run_simulation(params)
        
        # Return standardized results
        return SimulationResults(
            time_series_data=results_df,
            kpis={"peak": results_df['metric'].max()},
            metadata={"model_version": "1.0.0"},
            parameters=params
        )
    
    def get_parameter_space(self):
        return {
            "beta": (0.1, 0.5),
            "gamma": (0.01, 0.1)
        }
    
    def get_kpi_definitions(self):
        return {
            "peak": lambda df: df['metric'].max(),
            "total": lambda df: df['metric'].sum()
        }
```

## Configuration-Based Integration

```yaml
# config.yaml
model:
  type: "cadcad"
  module: "my_model"
  entry_point: "MyModel"
  
parameters:
  beta: [0.1, 0.5]
  gamma: [0.01, 0.1]
  
kpis:
  peak:
    function: "peak_metric"
    description: "Maximum value of the metric"
  
optimization:
  method: "bayesian"
  objective: "peak"
  maximize: false
  iterations: 30
```

```python
from psuu import PsuuConfig

# Load configuration
config = PsuuConfig("config.yaml")

# Load model
model = config.load_model()

# Run optimization
# ...
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

## Examples

Check out the `examples` directory for comprehensive examples:

- `protocol_example`: Demonstrates the use of the model protocol interface
- `cadcad_integration.py`: Shows how to integrate cadCAD models using the new protocol

## License

MIT
