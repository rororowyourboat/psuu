"""
Protocols module for PSUU.

This module provides protocol interfaces for standardizing 
the integration of simulation models with PSUU.
"""

from .cadcad_protocol import CadcadModelProtocol
from .model_protocol import ModelProtocol

__all__ = ['ModelProtocol', 'CadcadModelProtocol']
