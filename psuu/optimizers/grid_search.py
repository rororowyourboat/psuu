"""
Grid Search Optimizer Module

This module implements the grid search optimization algorithm.
"""

from typing import Dict, Any, List, Tuple, Optional, Union, Iterator
import itertools
import numpy as np
from .base import Optimizer


class GridSearchOptimizer(Optimizer):
    """
    Grid search optimizer that exhaustively searches the parameter space.
    
    For continuous parameters, the optimizer discretizes the space into a specified
    number of points.
    """
    
    def __init__(
        self,
        parameter_space: Dict[str, Union[List[Any], Tuple[float, float]]],
        objective_name: str,
        maximize: bool = True,
        num_points: int = 5,
    ):
        """
        Initialize the grid search optimizer.
        
        Args:
            parameter_space: Dictionary mapping parameter names to their possible values
                For continuous parameters, provide a tuple of (min, max)
                For discrete parameters, provide a list of possible values
            objective_name: Name of the KPI to optimize
            maximize: Whether to maximize (True) or minimize (False) the objective
            num_points: Number of points to use for discretizing continuous parameters
        """
        super().__init__(parameter_space, objective_name, maximize)
        self.num_points = num_points
        self._grid = self._build_grid()
        self._iterator = iter(self._grid)
        self._suggested_points: List[Dict[str, Any]] = []
    
    def _build_grid(self) -> List[Dict[str, Any]]:
        """
        Build the parameter grid by discretizing continuous parameters and
        creating all possible combinations.
        
        Returns:
            List of parameter dictionaries for all grid points
        """
        param_values = {}
        
        for param_name, param_range in self.parameter_space.items():
            if isinstance(param_range, tuple) and len(param_range) == 2:
                # Continuous parameter, discretize
                min_val, max_val = param_range
                param_values[param_name] = np.linspace(
                    min_val, max_val, self.num_points
                ).tolist()
            else:
                # Discrete parameter, use as-is
                param_values[param_name] = param_range
        
        # Create all combinations
        param_names = list(param_values.keys())
        combinations = list(itertools.product(*[param_values[name] for name in param_names]))
        
        # Convert to list of dictionaries
        grid_points = []
        for combo in combinations:
            point = {name: value for name, value in zip(param_names, combo)}
            grid_points.append(point)
        
        return grid_points
    
    def suggest(self) -> Dict[str, Any]:
        """
        Suggest the next set of parameters to evaluate.
        
        Returns:
            Dictionary of parameter values to evaluate next
            
        Raises:
            StopIteration: If all grid points have been suggested
        """
        try:
            point = next(self._iterator)
            self._suggested_points.append(point)
            return point
        except StopIteration:
            # If we've exhausted the grid, return the best point
            if self.evaluations:
                return self.get_best_parameters()
            raise StopIteration("Grid search complete, all points evaluated")
    
    def is_finished(self) -> bool:
        """
        Check if the grid search is complete.
        
        Returns:
            True if all grid points have been evaluated, False otherwise
        """
        return len(self._suggested_points) >= len(self._grid)
