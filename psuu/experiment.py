"""
Experiment Module

This module provides the main interface for setting up and running parameter
optimization experiments with PSUU.
"""

from typing import Dict, Any, List, Tuple, Optional, Union, Callable, Type
import os
import time
import json
import yaml
import pandas as pd
import numpy as np
import logging

from .simulation_connector import SimulationConnector
from .data_aggregator import DataAggregator, KPICalculator
from .optimizers import AVAILABLE_OPTIMIZERS, Optimizer
from .protocols.model_protocol import ModelProtocol
from .results import SimulationResults, convert_numpy_types

# Set up logging
logger = logging.getLogger(__name__)

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


class PsuuExperiment:
    """
    Main class for setting up and running parameter optimization experiments.
    
    This class supports two integration modes:
    1. Protocol Integration: Using a model class implementing ModelProtocol
    2. CLI Integration: Using a command-line interface via SimulationConnector
    """
    
    def __init__(
        self,
        model: Optional[ModelProtocol] = None,
        simulation_command: Optional[str] = None,
        param_format: str = "--{name} {value}",
        output_format: str = "csv",
        output_file: Optional[str] = None,
        working_dir: Optional[str] = None,
        connector_class: Optional[Type[SimulationConnector]] = None,
    ):
        """
        Initialize a new experiment with either a model or simulation command.
        
        Args:
            model: Instance of a class implementing ModelProtocol
            simulation_command: Command to run the simulation (if model not provided)
            param_format: Format string for parameter arguments (CLI mode only)
            output_format: Format of simulation output ('csv' or 'json' - CLI mode only)
            output_file: Path to output file (CLI mode only)
            working_dir: Working directory for the simulation (CLI mode only)
            connector_class: Custom connector class (defaults to SimulationConnector for CLI)
        
        Raises:
            ValueError: If neither model nor simulation_command is provided
        """
        # Track integration mode
        self.integration_mode = None
        self.model = None
        self.simulation_connector = None
        
        # Set up the integration mode
        if model is not None:
            # Protocol Integration mode
            self.integration_mode = "protocol"
            self.model = model
            
            # Import parameter space and KPIs from the model if available
            if hasattr(model, 'get_parameter_space') and callable(getattr(model, 'get_parameter_space')):
                self.parameter_space = model.get_parameter_space()
            else:
                self.parameter_space = {}
                
        elif simulation_command is not None:
            # CLI Integration mode
            self.integration_mode = "cli"
            
            # Use custom connector class if provided, otherwise default
            connector_cls = connector_class or SimulationConnector
            self.simulation_connector = connector_cls(
                command=simulation_command,
                param_format=param_format,
                output_format=output_format,
                output_file=output_file,
                working_dir=working_dir,
            )
            
            self.parameter_space = {}
        else:
            raise ValueError("Either model or simulation_command must be provided")
        
        # Set up KPI calculator and data aggregator
        self.kpi_calculator = KPICalculator()
        self.data_aggregator = DataAggregator(self.kpi_calculator)
        
        # Initialize optimization settings
        self.optimizer = None
        self.objective_name = None
        self.maximize = True
        
        # Load KPI definitions from model if available
        if self.integration_mode == "protocol" and hasattr(model, 'get_kpi_definitions') and callable(getattr(model, 'get_kpi_definitions')):
            self._load_kpi_definitions_from_model()
    
    def _load_kpi_definitions_from_model(self) -> None:
        """Load KPI definitions from the model's get_kpi_definitions method."""
        if not self.model:
            return
            
        try:
            kpi_defs = self.model.get_kpi_definitions()
            for name, func_or_dict in kpi_defs.items():
                if callable(func_or_dict):
                    self.kpi_calculator.add_kpi_function(name, func_or_dict)
                elif isinstance(func_or_dict, dict) and 'function' in func_or_dict:
                    self.kpi_calculator.add_kpi_function(
                        name, 
                        func_or_dict['function'],
                        description=func_or_dict.get('description', '')
                    )
        except (AttributeError, Exception) as e:
            logger.warning(f"Failed to load KPI definitions from model: {e}")
    
    def add_kpi(
        self, 
        name: str, 
        function: Optional[Callable[[pd.DataFrame], float]] = None,
        column: Optional[str] = None,
        operation: Optional[str] = None,
        filter_condition: Optional[str] = None,
        objective: Optional[str] = None,
    ) -> None:
        """
        Add a KPI to calculate from simulation results.
        
        Args:
            name: Name of the KPI
            function: Custom function to calculate the KPI (takes DataFrame, returns value)
            column: Column name for simple KPI calculation
            operation: Operation for simple KPI ('max', 'min', 'mean', 'sum', etc.)
            filter_condition: Optional condition to filter the DataFrame
            objective: Set this KPI as objective ('maximize' or 'minimize')
            
        Raises:
            ValueError: If neither function nor column/operation are provided
        """
        if function is not None:
            self.kpi_calculator.add_kpi_function(name, function)
        elif column is not None:
            if operation is not None:
                self.kpi_calculator.add_simple_kpi(name, column, operation, filter_condition)
            else:
                # If no operation specified, use 'identity' (pass-through)
                self.kpi_calculator.add_simple_kpi(name, column, "identity", filter_condition)
        else:
            raise ValueError(
                "Must provide either a custom function or column name"
            )
            
        # Set as objective if specified
        if objective is not None:
            if objective.lower() in ['maximize', 'max']:
                self.objective_name = name
                self.maximize = True
            elif objective.lower() in ['minimize', 'min']:
                self.objective_name = name
                self.maximize = False
            else:
                raise ValueError(f"Invalid objective value: {objective}. Use 'maximize' or 'minimize'")
    
    def set_parameter_space(
        self, 
        parameter_space: Optional[Dict[str, Union[List[Any], Tuple[float, float]]]] = None
    ) -> None:
        """
        Set the parameter space to explore.
        
        If no parameter_space is provided and integration_mode is 'protocol',
        attempts to get it from the model.
        
        Args:
            parameter_space: Dictionary mapping parameter names to their possible values
                For continuous parameters, provide a tuple of (min, max)
                For discrete parameters, provide a list of possible values
                
        Raises:
            ValueError: If parameter_space not provided and can't be fetched from model
        """
        if parameter_space is not None:
            self.parameter_space = parameter_space
        elif self.integration_mode == "protocol" and self.model is not None:
            try:
                self.parameter_space = self.model.get_parameter_space()
            except (AttributeError, NotImplementedError) as e:
                raise ValueError(
                    f"Failed to get parameter space from model: {e}\n"
                    "Please provide parameter_space explicitly."
                )
        else:
            raise ValueError("Parameter space must be provided")
    
    def set_optimizer(
        self,
        method: str = "random",
        objective_name: Optional[str] = None,
        maximize: Optional[bool] = None,
        **kwargs
    ) -> None:
        """
        Set the optimization method.
        
        Args:
            method: Optimization method ('grid', 'random', 'bayesian', 'nsga2', etc.)
            objective_name: Name of the KPI to optimize (if None, uses previously set objective)
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
        
        # Update objective if provided
        if objective_name is not None:
            self.objective_name = objective_name
        
        # Update maximize if provided
        if maximize is not None:
            self.maximize = maximize
            
        if self.objective_name is None:
            raise ValueError("Objective KPI name must be set before or with set_optimizer")
        
        # Initialize the optimizer
        optimizer_class = AVAILABLE_OPTIMIZERS[method]
        self.optimizer = optimizer_class(
            parameter_space=self.parameter_space,
            objective_name=self.objective_name,
            maximize=self.maximize,
            **kwargs
        )
    
    def _evaluate_parameters(self, parameters: Dict[str, Any]) -> Dict[str, float]:
        """
        Evaluate a set of parameters using the configured model or connector.
        
        Args:
            parameters: Dictionary of parameter values
            
        Returns:
            Dictionary of KPI values
            
        Raises:
            ValueError: If neither model nor simulation_connector is configured
        """
        if self.integration_mode == "protocol" and self.model is not None:
            # Protocol Integration mode - call model.run()
            sim_results = self.model.run(parameters)
            
            # Handle both SimulationResults objects and raw DataFrames
            if isinstance(sim_results, SimulationResults):
                kpis = sim_results.kpis.copy()
                df = sim_results.time_series_data
                
                # Compute any KPIs not already in results
                for name, func in self.kpi_calculator.kpi_functions.items():
                    if name not in kpis and not df.empty:
                        kpis[name] = func(df)
                        
                return kpis
            else:
                # Assume it's a DataFrame and compute KPIs
                df = sim_results
                return self.kpi_calculator.calculate_kpis(df)
                
        elif self.integration_mode == "cli" and self.simulation_connector is not None:
            # CLI Integration mode - use simulation connector
            result_df = self.simulation_connector.run_simulation(parameters)
            return self.kpi_calculator.calculate_kpis(result_df)
        else:
            raise ValueError("Neither model nor simulation_connector is configured")
    
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
            print(f"Integration mode: {self.integration_mode}")
        
        # Store all evaluation results
        all_evaluations = []
        
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
                # Validate parameters if using protocol model
                if self.integration_mode == "protocol" and hasattr(self.model, 'validate_params'):
                    is_valid, error_msg = self.model.validate_params(parameters)
                    if not is_valid:
                        raise ValueError(f"Invalid parameters: {error_msg}")
                
                # Evaluate parameters
                kpis = self._evaluate_parameters(parameters)
                
                # Add to evaluations
                all_evaluations.append({
                    "parameters": parameters,
                    "kpis": kpis,
                    "iteration": iteration
                })
                
                # Update optimizer with result
                objective_value = kpis.get(self.objective_name)
                if objective_value is None:
                    raise ValueError(f"Objective KPI '{self.objective_name}' not found in evaluation results")
                
                self.optimizer.update(parameters, objective_value)
                
                # Add to data aggregator
                if self.integration_mode == "cli":
                    # For CLI mode, data aggregator needs the DataFrame
                    result_df = self.simulation_connector.run_simulation(parameters)
                    self.data_aggregator.add_simulation_result(parameters, result_df)
                else:
                    # For protocol mode, add directly
                    self.data_aggregator.add_direct_result(parameters, kpis)
                
                if verbose:
                    print(f"  Result: {self.objective_name} = {objective_value:.6g}")
            
            except Exception as e:
                if verbose:
                    print(f"  Error evaluating parameters: {e}")
                
                # Add failed evaluation
                all_evaluations.append({
                    "parameters": parameters,
                    "kpis": {},
                    "iteration": iteration,
                    "error": str(e)
                })
            
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
            all_evaluations=all_evaluations,
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
        all_evaluations: Optional[List[Dict[str, Any]]] = None,
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
            all_evaluations: List of all parameter evaluations with KPIs
        """
        self.experiment = experiment
        self.iterations = iterations
        self.elapsed_time = elapsed_time
        self.best_result = best_result
        self.all_results = all_results
        self.summary = summary
        self.all_evaluations = all_evaluations or []
    
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
            "all_evaluations": convert_numpy_types(self.all_evaluations),
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
    experiment = PsuuExperiment(simulation_command=command, **kwargs)
    
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
