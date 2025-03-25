# Getting Started with PSUU

This guide will walk you through the basic steps to set up and run a parameter optimization experiment using PSUU.

## Installation

First, install the PSUU package:

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

## Basic Concepts

PSUU works with the following key concepts:

1. **Model Protocol**: Standard interface for model integration
2. **Simulation Connector**: Interfaces with simulation models
3. **Parameter Space**: The range of parameters to explore
4. **KPIs (Key Performance Indicators)**: Metrics to optimize
5. **Optimizer**: Algorithm to navigate the parameter space
6. **Experiment**: Manages the optimization process
7. **Configuration**: YAML/JSON based configuration files
8. **Results Format**: Standardized container for simulation results

## Approach 1: Using the Python API

### Step 1: Define Your Simulation

Start by identifying the command-line interface to your simulation model:

```python
from psuu import PsuuExperiment

# Create experiment with simulation command
experiment = PsuuExperiment(
    simulation_command="python -m my_simulation",
    param_format="--{name}={value}",  # Format for CLI parameters
    output_format="csv",              # Output format (csv or json)
    output_file="results.csv",        # Expected output file (optional)
    working_dir="/path/to/simulation"  # Working directory (optional)
)
```

### Step 2: Define KPIs

Define the key performance indicators you want to track and optimize:

```python
# Simple KPI based on column and operation
experiment.add_kpi(
    name="performance",
    column="performance_score",
    operation="max"
)

# Custom KPI function
def calculate_resilience(df):
    """Calculate resilience score from simulation results."""
    return df["failure_rate"].mean() * -1  # Negative for maximizing

experiment.add_kpi(
    name="resilience",
    function=calculate_resilience
)
```

### Step 3: Define Parameter Space

Specify the parameters and their possible values to explore:

```python
experiment.set_parameter_space({
    # Continuous parameters as (min, max) tuples
    "learning_rate": (0.001, 0.1),
    "momentum": (0.8, 0.99),
    
    # Discrete parameters as lists
    "batch_size": [32, 64, 128, 256],
    "activation": ["relu", "tanh", "sigmoid"]
})
```

### Step 4: Configure Optimizer

Choose an optimization algorithm and set its parameters:

```python
# Random Search
experiment.set_optimizer(
    method="random",
    objective_name="performance",  # KPI to optimize
    maximize=True,                 # True to maximize, False to minimize
    num_iterations=50              # Number of iterations
)

# OR: Grid Search
experiment.set_optimizer(
    method="grid",
    objective_name="performance",
    maximize=True,
    num_points=5  # Number of points per dimension
)

# OR: Bayesian Optimization
experiment.set_optimizer(
    method="bayesian",
    objective_name="performance",
    maximize=True,
    num_iterations=50,
    n_initial_points=10  # Initial random points before Bayesian optimization
)
```

### Step 5: Run the Optimization

Execute the optimization experiment:

```python
results = experiment.run(
    verbose=True,                      # Print progress information
    save_results="results/experiment"  # Base path for saving results
)
```

### Step 6: Analyze Results

Examine the optimization results:

```python
# Get best parameters and KPIs
print(f"Best parameters: {results.best_parameters}")
print(f"Best performance: {results.best_kpis['performance']}")

# Get all results as a DataFrame
all_results = results.all_results
print(all_results.head())

# Get summary statistics for KPIs
print(results.summary)
```

## Approach 2: Using the Model Protocol Interface

For more direct integration, you can implement the Model Protocol interface:

### Step 1: Implement the Protocol

Create a class that implements the CadcadModelProtocol:

```python
from psuu import CadcadModelProtocol, SimulationResults
import pandas as pd

class MyModel(CadcadModelProtocol):
    """My simulation model implementing the CadcadModelProtocol."""
    
    def __init__(self, timesteps=100, samples=1):
        self.timesteps = timesteps
        self.samples = samples
    
    def run(self, params, **kwargs):
        """Run the simulation with given parameters."""
        # Your simulation logic here
        # This is just a simple example
        df = pd.DataFrame({
            'timestep': range(self.timesteps),
            'metric': [i * params.get('alpha', 0.5) for i in range(self.timesteps)]
        })
        
        # Calculate KPIs
        kpis = {
            'max_metric': df['metric'].max(),
            'avg_metric': df['metric'].mean()
        }
        
        # Return standardized results
        return SimulationResults(
            time_series_data=df,
            kpis=kpis,
            metadata={'timesteps': self.timesteps, 'samples': self.samples},
            parameters=params
        )
    
    def get_parameter_space(self):
        """Define the parameter space."""
        return {
            'alpha': (0.1, 1.0),
            'beta': [1, 2, 3, 4, 5]
        }
    
    def get_kpi_definitions(self):
        """Define the KPI calculations."""
        return {
            'max_metric': lambda df: df['metric'].max(),
            'avg_metric': lambda df: df['metric'].mean()
        }
```

### Step 2: Use the Model Directly

Run the model directly with specific parameters:

```python
# Initialize the model
model = MyModel(timesteps=100, samples=3)

# Run with specific parameters
params = {'alpha': 0.5, 'beta': 3}
results = model.run(params)

# Access results
print(f"Time series data shape: {results.time_series_data.shape}")
print("\nKPI Results:")
for kpi_name, kpi_value in results.kpis.items():
    print(f"  {kpi_name}: {kpi_value}")

# Save results
saved_files = results.save("results/my_simulation", formats=["csv", "json"])
```

### Step 3: Optimize Using the Model Protocol

You can use the model with the PSUU optimization framework:

```python
from psuu import PsuuExperiment

# Create experiment
experiment = PsuuExperiment()

# Create a model adapter function for the experiment
def model_adapter(params):
    """Adapter function to run the model and return a DataFrame."""
    results = model.run(params)
    return results.to_dataframe()

# Set up the experiment to use the adapter function
experiment.simulation_connector.run_simulation = model_adapter

# Add KPIs from model
kpi_defs = model.get_kpi_definitions()
for kpi_name, kpi_func in kpi_defs.items():
    experiment.add_kpi(kpi_name, function=kpi_func)

# Set parameter space from model
experiment.set_parameter_space(model.get_parameter_space())

# Configure optimizer
experiment.set_optimizer(
    method="random",
    objective_name="max_metric",
    maximize=True,
    num_iterations=20
)

# Run optimization
results = experiment.run(verbose=True)
```

## Approach 3: Using Configuration Files

You can configure PSUU through YAML or JSON configuration files:

### Step 1: Create a Configuration File

Create a YAML configuration file (`config.yaml`):

```yaml
model:
  type: "cadcad"
  module: "my_model"
  entry_point: "MyModel"
  init_params:
    timesteps: 100
    samples: 5
  
parameters:
  alpha:
    type: "continuous"
    range: [0.1, 1.0]
    description: "Learning rate"
  beta:
    type: "discrete"
    range: [1, 2, 3, 4, 5]
    description: "Batch size"
  
kpis:
  max_metric:
    function: "calculate_max"
    description: "Maximum value of the metric"
  avg_metric:
    function: "calculate_avg"
    description: "Average value of the metric"
  
optimization:
  method: "bayesian"
  objective: "max_metric"
  maximize: true
  iterations: 30
  options:
    acquisition_function: "ei"
    random_state: 42
    initial_points: 5

output:
  directory: "results"
  formats: ["csv", "json"]
  save_all_runs: true
```

### Step 2: Load the Configuration

```python
from psuu import PsuuConfig

# Load configuration
config = PsuuConfig("config.yaml")

# Validate configuration
is_valid, errors = config.validate()
if not is_valid:
    print("Configuration errors:")
    for error in errors:
        print(f"  {error}")
else:
    print("Configuration is valid!")
```

### Step 3: Load the Model

```python
# Load model from configuration
try:
    model = config.load_model()
    print(f"Loaded model: {model.__class__.__name__}")
    
    # Get parameter space
    param_space = model.get_parameter_space()
    print("\nParameter space:")
    for param, spec in param_space.items():
        print(f"  {param}: {spec}")
    
    # Get KPI definitions
    kpi_defs = model.get_kpi_definitions()
    print("\nKPI definitions:")
    for kpi, func in kpi_defs.items():
        print(f"  {kpi}")
    
    # Run model with parameters from config
    params = {'alpha': 0.5, 'beta': 3}
    results = model.run(params)
    
    # Print results
    print("\nResults:")
    for kpi_name, kpi_value in results.kpis.items():
        print(f"  {kpi_name}: {kpi_value}")
        
except Exception as e:
    print(f"Error loading model: {e}")
```

## Using the CLI Interface

You can also run PSUU from the command line:

```bash
# Initialize a configuration file
psuu init

# Add parameters
psuu add-param --name "alpha" --range 0.1 1.0
psuu add-param --name "beta" --values 1 2 3 4 5

# Add KPIs
psuu add-kpi --name "max_metric" --column "metric" --operation "max"
psuu add-kpi --name "avg_metric" --column "metric" --operation "mean"

# Configure optimizer
psuu set-optimizer --method "random" --objective "max_metric" --maximize --iterations 20

# Run optimization
psuu run --output "results/experiment"
```

## Next Steps

Once you're comfortable with the basics, check out these resources:

- [Model Protocol Interface](model_protocol.md) for more details on implementing the protocol
- [Configuration-Based Integration](configuration.md) for using configuration files
- [Simulation Connectors](custom_connectors.md) for integrating with custom simulation models
- [Robust Error Handling](error_handling.md) for improving resilience
- [API Reference](api_reference.md) for detailed API documentation
