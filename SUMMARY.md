# PSUU Package - Project Summary

## Architecture Overview

PSUU (Parameter Selection Under Uncertainty) is a framework for optimizing parameters of simulation models under uncertainty. The architecture follows a modular design with clear separation of concerns.

## Project Structure

```
psuu/
├── psuu/                         # Main package code
│   ├── __init__.py               # Package initialization
│   ├── version.py                # Version information
│   ├── simulation_connector.py   # Interface to simulation models
│   ├── data_aggregator.py        # Processing simulation outputs and KPIs
│   ├── experiment.py             # Main experiment controller
│   ├── cli.py                    # Command-line interface
│   ├── config.py                 # Configuration management 
│   ├── results.py                # Standardized results container
│   ├── exceptions.py             # Custom exceptions
│   ├── validation.py             # Parameter validation utilities
│   ├── protocols/                # Protocol interfaces
│   │   ├── __init__.py           # Protocol initialization
│   │   ├── model_protocol.py     # Base model protocol
│   │   └── cadcad_protocol.py    # cadCAD specific protocol
│   ├── custom_connectors/        # Custom simulation connectors
│   │   ├── __init__.py           # Connector initialization
│   │   └── cadcad_connector.py   # cadCAD specific connector
│   └── optimizers/               # Optimization algorithms
│       ├── __init__.py           # Optimizer registration
│       ├── base.py               # Abstract base optimizer
│       ├── grid_search.py        # Grid search implementation
│       ├── random_search.py      # Random search implementation
│       └── bayesian.py           # Bayesian optimization implementation
├── tests/                        # Test directory
│   ├── __init__.py
│   └── test_simulation_connector.py
├── examples/                     # Example usage
│   ├── basic_usage/              # Basic usage examples
│   ├── cadcad_integration/       # cadCAD integration examples
│   ├── cli_usage/                # CLI usage examples
│   └── protocol_example/         # Protocol interface examples
├── docs/                         # Documentation
│   ├── index.md                  # Documentation home
│   ├── getting_started.md        # Getting started guide
│   └── api_reference.md          # API reference
├── LICENSE                       # MIT License
├── README.md                     # Project documentation
├── SUMMARY.md                    # This summary file
├── WAYS_TO_RUN.md                # Ways to run the package
├── pyproject.toml                # Modern Python packaging
├── setup.py                      # Traditional setup script
└── .gitignore                    # Git ignore patterns
```

## Key Components

### Core Modules

1. **Simulation Connector**: Interfaces with simulation models via CLI or Python API
2. **Model Protocol Interfaces**: Standardized interfaces for model integration
3. **Standardized Results Format**: Common format for simulation results
4. **Configuration Management**: YAML/JSON based configuration
5. **Data Aggregator & KPI Calculator**: Processes simulation outputs and calculates KPIs
6. **Optimization Engine**: Implements multiple optimization strategies
7. **Experiment Controller**: Manages the optimization workflow
8. **Validation & Error Handling**: Robust parameter validation and error handling
9. **Command-line Interface**: User-friendly CLI access

### Protocol Interfaces

1. **ModelProtocol**: Base protocol interface for all model types
2. **CadcadModelProtocol**: Specialized protocol for cadCAD models

### Simulation Connectors

1. **SimulationConnector**: Base connector for CLI-based models
2. **CadcadSimulationConnector**: Specialized connector for cadCAD
3. **RobustCadcadConnector**: Enhanced connector with error handling

### Optimization Algorithms

1. **Grid Search**: Exhaustive search across discretized parameter space
2. **Random Search**: Stochastic sampling of parameter combinations
3. **Bayesian Optimization**: Probabilistic model-based approach for efficient exploration

## User Workflows

### Direct Model Usage

```python
# Initialize model with protocol interface
model = SIRModel(timesteps=100, samples=3)

# Run with specific parameters
params = {"beta": 0.3, "gamma": 0.05}
results = model.run(params)

# Access results
for kpi_name, kpi_value in results.kpis.items():
    print(f"{kpi_name}: {kpi_value}")
```

### Configuration-Based Usage

```python
# Load configuration
config = PsuuConfig("config.yaml")

# Load model from config
model = config.load_model()

# Run model with parameters
params = {"beta": 0.3, "gamma": 0.05}
results = model.run(params)
```

### Python API with Optimization

```python
from psuu import PsuuExperiment

# Create experiment
experiment = PsuuExperiment(simulation_command="cadcad-sir")

# Add KPIs
experiment.add_kpi("peak", column="I", operation="max")

# Set parameter space
experiment.set_parameter_space({
    "beta": (0.1, 0.5),
    "gamma": (0.01, 0.1)
})

# Configure optimizer
experiment.set_optimizer(method="bayesian", objective_name="peak", maximize=False)

# Run optimization
results = experiment.run()
```

### Command-line Interface

```bash
# Initialize configuration
psuu init

# Define parameters and KPIs
psuu add-param --name "beta" --range 0.1 0.5
psuu add-kpi --name "peak" --column "I" --operation "max"

# Configure optimizer
psuu set-optimizer --method "random" --objective "peak" --minimize

# Run optimization
psuu run
```

## Dependencies

- Core: numpy, pandas, pyyaml, click
- Bayesian optimization: scikit-optimize
- Development: pytest, black, isort, mypy, flake8
- Visualization (optional): matplotlib, seaborn
- cadCAD integration (optional): cadCAD

## Future Development

1. **Asynchronous Execution**: Support for async execution of simulations
2. **Parallel Processing**: Optimization with parallel simulation runs
3. **Enhanced Visualization**: Interactive visualization components
4. **Extended Protocol Support**: Additional protocol interfaces
5. **Reinforcement Learning**: RL-based optimization strategies
6. **Cloud Integration**: Support for running simulations in the cloud
