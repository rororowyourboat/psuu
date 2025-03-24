"""
Exceptions Module for PSUU.

This module provides custom exceptions for PSUU.
"""

class PsuuError(Exception):
    """Base class for all PSUU exceptions."""
    pass

class ModelInitializationError(PsuuError):
    """Error during model initialization."""
    pass

class ModelExecutionError(PsuuError):
    """Error during model execution."""
    pass

class ParameterValidationError(PsuuError):
    """Error during parameter validation."""
    pass

class KpiCalculationError(PsuuError):
    """Error during KPI calculation."""
    pass

class ConfigurationError(PsuuError):
    """Error in configuration."""
    pass

class SimulationError(PsuuError):
    """Error during simulation execution."""
    pass

class OptimizationError(PsuuError):
    """Error during optimization."""
    pass

class ResultsError(PsuuError):
    """Error with simulation results."""
    pass
