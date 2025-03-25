# cadCAD-PSUU Template Model

This directory contains a template implementation of a cadCAD model that follows the recommended structure for integration with the PSUU (Parameter Selection Under Uncertainty) optimization framework.

## Usage

### Direct CLI Usage

Run the model directly from the command line:

```bash
# Activate virtual environment
source /path/to/venv/bin/activate

# Run with specific parameters
python -m template --beta 0.3 --gamma 0.05 --population 1000 --output test_run

# Get help
python -m template --help
```

### PSUU Protocol Integration

Use the model with PSUU's Protocol integration approach:

```python
from psuu import PsuuExperiment
from template.model import SIRModel

# Create model instance
model = SIRModel()

# Create experiment with model
experiment = PsuuExperiment(model=model)

# Configure optimizer
experiment.set_optimizer(
    method="random",
    objective_name="peak_infected",
    maximize=False,
    num_iterations=10
)

# Run optimization
results = experiment.run()

# Print results
print(f"Best parameters: {results.best_parameters}")
print(f"Best KPIs: {results.best_kpis}")
```

### PSUU CLI Integration

Use the model with PSUU's CLI integration approach:

```python
from psuu import PsuuExperiment

# Create experiment with CLI
experiment = PsuuExperiment(
    simulation_command="python -m template",
    param_format="--{name} {value}",
    output_format="json"
)

# Set parameter space
experiment.set_parameter_space({
    "beta": (0.1, 0.5),
    "gamma": (0.01, 0.1),
    "population": [1000, 5000, 10000]
})

# Add KPIs
experiment.add_kpi("peak_infected", column="peak_infected")
experiment.add_kpi("total_infected", column="total_infected")
experiment.add_kpi("r0", column="r0")

# Configure optimizer
experiment.set_optimizer(
    method="bayesian",
    objective_name="peak_infected",
    maximize=False,
    num_iterations=20
)

# Run optimization
results = experiment.run()
```

### YAML Configuration

Use a YAML configuration file:

```yaml
# config.yaml
model:
  class: "template.model.SIRModel"
  protocol: "cadcad"
  
parameters:
  beta:
    type: continuous
    min: 0.1
    max: 0.5
  gamma:
    type: continuous
    min: 0.01
    max: 0.1
  
kpis:
  peak_infected:
    objective: minimize
```

```python
from psuu.config import configure_experiment_from_yaml

# Create and run experiment from YAML
experiment = configure_experiment_from_yaml("config.yaml")
results = experiment.run()
```

## Key Components

- **model.py**: Main model class implementing `CadcadModelProtocol`
- **params.py**: Parameter definitions and ranges
- **__main__.py**: CLI entry point
- **sir_config.yaml**: Example YAML configuration

## Customization

To adapt this template for your own model:

1. Modify `params.py` with your model's parameters
2. Update the state update functions in `model.py`
3. Implement KPI calculation functions relevant to your model
4. Update the initial state and any other model-specific logic

## Requirements

- Python 3.7+
- cadCAD 0.4.28+
- pandas 2.0.0+
- click 8.0.0+
- pyyaml
- typing_extensions 4.0.0+

## Model Structure

The template follows the recommended structure for cadCAD models:

```
template/
├── __init__.py         # Package initialization
├── __main__.py         # CLI entry point
├── model.py            # Main model implementation
├── params.py           # Parameter definitions and ranges
├── kpi.py              # KPI calculation functions (included in model.py for simplicity)
├── core_logic.py       # Core simulation logic (included in model.py for simplicity)
└── sir_config.yaml     # Example YAML configuration
```

## SIR Model Description

This template implements a simple SIR (Susceptible-Infected-Recovered) epidemic model:

- **Susceptible (S)**: Population vulnerable to infection
- **Infected (I)**: Population currently infected
- **Recovered (R)**: Population that has recovered and is immune

The model dynamics are governed by:
- **Beta (β)**: Infection rate parameter
- **Gamma (γ)**: Recovery rate parameter

The basic reproduction number R₀ = β/γ determines epidemic severity.

## Key Performance Indicators (KPIs)

The model calculates several KPIs:

- **peak_infected**: Maximum number of infected individuals at any time
- **total_infected**: Total number of individuals who became infected
- **epidemic_duration**: Duration of the epidemic in timesteps
- **r0**: Basic reproduction number (β/γ)

## License

This template is provided as part of the PSUU project.

## Acknowledgments

This template is based on the integration guidelines for cadCAD and PSUU, drawing inspiration from the cadcad-sandbox repository.
