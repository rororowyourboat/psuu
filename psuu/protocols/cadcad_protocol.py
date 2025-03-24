"""
cadCAD Model Protocol for PSUU.

This module provides the protocol interface specifically for cadCAD models.
"""

from typing import Dict, Any, List, Tuple, Optional, Union, Callable
import pandas as pd

from .model_protocol import ModelProtocol


class CadcadModelProtocol(ModelProtocol):
    """
    Protocol interface for cadCAD models to integrate with PSUU.
    
    This protocol defines the methods that cadCAD models should implement
    to ensure seamless integration with PSUU.
    """
    
    def run(self, params: Dict[str, Any], **kwargs) -> Union['SimulationResults', pd.DataFrame]:
        """
        Run cadCAD simulation with given parameters.
        
        Args:
            params: Dictionary of parameter values
            **kwargs: Additional run-specific options (timesteps, samples, etc.)
            
        Returns:
            Simulation results as SimulationResults object or DataFrame
        """
        # Implement cadCAD-specific simulation logic
        # This should be overridden by implementing classes
        raise NotImplementedError("Subclasses must implement run()")
    
    def get_parameter_space(self) -> Dict[str, Union[List, Tuple, Dict]]:
        """
        Return the parameter space definition.
        
        Returns:
            Dictionary mapping parameter names to:
            - Tuple of (min, max) for continuous parameters
            - List of values for discrete parameters
            - Dict with 'type', 'range', and optional 'description' for complex parameters
        """
        # This should be overridden by implementing classes
        raise NotImplementedError("Subclasses must implement get_parameter_space()")
    
    def get_kpi_definitions(self) -> Dict[str, Union[Callable, Dict]]:
        """
        Return KPI calculation functions for cadCAD simulations.
        
        Returns:
            Dictionary mapping KPI names to either:
            - Callable function that computes the KPI from simulation results
            - Dict with 'function', 'description', and optional 'tags'
        """
        # This should be overridden by implementing classes
        raise NotImplementedError("Subclasses must implement get_kpi_definitions()")
    
    def validate_sweep_config(self, sweep_config: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validate cadCAD sweep configuration.
        
        Args:
            sweep_config: cadCAD sweep configuration
            
        Returns:
            Tuple of (is_valid, error_message_if_any)
        """
        # Default implementation - can be overridden by implementing classes
        return True, None
    
    def get_cadcad_config(self) -> Dict[str, Any]:
        """
        Get cadCAD configuration.
        
        Returns:
            Dictionary with cadCAD configuration
        """
        # This should be overridden by implementing classes
        raise NotImplementedError("Subclasses must implement get_cadcad_config()")
