# PSUU Examples

This directory contains examples demonstrating how to use the PSUU package for parameter optimization under uncertainty.

## Directory Structure

- **basic_usage/**: Simple examples demonstrating the core functionality
- **cadcad_integration/**: Examples integrating with cadCAD simulation models
- **cli_usage/**: Examples showing how to use the command-line interface
- **protocol_example/**: Examples demonstrating the new protocol-based integration
- **cadcad_integration.py**: Comprehensive example of integrating cadCAD models using the new protocol

## Basic Usage Examples

- **simple_sir_optimization.py**: A simple example showing how to optimize parameters for an SIR epidemic model using the Python API

## cadCAD Integration Examples

- **sir_model_optimization.py**: Demonstrates how to create a custom SimulationConnector to integrate with the cadcad-sandbox SIR model, showcasing both random search and Bayesian optimization

## Protocol-Based Examples

- **protocol_example/sir_model.py**: Example implementation of a model using the CadcadModelProtocol
- **protocol_example/run_sir_model.py**: Script demonstrating different ways to use the protocol-based model
- **protocol_example/sir_config.yaml**: Example configuration file for the protocol-based model
- **cadcad_integration.py**: Script showing how to wrap existing cadCAD models to use with the new protocol

## CLI Usage Examples

- **basic_cli_example.sh**: A shell script demonstrating how to use the PSUU command-line interface

## Running the Examples

### Basic Usage

```bash
# Activate virtual environment
source .venv/bin/activate

# Run simple SIR optimization
python examples/basic_usage/simple_sir_optimization.py
```

### cadCAD Integration

To run the cadCAD integration examples, you'll need to install the cadcad-sandbox package:

```bash
# Clone the repository
git clone https://github.com/rororowyourboat/cadcad-sandbox.git

# Install the package
cd cadcad-sandbox
pip install -e .

# Run the example
cd ../psuu
python examples/cadcad_integration/sir_model_optimization.py
```

### Protocol-Based Examples

```bash
# Run the SIR model example
python examples/protocol_example/run_sir_model.py

# Run specific parts of the example
python examples/protocol_example/run_sir_model.py --direct
python examples/protocol_example/run_sir_model.py --config
python examples/protocol_example/run_sir_model.py --optimize

# Run the cadCAD integration example
python examples/cadcad_integration.py
```

### CLI Usage

```bash
# Make the script executable
chmod +x examples/cli_usage/basic_cli_example.sh

# Run the script
./examples/cli_usage/basic_cli_example.sh
```

## Using the New Protocol Interface

The new protocol interface provides a standardized way to integrate models with PSUU:

1. **Implement the Protocol**: Have your model implement the `CadcadModelProtocol`
2. **Return StandardResults**: Ensure simulations return results in the `SimulationResults` format
3. **Define Configuration**: Create configuration files for your models
4. **Use Robust Connectors**: Employ the `RobustCadcadConnector` for enhanced error handling

See the protocol_example directory for detailed examples.

## Creating Your Own Examples

The PSUU package is designed to be flexible and can be integrated with various simulation models. To create your own examples:

1. Define your simulation command and parameter format
2. Create KPI functions to evaluate simulation outputs
3. Define the parameter space to explore
4. Choose an optimization algorithm
5. Run the optimization and analyze the results

See the existing examples for inspiration and refer to the [documentation](../docs/) for more details.
