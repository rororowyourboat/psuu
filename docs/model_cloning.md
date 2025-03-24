# Model Cloning and Management

PSUU provides functionality to easily clone and integrate with known simulation models. This feature helps you quickly set up and start using various simulation models without having to manually configure the connection.

## Available Commands

### Listing Available Models

To see which models are currently supported for automatic cloning:

```bash
psuu list-models
```

This will display all registered models with their descriptions and repository URLs.

### Cloning a Model

To clone a model and automatically configure PSUU to work with it:

```bash
psuu clone-model MODEL_NAME
```

For example:

```bash
psuu clone-model cadcad-sandbox
```

This will:
1. Clone the model's repository
2. Install its dependencies (if --no-install is not specified)
3. Generate a custom connector module if needed
4. Create a PSUU configuration file (psuu_config.yaml)
5. Generate an example script to run the model with PSUU

#### Options

- `--directory` or `-d`: Specify a directory to clone into (default: current directory)
- `--no-install`: Skip installing the model's dependencies

Example:

```bash
psuu clone-model cadcad-sandbox --directory models --no-install
```

### Using a Cloned Model

After cloning a model, you can immediately start optimizing its parameters:

1. **Using the CLI**:
   ```bash
   # Review and possibly edit the generated configuration
   cat psuu_config.yaml
   
   # Run the optimization
   psuu run
   ```

2. **Using the Example Script**:
   ```bash
   # Run the generated example script
   python run_MODEL_NAME.py
   ```

## Currently Supported Models

### cadcad-sandbox

A cadCAD-based SIR (Susceptible, Infected, Recovered) epidemic model.

- **Repository**: https://github.com/rororowyourboat/cadcad-sandbox
- **Description**: SIR epidemic simulation model using cadCAD
- **Parameters**:
  - `beta`: Transmission rate (range: 0.1-0.5)
  - `gamma`: Recovery rate (range: 0.01-0.1)
  - `population`: Population size (options: 1000, 5000)
- **KPIs**:
  - `peak`: Peak infections
  - `total`: Total infections
  - `duration`: Epidemic duration
  - `r0`: Basic reproduction number

## Custom Models

In the future, you'll be able to add your own models to the registry using:

```bash
psuu add-custom-model NAME REPO_URL [OPTIONS]
```

This feature is planned for an upcoming release.

## Advanced Usage

If you need more control over how a model is integrated with PSUU, you can:

1. Clone the model manually
2. Create a custom connector module (see [Custom Simulation Connectors](custom_connectors.md))
3. Configure PSUU to use your custom connector

Here's an example of doing this manually:

```python
from psuu import PsuuExperiment
from custom_connectors.my_model_connector import MyModelConnector

# Create experiment
experiment = PsuuExperiment(
    simulation_command="python -m my_model",
    working_dir="/path/to/my_model"
)

# Replace with custom connector
experiment.simulation_connector = MyModelConnector(
    command="python -m my_model",
    working_dir="/path/to/my_model"
)

# Configure as usual...
experiment.add_kpi(...)
experiment.set_parameter_space(...)
experiment.set_optimizer(...)
```

## Troubleshooting

### Model Not Found

If you get an "Unknown model" error, make sure the model name is correct and appears in the list from `psuu list-models`.

### Dependency Installation Issues

If you encounter issues with dependency installation, try:

1. Using the `--no-install` flag and manually installing dependencies
2. Running the installation in a clean virtual environment
3. Checking the model's documentation for specific installation requirements

### Custom Connector Errors

If there are issues with the generated custom connector:

1. Check the connector module in the `custom_connectors` directory
2. Review the model's documentation for any special requirements
3. Consider modifying the connector or creating your own custom connector
