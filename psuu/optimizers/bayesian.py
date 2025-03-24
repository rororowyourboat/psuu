"""
Bayesian Optimizer Module

This module implements Bayesian optimization using Gaussian Process regression.
It requires scikit-optimize to be installed.
"""

from typing import Dict, Any, List, Tuple, Optional, Union, Callable
import numpy as np
from .base import Optimizer

try:
    from skopt import Optimizer as SkOptimizer
    from skopt.space import Real, Integer, Categorical
    SKOPT_AVAILABLE = True
except ImportError:
    SKOPT_AVAILABLE = False


class BayesianOptimizer(Optimizer):
    """
    Bayesian optimizer using Gaussian Process regression from scikit-optimize.
    
    This optimizer builds a probabilistic model of the objective function and
    uses it to select the most promising points to evaluate next.
    """
    
    def __init__(
        self,
        parameter_space: Dict[str, Union[List[Any], Tuple[float, float]]],
        objective_name: str,
        maximize: bool = True,
        num_iterations: int = 50,
        n_initial_points: int = 10,
        acq_func: str = "EI",
        seed: Optional[int] = None,
    ):
        """
        Initialize the Bayesian optimizer.
        
        Args:
            parameter_space: Dictionary mapping parameter names to their possible values
                For continuous parameters, provide a tuple of (min, max)
                For discrete parameters, provide a list of possible values
            objective_name: Name of the KPI to optimize
            maximize: Whether to maximize (True) or minimize (False) the objective
            num_iterations: Maximum number of iterations
            n_initial_points: Number of initial points to sample randomly
            acq_func: Acquisition function ('EI', 'PI', 'LCB', 'gp_hedge')
            seed: Random seed for reproducibility
            
        Raises:
            ImportError: If scikit-optimize is not installed
        """
        if not SKOPT_AVAILABLE:
            raise ImportError(
                "Bayesian optimization requires scikit-optimize. "
                "Install it with 'pip install scikit-optimize'."
            )
        
        super().__init__(parameter_space, objective_name, maximize)
        self.num_iterations = num_iterations
        self.n_initial_points = n_initial_points
        self.acq_func = acq_func
        self.seed = seed
        self.iteration = 0
        
        # Convert parameter space to skopt format
        self.space, self.param_names = self._convert_param_space()
        
        # Initialize skopt optimizer
        self.opt = SkOptimizer(
            dimensions=self.space,
            base_estimator="GP",
            acq_func=acq_func,
            acq_optimizer="auto",
            n_initial_points=n_initial_points,
            random_state=seed,
        )
    
    def _convert_param_space(self) -> Tuple[List, List[str]]:
        """
        Convert the parameter space to the format expected by scikit-optimize.
        
        Returns:
            Tuple of (list of skopt dimensions, list of parameter names)
        """
        space = []
        param_names = []
        
        for param_name, param_range in self.parameter_space.items():
            param_names.append(param_name)
            
            if isinstance(param_range, tuple) and len(param_range) == 2:
                # Continuous parameter
                min_val, max_val = param_range
                
                # Check if values appear to be integers
                if all(isinstance(v, int) or v.is_integer() for v in param_range):
                    space.append(Integer(int(min_val), int(max_val), name=param_name))
                else:
                    space.append(Real(min_val, max_val, name=param_name))
            else:
                # Discrete parameter
                space.append(Categorical(param_range, name=param_name))
        
        return space, param_names
    
    def suggest(self) -> Dict[str, Any]:
        """
        Suggest the next set of parameters to evaluate.
        
        Returns:
            Dictionary of parameter values to evaluate next
        """
        if self.is_finished():
            if self.evaluations:
                return self.get_best_parameters()
            raise StopIteration("Bayesian optimization complete")
        
        # Get next point from skopt
        x = self.opt.ask()
        
        # Convert to parameter dictionary
        parameters = {name: val for name, val in zip(self.param_names, x)}
        
        self.iteration += 1
        return parameters
    
    def update(self, parameters: Dict[str, Any], objective_value: float) -> None:
        """
        Update the optimizer with a new evaluation result.
        
        Args:
            parameters: Parameter set that was evaluated
            objective_value: Value of the objective function
        """
        # Call parent method to store the evaluation
        super().update(parameters, objective_value)
        
        # Convert parameters to the format expected by skopt
        x = [parameters[name] for name in self.param_names]
        
        # Convert objective value (skopt minimizes by default)
        y = -objective_value if self.maximize else objective_value
        
        # Update the skopt optimizer
        self.opt.tell(x, y)
    
    def is_finished(self) -> bool:
        """
        Check if the Bayesian optimization is complete.
        
        Returns:
            True if maximum iterations reached, False otherwise
        """
        return self.iteration >= self.num_iterations
