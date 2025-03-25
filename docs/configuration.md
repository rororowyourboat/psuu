# Configuration-Based Integration

PSUU supports configuration-based integration through YAML or JSON files. This approach allows you to define your model, parameters, KPIs, and optimization settings in a declarative way, without writing code.

## Configuration File Structure

A typical PSUU configuration file has the following structure:

```yaml
model:
  type: "cadcad"
  module: "my_model"
  entry_point: "MyModel"
  init_params:
    param1: value1
    param2: value2

parameters:
  param1:
    type: "continuous"
    range: [min, max]
    description: "Parameter description"
  param2:
    type: "discrete"
    range: [value1, value2, value3]
    description: "Parameter description"

kpis:
  kpi1:
    function: "function_name"
    description: "KPI description"
  kpi2:
    function: "function_name"
    description: "KPI description"

optimization:
  method: "bayesian"
  objective: "kpi1"
  maximize: true
  iterations: 30
  options:
    option1: value1
    option2: value2

output:
  directory: "results"
  formats: ["csv", "json"]
  save_all_runs: true
  visualizations: ["parameter_importance", "optimization_progress"]
```

## Configuration Sections

### Model Section

The `model` section defines the simulation model to use:

```yaml
model:
  type: "cadcad"            # Model type (cadcad or custom)
  module: "my_model"        # Python module containing the model
  entry_point: "MyModel"    # Class or function name
  init_params:              # Parameters for model initialization
    timesteps: 100
    samples: 5
```

### Parameters Section

The `parameters` section defines the parameter space to explore:

```yaml
parameters:
  learning_rate:
    type: "continuous"                 # Parameter type
    range: [0.001, 0.1]                # Value range [min, max]
    description: "Learning rate"        # Description
  batch_size:
    type: "discrete"                    # Discrete parameter
    range: [32, 64, 128, 256]           # List of possible values
    description: "Mini-batch size"
  activation:
    type: "categorical"                 # Categorical parameter
    categories: ["relu", "tanh", "sigmoid"]
    description: "Activation function"
  use_dropout:
    type: "boolean"                     # Boolean parameter
    description: "Whether to use dropout"
```

Alternative simplified syntax for simpler cases:

```yaml
parameters:
  learning_rate: [0.001, 0.1]           # Continuous parameter
  batch_size: [32, 64, 128, 256]        # Discrete parameter
  activation: ["relu", "tanh", "sigmoid"]  # Categorical parameter
```

### KPIs Section

The `kpis` section defines the Key Performance Indicators to calculate:

```yaml
kpis:
  accuracy:
    function: "calculate_accuracy"    # Function name
    description: "Model accuracy"     # Description
    tags: ["performance"]            # Optional tags
  training_time:
    function: "calculate_time"
    description: "Training time in seconds"
    tags: ["efficiency"]
```

### Optimization Section

The `optimization` section configures the optimization algorithm:

```yaml
optimization:
  method: "bayesian"        # Optimization method
  objective: "accuracy"     # KPI to optimize
  maximize: true            # Whether to maximize or minimize
  iterations: 30            # Number of iterations
  options:                  # Method-specific options
    acquisition_function: "ei"
    random_state: 42
    initial_points: 5
```

### Output Section

The `output` section configures result storage and visualization:

```yaml
output:
  directory: "results/experiment1"    # Output directory
  formats: ["csv", "json", "yaml"]    # Output formats
  save_all_runs: true                 # Save all runs or only the best
  visualizations:                      # Visualizations to generate
    - "parameter_importance"
    - "optimization_progress"
```

## Using Configuration Files

### Loading a Configuration File

You can load a configuration file using the `PsuuConfig` class:

```python
from psuu import PsuuConfig

# Load from YAML
config = PsuuConfig("config.yaml")

# Load from JSON
config = PsuuConfig("config.json")

# Load from dictionary
config_dict = {
    "model": {"type": "cadcad", "module": "my_model", "entry_point": "MyModel"},
    "parameters": {"param1": [0, 1]},
    # ...
}
config = PsuuConfig(config_dict=config_dict)
```

### Validating a Configuration

You can validate the configuration to check for errors:

```python
is_valid, errors = config.validate()

if not is_valid:
    print("Configuration errors:")
    for error in errors:
        print(f"  {error}")
else:
    print("Configuration is valid!")
```

### Loading a Model from Configuration

You can load the model defined in the configuration:

```python
try:
    model = config.load_model()
    print(f"Loaded model: {model.__class__.__name__}")
except Exception as e:
    print(f"Error loading model: {e}")
```

### Accessing Configuration Sections

You can access specific sections of the configuration:

```python
# Get model configuration
model_config = config.get_model_config()
print(f"Model type: {model_config.get('type')}")
print(f"Model module: {model_config.get('module')}")

# Get parameters configuration
param_config = config.get_parameters_config()
for param, spec in param_config.items():
    print(f"Parameter: {param}, Spec: {spec}")

# Get KPIs configuration
kpi_config = config.get_kpis_config()
for kpi, spec in kpi_config.items():
    print(f"KPI: {kpi}, Function: {spec.get('function')}")

# Get optimization configuration
opt_config = config.get_optimization_config()
print(f"Optimization method: {opt_config.get('method')}")
print(f"Objective: {opt_config.get('objective')}")

# Get output configuration
out_config = config.get_output_config()
print(f"Output directory: {out_config.get('directory')}")
print(f"Output formats: {out_config.get('formats')}")
```

### Modifying and Saving Configuration

You can modify the configuration and save it:

```python
# Set model configuration
config.set_model_config(
    model_type="cadcad",
    module="new_model",
    entry_point="NewModel",
    init_params={"timesteps": 200, "samples": 10}
)

# Set parameters configuration
config.set_parameter_config({
    "learning_rate": {
        "type": "continuous",
        "range": [0.0001, 0.01],
        "description": "Learning rate"
    }
})

# Set optimization configuration
config.set_optimization_config(
    method="random",
    objective="accuracy",
    maximize=True,
    iterations=50,
    options={"seed": 42}
)

# Save configuration
config.save("new_config.yaml")
```

## Complete Example

Here's a complete example of using configuration-based integration:

```python
from psuu import PsuuConfig, PsuuExperiment
import os

# Create output directory
os.makedirs("results", exist_ok=True)

# Load configuration
config = PsuuConfig("config.yaml")

# Validate configuration
is_valid, errors = config.validate()
if not is_valid:
    print("Configuration errors:")
    for error in errors:
        print(f"  {error}")
    exit(1)

# Load model
try:
    model = config.load_model()
    print(f"Loaded model: {model.__class__.__name__}")
except Exception as e:
    print(f"Error loading model: {e}")
    exit(1)

# Create experiment
experiment = PsuuExperiment()

# Create a model adapter function
def model_adapter(params):
    """Adapter function to run the model and return a DataFrame."""
    results = model.run(params)
    return results.to_dataframe()

# Set up the experiment to use the adapter function
experiment.simulation_connector.run_simulation = model_adapter

# Add KPIs from model
kpi_defs = model.get_kpi_definitions()
for kpi_name, kpi_def in kpi_defs.items():
    if isinstance(kpi_def, dict) and 'function' in kpi_def:
        experiment.add_kpi(kpi_name, function=kpi_def['function'])
    else:
        experiment.add_kpi(kpi_name, function=kpi_def)

# Set parameter space from model
experiment.set_parameter_space(model.get_parameter_space())

# Configure optimizer from config
opt_config = config.get_optimization_config()
experiment.set_optimizer(
    method=opt_config.get('method', 'random'),
    objective_name=opt_config.get('objective'),
    maximize=opt_config.get('maximize', False),
    **opt_config.get('options', {})
)

# Run optimization
output_config = config.get_output_config()
output_dir = output_config.get('directory', 'results')
os.makedirs(output_dir, exist_ok=True)

results = experiment.run(
    max_iterations=opt_config.get('iterations'),
    verbose=True,
    save_results=f"{output_dir}/optimization"
)

# Print results
print("\nOptimization Results:")
print(f"Best parameters: {results.best_parameters}")
for kpi, value in results.best_kpis.items():
    print(f"Best {kpi}: {value:.4f}")
```

## Benefits of Configuration-Based Integration

Using configuration-based integration provides several benefits:

1. **Separation of Concerns**: Keep model and experiment configuration separate from code
2. **Reusability**: Easily reuse the same configuration across different experiments
3. **Versioning**: Track changes to your configuration over time
4. **Simplicity**: Simple, declarative syntax for defining complex experiments
5. **Flexibility**: Configure many aspects of your experiment without changing code
6. **Consistency**: Ensure consistent configuration across multiple runs
7. **Shareability**: Share experiment configurations with colleagues

Configuration-based integration is particularly useful for:
- Running many similar experiments with slight variations
- Sharing experiment configurations with team members
- Creating standardized experiment templates
- Automating experiment setups
- Maintaining reproducibility across different environments
