# PSUU - Parameter Selection Under Uncertainty

PSUU is a Python package designed to automate the process of parameter selection and optimization for simulation models under uncertainty, with a focus on cadCAD simulations.

## 📋 Overview

PSUU provides a framework for:
- Interfacing with simulation models via standardized protocols
- Defining custom Key Performance Indicators (KPIs) for evaluation
- Exploring parameter spaces using various optimization algorithms
- Analyzing and visualizing results
- Implementing robust error handling and validation

## ✨ Key Features

- **Standardized Model Protocol**: Define a consistent interface for model integration
- **Flexible Simulation Interface**: Connect to any CLI-based or Python-based simulation model
- **Configuration-Based Integration**: Integration through YAML or JSON configuration files
- **Custom KPI Definitions**: Define your own metrics to optimize for your specific model
- **Multiple Optimization Strategies**: Choose from grid search, random search, Bayesian optimization, and more
- **Robust Error Handling**: Improved error handling and parameter validation
- **Standardized Results Format**: Unified format for simulation results
- **Extensible Architecture**: Easily add new optimization algorithms or KPI calculations

## 🔧 Installation

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

## 🚀 Quick Start

### Python API

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

### Using the Model Protocol

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

### Configuration-Based Integration

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

# Run optimization with the model
# ...
```

### CLI Usage

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

## 📚 Documentation

For more detailed information, check out the following resources:

- [Getting Started](docs/getting_started.md): Basic usage instructions
- [User Guide](docs/user_guide.md): More detailed guidance
- [API Reference](docs/api_reference.md): Detailed API documentation
- [Examples](examples/README.md): Example usage scenarios

## 🧪 Examples

Check out the `examples` directory for comprehensive examples:

- `protocol_example`: Demonstrates the use of the model protocol interface
- `cadcad_integration.py`: Shows how to integrate cadCAD models using the new protocol

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📜 License

MIT
