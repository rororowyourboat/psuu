# Creating Custom Simulation Connectors

While PSUU provides a built-in `SimulationConnector` for interfacing with CLI-based simulation models, sometimes you may need to customize this connector to work with specific simulation frameworks or output formats.

This guide demonstrates how to create a custom simulation connector for the cadcad-sandbox SIR model.

## Understanding the Challenge

The cadcad-sandbox SIR model:
- Takes parameters via CLI (beta, gamma, population, etc.)
- Runs simulations using cadCAD
- Outputs results as pickle and JSON files
- Doesn't directly provide CSV output

Our PSUU package, by default:
- Expects simulation output as CSV or JSON data
- Directly processes DataFrame results for KPI calculations

## Custom Connector Implementation

Here's how to create a custom connector that bridges these differences:

```python
import os
import tempfile
import subprocess
import json
import pandas as pd
import numpy as np
from typing import Dict, Any
import time

from psuu.simulation_connector import SimulationConnector

class CadcadSimulationConnector(SimulationConnector):
    """
    Custom simulation connector for cadcad-sandbox that handles its specific output format.
    """
    
    def run_simulation(self, parameters: Dict[str, Any]) -> pd.DataFrame:
        """
        Run the simulation with the given parameters and return results.
        
        Args:
            parameters: Dictionary of parameter names and values
            
        Returns:
            DataFrame containing simulation results
        """
        # Convert any numpy types to native Python types
        cleaned_params = {}
        for key, value in parameters.items():
            if isinstance(value, np.integer):
                cleaned_params[key] = int(value)
            elif isinstance(value, np.floating):
                cleaned_params[key] = float(value)
            else:
                cleaned_params[key] = value
        
        cmd = self._build_command(cleaned_params)
        timestamp = time.strftime("%Y_%m_%d_%H_%M_%S")
        output_name = f"psuu_run_{timestamp}"
        
        # Add output parameter to command
        cmd = f"{cmd} --output {output_name}"
        
        # Run simulation
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                check=True,
                cwd=self.working_dir,
                env=os.environ.copy(),
                capture_output=True,
                text=True
            )
            
            # Find the latest simulation output files
            sim_dir = os.path.join(self.working_dir, "data", "simulations")
            files = [f for f in os.listdir(sim_dir) if f.endswith('.json') and output_name in f]
            
            if not files:
                raise FileNotFoundError(f"No output files found with name {output_name}")
            
            # Get the latest KPI file
            kpi_file = sorted(files)[-1]
            
            # Load KPI data
            with open(os.path.join(sim_dir, kpi_file), 'r') as f:
                kpi_data = json.load(f)
            
            # Convert KPI data to DataFrame for compatibility with our KPI functions
            # Create a synthetic DataFrame with just the KPI values
            peak = kpi_data['peak_infections']['mean']
            total = kpi_data['total_infections']['mean']
            duration = kpi_data['epidemic_duration']['mean']
            r0 = kpi_data['r0']['mean']
            
            df = pd.DataFrame({
                'timestep': [0],
                'I': [peak],         # Using peak as I value
                'S': [1000 - total], # Estimating S from total infections
                'R': [total],        # Using total as R value
                'duration': [duration],
                'r0': [r0]
            })
            
            return df
            
        except subprocess.CalledProcessError as e:
            print(f"Simulation failed with error: {e}")
            print(f"Stdout: {e.stdout}")
            print(f"Stderr: {e.stderr}")
            # Return empty DataFrame with expected columns
            return pd.DataFrame(columns=['timestep', 'I', 'S', 'R', 'duration', 'r0'])
```

## Using the Custom Connector

To use this custom connector in your optimization:

```python
from psuu import PsuuExperiment

# Create experiment with default connector
experiment = PsuuExperiment(
    simulation_command="python -m model",
    param_format="--{name} {value}",
    working_dir="/path/to/cadcad-sandbox"
)

# Replace with custom connector
experiment.simulation_connector = CadcadSimulationConnector(
    command="python -m model",
    param_format="--{name} {value}",
    working_dir="/path/to/cadcad-sandbox"
)

# Define KPI functions for the synthetic DataFrame
def peak_infections(df):
    return df['I'].iloc[0]  # Peak infections is stored directly in the I column

# Add KPIs and continue as normal
experiment.add_kpi("peak", function=peak_infections)
```

## Handling Type Conversion

When working with simulation outputs, you may encounter JSON serialization issues with NumPy types. Here's a utility function to convert them:

```python
def convert_numpy_types(obj):
    """Convert NumPy types to native Python types."""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, dict):
        return {k: convert_numpy_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    else:
        return obj
```

## Complete Example

See the complete example in the repository at `examples/sir_cadcad_optimization_final.py`.

This example shows:
1. How to create and use a custom simulation connector
2. How to define KPI functions for the connector's output
3. How to handle NumPy type conversion for JSON serialization
4. How to perform Bayesian optimization after random search
