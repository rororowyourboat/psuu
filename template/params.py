"""
Model parameter definitions.

This module defines the parameters for the model, including default values
and valid ranges for optimization.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Tuple, Union


@dataclass
class ModelParameters:
    """
    Parameters for the model with defaults and parameter space definitions.
    
    This dataclass centralizes all tunable parameters in the model, providing
    both default values and valid ranges for optimization.
    """
    # Example parameters for SIR model
    beta: float = 0.3  # Infection rate
    gamma: float = 0.05  # Recovery rate 
    population: int = 1000  # Initial population
    
    # Parameter space definitions for optimization
    parameter_space: Dict[str, Union[Tuple, List]] = field(default_factory=lambda: {
        "beta": (0.1, 0.5),  # (min, max) for continuous parameters
        "gamma": (0.01, 0.1),
        "population": [100, 500, 1000, 5000]  # List for discrete options
    })
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert parameters to dictionary, excluding parameter_space."""
        return {
            key: value for key, value in self.__dict__.items()
            if key != "parameter_space"
        }


# Default parameter instance
default_params = ModelParameters()


# Helper functions for parameter manipulation
def override_params(base_params: ModelParameters, **kwargs) -> ModelParameters:
    """
    Create a new parameters instance with overridden values.
    
    Args:
        base_params: Base parameters instance
        **kwargs: Parameter values to override
        
    Returns:
        New ModelParameters instance with overridden values
    """
    # Create a copy of the base parameters
    new_params = ModelParameters(
        beta=base_params.beta,
        gamma=base_params.gamma,
        population=base_params.population
    )
    
    # Update with provided values
    for key, value in kwargs.items():
        if hasattr(new_params, key):
            setattr(new_params, key, value)
    
    return new_params
