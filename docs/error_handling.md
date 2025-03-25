# Robust Error Handling

PSUU provides robust error handling and validation mechanisms to make your parameter optimization experiments more reliable. This document explains how to use these features to handle errors gracefully and validate parameter values.

## Error Hierarchy

PSUU defines a hierarchy of exception types to help you handle specific error scenarios:

```
PsuuError (base class)
├── ModelInitializationError
├── ModelExecutionError
├── ParameterValidationError
├── KpiCalculationError
├── ConfigurationError
├── SimulationError
├── OptimizationError
└── ResultsError
```

## Using Custom Exceptions

You can use these exceptions in your code to handle specific error types:

```python
from psuu import (
    PsuuError,
    ModelExecutionError,
    ParameterValidationError,
    ConfigurationError
)

try:
    # Try loading a configuration file
    config = PsuuConfig("config.yaml")
    model = config.load_model()
    
    # Validate parameters
    params = {"alpha": 1.5, "beta": 2}
    is_valid, error_msg = model.validate_parameters(params)
    if not is_valid:
        raise ParameterValidationError(error_msg)
    
    # Run the model
    results = model.run(params)
    
except ConfigurationError as e:
    print(f"Configuration error: {e}")
    # Handle configuration error
    
except ParameterValidationError as e:
    print(f"Parameter validation error: {e}")
    # Handle validation error
    
except ModelExecutionError as e:
    print(f"Model execution error: {e}")
    # Handle execution error
    
except PsuuError as e:
    print(f"PSUU error: {e}")
    # Handle any other PSUU error
    
except Exception as e:
    print(f"Unexpected error: {e}")
    # Handle any other error
```

## Parameter Validation

### Using the ParameterValidator Class

The `ParameterValidator` class provides a way to validate parameters against their defined space:

```python
from psuu import ParameterValidator

# Define parameter space
parameter_space = {
    "alpha": (0.1, 1.0),
    "beta": [1, 2, 3, 4, 5],
    "gamma": {
        "type": "continuous",
        "range": (0.01, 0.1),
        "description": "Recovery rate"
    }
}

# Create validator
validator = ParameterValidator(parameter_space)

# Validate a single parameter
is_valid, error_msg = validator.validate_parameter("alpha", 0.5)
print(f"Alpha validation: {'Valid' if is_valid else 'Invalid'} - {error_msg or ''}")

# Validate a set of parameters
params = {"alpha": 0.5, "beta": 3, "gamma": 0.05}
is_valid, errors = validator.validate_parameters(params)

if not is_valid:
    print("Parameter validation errors:")
    for param, error in errors.items():
        print(f"  {param}: {error}")
else:
    print("All parameters are valid")
```

### Using Model Protocol Validation

Models implementing the `ModelProtocol` interface have a built-in `validate_parameters` method:

```python
from my_model import MyModel

# Create model
model = MyModel()

# Validate parameters
params = {"alpha": 0.5, "beta": 3}
is_valid, error_msg = model.validate_parameters(params)

if not is_valid:
    print(f"Parameter validation error: {error_msg}")
else:
    print("Parameters are valid")
    
    # Run the model with validated parameters
    results = model.run(params)
```

## Robust Simulation Connector

PSUU provides a `RobustCadcadConnector` class that enhances error handling for cadCAD simulations:

```python
from psuu import RobustCadcadConnector

# Create robust connector with error handling
connector = RobustCadcadConnector(
    command="python -m model",
    param_format="--{name} {value}",
    working_dir="cadcad-sandbox",
    error_policy="retry",        # 'raise', 'retry', or 'fallback'
    retry_attempts=3,            # Number of retry attempts
    error_log_file="errors.log", # File to log errors
    fallback_values={            # Values to return on failure
        "timestep": [0],
        "I": [0],
        "S": [1000],
        "R": [0]
    }
)

# Run simulation with robust error handling
try:
    results_df = connector.run_simulation({
        "beta": 0.3,
        "gamma": 0.05
    })
    print("Simulation successful")
except Exception as e:
    print(f"Error running simulation: {e}")
```

### Error Policies

The `RobustCadcadConnector` supports three error policies:

1. **raise**: Raise an exception when a simulation fails (after retrying)
2. **retry**: Retry the simulation with slight parameter variations
3. **fallback**: Return fallback values when a simulation fails

```python
# Raise policy (default)
connector = RobustCadcadConnector(
    command="python -m model",
    error_policy="raise"
)

# Retry policy
connector = RobustCadcadConnector(
    command="python -m model",
    error_policy="retry",
    retry_attempts=5  # Try up to 5 times
)

# Fallback policy
connector = RobustCadcadConnector(
    command="python -m model",
    error_policy="fallback",
    fallback_values={
        # Default values to return on failure
        "timestep": [0],
        "I": [0],
        "S": [1000],
        "R": [0]
    }
)
```

### Error Logging

You can enable error logging to track simulation failures:

```python
connector = RobustCadcadConnector(
    command="python -m model",
    error_log_file="simulation_errors.log"
)

# Run multiple simulations
for i in range(10):
    try:
        params = {"beta": 0.1 + i * 0.05, "gamma": 0.05}
        results = connector.run_simulation(params)
    except Exception as e:
        print(f"Error with params {params}: {e}")

# Error log format (JSON lines)
# {"timestamp": 1647123456.789, "parameters": {"beta": 0.3, "gamma": 0.05}, "error_type": "CalledProcessError", "error_message": "Command failed with return code 1", "traceback": "..."}
```

## Parameter Jittering

When using the `retry` error policy, the `RobustCadcadConnector` adds small random variations to numeric parameters to help overcome transient failures:

```python
# Original parameters
params = {"beta": 0.3, "gamma": 0.05, "population": 1000}

# After jittering (example)
jittered_params = connector._add_jitter(params)
# Might become something like:
# {"beta": 0.298, "gamma": 0.0502, "population": 999}
```

The jitter is up to ±1% of the parameter value, which is usually small enough not to significantly affect the simulation while potentially helping to overcome numerical issues.

## Configuration Validation

You can validate configuration files before using them:

```python
from psuu import PsuuConfig, ConfigurationError

try:
    # Load configuration
    config = PsuuConfig("config.yaml")
    
    # Validate configuration
    is_valid, errors = config.validate()
    
    if not is_valid:
        print("Configuration validation errors:")
        for error in errors:
            print(f"  {error}")
        raise ConfigurationError("Invalid configuration")
    
    # Use the validated configuration
    model = config.load_model()
    param_space = config.get_parameters_config()
    # ...
    
except ConfigurationError as e:
    print(f"Configuration error: {e}")
    # Handle configuration error
```

## Handling KPI Calculation Errors

PSUU provides a way to handle errors in KPI calculations:

```python
from psuu import PsuuExperiment, KpiCalculationError

# Define a KPI function that handles potential errors
def safe_kpi_calculation(df):
    try:
        # Try to calculate the KPI
        return df["metric"].max()
    except Exception as e:
        # Handle the error (e.g., return a default value or raise a custom exception)
        print(f"Error calculating KPI: {e}")
        return float("nan")  # Return NaN for missing/error values

# Create experiment
experiment = PsuuExperiment(simulation_command="python -m model")

# Add the safe KPI function
experiment.add_kpi("safe_metric", function=safe_kpi_calculation)
```

## Best Practices for Error Handling

Here are some best practices for robust error handling in PSUU:

1. **Use specific exception types** to catch and handle specific error scenarios
2. **Validate parameters** before running simulations to catch errors early
3. **Use retry mechanisms** for simulations that might have transient failures
4. **Log errors** for later analysis and debugging
5. **Provide fallbacks** for non-critical errors to allow experiments to continue
6. **Validate configurations** before using them
7. **Handle KPI calculation errors** to prevent experiment failures due to data issues
8. **Implement custom validation** for complex parameter constraints

## Example: Comprehensive Error Handling

Here's a comprehensive example that combines various error handling techniques:

```python
from psuu import (
    PsuuExperiment,
    PsuuConfig,
    RobustCadcadConnector,
    ParameterValidator,
    PsuuError,
    ConfigurationError,
    ParameterValidationError,
    ModelExecutionError
)
import os
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("psuu_experiment.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("psuu_experiment")

try:
    # Load configuration
    config_path = "config.yaml"
    logger.info(f"Loading configuration from {config_path}")
    
    try:
        config = PsuuConfig(config_path)
    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
        raise ConfigurationError(f"Failed to load configuration: {e}")
    
    # Validate configuration
    logger.info("Validating configuration")
    is_valid, errors = config.validate()
    if not is_valid:
        for error in errors:
            logger.error(f"Configuration error: {error}")
        raise ConfigurationError("Invalid configuration")
    
    # Create output directory
    output_dir = config.get_output_config().get("directory", "results")
    os.makedirs(output_dir, exist_ok=True)
    
    # Load model
    logger.info("Loading model")
    try:
        model = config.load_model()
        logger.info(f"Loaded model: {model.__class__.__name__}")
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        raise ModelInitializationError(f"Failed to load model: {e}")
    
    # Create robust connector
    logger.info("Creating robust connector")
    connector = RobustCadcadConnector(
        command="python -m model",
        param_format="--{name} {value}",
        working_dir="cadcad-sandbox",
        error_policy="retry",
        retry_attempts=3,
        error_log_file=f"{output_dir}/simulation_errors.log"
    )
    
    # Create parameter validator
    parameter_space = model.get_parameter_space()
    validator = ParameterValidator(parameter_space)
    
    # Create experiment
    logger.info("Creating experiment")
    experiment = PsuuExperiment()
    experiment.simulation_connector = connector
    
    # Add KPIs from model
    logger.info("Adding KPIs")
    kpi_defs = model.get_kpi_definitions()
    for kpi_name, kpi_def in kpi_defs.items():
        if isinstance(kpi_def, dict) and 'function' in kpi_def:
            experiment.add_kpi(kpi_name, function=kpi_def['function'])
        else:
            experiment.add_kpi(kpi_name, function=kpi_def)
    
    # Set parameter space
    logger.info("Setting parameter space")
    experiment.set_parameter_space(parameter_space)
    
    # Configure optimizer
    logger.info("Configuring optimizer")
    opt_config = config.get_optimization_config()
    experiment.set_optimizer(
        method=opt_config.get('method', 'random'),
        objective_name=opt_config.get('objective'),
        maximize=opt_config.get('maximize', False),
        **opt_config.get('options', {})
    )
    
    # Run optimization
    logger.info("Running optimization")
    results = experiment.run(
        max_iterations=opt_config.get('iterations'),
        verbose=True,
        save_results=f"{output_dir}/optimization"
    )
    
    # Log results
    logger.info("Optimization completed")
    logger.info(f"Best parameters: {results.best_parameters}")
    for kpi_name, kpi_value in results.best_kpis.items():
        logger.info(f"Best {kpi_name}: {kpi_value:.4f}")
    
except ConfigurationError as e:
    logger.error(f"Configuration error: {e}")
    print(f"Configuration error: {e}")
    # Handle configuration error
    
except ParameterValidationError as e:
    logger.error(f"Parameter validation error: {e}")
    print(f"Parameter validation error: {e}")
    # Handle validation error
    
except ModelExecutionError as e:
    logger.error(f"Model execution error: {e}")
    print(f"Model execution error: {e}")
    # Handle execution error
    
except PsuuError as e:
    logger.error(f"PSUU error: {e}")
    print(f"PSUU error: {e}")
    # Handle any other PSUU error
    
except Exception as e:
    logger.exception(f"Unexpected error: {e}")
    print(f"Unexpected error: {e}")
    # Handle any other error
    
finally:
    logger.info("Experiment script completed")
```

By implementing robust error handling, you can make your parameter optimization experiments more reliable, even when working with complex or unstable simulation models.
