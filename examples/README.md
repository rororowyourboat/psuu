# PSUU Examples

This directory contains examples demonstrating how to use the PSUU package for parameter optimization under uncertainty.

## Directory Structure

- **basic_usage/**: Simple examples demonstrating the core functionality
- **cadcad_integration/**: Examples integrating with cadCAD simulation models
- **cli_usage/**: Examples showing how to use the command-line interface

## Basic Usage Examples

- **simple_sir_optimization.py**: A simple example showing how to optimize parameters for an SIR epidemic model using the Python API

## cadCAD Integration Examples

- **sir_model_optimization.py**: Demonstrates how to create a custom SimulationConnector to integrate with the cadcad-sandbox SIR model, showcasing both random search and Bayesian optimization

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

### CLI Usage

```bash
# Make the script executable
chmod +x examples/cli_usage/basic_cli_example.sh

# Run the script
./examples/cli_usage/basic_cli_example.sh
```

## Creating Your Own Examples

The PSUU package is designed to be flexible and can be integrated with various simulation models. To create your own examples:

1. Define your simulation command and parameter format
2. Create KPI functions to evaluate simulation outputs
3. Define the parameter space to explore
4. Choose an optimization algorithm
5. Run the optimization and analyze the results

See the existing examples for inspiration and refer to the [documentation](../docs/) for more details.
