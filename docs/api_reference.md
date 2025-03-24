# PSUU API Reference

This page documents the main classes and functions in the PSUU package.

## PsuuExperiment

The main class for setting up and running parameter optimization experiments.

```python
from psuu import PsuuExperiment

experiment = PsuuExperiment(
    simulation_command="python -m model",
    param_format="--{name} {value}",
    output_format="csv",
    output_file=None,
    working_dir=None
)
```

### Constructor Parameters

- `simulation_command` (str): Command to run the simulation
- `param_format` (str, optional): Format string for parameter arguments. Default is `"--{name} {value}"`
- `output_format` (str, optional): Format of simulation output ('csv' or 'json'). Default is `"csv"`
- `output_file` (str, optional): Path to output file (if None, stdout is used). Default is `None`
- `working_dir` (str, optional): Working directory for the simulation. Default is `None`

### Methods

#### `add_kpi`

Add a KPI to calculate from simulation results.

```python
experiment.add_kpi(
    name="metric_name",
    function=None,
    column=None,
    operation=None,
    filter_condition=None
)
```

Parameters:
- `name` (str): Name of the KPI
- `function` (callable, optional): Custom function to calculate the KPI (takes DataFrame, returns value)
- `column` (str, optional): Column name for simple KPI calculation
- `operation` (str, optional): Operation for simple KPI ('max', 'min', 'mean', 'sum', etc.)
- `filter_condition` (str, optional): Optional condition to filter the DataFrame

#### `set_parameter_space`

Set the parameter space to explore.

```python
experiment.set_parameter_space({
    "param1": (min_value, max_value),  # Continuous parameter
    "param2": [value1, value2, value3]  # Discrete parameter
})
```

Parameters:
- `parameter_space` (dict): Dictionary mapping parameter names to their possible values

#### `set_optimizer`

Set the optimization method.

```python
experiment.set_optimizer(
    method="random",
    objective_name="metric_name",
    maximize=True,
    **kwargs
)
```

Parameters:
- `method` (str): Optimization method ('grid', 'random', 'bayesian')
- `objective_name` (str): Name of the KPI to optimize
- `maximize` (bool, optional): Whether to maximize (True) or minimize (False) the objective. Default is `True`
- `**kwargs`: Additional arguments for the specific optimizer

Method-specific parameters:
- **Grid search**: `num_points` (int): Number of points per dimension
- **Random search**: `num_iterations` (int): Number of iterations, `seed` (int): Random seed
- **Bayesian optimization**: `num_iterations` (int): Number of iterations, `n_initial_points` (int): Initial random points, `seed` (int): Random seed

#### `run`

Run the parameter optimization experiment.

```python
results = experiment.run(
    max_iterations=None,
    verbose=True,
    save_results="results/experiment"
)
```

Parameters:
- `max_iterations` (int, optional): Maximum number of iterations (None for optimizer default). Default is `None`
- `verbose` (bool, optional): Whether to print progress information. Default is `True`
- `save_results` (str, optional): Path to save results (None to skip saving). Default is `None`

Returns:
- `ExperimentResults`: Object containing optimization results

## ExperimentResults

Container for experiment results.

### Properties

- `iterations` (int): Number of iterations performed
- `elapsed_time` (float): Total elapsed time (seconds)
- `best_parameters` (dict): Best parameter set found
- `best_kpis` (dict): KPIs for the best parameters
- `all_results` (pd.DataFrame): DataFrame with all results
- `summary` (dict): Summary statistics for KPIs

### Methods

#### `to_csv`

Save all results to a CSV file.

```python
results.to_csv("results.csv")
```

#### `to_json`

Save results to a JSON file.

```python
results.to_json("results.json")
```

#### `save`

Save results to multiple formats (CSV, JSON, YAML).

```python
results.save("results/experiment")
```

## quick_optimize

A convenience function for quick optimization experiments.

```python
from psuu import quick_optimize

results = quick_optimize(
    command="python -m model",
    params={"beta": (0.1, 0.5), "gamma": (0.01, 0.1)},
    kpi_column="metric",
    objective="max",
    iterations=20
)
```

Parameters:
- `command` (str): Simulation command
- `params` (dict): Parameter space to explore
- `kpi_column` (str): Column name for the KPI
- `objective` (str, optional): 'max' or 'min'. Default is `"max"`
- `iterations` (int, optional): Number of iterations. Default is `20`
- `**kwargs`: Additional arguments for SimulationConnector

## SimulationConnector

Connects to and runs external simulation models through command-line interfaces.

```python
from psuu.simulation_connector import SimulationConnector

connector = SimulationConnector(
    command="python -m model",
    param_format="--{name} {value}",
    output_format="csv",
    output_file=None,
    working_dir=None
)
```

### Methods

#### `run_simulation`

Run the simulation with the given parameters and return results.

```python
df = connector.run_simulation({"param1": value1, "param2": value2})
```

## Optimizer Classes

### Base Optimizer

Abstract base class for parameter space optimization algorithms.

```python
from psuu.optimizers.base import Optimizer

# Don't instantiate directly - use a concrete optimizer instead
```

### GridSearchOptimizer

Grid search optimizer that exhaustively searches the parameter space.

```python
from psuu.optimizers.grid_search import GridSearchOptimizer

optimizer = GridSearchOptimizer(
    parameter_space={"param1": (0, 1), "param2": [1, 2, 3]},
    objective_name="metric",
    maximize=True,
    num_points=5
)
```

### RandomSearchOptimizer

Random search optimizer that samples random points from the parameter space.

```python
from psuu.optimizers.random_search import RandomSearchOptimizer

optimizer = RandomSearchOptimizer(
    parameter_space={"param1": (0, 1), "param2": [1, 2, 3]},
    objective_name="metric",
    maximize=True,
    num_iterations=50,
    seed=42
)
```

### BayesianOptimizer

Bayesian optimizer using Gaussian Process regression from scikit-optimize.

```python
from psuu.optimizers.bayesian import BayesianOptimizer

optimizer = BayesianOptimizer(
    parameter_space={"param1": (0, 1), "param2": [1, 2, 3]},
    objective_name="metric",
    maximize=True,
    num_iterations=50,
    n_initial_points=10,
    acq_func="EI",
    seed=42
)
```
