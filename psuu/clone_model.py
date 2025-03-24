"""
Clone Model Module

This module provides functionality to clone simulation models from GitHub
and automatically configure PSUU to work with them.
"""

import os
import sys
import subprocess
import yaml
import json
import importlib.util
from typing import Optional, Dict, Any, List, Tuple
import tempfile
import shutil


# Registry of known simulation models with their connection details
KNOWN_MODELS = {
    "cadcad-sandbox": {
        "repo": "https://github.com/rororowyourboat/cadcad-sandbox.git",
        "main_command": "python -m model",
        "param_format": "--{name} {value}",
        "output_format": "json",
        "description": "SIR epidemic simulation model using cadCAD",
        "default_params": {
            "beta": (0.1, 0.5),
            "gamma": (0.01, 0.1),
            "population": [1000, 5000]
        },
        "default_kpis": {
            "peak": {"type": "custom", "function": "peak_infections"},
            "total": {"type": "custom", "function": "total_infections"},
            "duration": {"type": "custom", "function": "epidemic_duration"},
            "r0": {"type": "custom", "function": "calculate_r0"}
        },
        "connector_type": "cadcad",
        "connector_module": "psuu.custom_connectors.cadcad_connector",
        "dependencies": ["cadCAD==0.5.3"]
    },
    # Add more models here as they become supported
}


def clone_repo(repo_url: str, target_dir: Optional[str] = None) -> str:
    """
    Clone a Git repository.
    
    Args:
        repo_url: URL of the repository to clone
        target_dir: Directory to clone into (optional)
        
    Returns:
        Path to the cloned repository
    
    Raises:
        subprocess.CalledProcessError: If the clone fails
    """
    if target_dir:
        # Make sure the target directory exists
        os.makedirs(target_dir, exist_ok=True)
        clone_path = os.path.join(target_dir, os.path.basename(repo_url).replace('.git', ''))
        
        # Check if directory already exists
        if os.path.exists(clone_path):
            print(f"Directory already exists: {clone_path}")
            return clone_path
        
        # Clone to the specified directory
        subprocess.run(
            ["git", "clone", repo_url, clone_path],
            check=True,
            capture_output=True,
            text=True
        )
    else:
        # Clone to current directory
        clone_path = os.path.basename(repo_url).replace('.git', '')
        
        # Check if directory already exists
        if os.path.exists(clone_path):
            print(f"Directory already exists: {clone_path}")
            return clone_path
        
        # Clone to current directory
        subprocess.run(
            ["git", "clone", repo_url],
            check=True,
            capture_output=True,
            text=True
        )
    
    return clone_path


def install_dependencies(repo_path: str, model_name: str = None) -> None:
    """
    Install dependencies for the cloned repository.
    
    Args:
        repo_path: Path to the cloned repository
        model_name: Name of the model (to check for specific dependencies)
        
    Raises:
        subprocess.CalledProcessError: If installation fails
    """
    # Install specific dependencies if provided in registry
    if model_name and model_name in KNOWN_MODELS and "dependencies" in KNOWN_MODELS[model_name]:
        print(f"Installing specific dependencies for {model_name}...")
        for dependency in KNOWN_MODELS[model_name]["dependencies"]:
            subprocess.run(
                ["pip", "install", dependency],
                check=True,
                capture_output=True,
                text=True
            )
    
    # Check for requirements.txt
    req_file = os.path.join(repo_path, "requirements.txt")
    if os.path.exists(req_file):
        print(f"Installing dependencies from requirements.txt...")
        subprocess.run(
            ["pip", "install", "-r", req_file],
            check=True,
            capture_output=True,
            text=True
        )
        return
    
    # Check for setup.py
    setup_file = os.path.join(repo_path, "setup.py")
    if os.path.exists(setup_file):
        print(f"Installing package in development mode...")
        subprocess.run(
            ["pip", "install", "-e", repo_path],
            check=True,
            capture_output=True,
            text=True
        )
        return
    
    # Check for pyproject.toml
    pyproject_file = os.path.join(repo_path, "pyproject.toml")
    if os.path.exists(pyproject_file):
        print(f"Installing package from pyproject.toml...")
        subprocess.run(
            ["pip", "install", "-e", repo_path],
            check=True,
            capture_output=True,
            text=True
        )
        return
    
    print("No recognized dependency files found. Skipping dependency installation.")


def generate_custom_connector(model_name: str, repo_path: str) -> Tuple[str, str]:
    """
    Generate a custom connector module for the model.
    
    Args:
        model_name: Name of the model
        repo_path: Path to the cloned repository
    
    Returns:
        Tuple of (module_path, module_name)
    """
    if model_name not in KNOWN_MODELS:
        raise ValueError(f"Unknown model: {model_name}")
    
    # Get connector module info
    model_info = KNOWN_MODELS[model_name]
    connector_module = model_info.get("connector_module")
    
    # If connector_module is specified and already exists, just return it
    if connector_module:
        module_name = connector_module.split(".")[-1]
        package_parts = connector_module.split(".")[:-1]
        package_path = os.path.join(*package_parts)
        connector_path = os.path.join(package_path, f"{module_name}.py")
        
        # Return the path relative to the current directory
        base_dir = os.getcwd()
        if os.path.isabs(connector_path):
            rel_path = os.path.relpath(connector_path, base_dir)
        else:
            rel_path = connector_path
            
        return rel_path, connector_module
    
    # Otherwise, we need to generate it
    connector_type = model_info.get("connector_type", "generic")
    
    if connector_type == "cadcad":
        # Use the existing connector in the psuu package
        return "psuu/custom_connectors/cadcad_connector.py", "psuu.custom_connectors.cadcad_connector"
    else:
        # Generic connector - create a custom one
        connectors_dir = os.path.join(os.getcwd(), "psuu", "custom_connectors")
        os.makedirs(connectors_dir, exist_ok=True)
        
        # Initialize __init__.py if it doesn't exist
        init_file = os.path.join(connectors_dir, "__init__.py")
        if not os.path.exists(init_file):
            with open(init_file, "w") as f:
                f.write('"""Custom connector modules for PSUU."""\n')
        
        connector_path = os.path.join(connectors_dir, f"{model_name}_connector.py")
        
        # Only create if it doesn't exist
        if not os.path.exists(connector_path):
            with open(connector_path, "w") as f:
                f.write(f'''"""
{model_name.capitalize()} Simulation Connector for PSUU.

This module provides a custom connector for {model_name}.
"""

import os
import subprocess
import pandas as pd
from typing import Dict, Any

from psuu.simulation_connector import SimulationConnector


class {model_name.capitalize().replace('-', '')}Connector(SimulationConnector):
    """
    Custom simulation connector for {model_name}.
    """
    
    def run_simulation(self, parameters: Dict[str, Any]) -> pd.DataFrame:
        """
        Run the simulation with the given parameters and return results.
        
        Args:
            parameters: Dictionary of parameter names and values
            
        Returns:
            DataFrame containing simulation results
        """
        cmd = self._build_command(parameters)
        
        # Run the command
        result = subprocess.run(
            cmd,
            shell=True,
            check=True,
            cwd=self.working_dir,
            capture_output=True,
            text=True
        )
        
        # Process output based on the format (CSV by default)
        if self.output_file:
            # Read from output file
            return pd.read_csv(os.path.join(self.working_dir, self.output_file))
        else:
            # Read from stdout
            with tempfile.NamedTemporaryFile(mode='w+', suffix='.csv', delete=False) as temp_file:
                temp_file.write(result.stdout)
                temp_file_path = temp_file.name
            
            try:
                return pd.read_csv(temp_file_path)
            finally:
                os.unlink(temp_file_path)
''')
        
        module_name = f"psuu.custom_connectors.{model_name}_connector"
        return connector_path, module_name


def create_kpi_functions(model_name: str) -> Dict[str, Any]:
    """
    Create KPI functions configuration for the model.
    
    Args:
        model_name: Name of the model
        
    Returns:
        Dictionary of KPI configurations
    """
    if model_name not in KNOWN_MODELS:
        # Generic KPIs
        return {}
    
    model_info = KNOWN_MODELS[model_name]
    default_kpis = model_info.get("default_kpis", {})
    
    # Process KPIs
    kpi_config = {}
    
    for kpi_name, kpi_info in default_kpis.items():
        if kpi_info.get("type") == "custom":
            # Get connector module name from model info
            connector_module = model_info.get("connector_module", f"psuu.custom_connectors.{model_name}_connector")
            kpi_config[kpi_name] = {
                "type": "custom",
                "module": connector_module,
                "function": kpi_info.get("function")
            }
        else:
            # Simple KPI
            kpi_config[kpi_name] = {
                "column": kpi_info.get("column", kpi_name),
                "operation": kpi_info.get("operation", "max")
            }
    
    return kpi_config


def configure_psuu(model_name: str, repo_path: str) -> None:
    """
    Configure PSUU to work with the cloned model.
    
    Args:
        model_name: Name of the model
        repo_path: Path to the cloned repository
    """
    # Create default configuration
    config = {
        "simulation": {
            "command": KNOWN_MODELS.get(model_name, {}).get("main_command", "python -m model"),
            "param_format": KNOWN_MODELS.get(model_name, {}).get("param_format", "--{name} {value}"),
            "output_format": KNOWN_MODELS.get(model_name, {}).get("output_format", "csv"),
            "output_file": None,
            "working_dir": repo_path,
        },
        "parameters": {},
        "kpis": {},
        "optimizer": {
            "method": "random",
            "objective": None,
            "maximize": False,
            "iterations": 20,
        }
    }
    
    # Add default parameters if available
    if model_name in KNOWN_MODELS and "default_params" in KNOWN_MODELS[model_name]:
        for param_name, param_value in KNOWN_MODELS[model_name]["default_params"].items():
            if isinstance(param_value, tuple) and len(param_value) == 2:
                config["parameters"][param_name] = list(param_value)
            else:
                config["parameters"][param_name] = param_value
    
    # Add KPIs
    kpi_config = create_kpi_functions(model_name)
    config["kpis"] = kpi_config
    
    # If there are KPIs, set the first one as the objective
    if kpi_config:
        first_kpi = next(iter(kpi_config.keys()))
        config["optimizer"]["objective"] = first_kpi
        # Determine if we should maximize or minimize
        if "peak" in first_kpi or "duration" in first_kpi:
            config["optimizer"]["maximize"] = False
        else:
            config["optimizer"]["maximize"] = True
    
    # Write configuration file
    with open("psuu_config.yaml", "w") as f:
        yaml.dump(config, f, default_flow_style=False)
    
    print(f"Created PSUU configuration for {model_name} in psuu_config.yaml")


def generate_example_script(model_name: str, repo_path: str) -> str:
    """
    Generate an example script to run the model with PSUU.
    
    Args:
        model_name: Name of the model
        repo_path: Path to the cloned repository
        
    Returns:
        Path to the generated script
    """
    script_path = f"run_{model_name.replace('-', '_')}.py"
    
    # Get connector module info
    connector_module = KNOWN_MODELS.get(model_name, {}).get("connector_module", "")
    connector_class = None
    
    if connector_module:
        if "." in connector_module:
            module_name = connector_module.split(".")[-1]
            
            if module_name == "cadcad_connector":
                connector_class = "CadcadSimulationConnector"
            else:
                connector_class = f"{model_name.capitalize().replace('-', '')}Connector"
    
    # Create the script
    with open(script_path, "w") as f:
        f.write(f'''#!/usr/bin/env python
"""
Example script to run {model_name} with PSUU.

This script demonstrates how to use PSUU to optimize parameters for {model_name}.
"""

import os
import sys
import pandas as pd
from psuu import PsuuExperiment

''')
        
        # Import custom connector if available
        if connector_module and connector_class:
            f.write(f'from {connector_module} import {connector_class}\n')
            f.write(f'from {connector_module} import peak_infections, total_infections, epidemic_duration, calculate_r0\n\n')
        
        f.write(f'''
def main():
    """Run optimization for {model_name}."""
    print("PSUU - {model_name.capitalize()} Parameter Optimization")
    print("=" * 50)
    
    # Create experiment
    experiment = PsuuExperiment(
        simulation_command="{KNOWN_MODELS.get(model_name, {}).get("main_command", "python -m model")}",
        param_format="{KNOWN_MODELS.get(model_name, {}).get("param_format", "--{name} {value}")}",
        output_format="{KNOWN_MODELS.get(model_name, {}).get("output_format", "csv")}",
        working_dir="{repo_path}"
    )
    
''')
        
        # Add custom connector if available
        if connector_module and connector_class:
            f.write(f'''    # Replace default connector with custom connector
    experiment.simulation_connector = {connector_class}(
        command="{KNOWN_MODELS.get(model_name, {}).get("main_command", "python -m model")}",
        param_format="{KNOWN_MODELS.get(model_name, {}).get("param_format", "--{name} {value}")}",
        working_dir="{repo_path}"
    )
    
''')
        
        # Add KPIs
        if model_name in KNOWN_MODELS and "default_kpis" in KNOWN_MODELS[model_name]:
            f.write("    # Add KPIs\n")
            
            for kpi_name, kpi_info in KNOWN_MODELS[model_name]["default_kpis"].items():
                if kpi_info.get("type") == "custom":
                    f.write(f'    experiment.add_kpi("{kpi_name}", function={kpi_info.get("function")})\n')
                else:
                    f.write(f'    experiment.add_kpi("{kpi_name}", column="{kpi_info.get("column", kpi_name)}", operation="{kpi_info.get("operation", "max")}")\n')
            
            f.write("\n")
        
        # Add parameter space
        if model_name in KNOWN_MODELS and "default_params" in KNOWN_MODELS[model_name]:
            f.write("    # Set parameter space\n")
            f.write("    experiment.set_parameter_space({\n")
            
            for param_name, param_value in KNOWN_MODELS[model_name]["default_params"].items():
                if isinstance(param_value, tuple) and len(param_value) == 2:
                    f.write(f'        "{param_name}": ({param_value[0]}, {param_value[1]}),\n')
                elif isinstance(param_value, list):
                    f.write(f'        "{param_name}": {param_value},\n')
                else:
                    f.write(f'        "{param_name}": {param_value},\n')
            
            f.write("    })\n\n")
        
        # Configure optimizer
        if model_name in KNOWN_MODELS and "default_kpis" in KNOWN_MODELS[model_name]:
            first_kpi = next(iter(KNOWN_MODELS[model_name]["default_kpis"].keys()))
            maximize = "True" if "peak" not in first_kpi and "duration" not in first_kpi else "False"
            
            f.write("    # Configure optimizer\n")
            f.write("    experiment.set_optimizer(\n")
            f.write('        method="random",\n')
            f.write(f'        objective_name="{first_kpi}",\n')
            f.write(f'        maximize={maximize},\n')
            f.write('        num_iterations=20\n')
            f.write("    )\n\n")
        
        # Run optimization
        f.write("    # Run optimization\n")
        f.write('    results = experiment.run(verbose=True, save_results="results/{model_name}_optimization")\n\n')
        
        # Print results
        f.write("    # Print results\n")
        f.write('    print("\\nOptimization Results:")\n')
        f.write('    print(f"Best parameters: {results.best_parameters}")\n')
        
        if model_name in KNOWN_MODELS and "default_kpis" in KNOWN_MODELS[model_name]:
            for kpi_name in KNOWN_MODELS[model_name]["default_kpis"].keys():
                f.write(f'    print(f"Best {kpi_name}: {{results.best_kpis[\'{kpi_name}\']:.2f}}")\n')
        
        f.write('''

if __name__ == "__main__":
    main()
''')
    
    # Make the script executable
    os.chmod(script_path, 0o755)
    return script_path


def clone_model(model_name: str, target_dir: Optional[str] = None, install: bool = True) -> None:
    """
    Clone and configure a simulation model.
    
    Args:
        model_name: Name of the model to clone
        target_dir: Directory to clone into (optional)
        install: Whether to install dependencies (default: True)
        
    Raises:
        ValueError: If the model is unknown
    """
    # Check if model is known
    if model_name not in KNOWN_MODELS:
        known_models = ", ".join(KNOWN_MODELS.keys())
        raise ValueError(f"Unknown model: {model_name}. Known models: {known_models}")
    
    repo_url = KNOWN_MODELS[model_name]["repo"]
    print(f"Cloning {model_name} from {repo_url}...")
    
    # Clone repository
    repo_path = clone_repo(repo_url, target_dir)
    print(f"Cloned {model_name} to {repo_path}")
    
    # Install dependencies if requested
    if install:
        try:
            install_dependencies(repo_path, model_name)
            print(f"Installed dependencies for {model_name}")
        except subprocess.CalledProcessError as e:
            print(f"Error installing dependencies: {e}")
            print("You may need to manually install dependencies.")
    
    # Generate custom connector
    connector_path, connector_module = generate_custom_connector(model_name, repo_path)
    print(f"Generated custom connector at {connector_path}")
    
    # Configure PSUU
    configure_psuu(model_name, repo_path)
    
    # Generate example script
    script_path = generate_example_script(model_name, repo_path)
    print(f"Generated example script at {script_path}")
    
    print(f"\nSuccessfully set up {model_name}!")
    print(f"You can now run optimization with:")
    print(f"  psuu run")
    print(f"Or use the example script:")
    print(f"  python {script_path}")


def list_available_models() -> None:
    """List all available models that can be cloned."""
    print("Available models:")
    print("=" * 50)
    
    for name, info in KNOWN_MODELS.items():
        print(f"- {name}")
        print(f"  Repository: {info['repo']}")
        print(f"  Description: {info.get('description', 'No description')}")
        print(f"  Command: {info.get('main_command', 'python -m model')}")
        if "dependencies" in info:
            print(f"  Dependencies: {', '.join(info['dependencies'])}")
        print()
