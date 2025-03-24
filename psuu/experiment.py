"""
Experiment Module

This module provides the main interface for setting up and running parameter
optimization experiments.
"""

from typing import Dict, Any, List, Tuple, Optional, Union, Callable
import os
import time
import json
import yaml
import pandas as pd
import numpy as np

from .simulation_connector import SimulationConnector
from .data_aggregator import DataAggregator, KPICalculator
from .optimizers import AVAILABLE_OPTIMIZERS, Optimizer


# Custom JSON encoder to handle NumPy types
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)


def convert_numpy_types(obj: Any) -> Any:
    """Convert NumPy types to native Python types."""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {k: convert_numpy_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    else:
        return obj


class PsuuExperiment:
    """
    Main class for setting up and running parameter optimization experiments.
    """
    
    def __init__(
        self,
        simulation_command: str,
        param_format: str = "--{name} {value}",
        output_format: str = "csv",
        output_file: Optional[str] = None,
        working_dir: Optional[str] = None,
    ):
        """
        Initialize a new experiment.
        
        Args:
            simulation_command: Command to run the simulation
            param_format: Format string for parameter arguments
            output_format: Format of simulation output ('csv' or 'json')
            output_file: Path to output file (if None, stdout is used)
            working_dir: Working directory for the simulation
        """
        self.simulation_connector = SimulationConnector(
            command=simulation_command,
            param_format=param_format,
            output_format=output_format,
            output_file=output_file,
            working_dir=working_dir,
        )
        
        self.kpi_calculator = KPICalculator()
        self.data_aggregator = DataAggregator(self.kpi_calculator)
        
        self.parameter_space: Dict[str, Union[List[Any], Tuple[float, float]]] = {}
        self.optimizer: Optional[Optimizer] = None
        self.objective_name: Optional[str] = None
        self.maximize: bool = True
    
    def add_kpi(
        self, 
        name: str, 
        function: Optional[Callable[[pd.DataFrame], float]] = None,
        column: Optional[str] = None,
        operation: Optional[str] = None,
        filter_condition: Optional[str] = None,
    ) -> None:
        """
        Add a KPI to calculate from simulation results.
        
        Args:
            name: Name of the KPI
            function: Custom function to calculate the KPI (takes DataFrame, returns value)
            column: Column name for simple KPI calculation
            operation: Operation for simple KPI ('max', 'min', 'mean', 'sum', etc.)
            filter_condition: Optional condition to filter the DataFrame
            
        Raises:
            ValueError: If neither function nor column/operation are provided
        """
        if function is not None:
            self.kpi_calculator.add_kpi_function(name, function)
        elif column is not None and operation is not None:
            self.kpi_calculator.add_simple_kpi(name, column, operation, filter_condition)
        else:
            raise ValueError(
                "Must provide either a custom function or column/operation combination"
            )
    
    def set_parameter_space(
        self, 
        parameter_space: Dict[str, Union[List[Any], Tuple[float, float]]]
    ) -> None:
        """
        Set the parameter space to explore.
        
        Args:
            parameter_space: Dictionary mapping parameter names to their possible values
                For continuous parameters, provide a tuple of (min, max)
                For discrete parameters, provide a list of possible values
        """
        self.parameter_space = parameter_space
    
    def set_optimizer(
        self,
        method: str = "random",
        objective_name: Optional[str] = None,
        maximize: bool = True,
        **kwargs
    ) -> None:
        """
        Set the optimization method.
        
        Args:
            method: Optimization method ('grid', 'random', 'bayesian')
            objective_name: Name of the KPI to optimize
            maximize: Whether to maximize (True) or minimize (False) the objective
            **kwargs: Additional arguments for the specific optimizer
            
        Raises:
            ValueError: If method is not supported or parameter space is not set
        """
        if not self.parameter_space:
            raise ValueError("Parameter space must be set before configuring optimizer")
        
        if method not in AVAILABLE_OPTIMIZERS:
            raise ValueError(
                f"Unsupported optimization method: {method}. "
                f"Available methods: {', '.join(AVAILABLE_OPTIMIZERS.keys())}"
            )
        
        self.objective_name = objective_name
        self.maximize = maximize
        
        # Initialize the optimizer
        optimizer_class = AVAILABLE_OPTIMIZERS[method]
        self.optimizer = optimizer_class(
            parameter_space=self.parameter_space,
            objective_name=objective_name,
            maximize=maximize,
            **kwargs
        )
    
    def run(
        self,
        max_iterations: Optional[int] = None,
        verbose: bool = True,
        save_results: Optional[str] = None,
    ) -> "ExperimentResults":
        """
        Run the parameter optimization experiment.
        
        Args:
            max_iterations: Maximum number of iterations (None for optimizer default)
            verbose: Whether to print progress information
            save_results: Path to save results (None to skip saving)
            
        Returns:
            ExperimentResults object containing optimization results
            
        Raises:
            ValueError: If optimizer or objective KPI is not set
        """
        if self.optimizer is None:
            raise ValueError("Optimizer must be set before running experiment")
        
        if self.objective_name is None:
            raise ValueError("Objective KPI must be set before running experiment")
        
        iteration = 0
        start_time = time.time()
        
        if verbose:
            print(f"Starting parameter optimization experiment")
            print(f"Objective: {'Maximize' if self.maximize else 'Minimize'} {self.objective_name}")
        
        while not self.optimizer.is_finished():
            if max_iterations is not None and iteration >= max_iterations:
                if verbose:
                    print(f"Reached maximum iterations ({max_iterations})")
                break
            
            # Get next parameter set to evaluate
            parameters = self.optimizer.suggest()
            
            if verbose:
                params_str = ", ".join(f"{k}={v:.4g}" if isinstance(v, float) else f"{k}={v}" 
                                      for k, v in parameters.items())
                print(f"Iteration {iteration + 1}: Evaluating parameters {params_str}")
            
            # Run simulation with these parameters
            try:
                result_df = self.simulation_connector.run_simulation(parameters)
                
                # Calculate KPIs
                kpis = self.data_aggregator.add_simulation_result(parameters, result_df)
                
                # Update optimizer with result
                objective_value = kpis[self.objective_name]
                self.optimizer.update(parameters, objective_value)
                
                if verbose:
                    print(f"  Result: {self.objective_name} = {objective_value:.6g}")
            
            except Exception as e:
                if verbose:
                    print(f"  Error evaluating parameters: {e}")
            
            iteration += 1
        
        # Get the best result
        best_result = self.data_aggregator.get_best_result(
            self.objective_name, self.maximize
        )
        
        elapsed_time = time.time() - start_time
        
        if verbose:
            print(f"\nOptimization completed in {elapsed_time:.2f} seconds")
            print(f"Best parameters: {best_result['parameters']}")
            print(f"Best {self.objective_name}: {best_result['kpis'][self.objective_name]:.6g}")
        
        # Create results object
        results = ExperimentResults(
            experiment=self,
            iterations=iteration,
            elapsed_time=elapsed_time,
            best_result=best_result,
            all_results=self.data_aggregator.get_all_results(),
            summary=self.data_aggregator.summarize_results(),
        )
        
        # Save results if requested
        if save_results:
            results.save(save_results)
        
        return results


class ExperimentResults:
    """
    Container for experiment results.
    """
    
    def __init__(
        self,
        experiment: PsuuExperiment,
        iterations: int,
        elapsed_time: float,
        best_result: Dict[str, Any],
        all_results: pd.DataFrame,
        summary: Dict[str, Dict[str, float]],
    ):
        """
        Initialize results container.
        
        Args:
            experiment: Reference to the experiment
            iterations: Number of iterations performed
            elapsed_time: Total elapsed time (seconds)
            best_result: Best parameter set and KPIs
            all_results: DataFrame with all results
            summary: Summary statistics for KPIs
        """
        self.experiment = experiment
        self.iterations = iterations
        self.elapsed_time = elapsed_time
        self.best_result = best_result
        self.all_results = all_results
        self.summary = summary
    
    @property
    def best_parameters(self) -> Dict[str, Any]:
        """Get the best parameters."""
        return self.best_result["parameters"]
    
    @property
    def best_kpis(self) -> Dict[str, float]:
        """Get the KPIs for the best parameters."""
        return self.best_result["kpis"]
    
    def to_csv(self, path: str) -> None:
        """
        Save all results to a CSV file.
        
        Args:
            path: Path to save the CSV file
        """
        self.all_results.to_csv(path, index=False)
    
    def to_json(self, path: str) -> None:
        """
        Save results to a JSON file.
        
        Args:
            path: Path to save the JSON file
        """
        # Convert results to serializable format
        results_dict = {
            "iterations": self.iterations,
            "elapsed_time": self.elapsed_time,
            "best_parameters": convert_numpy_types(self.best_parameters),
            "best_kpis": convert_numpy_types(self.best_kpis),
            "summary": convert_numpy_types(self.summary),
        }
        
        with open(path, "w") as f:
            json.dump(results_dict, f, indent=2, cls=NumpyEncoder)
    
    def save(self, base_path: str) -> None:
        """
        Save results to multiple formats.
        
        Args:
            base_path: Base path for saving results
        """
        # Create directory if needed
        os.makedirs(os.path.dirname(base_path) or ".", exist_ok=True)
        
        # Save to CSV
        self.to_csv(f"{base_path}.csv")
        
        # Save to JSON
        self.to_json(f"{base_path}.json")
        
        # Save full details to YAML
        results_dict = {
            "iterations": self.iterations,
            "elapsed_time": self.elapsed_time,
            "best_parameters": convert_numpy_types(self.best_parameters),
            "best_kpis": convert_numpy_types(self.best_kpis),
            "summary": convert_numpy_types(self.summary),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        
        with open(f"{base_path}.yaml", "w") as f:
            yaml.dump(results_dict, f, default_flow_style=False)


def quick_optimize(
    command: str,
    params: Dict[str, Union[List[Any], Tuple[float, float]]],
    kpi_column: str,
    objective: str = "max",
    iterations: int = 20,
    **kwargs
) -> ExperimentResults:
    """
    Quickly set up and run an optimization experiment.
    
    Args:
        command: Simulation command
        params: Parameter space to explore
        kpi_column: Column name for the KPI
        objective: 'max' or 'min'
        iterations: Number of iterations
        **kwargs: Additional arguments for SimulationConnector
        
    Returns:
        ExperimentResults with optimization results
    """
    # Create experiment
    experiment = PsuuExperiment(command, **kwargs)
    
    # Add KPI
    experiment.add_kpi(
        name="objective",
        column=kpi_column,
        operation="max" if objective == "max" else "min"
    )
    
    # Set parameter space
    experiment.set_parameter_space(params)
    
    # Configure optimizer (use random by default)
    experiment.set_optimizer(
        method="random",
        objective_name="objective",
        maximize=objective == "max",
        num_iterations=iterations
    )
    
    # Run optimization
    return experiment.run(verbose=True)
