"""
cadCAD Model Protocol for PSUU.

This module provides the protocol interface specifically for cadCAD models
to ensure a consistent API for PSUU integration.
"""

from typing import Dict, Any, List, Tuple, Optional, Union, Callable
import pandas as pd
from abc import abstractmethod

from .model_protocol import ModelProtocol
from psuu.results import SimulationResults


class CadcadModelProtocol(ModelProtocol):
    """
    Protocol interface for cadCAD models to integrate with PSUU.
    
    This protocol defines the methods that cadCAD models must implement
    to ensure seamless integration with PSUU. It standardizes how PSUU
    interacts with different cadCAD models, allowing for a plug-and-play
    approach to model optimization.
    """
    
    @abstractmethod
    def run(self, params: Dict[str, Any], **kwargs) -> SimulationResults:
        """
        Run cadCAD simulation with given parameters.
        
        Args:
            params: Dictionary of parameter values
            **kwargs: Additional run-specific options (timesteps, samples, etc.)
            
        Returns:
            SimulationResults object containing time_series_data, KPIs, metadata, and parameters
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
        Return KPI calculation functions for cadCAD simulations.
        
        Returns:
            Dictionary mapping KPI names to either:
            - Callable function that computes the KPI from simulation results
            - Dict with 'function', 'description', and optional 'tags'
        """
        pass
    
    def get_cadcad_config(self) -> Dict[str, Any]:
        """
        Get cadCAD configuration details.
        
        Returns:
            Dictionary with cadCAD configuration including state variables,
            policies, and other cadCAD-specific settings
        """
        # Default empty implementation - must be overridden by implementing classes
        return {}
    
    def get_initial_state(self) -> Dict[str, Any]:
        """
        Get the initial state for the simulation.
        
        Returns:
            Dictionary of initial state variable values
        """
        # Default empty implementation - must be overridden by implementing classes
        return {}
    
    def validate_params(self, params: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validate simulation parameters.
        
        This extends the basic parameter validation from ModelProtocol
        with cadCAD-specific validation.
        
        Args:
            params: Dictionary of parameter values to validate
            
        Returns:
            Tuple of (is_valid, error_message_if_any)
        """
        # First run base validation from parent class
        is_valid, error_msg = super().validate_parameters(params)
        if not is_valid:
            return is_valid, error_msg
            
        # Add cadCAD-specific validation here
        try:
            # Additional model-specific validation logic
            return True, None
        except Exception as e:
            return False, f"Parameter validation error: {str(e)}"
