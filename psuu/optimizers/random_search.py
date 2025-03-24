"""
Random Search Optimizer Module

This module implements the random search optimization algorithm.
"""

from typing import Dict, Any, List, Tuple, Optional, Union
import random
import numpy as np
from .base import Optimizer


class RandomSearchOptimizer(Optimizer):
    """
    Random search optimizer that samples random points from the parameter space.
    
    This is often more efficient than grid search for high-dimensional spaces.
    """
    
    def __init__(
        self,
        parameter_space: Dict[str, Union[List[Any], Tuple[float, float]]],
        objective_name: str,
        maximize: bool = True,
        num_iterations: int = 100,
        seed: Optional[int] = None,
    ):
        """
        Initialize the random search optimizer.
        
        Args:
            parameter_space: Dictionary mapping parameter names to their possible values
                For continuous parameters, provide a tuple of (min, max)
                For discrete parameters, provide a list of possible values
            objective_name: Name of the KPI to optimize
            maximize: Whether to maximize (True) or minimize (False) the objective
            num_iterations: Number of random points to sample
            seed: Random seed for reproducibility
        """
        super().__init__(parameter_space, objective_name, maximize)
        self.num_iterations = num_iterations
        self.seed = seed
        self.rng = np.random.RandomState(seed)
        self.iteration = 0
    
    def suggest(self) -> Dict[str, Any]:
        """
        Suggest the next set of parameters to evaluate by random sampling.
        
        Returns:
            Dictionary of parameter values to evaluate next
        """
        if self.is_finished():
            if self.evaluations:
                return self.get_best_parameters()
            raise StopIteration("Random search complete")
        
        parameters = {}
        
        for param_name, param_range in self.parameter_space.items():
            if isinstance(param_range, tuple) and len(param_range) == 2:
                # Continuous parameter, sample from uniform distribution
                min_val, max_val = param_range
                parameters[param_name] = self.rng.uniform(min_val, max_val)
            elif isinstance(param_range, list) and len(param_range) == 2 and all(isinstance(x, (int, np.integer)) for x in param_range):
                # Integer range, sample uniformly from integers in range
                min_val, max_val = param_range
                parameters[param_name] = int(self.rng.randint(min_val, max_val + 1))
            else:
                # Discrete parameter, choose random value
                parameters[param_name] = self.rng.choice(param_range)
        
        self.iteration += 1
        return parameters
    
    def is_finished(self) -> bool:
        """
        Check if the random search is complete.
        
        Returns:
            True if all iterations have been performed, False otherwise
        """
        return self.iteration >= self.num_iterations
