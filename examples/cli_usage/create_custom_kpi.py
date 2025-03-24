#!/usr/bin/env python
"""
Custom KPI Module for CLI Example

This module demonstrates how to create custom KPI functions that can be
used with the PSUU CLI through the configuration file.
"""

import pandas as pd
import numpy as np


def epidemic_duration(df, threshold=1.0):
    """
    Calculate the duration of an epidemic.
    
    Args:
        df: DataFrame with simulation results
        threshold: Infection threshold to consider epidemic active
        
    Returns:
        Duration in timesteps
    """
    if 'I' not in df.columns or df.empty:
        return 0.0
    
    # Get periods where infections are above threshold
    above_threshold = df[df['I'] > threshold]
    
    if above_threshold.empty:
        return 0.0
    
    # Calculate duration (last timestep with infections above threshold - first)
    return float(above_threshold['timestep'].max() - above_threshold['timestep'].min())


def peak_timing(df):
    """
    Calculate when the peak of infections occurs.
    
    Args:
        df: DataFrame with simulation results
        
    Returns:
        Timestep of peak infections
    """
    if 'I' not in df.columns or df.empty:
        return 0.0
    
    # Find the timestep with maximum infections
    peak_idx = df['I'].idxmax()
    return float(df.loc[peak_idx, 'timestep'])


def infection_rate_of_change(df, window=5):
    """
    Calculate the maximum rate of change of infections.
    
    Args:
        df: DataFrame with simulation results
        window: Window size for rolling calculation
        
    Returns:
        Maximum rate of change in infections
    """
    if 'I' not in df.columns or df.empty or len(df) < window:
        return 0.0
    
    # Sort by timestep to ensure proper order
    df_sorted = df.sort_values('timestep')
    
    # Calculate change in infections
    df_sorted['I_diff'] = df_sorted['I'].diff()
    
    # Calculate rolling mean of change
    df_sorted['I_diff_rolling'] = df_sorted['I_diff'].rolling(window=window).mean()
    
    # Return the maximum rate of change (could be negative if focusing on decline)
    return float(df_sorted['I_diff_rolling'].max())


def herd_immunity_threshold(df, population_column='S', initial_population=None):
    """
    Calculate how many people need to be immune for herd immunity.
    
    Args:
        df: DataFrame with simulation results
        population_column: Column with susceptible population
        initial_population: Initial total population (if None, inferred from data)
        
    Returns:
        Percentage of population needed for herd immunity
    """
    if population_column not in df.columns or df.empty:
        return 0.0
    
    # Determine total population
    if initial_population is None:
        # Assume first row has initial susceptible population
        initial_population = df[population_column].iloc[0]
    
    # Calculate minimum susceptible population (when epidemic starts declining)
    peak_idx = df['I'].idxmax()
    
    # If peak is at the very start or end, return 0
    if peak_idx == 0 or peak_idx == len(df) - 1:
        return 0.0
    
    # Get susceptible population at peak
    s_at_peak = df.loc[peak_idx, population_column]
    
    # Calculate herd immunity threshold as percentage
    herd_threshold = 1.0 - (s_at_peak / initial_population)
    
    return float(herd_threshold * 100)  # Return as percentage


if __name__ == "__main__":
    print("This module contains custom KPI functions for use with PSUU CLI.")
    print("Import it in your psuu_config.yaml file using the 'module' parameter.")
