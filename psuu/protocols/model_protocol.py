"""
Base Model Protocol for PSUU.

This module provides the base protocol interface that all model types should implement.
"""

from typing import Dict, Any, List, Tuple, Optional, Union, Callable
import pandas as pd
from abc import ABC, abstractmethod


class ModelProtocol(ABC):
    """
    Base protocol interface for simulation models to integrate with PSUU.
    
    This abstract class defines the methods that all model types should implement
    to ensure seamless integration with PSUU.
    """
    
    @abstractmethod
    def run(self, params: Dict[str, Any], **kwargs) -> Union['SimulationResults', pd.DataFrame]:
        """
        Run simulation with given parameters.
        
        Args:
            params: Dictionary of parameter values
            **kwargs: Additional run-specific options (timesteps, samples, etc.)
            
        Returns:
            Simulation results as SimulationResults object or DataFrame
        """
        pass
    
    @abstractmethod
    def get_parameter_space(self) -> Dict[str, Union[List, Tuple, Dict]]:
        """
        Return the parameter space definition.
        
        Returns:
            Dictionary mapping parameter names to:
            - Tuple of (min, max) for continuous parameters
            - List of values for discrete parameters
            - Dict with 'type', 'range', and optional 'description' for complex parameters
        """
        pass
    
    @abstractmethod
    def get_kpi_definitions(self) -> Dict[str, Union[Callable, Dict]]:
        """
        Return KPI calculation functions.
        
        Returns:
            Dictionary mapping KPI names to either:
            - Callable function that computes the KPI from simulation results
            - Dict with 'function', 'description', and optional 'tags' 
        """
        pass
    
    def validate_parameters(self, params: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validate if the parameters are valid for this model.
        
        Args:
            params: Dictionary of parameter values to validate
            
        Returns:
            Tuple of (is_valid, error_message_if_any)
        """
        # Default implementation using parameter space
        param_space = self.get_parameter_space()
        for name, value in params.items():
            if name not in param_space:
                return False, f"Unknown parameter: {name}"
                
            space_def = param_space[name]
            if isinstance(space_def, tuple) and len(space_def) == 2:
                min_val, max_val = space_def
                if not (min_val <= value <= max_val):
                    return False, f"Parameter {name} value {value} out of range [{min_val}, {max_val}]"
            elif isinstance(space_def, list):
                if value not in space_def:
                    return False, f"Parameter {name} value {value} not in allowed values {space_def}"
            elif isinstance(space_def, dict) and 'range' in space_def:
                range_def = space_def['range']
                if isinstance(range_def, tuple) and len(range_def) == 2:
                    min_val, max_val = range_def
                    if not (min_val <= value <= max_val):
                        return False, f"Parameter {name} value {value} out of range [{min_val}, {max_val}]"
                elif isinstance(range_def, list) and value not in range_def:
                    return False, f"Parameter {name} value {value} not in allowed values {range_def}"
                
        return True, None
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Return metadata about the model.
        
        Returns:
            Dictionary with model metadata like name, description, version, etc.
        """
        return {
            "name": self.__class__.__name__,
            "description": self.__doc__ or "No description provided",
            "version": getattr(self, "VERSION", "0.1.0"),
        }
