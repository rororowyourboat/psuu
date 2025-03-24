"""
Data Aggregator Module

This module handles the loading, processing, and aggregation of simulation results
and computes KPIs.
"""

from typing import Dict, List, Callable, Any, Union, Optional
import pandas as pd
import numpy as np
from collections import defaultdict


class KPICalculator:
    """
    Calculates Key Performance Indicators (KPIs) from simulation results.
    """
    
    def __init__(self):
        """Initialize the KPI calculator with an empty set of KPI functions."""
        self.kpi_functions: Dict[str, Callable[[pd.DataFrame], float]] = {}
        self.simple_kpis: Dict[str, Dict[str, Any]] = {}
    
    def add_kpi_function(self, name: str, function: Callable[[pd.DataFrame], float]) -> None:
        """
        Add a custom KPI calculation function.
        
        Args:
            name: Name of the KPI
            function: Function that takes a DataFrame and returns a numeric KPI value
        """
        self.kpi_functions[name] = function
    
    def add_simple_kpi(
        self, 
        name: str, 
        column: str, 
        operation: str,
        filter_condition: Optional[str] = None
    ) -> None:
        """
        Add a simple KPI based on column and aggregation operation.
        
        Args:
            name: Name of the KPI
            column: DataFrame column to operate on
            operation: Operation to perform ('max', 'min', 'mean', 'sum', etc.)
            filter_condition: Optional condition to filter the DataFrame before calculation
        """
        self.simple_kpis[name] = {
            "column": column,
            "operation": operation,
            "filter_condition": filter_condition
        }
    
    def calculate_kpis(self, df: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate all defined KPIs for a given DataFrame.
        
        Args:
            df: Simulation results DataFrame
            
        Returns:
            Dictionary of KPI names and values
        """
        results = {}
        
        # Calculate custom KPIs
        for name, func in self.kpi_functions.items():
            try:
                results[name] = func(df)
            except Exception as e:
                print(f"Error calculating KPI '{name}': {e}")
                results[name] = np.nan
        
        # Calculate simple KPIs
        for name, config in self.simple_kpis.items():
            try:
                # Apply filter if specified
                filtered_df = df
                if config["filter_condition"]:
                    filtered_df = df.query(config["filter_condition"])
                
                # Get the column and apply operation
                col = filtered_df[config["column"]]
                
                if config["operation"] == "max":
                    results[name] = col.max()
                elif config["operation"] == "min":
                    results[name] = col.min()
                elif config["operation"] == "mean":
                    results[name] = col.mean()
                elif config["operation"] == "sum":
                    results[name] = col.sum()
                elif config["operation"] == "count":
                    results[name] = col.count()
                elif config["operation"] == "median":
                    results[name] = col.median()
                elif config["operation"] == "std":
                    results[name] = col.std()
                else:
                    print(f"Unknown operation '{config['operation']}' for KPI '{name}'")
                    results[name] = np.nan
            except Exception as e:
                print(f"Error calculating simple KPI '{name}': {e}")
                results[name] = np.nan
        
        return results


class DataAggregator:
    """
    Aggregates and processes simulation results from multiple runs.
    """
    
    def __init__(self, kpi_calculator: Optional[KPICalculator] = None):
        """
        Initialize the data aggregator.
        
        Args:
            kpi_calculator: Optional KPI calculator for computing KPIs
        """
        self.kpi_calculator = kpi_calculator or KPICalculator()
        self.simulation_results: List[Dict[str, Any]] = []
    
    def add_simulation_result(
        self, 
        parameters: Dict[str, Any], 
        result_df: pd.DataFrame
    ) -> Dict[str, float]:
        """
        Add a simulation result and calculate its KPIs.
        
        Args:
            parameters: Parameters used for this simulation run
            result_df: DataFrame containing simulation results
            
        Returns:
            Dictionary of calculated KPI values
        """
        # Calculate KPIs
        kpis = self.kpi_calculator.calculate_kpis(result_df)
        
        # Store results
        result_entry = {
            "parameters": parameters.copy(),
            "kpis": kpis.copy(),
            "result_index": len(self.simulation_results)
        }
        self.simulation_results.append(result_entry)
        
        return kpis
    
    def get_best_result(
        self, 
        kpi_name: str, 
        maximize: bool = True
    ) -> Dict[str, Any]:
        """
        Get the best result based on a specific KPI.
        
        Args:
            kpi_name: Name of the KPI to optimize
            maximize: Whether to maximize (True) or minimize (False) the KPI
            
        Returns:
            Dictionary containing the best parameters and KPIs
            
        Raises:
            ValueError: If no results are available
        """
        if not self.simulation_results:
            raise ValueError("No simulation results available")
        
        # Filter out results with NaN values for the target KPI
        valid_results = [
            r for r in self.simulation_results 
            if kpi_name in r["kpis"] and not np.isnan(r["kpis"][kpi_name])
        ]
        
        if not valid_results:
            raise ValueError(f"No valid results for KPI '{kpi_name}'")
        
        # Sort by KPI value
        sorted_results = sorted(
            valid_results,
            key=lambda r: r["kpis"][kpi_name],
            reverse=maximize
        )
        
        return sorted_results[0]
    
    def get_all_results(self) -> pd.DataFrame:
        """
        Get all simulation results as a DataFrame.
        
        Returns:
            DataFrame with parameters and KPIs
        """
        rows = []
        
        for result in self.simulation_results:
            row = {}
            # Add parameters
            for param_name, param_value in result["parameters"].items():
                row[f"param_{param_name}"] = param_value
            
            # Add KPIs
            for kpi_name, kpi_value in result["kpis"].items():
                row[f"kpi_{kpi_name}"] = kpi_value
            
            rows.append(row)
        
        return pd.DataFrame(rows)
    
    def summarize_results(self) -> Dict[str, Dict[str, float]]:
        """
        Summarize results across all simulations.
        
        Returns:
            Dictionary of KPI names and their summary statistics
        """
        if not self.simulation_results:
            return {}
        
        # Collect all KPI values
        kpi_values = defaultdict(list)
        
        for result in self.simulation_results:
            for kpi_name, kpi_value in result["kpis"].items():
                if not np.isnan(kpi_value):
                    kpi_values[kpi_name].append(kpi_value)
        
        # Calculate summary statistics
        summary = {}
        for kpi_name, values in kpi_values.items():
            if values:
                summary[kpi_name] = {
                    "mean": np.mean(values),
                    "std": np.std(values),
                    "min": np.min(values),
                    "max": np.max(values),
                    "median": np.median(values),
                    "count": len(values)
                }
        
        return summary
