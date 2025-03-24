#!/usr/bin/env python
"""
Example script for integrating cadCAD models with PSUU using the new protocol.

This script demonstrates how to adapt an existing cadCAD model to work with PSUU
using the new standardized protocols and formats.
"""

import os
import sys
import argparse
import pandas as pd
from typing import Dict, Any, List, Union, Callable, Optional

# Add project root to path if needed
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from psuu import (
    PsuuExperiment,
    PsuuConfig,
    CadcadModelProtocol,
    SimulationResults,
    RobustCadcadConnector
)


class CadcadModelWrapper(CadcadModelProtocol):
    """
    Wrapper for existing cadCAD models to adapt them to the new PSUU protocol.
    
    This class serves as an adapter between existing cadCAD models and the
    new standardized PSUU protocol interface.
    """
    
    def __init__(
        self, 
        model_path: str,
        entry_point: str = "run_model",
        parameter_space: Optional[Dict] = None,
        kpi_functions: Optional[Dict] = None
    ):
        """
        Initialize the cadCAD model wrapper.
        
        Args:
            model_path: Path to the cadCAD model module
            entry_point: Name of the function to run the model
            parameter_space: Optional parameter space definition
            kpi_functions: Optional KPI functions
        """
        self.model_path = model_path
        self.entry_point = entry_point
        self._parameter_space = parameter_space or {}
        self._kpi_functions = kpi_functions or {}
        
        # Import the model module
        sys.path.insert(0, os.path.dirname(model_path))
        module_name = os.path.basename(model_path).replace('.py', '')
        
        try:
            self.model_module = __import__(module_name)
            
            # Get the entry point function
            if hasattr(self.model_module, entry_point):
                self.model_function = getattr(self.model_module, entry_point)
            else:
                raise ImportError(f"Entry point '{entry_point}' not found in module '{module_name}'")
                
            # Auto-discover parameter space
            if not self._parameter_space and hasattr(self.model_module, "PARAMETER_RANGES"):
                self._parameter_space = self.model_module.PARAMETER_RANGES
                
            # Auto-discover KPI functions
            if not self._kpi_functions and hasattr(self.model_module, "KPI_FUNCTIONS"):
                self._kpi_functions = self.model_module.KPI_FUNCTIONS
                
        except ImportError as e:
            raise ImportError(f"Failed to import cadCAD model module: {e}")
    
    def run(self, params: Dict[str, Any], **kwargs) -> SimulationResults:
        """
        Run the cadCAD model with given parameters.
        
        Args:
            params: Dictionary of parameter values
            **kwargs: Additional simulation options
            
        Returns:
            SimulationResults object with simulation results
        """
        # Run the model using its entry point function
        try:
            # Call the model's entry point function
            results = self.model_function(params, **kwargs)
            
            # Convert results to SimulationResults if needed
            if isinstance(results, SimulationResults):
                return results
            elif isinstance(results, pd.DataFrame):
                # Calculate KPIs
                kpis = {}
                for kpi_name, kpi_func in self._kpi_functions.items():
                    if callable(kpi_func):
                        kpis[kpi_name] = kpi_func(results)
                    elif isinstance(kpi_func, dict) and callable(kpi_func.get('function')):
                        kpis[kpi_name] = kpi_func['function'](results)
                
                # Create metadata
                metadata = {
                    "model_path": self.model_path,
                    "entry_point": self.entry_point
                }
                
                # Create SimulationResults
                return SimulationResults(
                    time_series_data=results,
                    kpis=kpis,
                    metadata=metadata,
                    parameters=params
                )
            else:
                # Handle other return types (dict, tuple, etc.)
                raise ValueError(f"Unsupported result type from model function: {type(results)}")
                
        except Exception as e:
            print(f"Error running cadCAD model: {e}")
            # Return empty results
            return SimulationResults(
                time_series_data=pd.DataFrame(),
                kpis={},
                metadata={"error": str(e)},
                parameters=params
            )
    
    def get_parameter_space(self) -> Dict[str, Union[List, tuple, Dict]]:
        """
        Return the parameter space definition.
        
        Returns:
            Dictionary mapping parameter names to their valid ranges/values
        """
        return self._parameter_space
    
    def get_kpi_definitions(self) -> Dict[str, Union[Callable, Dict]]:
        """
        Return KPI calculation functions.
        
        Returns:
            Dictionary mapping KPI names to their calculation functions
        """
        return self._kpi_functions
    
    def get_cadcad_config(self) -> Dict[str, Any]:
        """
        Get cadCAD configuration.
        
        Returns:
            Dictionary with cadCAD configuration
        """
        # Try to get cadCAD config from the model module
        if hasattr(self.model_module, "CADCAD_CONFIG"):
            return self.model_module.CADCAD_CONFIG
        
        # Default config
        return {
            "model_path": self.model_path,
            "entry_point": self.entry_point
        }


def integrate_cadcad_model(model_path, config_path=None):
    """
    Integrate a cadCAD model with PSUU using the new protocol.
    
    Args:
        model_path: Path to the cadCAD model module
        config_path: Optional path to configuration file
    
    Returns:
        Wrapped model instance
    """
    # Define KPI functions for cadCAD
    kpi_functions = {
        "peak_infections": lambda df: df['I'].max(),
        "total_infections": lambda df: df['R'].iloc[-1],
        "epidemic_duration": lambda df: len(df)
    }
    
    # Define parameter space
    parameter_space = {
        "beta": (0.1, 0.5),
        "gamma": (0.01, 0.1),
        "population": [1000, 5000, 10000]
    }
    
    # Create wrapper
    model = CadcadModelWrapper(
        model_path=model_path,
        parameter_space=parameter_space,
        kpi_functions=kpi_functions
    )
    
    # Load configuration if provided
    if config_path:
        config = PsuuConfig(config_path)
        
        # Override parameter space and KPIs if in config
        param_config = config.get_parameters_config()
        if param_config:
            model._parameter_space = param_config
        
        kpi_config = config.get_kpis_config()
        if kpi_config:
            # Convert any function names to actual functions
            for kpi_name, kpi_def in kpi_config.items():
                if isinstance(kpi_def, dict) and 'function' in kpi_def:
                    func_name = kpi_def['function']
                    if func_name in kpi_functions:
                        kpi_def['function'] = kpi_functions[func_name]
            
            model._kpi_functions = kpi_config
    
    return model


def optimize_cadcad_model(model, method="random", iterations=10):
    """
    Run optimization on a cadCAD model.
    
    Args:
        model: CadcadModelWrapper instance
        method: Optimization method
        iterations: Number of iterations
        
    Returns:
        Optimization results
    """
    # Create experiment
    experiment = PsuuExperiment()
    
    # Create a model adapter function
    def model_adapter(params):
        """Adapter function to run the model and return a DataFrame."""
        results = model.run(params)
        return results.to_dataframe()
    
    # Set up the experiment to use the adapter function
    experiment.simulation_connector.run_simulation = model_adapter
    
    # Add KPIs from model
    kpi_defs = model.get_kpi_definitions()
    for kpi_name, kpi_def in kpi_defs.items():
        if isinstance(kpi_def, dict) and 'function' in kpi_def:
            experiment.add_kpi(kpi_name, function=kpi_def['function'])
        else:
            experiment.add_kpi(kpi_name, function=kpi_def)
    
    # Set parameter space from model
    experiment.set_parameter_space(model.get_parameter_space())
    
    # Configure optimizer
    experiment.set_optimizer(
        method=method,
        objective_name="peak_infections",
        maximize=False,
        num_iterations=iterations
    )
    
    # Run optimization
    print("\nRunning optimization...")
    return experiment.run(
        max_iterations=iterations,
        verbose=True,
        save_results="results/cadcad_integration/optimization"
    )


def main():
    """Main function to run the cadCAD integration example."""
    parser = argparse.ArgumentParser(description="Integrate cadCAD model with PSUU")
    parser.add_argument('--model', type=str, help='Path to cadCAD model module')
    parser.add_argument('--config', type=str, help='Path to configuration file')
    parser.add_argument('--optimize', action='store_true', help='Run optimization')
    parser.add_argument('--method', type=str, default='random', help='Optimization method')
    parser.add_argument('--iterations', type=int, default=10, help='Number of iterations')
    
    args = parser.parse_args()
    
    # Default to the cadcad-sandbox model if not specified
    model_path = args.model or os.path.join(project_root, "cadcad-sandbox/model/__main__.py")
    
    print(f"Integrating cadCAD model: {model_path}")
    
    # Create wrapped model
    model = integrate_cadcad_model(model_path, args.config)
    
    # Print model information
    print("\nModel Parameter Space:")
    for param, space in model.get_parameter_space().items():
        print(f"  {param}: {space}")
    
    print("\nModel KPIs:")
    for kpi, func in model.get_kpi_definitions().items():
        if isinstance(func, dict) and 'description' in func:
            print(f"  {kpi}: {func['description']}")
        else:
            print(f"  {kpi}")
    
    # Run a single simulation
    print("\nRunning single simulation...")
    results = model.run({
        "beta": 0.3,
        "gamma": 0.05,
        "population": 1000
    })
    
    # Print results
    if results.kpis:
        print("\nSimulation KPIs:")
        for kpi, value in results.kpis.items():
            print(f"  {kpi}: {value}")
    
    # Save results
    os.makedirs("results/cadcad_integration", exist_ok=True)
    saved_files = results.save("results/cadcad_integration/single_run", formats=["csv", "json"])
    
    print("\nResults saved to:")
    for fmt, path in saved_files.items():
        print(f"  {fmt}: {path}")
    
    # Run optimization if requested
    if args.optimize:
        opt_results = optimize_cadcad_model(
            model, 
            method=args.method,
            iterations=args.iterations
        )
        
        # Print optimization results
        print("\nOptimization Results:")
        print(f"Best parameters: {opt_results.best_parameters}")
        print("\nBest KPIs:")
        for kpi_name, kpi_value in opt_results.best_kpis.items():
            print(f"  {kpi_name}: {kpi_value}")


if __name__ == "__main__":
    main()
