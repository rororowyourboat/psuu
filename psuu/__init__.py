"""
PSUU - Parameter Selection Under Uncertainty

A framework for automated parameter selection and optimization 
for simulation models under uncertainty.
"""

from .experiment import PsuuExperiment, quick_optimize
from .version import __version__

__all__ = ["PsuuExperiment", "quick_optimize", "__version__"]
