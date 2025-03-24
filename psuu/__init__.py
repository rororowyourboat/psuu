"""
PSUU - Parameter Selection Under Uncertainty

A framework for automated parameter selection and optimization 
for simulation models under uncertainty.
"""

from .experiment import PsuuExperiment, quick_optimize
from .protocols import ModelProtocol, CadcadModelProtocol
from .results import SimulationResults
from .config import PsuuConfig
from .validation import ParameterValidator, RobustCadcadConnector
from .exceptions import (
    PsuuError,
    ModelInitializationError,
    ModelExecutionError,
    ParameterValidationError,
    KpiCalculationError,
    ConfigurationError,
    SimulationError,
    OptimizationError,
    ResultsError
)
from .version import __version__

__all__ = [
    "PsuuExperiment",
    "quick_optimize",
    "ModelProtocol",
    "CadcadModelProtocol",
    "SimulationResults",
    "PsuuConfig",
    "ParameterValidator",
    "RobustCadcadConnector",
    "PsuuError",
    "ModelInitializationError",
    "ModelExecutionError",
    "ParameterValidationError",
    "KpiCalculationError",
    "ConfigurationError",
    "SimulationError",
    "OptimizationError",
    "ResultsError",
    "__version__"
]
