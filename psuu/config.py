"""
Configuration Module for PSUU.

This module provides configuration handling for PSUU integration,
including loading and validating YAML configuration files.
"""

import os
import yaml
import json
from typing import Dict, Any, Optional, List, Union, Tuple, Type
import importlib
import logging
from pathlib import Path

from .exceptions import ConfigurationError

# Set up logging
logger = logging.getLogger(__name__)


class PsuuConfig:
    """
    Configuration handler for PSUU integration.
    
    This class provides methods for loading, validating, and accessing
    configuration settings for PSUU experiments.
    """
    
    def __init__(self, config_path: Optional[str] = None, config_dict: Optional[Dict] = None):
        """
        Initialize configuration from file or dictionary.
        
        Args:
            config_path: Path to YAML or JSON configuration file
            config_dict: Dictionary with configuration
            
        Raises:
            ConfigurationError: If file format is not supported or file doesn't exist
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
    
    def get_advanced_config(self) -> Dict:
        """Get advanced configuration section."""
        return self.config.get('advanced', {})
    
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
        Validate the configuration against schema requirements.
        
        Returns:
            Tuple of (is_valid, list_of_error_messages)
        """
        errors = []
        
        # Validate model section
        try:
            self._validate_model_section()
        except ConfigurationError as e:
            errors.append(str(e))
        
        # Validate parameters section
        try:
            self._validate_parameters_section()
        except ConfigurationError as e:
            errors.append(str(e))
        
        # Validate KPIs section if present
        if 'kpis' in self.config:
            try:
                self._validate_kpis_section()
            except ConfigurationError as e:
                errors.append(str(e))
        
        # Validate optimization section if present
        if 'optimization' in self.config:
            try:
                self._validate_optimization_section()
            except ConfigurationError as e:
                errors.append(str(e))
        
        return len(errors) == 0, errors
    
    def _validate_model_section(self) -> None:
        """
        Validate model section of configuration.
        
        Raises:
            ConfigurationError: If model configuration is invalid
        """
        model_config = self.get_model_config()
        if not model_config:
            raise ConfigurationError("Missing 'model' configuration section")
        
        # Check if using CLI or Protocol integration
        if 'class' in model_config:
            # Protocol integration
            if not isinstance(model_config['class'], str):
                raise ConfigurationError("Model 'class' must be a string")
            
            # Protocol is optional, defaults to 'cadcad'
            if 'protocol' in model_config and not isinstance(model_config['protocol'], str):
                raise ConfigurationError("Model 'protocol' must be a string")
                
        elif 'entry_point' in model_config:
            # CLI integration
            required_fields = ['entry_point', 'param_format', 'output_format']
            for field in required_fields:
                if field not in model_config:
                    raise ConfigurationError(f"Missing required field in model section: {field}")
                    
            if not isinstance(model_config['entry_point'], str):
                raise ConfigurationError("Model 'entry_point' must be a string")
                
            if not isinstance(model_config['param_format'], str):
                raise ConfigurationError("Model 'param_format' must be a string")
                
            if model_config['output_format'] not in ['json', 'csv']:
                raise ConfigurationError("Model 'output_format' must be 'json' or 'csv'")
        else:
            raise ConfigurationError("Model section must specify either 'class' or 'entry_point'")
    
    def _validate_parameters_section(self) -> None:
        """
        Validate parameters section of configuration.
        
        Raises:
            ConfigurationError: If parameters configuration is invalid
        """
        params_config = self.get_parameters_config()
        if not params_config:
            raise ConfigurationError("Missing 'parameters' configuration section")
        
        for param_name, param_def in params_config.items():
            if not isinstance(param_def, dict):
                raise ConfigurationError(f"Parameter '{param_name}' definition must be a dictionary")
            
            # Check parameter type
            if 'type' not in param_def:
                raise ConfigurationError(f"Parameter '{param_name}' missing 'type'")
            
            param_type = param_def['type'].lower()
            if param_type == 'continuous':
                # Continuous parameters need min and max
                if 'min' not in param_def or 'max' not in param_def:
                    raise ConfigurationError(f"Continuous parameter '{param_name}' must have 'min' and 'max'")
                if param_def['min'] >= param_def['max']:
                    raise ConfigurationError(f"Parameter '{param_name}': min must be less than max")
                    
            elif param_type == 'integer':
                # Integer parameters need either min/max or values
                if ('min' in param_def and 'max' in param_def):
                    if param_def['min'] >= param_def['max']:
                        raise ConfigurationError(f"Parameter '{param_name}': min must be less than max")
                elif 'values' not in param_def:
                    raise ConfigurationError(f"Integer parameter '{param_name}' must have 'min'/'max' or 'values'")
                    
            elif param_type == 'categorical':
                # Categorical parameters need values
                if 'values' not in param_def:
                    raise ConfigurationError(f"Categorical parameter '{param_name}' must have 'values'")
                if not isinstance(param_def['values'], list):
                    raise ConfigurationError(f"Parameter '{param_name}': 'values' must be a list")
                    
            else:
                raise ConfigurationError(f"Unknown parameter type for '{param_name}': {param_type}")
    
    def _validate_kpis_section(self) -> None:
        """
        Validate KPIs section of configuration.
        
        Raises:
            ConfigurationError: If KPIs configuration is invalid
        """
        kpis_config = self.get_kpis_config()
        if not kpis_config:
            logger.warning("KPIs section is empty. No optimization objectives defined.")
            return
        
        # Check if at least one KPI has an objective
        has_objective = False
        for kpi_name, kpi_def in kpis_config.items():
            if not isinstance(kpi_def, dict):
                raise ConfigurationError(f"KPI '{kpi_name}' definition must be a dictionary")
            
            if 'objective' in kpi_def:
                has_objective = True
                objective = kpi_def['objective'].lower()
                if objective not in ['maximize', 'minimize']:
                    raise ConfigurationError(f"KPI '{kpi_name}': objective must be 'maximize' or 'minimize'")
            
            # Validate constraints if present
            if 'constraint' in kpi_def:
                constraint = kpi_def['constraint']
                if not isinstance(constraint, str) or not any(op in constraint for op in ['<=', '>=', '==', '<', '>']):
                    raise ConfigurationError(f"KPI '{kpi_name}': constraint must be a string with comparison operator")
        
        if not has_objective:
            logger.warning("No optimization objectives defined in KPIs section.")
    
    def _validate_optimization_section(self) -> None:
        """
        Validate optimization section of configuration.
        
        Raises:
            ConfigurationError: If optimization configuration is invalid
        """
        opt_config = self.get_optimization_config()
        if not opt_config:
            raise ConfigurationError("Missing 'optimization' configuration section")
            
        if 'algorithm' not in opt_config:
            raise ConfigurationError("Optimization section must specify 'algorithm'")
        
        algorithm = opt_config['algorithm'].lower()
        
        # Check for required parameters based on algorithm
        if algorithm in ['random', 'grid', 'bayesian']:
            if 'iterations' not in opt_config:
                raise ConfigurationError(f"Algorithm '{algorithm}' requires 'iterations'")
        
        elif algorithm in ['nsga2', 'genetic']:
            if 'population_size' not in opt_config:
                raise ConfigurationError(f"Algorithm '{algorithm}' requires 'population_size'")
            if 'generations' not in opt_config:
                raise ConfigurationError(f"Algorithm '{algorithm}' requires 'generations'")
    
    def import_model_class(self) -> Any:
        """
        Import the model class specified in the configuration.
        
        Returns:
            The imported model class
            
        Raises:
            ConfigurationError: If model configuration is invalid
            ImportError: If class cannot be imported
        """
        model_config = self.get_model_config()
        if 'class' not in model_config:
            raise ConfigurationError("No model class specified in configuration")
            
        class_path = model_config['class']
        try:
            module_path, class_name = class_path.rsplit('.', 1)
            module = importlib.import_module(module_path)
            cls = getattr(module, class_name)
            return cls
        except (ImportError, AttributeError, ValueError) as e:
            raise ImportError(f"Failed to import model class '{class_path}': {str(e)}")
    
    def create_parameter_space(self) -> Dict[str, Union[List, Tuple]]:
        """
        Convert parameters configuration to PSUU parameter space format.
        
        Returns:
            Dictionary mapping parameter names to ranges or values in PSUU format
        """
        params_config = self.get_parameters_config()
        parameter_space = {}
        
        for param_name, param_def in params_config.items():
            param_type = param_def['type'].lower()
            
            if param_type == 'continuous':
                # Continuous parameters as (min, max) tuple
                parameter_space[param_name] = (param_def['min'], param_def['max'])
                
            elif param_type == 'integer':
                # Integer parameters as list or tuple
                if 'values' in param_def:
                    parameter_space[param_name] = param_def['values']
                else:
                    # Use range for optimization, not explicit list (more efficient)
                    parameter_space[param_name] = (param_def['min'], param_def['max'])
                    
            elif param_type == 'categorical':
                # Categorical parameters as list
                parameter_space[param_name] = param_def['values']
        
        return parameter_space
    
    def get_objective_kpi(self) -> Tuple[Optional[str], Optional[bool]]:
        """
        Get the objective KPI name and direction.
        
        Returns:
            Tuple of (kpi_name, maximize_flag) or (None, None) if no objective
        """
        kpis_config = self.get_kpis_config()
        
        # Find the first KPI marked as objective
        for kpi_name, kpi_def in kpis_config.items():
            if 'objective' in kpi_def:
                return kpi_name, kpi_def['objective'].lower() == 'maximize'
        
        return None, None
    
    def get_optimizer_settings(self) -> Dict[str, Any]:
        """
        Get optimizer settings.
        
        Returns:
            Dictionary with optimizer settings
        """
        opt_config = self.get_optimization_config()
        if not opt_config:
            return {}
            
        algorithm = opt_config.get('algorithm')
        if not algorithm:
            return {}
            
        settings = {'method': algorithm.lower()}
        
        # Add algorithm-specific settings
        if algorithm.lower() in ['random', 'grid', 'bayesian']:
            if 'iterations' in opt_config:
                settings['num_iterations'] = opt_config['iterations']
                
            if algorithm.lower() == 'bayesian' and 'initial_points' in opt_config:
                settings['initial_points'] = opt_config['initial_points']
                
        elif algorithm.lower() in ['nsga2', 'genetic']:
            if 'population_size' in opt_config:
                settings['population_size'] = opt_config['population_size']
                
            if 'generations' in opt_config:
                settings['num_generations'] = opt_config['generations']
        
        # Add any other settings in the 'options' dictionary
        if 'options' in opt_config:
            for key, value in opt_config['options'].items():
                settings[key] = value
                
        return settings


def configure_experiment_from_yaml(config_path: str) -> 'PsuuExperiment':
    """
    Configure a PSUU experiment from YAML file.
    
    Args:
        config_path: Path to YAML configuration file
        
    Returns:
        Configured PsuuExperiment object
        
    Raises:
        Various exceptions if configuration is invalid
    """
    # Import here to avoid circular imports
    from .experiment import PsuuExperiment
    
    # Load configuration
    config = PsuuConfig(config_path)
    
    # Validate configuration
    is_valid, errors = config.validate()
    if not is_valid:
        error_msg = "\n".join(errors)
        raise ConfigurationError(f"Invalid configuration:\n{error_msg}")
    
    # Create experiment based on model type
    model_config = config.get_model_config()
    experiment = None
    
    if 'class' in model_config:
        # Protocol integration - import and instantiate model class
        model_class = config.import_model_class()
        
        # Check for init parameters
        init_params = model_config.get('init_params', {})
        model = model_class(**init_params)
        
        # Create experiment with model
        experiment = PsuuExperiment(model=model)
        
    else:
        # CLI integration
        cmd = model_config['entry_point']
        param_format = model_config['param_format']
        output_format = model_config['output_format']
        working_dir = model_config.get('working_dir')
        
        # Check if we need a custom connector
        if model_config.get('type') == 'cadcad':
            # Import cadcad connector here to avoid circular imports
            from .custom_connectors.cadcad_connector import CadcadSimulationConnector
            
            # Create experiment with cadcad connector
            experiment = PsuuExperiment(
                simulation_command=cmd,
                param_format=param_format,
                output_format=output_format,
                working_dir=working_dir,
                connector_class=CadcadSimulationConnector
            )
        else:
            # Create standard experiment
            experiment = PsuuExperiment(
                simulation_command=cmd,
                param_format=param_format,
                output_format=output_format,
                working_dir=working_dir
            )
    
    # Configure parameter space
    parameter_space = config.create_parameter_space()
    experiment.set_parameter_space(parameter_space)
    
    # Configure KPIs from KPIs section
    kpis_config = config.get_kpis_config()
    for kpi_name, kpi_def in kpis_config.items():
        # Currently we don't have a good way to define complex KPI calculations in YAML
        # so we just register the KPI name and assume it matches a column or results field
        experiment.add_kpi(
            name=kpi_name,
            column=kpi_name  # Assume column name matches KPI name
        )
    
    # Configure optimizer
    objective_name, maximize = config.get_objective_kpi()
    optimizer_settings = config.get_optimizer_settings()
    
    if objective_name and 'method' in optimizer_settings:
        # Extract method and remove from settings
        method = optimizer_settings.pop('method')
        
        # Configure optimizer with remaining settings as kwargs
        experiment.set_optimizer(
            method=method,
            objective_name=objective_name,
            maximize=maximize,
            **optimizer_settings
        )
    
    return experiment
