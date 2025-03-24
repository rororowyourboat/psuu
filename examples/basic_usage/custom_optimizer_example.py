#!/usr/bin/env python
"""
Custom Optimizer Example

This example demonstrates how to create and use a custom optimizer algorithm with PSUU.
We implement a simple simulated annealing optimizer as an example.
"""

import random
import math
import numpy as np
from typing import Dict, Any, List, Tuple, Optional

from psuu import PsuuExperiment
from psuu.optimizers.base import Optimizer


class SimulatedAnnealingOptimizer(Optimizer):
    """
    Simulated Annealing optimizer for parameter optimization.
    
    This optimizer uses simulated annealing, a probabilistic technique
    for approximating the global optimum inspired by metallurgical annealing.
    """
    
    def __init__(
        self,
        parameter_space: Dict[str, Any],
        objective_name: str,
        maximize: bool = True,
        num_iterations: int = 100,
        initial_temp: float = 10.0,
        cooling_rate: float = 0.95,
        seed: Optional[int] = None,
    ):
        """
        Initialize the simulated annealing optimizer.
        
        Args:
            parameter_space: Dictionary mapping parameter names to their possible values
            objective_name: Name of the KPI to optimize
            maximize: Whether to maximize (True) or minimize (False) the objective
            num_iterations: Maximum number of iterations
            initial_temp: Initial temperature for annealing
            cooling_rate: Rate at which temperature decreases
            seed: Random seed for reproducibility
        """
        super().__init__(parameter_space, objective_name, maximize)
        self.num_iterations = num_iterations
        self.initial_temp = initial_temp
        self.cooling_rate = cooling_rate
        self.current_temp = initial_temp
        self.iteration = 0
        
        # Set random seed
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
        
        # Initialize with a random point
        self.current_solution = self._random_point()
        self.best_solution = self.current_solution.copy()
        self.current_value = None
        self.best_value = None
    
    def _random_point(self) -> Dict[str, Any]:
        """Generate a random point in the parameter space."""
        point = {}
        
        for param_name, param_range in self.parameter_space.items():
            if isinstance(param_range, tuple) and len(param_range) == 2:
                # Continuous parameter
                min_val, max_val = param_range
                point[param_name] = random.uniform(min_val, max_val)
            else:
                # Discrete parameter
                point[param_name] = random.choice(param_range)
        
        return point
    
    def _neighbor(self, point: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a neighboring point with small perturbations."""
        neighbor = {}
        
        for param_name, param_value in point.items():
            param_range = self.parameter_space[param_name]
            
            if isinstance(param_range, tuple) and len(param_range) == 2:
                # Continuous parameter - perturb by up to 10% of range
                min_val, max_val = param_range
                range_size = max_val - min_val
                perturbation = random.uniform(-0.1, 0.1) * range_size
                new_value = param_value + perturbation
                # Ensure we stay within bounds
                neighbor[param_name] = max(min_val, min(max_val, new_value))
            else:
                # Discrete parameter - 20% chance to change
                if random.random() < 0.2:
                    # Choose a different value
                    possible_values = [v for v in param_range if v != param_value]
                    if possible_values:
                        neighbor[param_name] = random.choice(possible_values)
                    else:
                        neighbor[param_name] = param_value
                else:
                    neighbor[param_name] = param_value
        
        return neighbor
    
    def suggest(self) -> Dict[str, Any]:
        """
        Suggest the next set of parameters to evaluate.
        
        Returns:
            Dictionary of parameter values to evaluate next
        """
        if self.is_finished():
            return self.best_solution
        
        # If first iteration, return the initial random solution
        if self.iteration == 0:
            return self.current_solution
        
        # Generate a neighboring solution
        neighbor = self._neighbor(self.current_solution)
        
        # Return the neighbor
        return neighbor
    
    def update(self, parameters: Dict[str, Any], objective_value: float) -> None:
        """
        Update the optimizer with a new evaluation result.
        
        Args:
            parameters: Parameter set that was evaluated
            objective_value: Value of the objective function
        """
        # Call parent method to store the evaluation
        super().update(parameters, objective_value)
        
        # Update current solution and value
        if self.current_value is None:
            self.current_solution = parameters.copy()
            self.current_value = objective_value
            self.best_solution = parameters.copy()
            self.best_value = objective_value
        else:
            # Determine if we should accept the new solution
            # For maximization, higher values are better; for minimization, lower values are better
            current_is_better = (self.maximize and objective_value > self.current_value) or \
                               (not self.maximize and objective_value < self.current_value)
            
            # Calculate acceptance probability
            if current_is_better:
                acceptance_probability = 1.0
            else:
                # For maximization, calculate exp((new - old) / temp)
                # For minimization, calculate exp((old - new) / temp)
                if self.maximize:
                    delta = objective_value - self.current_value
                else:
                    delta = self.current_value - objective_value
                
                acceptance_probability = math.exp(delta / self.current_temp)
            
            # Accept new solution with calculated probability
            if random.random() < acceptance_probability:
                self.current_solution = parameters.copy()
                self.current_value = objective_value
            
            # Update best solution if better
            best_is_better = (self.maximize and objective_value > self.best_value) or \
                            (not self.maximize and objective_value < self.best_value)
            
            if best_is_better:
                self.best_solution = parameters.copy()
                self.best_value = objective_value
        
        # Cool down temperature
        self.current_temp *= self.cooling_rate
        self.iteration += 1
    
    def is_finished(self) -> bool:
        """
        Check if the simulated annealing is complete.
        
        Returns:
            True if maximum iterations reached, False otherwise
        """
        return self.iteration >= self.num_iterations


def main():
    """Run an optimization example with custom simulated annealing optimizer."""
    print("PSUU - Custom Optimizer Example (Simulated Annealing)")
    print("====================================================")
    
    # Define a mock simulation command
    # In a real scenario, this would be your actual simulation command
    command = """python -c "
import sys, json, random
import numpy as np
import pandas as pd

# Get parameters from command line
x = float(sys.argv[1].split('=')[1])
y = float(sys.argv[2].split('=')[1])

# Rosenbrock function (a common optimization test function)
# f(x,y) = (a-x)² + b(y-x²)²
# Global minimum at (a,b) = (1,1) where f(1,1) = 0
a = 1
b = 100
result = (a-x)**2 + b*(y-x**2)**2

# Add some noise to make it more interesting
noise = random.uniform(0.9, 1.1)
result = result * noise

# Output as CSV
df = pd.DataFrame({
    'x': [x],
    'y': [y],
    'result': [result]
})
print(df.to_csv(index=False))
" --{name}={value}"""
    
    # Create experiment
    experiment = PsuuExperiment(
        simulation_command=command,
        param_format="--{name}={value}",
        output_format="csv"
    )
    
    # Add KPI
    experiment.add_kpi("function_value", column="result", operation="min")
    
    # Set parameter space
    experiment.set_parameter_space({
        "x": (-2.0, 2.0),
        "y": (-2.0, 2.0)
    })
    
    # Create custom optimizer
    custom_optimizer = SimulatedAnnealingOptimizer(
        parameter_space=experiment.parameter_space,
        objective_name="function_value",
        maximize=False,
        num_iterations=30,
        initial_temp=5.0,
        cooling_rate=0.9,
        seed=42
    )
    
    # Set custom optimizer
    experiment.optimizer = custom_optimizer
    
    # Run optimization
    print("\nRunning optimization with simulated annealing...")
    results = experiment.run(verbose=True)
    
    # Print results
    print("\nOptimization Results:")
    print(f"Minimum found at x={results.best_parameters['x']:.4f}, y={results.best_parameters['y']:.4f}")
    print(f"Function value: {results.best_kpis['function_value']:.6f}")
    print(f"True minimum is at x=1.0, y=1.0 with value 0.0")
    
    # Calculate error
    error = math.sqrt((results.best_parameters['x'] - 1.0)**2 + (results.best_parameters['y'] - 1.0)**2)
    print(f"Distance from true minimum: {error:.6f}")


if __name__ == "__main__":
    main()
