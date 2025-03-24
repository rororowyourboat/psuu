# Getting Started with PSUU

This guide will walk you through the basic steps to set up and run a parameter optimization experiment using PSUU.

## Installation

First, install the PSUU package:

```bash
pip install psuu
```

For Bayesian optimization support, install the optional dependencies:

```bash
pip install "psuu[bayesian]"
```

## Basic Concepts

PSUU works with the following key concepts:

1. **Simulation Connector**: Interfaces with your simulation model
2. **Parameter Space**: The range of parameters to explore
3. **KPIs (Key Performance Indicators)**: Metrics to optimize
4. **Optimizer**: Algorithm to navigate the parameter space
5. **Experiment**: Manages the optimization process

## Step 1: Define Your Simulation

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

## Step 2: Define KPIs

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

## Step 3: Define Parameter Space

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

## Step 4: Configure Optimizer

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

## Step 5: Run the Optimization

Execute the optimization experiment:

```python
results = experiment.run(
    verbose=True,                      # Print progress information
    save_results="results/experiment"  # Base path for saving results
)
```

## Step 6: Analyze Results

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

## Using the CLI Interface

You can also run PSUU from the command line:

```bash
# Initialize a configuration file
psuu init

# Add parameters
psuu add-param --name "learning_rate" --range 0.001 0.1
psuu add-param --name "batch_size" --values 32 64 128 256

# Add KPIs
psuu add-kpi --name "performance" --column "performance_score" --operation "max"

# Configure optimizer
psuu set-optimizer --method "random" --objective "performance" --maximize --iterations 50

# Run optimization
psuu run --output "results/experiment"
```

## Next Steps

Once you're comfortable with the basics, check out these resources:

- [User Guide](user_guide.md) for more detailed usage instructions
- [Custom Simulation Connectors](custom_connectors.md) for integrating with custom simulation models
- [Advanced Usage](advanced_usage.md) for advanced optimization techniques
