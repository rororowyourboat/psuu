"""
Base Optimizer Module

This module defines the base Optimizer class that all optimization algorithms must implement.
"""

from typing import Dict, Any, List, Tuple, Optional, Callable, Union
from abc import ABC, abstractmethod
import numpy as np


class Optimizer(ABC):
    """
    Abstract base class for parameter space optimization algorithms.
    
    All optimization algorithms should inherit from this class and implement
    the required methods.
    """
    
    def __init__(
        self, 
        parameter_space: Dict[str, Union[List[Any], Tuple[float, float]]],
        objective_name: str,
        maximize: bool = True,
    ):
        """
        Initialize the optimizer.
        
        Args:
            parameter_space: Dictionary mapping parameter names to their possible values
                For continuous parameters, provide a tuple of (min, max)
                For discrete parameters, provide a list of possible values
            objective_name: Name of the KPI to optimize
            maximize: Whether to maximize (True) or minimize (False) the objective
        """
        self.parameter_space = parameter_space
        self.objective_name = objective_name
        self.maximize = maximize
        self.evaluations: List[Dict[str, Any]] = []
        self._validate_parameter_space()
    
    def _validate_parameter_space(self) -> None:
        """
        Validate that the parameter space is properly formatted.
        
        Raises:
            ValueError: If parameter space is invalid
        """
        for param_name, param_values in self.parameter_space.items():
            if isinstance(param_values, (list, tuple)):
                if len(param_values) == 0:
                    raise ValueError(f"Parameter '{param_name}' has empty values")
                if isinstance(param_values, tuple) and len(param_values) != 2:
                    raise ValueError(
                        f"Continuous parameter '{param_name}' must be a tuple of (min, max)"
                    )
            else:
                raise ValueError(
                    f"Parameter '{param_name}' must be a list or tuple, got {type(param_values)}"
                )
    
    def update(self, parameters: Dict[str, Any], objective_value: float) -> None:
        """
        Update the optimizer with a new evaluation result.
        
        Args:
            parameters: Parameter set that was evaluated
            objective_value: Value of the objective function
        """
        self.evaluations.append({
            "parameters": parameters.copy(),
            "objective_value": objective_value
        })
    
    def get_best_parameters(self) -> Dict[str, Any]:
        """
        Get the best parameters found so far.
        
        Returns:
            Dictionary of best parameter values
            
        Raises:
            ValueError: If no evaluations are available
        """
        if not self.evaluations:
            raise ValueError("No evaluations available")
        
        # Sort by objective value (descending if maximizing, ascending if minimizing)
        sorted_evals = sorted(
            self.evaluations,
            key=lambda x: x["objective_value"],
            reverse=self.maximize
        )
        
        return sorted_evals[0]["parameters"].copy()
    
    @abstractmethod
    def suggest(self) -> Dict[str, Any]:
        """
        Suggest the next set of parameters to evaluate.
        
        Returns:
            Dictionary of parameter values to evaluate next
        """
        pass
    
    @abstractmethod
    def is_finished(self) -> bool:
        """
        Check if the optimization process has finished.
        
        Returns:
            True if optimization is complete, False otherwise
        """
        pass
