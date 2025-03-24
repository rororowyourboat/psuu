"""
Configuration Module for PSUU.

This module provides configuration handling for PSUU integration.
"""

from typing import Dict, List, Any, Optional, Union, Tuple
import json
import yaml
import os
from pathlib import Path
import importlib
import inspect

from .exceptions import ConfigurationError


class PsuuConfig:
    """Configuration handler for PSUU integration."""
    
    def __init__(self, config_path: Optional[str] = None, config_dict: Optional[Dict] = None):
        """
        Initialize configuration from file or dictionary.
        
        Args:
            config_path: Path to YAML or JSON configuration file
            config_dict: Dictionary with configuration
        """
        if config_path:
            self.config = self._load_config_file(config_path)
            self.config_path = config_path
        elif config_dict:
            self.config = config_dict
            self.config_path = None
        else:
            self.config = {}
            self.config_path = None
    
    def _load_config_file(self, config_path: str) -> Dict:
        """
        Load configuration from file.
        
        Args:
            config_path: Path to configuration file (YAML or JSON)
            
        Returns:
            Configuration dictionary
        
        Raises:
            ConfigurationError: If file format is not supported or file doesn't exist
        """
        path = Path(config_path)
        if not path.exists():
            raise ConfigurationError(f"Configuration file not found: {config_path}")
        
        suffix = path.suffix.lower()
        with open(path, 'r') as f:
            if suffix == '.yaml' or suffix == '.yml':
                return yaml.safe_load(f)
            elif suffix == '.json':
                return json.load(f)
            else:
                raise ConfigurationError(f"Unsupported configuration format: {suffix}")
    
    def get_model_config(self) -> Dict:
        """Get model configuration section."""
        return self.config.get('model', {})
    
    def get_parameters_config(self) -> Dict:
        """Get parameters configuration section."""
        return self.config.get('parameters', {})
    
    def get_kpis_config(self) -> Dict:
        """Get KPIs configuration section."""
        return self.config.get('kpis', {})
    
    def get_optimization_config(self) -> Dict:
        """Get optimization configuration section."""
        return self.config.get('optimization', {})
    
    def get_output_config(self) -> Dict:
        """Get output configuration section."""
        return self.config.get('output', {})
    
    def save(self, filepath: Optional[str] = None) -> None:
        """
        Save configuration to file.
        
        Args:
            filepath: Path to save the configuration
                     If None, uses the original config_path
        
        Raises:
            ConfigurationError: If no filepath specified and no original path exists
        """
        path = filepath or self.config_path
        
        if not path:
            raise ConfigurationError("No filepath specified and no original config_path exists")
        
        path = Path(path)
        suffix = path.suffix.lower()
        
        # Create directory if it doesn't exist
        os.makedirs(path.parent, exist_ok=True)
        
        with open(path, 'w') as f:
            if suffix == '.yaml' or suffix == '.yml':
                yaml.dump(self.config, f, default_flow_style=False)
            elif suffix == '.json':
                json.dump(self.config, f, indent=2)
            else:
                raise ConfigurationError(f"Unsupported configuration format: {suffix}")
    
    def validate(self) -> Tuple[bool, List[str]]:
        """
        Validate the configuration.
        
        Returns:
            Tuple of (is_valid, list_of_error_messages)
        """
        errors = []
        
        # Validate model section
        model_config = self.get_model_config()
        if not model_config:
            errors.append("Missing 'model' configuration section")
        elif 'type' not in model_config:
            errors.append("Missing 'type' in model configuration")
        
        if model_config.get('type') == 'cadcad':
            if 'module' not in model_config:
                errors.append("Missing 'module' in cadCAD model configuration")
        
        # Validate parameters section
        param_config = self.get_parameters_config()
        if not param_config:
            errors.append("Missing 'parameters' configuration section")
        
        # Validate optimization section
        opt_config = self.get_optimization_config()
        if not opt_config:
            errors.append("Missing 'optimization' configuration section")
        elif 'method' not in opt_config:
            errors.append("Missing 'method' in optimization configuration")
        elif 'objective' not in opt_config:
            errors.append("Missing 'objective' in optimization configuration")
        
        return len(errors) == 0, errors
    
    def load_model(self) -> Any:
        """
        Load the model specified in the configuration.
        
        Returns:
            Instantiated model object
            
        Raises:
            ConfigurationError: If model configuration is invalid
            ImportError: If module cannot be imported
        """
        model_config = self.get_model_config()
        if not model_config:
            raise ConfigurationError("Missing model configuration")
        
        model_type = model_config.get('type')
        if model_type == 'cadcad':
            module_name = model_config.get('module')
            if not module_name:
                raise ConfigurationError("Missing module name in cadCAD model configuration")
            
            try:
                module = importlib.import_module(module_name)
                
                # Get entry point class or function
                entry_point = model_config.get('entry_point', 'Model')
                if hasattr(module, entry_point):
                    model_class = getattr(module, entry_point)
                    if callable(model_class):
                        # If it's a class, instantiate it
                        if inspect.isclass(model_class):
                            # Pass any init parameters from config
                            init_params = model_config.get('init_params', {})
                            return model_class(**init_params)
                        # If it's already a function, return it
                        else:
                            return model_class
                else:
                    raise ConfigurationError(f"Entry point '{entry_point}' not found in module '{module_name}'")
            except ImportError as e:
                raise ImportError(f"Failed to import model module '{module_name}': {e}")
        else:
            raise ConfigurationError(f"Unsupported model type: {model_type}")
        
    def set_model_config(self, model_type: str, module: str, entry_point: str, init_params: Optional[Dict] = None) -> None:
        """
        Set the model configuration.
        
        Args:
            model_type: Type of model (e.g., 'cadcad')
            module: Module name
            entry_point: Entry point class or function name
            init_params: Parameters for model initialization
        """
        self.config['model'] = {
            'type': model_type,
            'module': module,
            'entry_point': entry_point
        }
        
        if init_params:
            self.config['model']['init_params'] = init_params
            
    def set_parameter_config(self, parameters: Dict[str, Any]) -> None:
        """
        Set the parameter configuration.
        
        Args:
            parameters: Parameter configuration dictionary
        """
        self.config['parameters'] = parameters
        
    def set_kpis_config(self, kpis: Dict[str, Any]) -> None:
        """
        Set the KPIs configuration.
        
        Args:
            kpis: KPIs configuration dictionary
        """
        self.config['kpis'] = kpis
        
    def set_optimization_config(self, method: str, objective: str, maximize: bool, iterations: int, options: Optional[Dict] = None) -> None:
        """
        Set the optimization configuration.
        
        Args:
            method: Optimization method
            objective: Objective KPI name
            maximize: Whether to maximize the objective
            iterations: Number of iterations
            options: Additional options for the optimizer
        """
        self.config['optimization'] = {
            'method': method,
            'objective': objective,
            'maximize': maximize,
            'iterations': iterations
        }
        
        if options:
            self.config['optimization']['options'] = options
            
    def set_output_config(self, directory: str, formats: List[str], save_all_runs: bool, visualizations: Optional[List[str]] = None) -> None:
        """
        Set the output configuration.
        
        Args:
            directory: Output directory
            formats: Output formats
            save_all_runs: Whether to save all runs
            visualizations: List of visualizations to generate
        """
        self.config['output'] = {
            'directory': directory,
            'formats': formats,
            'save_all_runs': save_all_runs
        }
        
        if visualizations:
            self.config['output']['visualizations'] = visualizations
