"""
Optimizers package for parameter selection.

This package contains various optimization algorithms for exploring parameter spaces.
"""

from .base import Optimizer
from .grid_search import GridSearchOptimizer
from .random_search import RandomSearchOptimizer

# Define available optimizers
AVAILABLE_OPTIMIZERS = {
    "grid": GridSearchOptimizer,
    "random": RandomSearchOptimizer,
}

try:
    from .bayesian import BayesianOptimizer
    AVAILABLE_OPTIMIZERS["bayesian"] = BayesianOptimizer
except ImportError:
    # Bayesian optimization requires additional dependencies
    pass

__all__ = [
    "Optimizer",
    "GridSearchOptimizer",
    "RandomSearchOptimizer",
    "AVAILABLE_OPTIMIZERS",
]
