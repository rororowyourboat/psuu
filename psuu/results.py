"""
Simulation Results Module for PSUU.

This module provides standardized containers for simulation results.
"""

from typing import Dict, Any, List, Optional, Union
import pandas as pd
import numpy as np
import json
import os
import pickle
import time

# Custom JSON encoder to handle NumPy types
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)


def convert_numpy_types(obj: Any) -> Any:
    """Convert NumPy types to native Python types."""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {k: convert_numpy_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    else:
        return obj


class SimulationResults:
    """
    Standardized container for simulation results.
    
    This class provides a unified interface for accessing simulation results,
    including time series data and calculated KPIs.
    """
    
    def __init__(
        self, 
        time_series_data: Optional[pd.DataFrame] = None,
        kpis: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        raw_data: Optional[Any] = None,
        parameters: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the results container.
        
        Args:
            time_series_data: DataFrame containing time series data from simulation
            kpis: Dictionary of calculated KPI values
            metadata: Dictionary of metadata about the simulation run
            raw_data: Raw simulation output in model-specific format
            parameters: Parameters used for this simulation run
        """
        self.time_series_data = time_series_data if time_series_data is not None else pd.DataFrame()
        self.kpis = kpis or {}
        self.metadata = metadata or {}
        self.raw_data = raw_data
        self.parameters = parameters or {}
        
        # Add timestamp if not provided
        if 'timestamp' not in self.metadata:
            self.metadata['timestamp'] = time.time()
    
    def to_dataframe(self) -> pd.DataFrame:
        """
        Convert to DataFrame format for PSUU.
        
        Returns:
            DataFrame containing simulation results and/or KPIs
        """
        if self.time_series_data.empty and self.kpis:
            # Create a single-row DataFrame with KPI values
            df = pd.DataFrame([self.kpis])
            
            # Add parameters as columns
            for param_name, param_value in self.parameters.items():
                df[f"param_{param_name}"] = param_value
                
            return df
            
        elif not self.time_series_data.empty and self.kpis:
            # Add KPIs as columns to the time series data for the last timestep
            last_row = self.time_series_data.iloc[[-1]].copy()
            for kpi_name, kpi_value in self.kpis.items():
                last_row[kpi_name] = kpi_value
                
            # Add parameters as columns if not already present
            for param_name, param_value in self.parameters.items():
                param_col = f"param_{param_name}"
                if param_col not in self.time_series_data.columns:
                    self.time_series_data[param_col] = param_value
                    
            return pd.concat([self.time_series_data, last_row]).reset_index(drop=True)
        else:
            return self.time_series_data
    
    def get_kpi(self, name: str, default: Any = None) -> Any:
        """
        Get a specific KPI value.
        
        Args:
            name: Name of the KPI
            default: Default value to return if KPI not found
            
        Returns:
            KPI value or default
        """
        return self.kpis.get(name, default)
    
    def add_kpi(self, name: str, value: Any) -> None:
        """
        Add a KPI value to the results.
        
        Args:
            name: Name of the KPI
            value: Value of the KPI
        """
        self.kpis[name] = value
    
    def update_kpis(self, kpis: Dict[str, Any]) -> None:
        """
        Update multiple KPIs at once.
        
        Args:
            kpis: Dictionary of KPI names and values
        """
        self.kpis.update(kpis)
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the simulation results.
        
        Returns:
            Dictionary containing summary information
        """
        summary = {
            "metadata": convert_numpy_types(self.metadata),
            "kpis": convert_numpy_types(self.kpis),
            "parameters": convert_numpy_types(self.parameters),
        }
        
        if not self.time_series_data.empty:
            # Add basic statistics for numeric columns
            numeric_cols = self.time_series_data.select_dtypes(include=[np.number]).columns
            stats = {}
            
            for col in numeric_cols:
                # Skip parameter columns
                if col.startswith("param_"):
                    continue
                    
                stats[f"{col}_stats"] = {
                    "mean": float(self.time_series_data[col].mean()),
                    "min": float(self.time_series_data[col].min()),
                    "max": float(self.time_series_data[col].max()),
                    "std": float(self.time_series_data[col].std()),
                }
                
            summary["statistics"] = stats
        
        return summary
    
    def save(self, filepath: str, formats: List[str] = None) -> Dict[str, str]:
        """
        Save the results to file(s).
        
        Args:
            filepath: Base filepath without extension
            formats: List of formats to save (default: ['csv', 'json'])
            
        Returns:
            Dictionary mapping format to saved filepath
        """
        formats = formats or ['csv', 'json']
        saved_files = {}
        
        # Create directory if needed
        os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
        
        for fmt in formats:
            if fmt.lower() == 'csv' and not self.time_series_data.empty:
                csv_path = f"{filepath}.csv"
                self.time_series_data.to_csv(csv_path, index=False)
                saved_files['csv'] = csv_path
            
            elif fmt.lower() == 'json':
                json_path = f"{filepath}.json"
                json_data = {
                    "metadata": convert_numpy_types(self.metadata),
                    "kpis": convert_numpy_types(self.kpis),
                    "parameters": convert_numpy_types(self.parameters),
                }
                
                # Add time series data if available
                if not self.time_series_data.empty:
                    # Convert to records format for JSON
                    json_data["time_series"] = convert_numpy_types(
                        self.time_series_data.to_dict(orient='records')
                    )
                
                with open(json_path, 'w') as f:
                    json.dump(json_data, f, indent=2, cls=NumpyEncoder)
                
                saved_files['json'] = json_path
            
            elif fmt.lower() == 'pickle':
                pickle_path = f"{filepath}.pkl"
                with open(pickle_path, 'wb') as f:
                    pickle.dump(self, f)
                saved_files['pickle'] = pickle_path
                
            elif fmt.lower() == 'yaml':
                try:
                    import yaml
                    yaml_path = f"{filepath}.yaml"
                    
                    # Prepare data for YAML
                    yaml_data = {
                        "metadata": convert_numpy_types(self.metadata),
                        "kpis": convert_numpy_types(self.kpis),
                        "parameters": convert_numpy_types(self.parameters),
                    }
                    
                    with open(yaml_path, 'w') as f:
                        yaml.dump(yaml_data, f, default_flow_style=False)
                        
                    saved_files['yaml'] = yaml_path
                except ImportError:
                    print("PyYAML not installed. Skipping YAML export.")
        
        return saved_files
