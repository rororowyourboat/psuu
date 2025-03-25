# cadCAD-PSUU Template Model

This directory contains a template implementation of a cadCAD model that follows the recommended structure for integration with the PSUU (Parameter Selection Under Uncertainty) optimization framework.

## Directory Structure

```
template/
├── __init__.py           # Package initialization
├── __main__.py           # CLI entry point
├── params.py             # Parameter definitions and ranges
├── core_logic.py         # Core model logic
├── kpi.py                # KPI calculation functions
├── model.py              # Main model class implementing CadcadModelProtocol
├── sir_config.yaml       # Example YAML configuration
└── README.md             # This file
```

## Key Components

- **params.py**: Defines model parameters, default values, and parameter ranges for optimization.
- **core_logic.py**: Contains the core model logic, independent of cadCAD or PSUU.
- **kpi.py**: Defines Key Performance Indicators (KPIs) that can be optimized by PSUU.
- **model.py**: Implements the `CadcadModelProtocol` for seamless integration with PSUU.
- **__main__.py**: Provides a CLI entry point for command-line execution.
- **sir_config.yaml**: Example YAML configuration for PSUU optimization.

## Integration Approaches

This template supports both integration approaches:

1. **Protocol Integration**: Using the `SIRModel` class directly in Python:

```python
from template.model import SIRModel
from psuu import PsuuExperiment

# Create model instance
model = SIRModel()

# Create experiment with model
experiment = PsuuExperiment(model=model)

# Run optimization
results = experiment.run()
```

2. **CLI Integration**: Using the command-line interface:

```python
from psuu import PsuuExperiment

# Create experiment with CLI
experiment = PsuuExperiment(
    simulation_command="python -m template",
    param_format="--{name} {value}",
    output_format="json"
)

# Run optimization
results = experiment.run()
```

## YAML Configuration

The `sir_config.yaml` file demonstrates how to configure PSUU for this model using YAML:

```yaml
model:
  class: "template.model.SIRModel"  # For Protocol integration
  
  # OR for CLI integration:
  # entry_point: "python -m template"
  # param_format: "--{name} {value}"
  # output_format: "json"
```

## Running the Model

### Directly from Python

```python
from template.model import SIRModel

model = SIRModel()
results = model.run({'beta': 0.3, 'gamma': 0.05, 'population': 1000})
print(results.kpis)
```

### Via Command Line

```bash
python -m template --beta 0.3 --gamma 0.05 --population 1000 --output sir_run
```

### Via PSUU with YAML Configuration

```bash
python -m psuu --config template/sir_config.yaml
```

## Customizing the Template

To create your own model based on this template:

1. Copy the template directory to your project
2. Modify the parameters in `params.py`
3. Update the state variables and logic in `core_logic.py`
4. Define your own KPIs in `kpi.py`
5. Adjust the model class in `model.py` as needed
6. Update the CLI in `__main__.py` to include your parameters

## License

This template is provided as part of the PSUU framework.
