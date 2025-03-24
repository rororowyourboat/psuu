"""
Validation Module for PSUU.

This module provides validation utilities for parameters and simulation inputs.
"""

from typing import Dict, Any, List, Tuple, Optional, Union, Callable
import time
import random
import traceback
import json
import pandas as pd
import numpy as np

from .exceptions import ParameterValidationError, ModelExecutionError
from .simulation_connector import SimulationConnector
from .custom_connectors.cadcad_connector import CadcadSimulationConnector


class ParameterValidator:
    """
    Validator for simulation parameters.
    
    Provides methods to validate parameters against their defined space
    and constraints.
    """
    
    def __init__(self, parameter_space: Dict[str, Any]):
        """
        Initialize with parameter space definition.
        
        Args:
            parameter_space: Dictionary mapping parameter names to their valid ranges/values
        """
        self.parameter_space = parameter_space
        self._parse_parameter_space()
    
    def _parse_parameter_space(self) -> None:
        """Parse and normalize the parameter space definition."""
        self.validators = {}
        
        for name, space_def in self.parameter_space.items():
            # Simple tuple range (continuous parameter)
            if isinstance(space_def, tuple) and len(space_def) == 2:
                min_val, max_val = space_def
                self.validators[name] = lambda x, min_v=min_val, max_v=max_val: min_v <= x <= max_v
            
            # List of discrete values
            elif isinstance(space_def, list):
                valid_values = set(space_def)
                self.validators[name] = lambda x, vals=valid_values: x in vals
            
            # Dictionary with detailed specification
            elif isinstance(space_def, dict):
                param_type = space_def.get('type', 'continuous')
                
                if param_type == 'continuous':
                    range_def = space_def.get('range', (0, 1))
                    min_val, max_val = range_def
                    self.validators[name] = lambda x, min_v=min_val, max_v=max_val: min_v <= x <= max_v
                
                elif param_type == 'discrete':
                    valid_values = set(space_def.get('range', []))
                    self.validators[name] = lambda x, vals=valid_values: x in vals
                
                elif param_type == 'categorical':
                    categories = set(space_def.get('categories', []))
                    self.validators[name] = lambda x, cats=categories: x in cats
                
                elif param_type == 'boolean':
                    self.validators[name] = lambda x: isinstance(x, bool)
                
                elif param_type == 'custom' and 'validator' in space_def:
                    # Custom validator function provided in the definition
                    self.validators[name] = space_def['validator']
            
            # Default: allow any value
            else:
                self.validators[name] = lambda x: True
    
    def validate_parameter(self, name: str, value: Any) -> Tuple[bool, Optional[str]]:
        """
        Validate a single parameter.
        
        Args:
            name: Parameter name
            value: Parameter value
            
        Returns:
            Tuple of (is_valid, error_message_if_any)
        """
        if name not in self.validators:
            return False, f"Unknown parameter: {name}"
        
        validator = self.validators[name]
        try:
            is_valid = validator(value)
            if is_valid:
                return True, None
            else:
                space_def = self.parameter_space[name]
                if isinstance(space_def, tuple):
                    return False, f"Parameter {name} value {value} out of range [{space_def[0]}, {space_def[1]}]"
                elif isinstance(space_def, list):
                    return False, f"Parameter {name} value {value} not in allowed values {space_def}"
                elif isinstance(space_def, dict) and 'range' in space_def:
                    range_def = space_def['range']
                    if isinstance(range_def, (tuple, list)):
                        return False, f"Parameter {name} value {value} not valid for range {range_def}"
                return False, f"Parameter {name} value {value} is invalid"
        except Exception as e:
            return False, f"Error validating parameter {name}: {str(e)}"
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> Tuple[bool, Dict[str, str]]:
        """
        Validate multiple parameters.
        
        Args:
            parameters: Dictionary of parameter names and values
            
        Returns:
            Tuple of (all_valid, dict_of_error_messages_by_param)
        """
        errors = {}
        
        # Check for missing required parameters
        for name in self.parameter_space:
            space_def = self.parameter_space[name]
            is_required = True
            if isinstance(space_def, dict) and 'required' in space_def:
                is_required = space_def['required']
            
            if is_required and name not in parameters:
                errors[name] = f"Missing required parameter: {name}"
        
        # Validate provided parameters
        for name, value in parameters.items():
            is_valid, error = self.validate_parameter(name, value)
            if not is_valid:
                errors[name] = error
        
        return len(errors) == 0, errors


class RobustCadcadConnector(CadcadSimulationConnector):
    """
    Enhanced connector with improved error handling and validation.
    """
    
    def __init__(
        self,
        parameter_validators: Optional[Dict[str, Callable]] = None,
        error_policy: str = "raise",
        retry_attempts: int = 3,
        fallback_values: Optional[Dict[str, Any]] = None,
        error_log_file: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize with error handling configuration.
        
        Args:
            parameter_validators: Dictionary of parameter validation functions
            error_policy: How to handle errors ('raise', 'retry', 'fallback')
            retry_attempts: Number of retry attempts for failed simulations
            fallback_values: Fallback values to return on failure
            error_log_file: Path to file for logging errors
            **kwargs: Other arguments for the parent class
        """
        super().__init__(**kwargs)
        self.parameter_validators = parameter_validators or {}
        self.error_policy = error_policy
        self.retry_attempts = retry_attempts
        self.fallback_values = fallback_values or {}
        self.error_log_file = error_log_file
        self.error_log = []
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validate if the parameters are valid for this model.
        
        Args:
            parameters: Dictionary of parameter values to validate
            
        Returns:
            Tuple of (is_valid, error_message_if_any)
        """
        for name, value in parameters.items():
            if name in self.parameter_validators:
                validator = self.parameter_validators[name]
                try:
                    if not validator(value):
                        return False, f"Invalid value for parameter {name}: {value}"
                except Exception as e:
                    return False, f"Error validating parameter {name}: {str(e)}"
        
        return True, None
    
    def log_error(self, parameters: Dict[str, Any], error: Exception) -> None:
        """
        Log an error that occurred during simulation.
        
        Args:
            parameters: Parameters that caused the error
            error: The exception that was raised
        """
        error_entry = {
            "timestamp": time.time(),
            "parameters": {k: (float(v) if isinstance(v, (np.integer, np.floating)) else v) 
                           for k, v in parameters.items()},
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": traceback.format_exc()
        }
        self.error_log.append(error_entry)
        
        # Optionally write to file
        if self.error_log_file:
            with open(self.error_log_file, 'a') as f:
                f.write(json.dumps(error_entry) + "\n")
    
    def generate_fallback_result(self) -> pd.DataFrame:
        """
        Generate fallback result when simulation fails.
        
        Returns:
            DataFrame with fallback values
        """
        if isinstance(self.fallback_values, pd.DataFrame):
            return self.fallback_values
        else:
            # Create a minimal DataFrame with expected columns
            return pd.DataFrame([self.fallback_values])
    
    def run_simulation(self, parameters: Dict[str, Any]) -> pd.DataFrame:
        """
        Run simulation with robust error handling.
        
        Args:
            parameters: Dictionary of parameter values
            
        Returns:
            DataFrame with simulation results
            
        Raises:
            ModelExecutionError: If simulation fails and error_policy is 'raise'
        """
        # Validate parameters
        is_valid, error_msg = self.validate_parameters(parameters)
        if not is_valid:
            raise ParameterValidationError(error_msg)
        
        # Try running the simulation
        attempt = 0
        last_error = None
        
        while attempt < self.retry_attempts:
            try:
                return super().run_simulation(parameters)
            
            except Exception as e:
                attempt += 1
                last_error = e
                self.log_error(parameters, e)
                
                if self.error_policy == 'retry' and attempt < self.retry_attempts:
                    # Add jitter to parameters if retry
                    jittered_params = self._add_jitter(parameters)
                    parameters = jittered_params
                    continue
                
                if self.error_policy == 'fallback':
                    return self.generate_fallback_result()
                
                # For 'raise' policy or if retries exhausted
                if attempt >= self.retry_attempts:
                    break
        
        # If we get here, all attempts failed
        if self.error_policy == 'raise':
            raise ModelExecutionError(f"Simulation failed after {attempt} attempts: {str(last_error)}")
        else:
            return self.generate_fallback_result()
    
    def _add_jitter(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add small random variations to numeric parameters.
        
        Args:
            parameters: Original parameters
            
        Returns:
            Parameters with jitter added
        """
        jittered = parameters.copy()
        for name, value in parameters.items():
            if isinstance(value, (int, float, np.integer, np.floating)):
                # Add up to 1% jitter
                jitter_factor = 1.0 + (random.random() - 0.5) * 0.02
                if isinstance(value, (int, np.integer)):
                    jittered[name] = int(value * jitter_factor)
                else:
                    jittered[name] = value * jitter_factor
        
        return jittered
