"""
KPI calculation module.

This module defines functions to calculate Key Performance Indicators (KPIs)
from simulation results.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any


def peak_infected(df: pd.DataFrame) -> float:
    """
    Calculate the peak number of infected individuals.
    
    Args:
        df: Simulation results DataFrame
        
    Returns:
        Maximum number of infected individuals
    """
    if df.empty or 'infected' not in df.columns:
        return 0.0
    
    return df['infected'].max()


def total_infected(df: pd.DataFrame) -> float:
    """
    Calculate the total number of individuals who became infected.
    
    Args:
        df: Simulation results DataFrame
        
    Returns:
        Total number of individuals who were infected
    """
    if df.empty or 'susceptible' not in df.columns:
        return 0.0
    
    # Total infected is the difference between initial susceptible and final susceptible
    initial_susceptible = df['susceptible'].iloc[0]
    final_susceptible = df['susceptible'].iloc[-1]
    
    return initial_susceptible - final_susceptible


def epidemic_duration(df: pd.DataFrame, threshold: float = 1.0) -> float:
    """
    Calculate the duration of the epidemic in timesteps.
    
    Args:
        df: Simulation results DataFrame
        threshold: Infection threshold to consider the epidemic active
        
    Returns:
        Duration of the epidemic in timesteps
    """
    if df.empty or 'infected' not in df.columns:
        return 0.0
    
    # Find where infection is above threshold
    above_threshold = df[df['infected'] > threshold]
    
    if above_threshold.empty:
        return 0.0
    
    # Duration is from first to last timestep with infections above threshold
    first_timestep = above_threshold['timestep'].min()
    last_timestep = above_threshold['timestep'].max()
    
    return last_timestep - first_timestep + 1


def calculate_r0(params: Dict[str, Any]) -> float:
    """
    Calculate the basic reproduction number (R0).
    
    Args:
        params: Model parameters
        
    Returns:
        Basic reproduction number (R0)
    """
    beta = params.get('beta', 0.0)
    gamma = params.get('gamma', 1.0)  # Avoid division by zero
    
    return beta / gamma


def get_all_kpis() -> Dict[str, Any]:
    """
    Get all KPI calculation functions.
    
    Returns:
        Dictionary mapping KPI names to calculation functions
    """
    return {
        "peak_infected": peak_infected,
        "total_infected": total_infected,
        "epidemic_duration": epidemic_duration,
        # For R0, we need a special wrapper since it depends on parameters, not data
        "r0": lambda df, params=None: calculate_r0(params) if params else 0.0
    }
