"""
Simulation Connector Module

This module provides the interface for running external simulation models via CLI
and collecting their outputs.
"""

import subprocess
from typing import Dict, Optional, Union, List, Any
import tempfile
import os
import json
import pandas as pd


class SimulationConnector:
    """
    Connects to and runs external simulation models through command-line interfaces.
    
    This class handles the execution of simulation models, passing parameters,
    and collecting output data.
    """
    
    def __init__(
        self, 
        command: str,
        param_format: str = "--{name} {value}",
        output_format: str = "csv",
        output_file: Optional[str] = None,
        working_dir: Optional[str] = None,
    ):
        """
        Initialize the simulation connector.
        
        Args:
            command: Base command to execute the simulation
            param_format: Format string for parameter arguments
            output_format: Format of the simulation output ('csv' or 'json')
            output_file: Filename where simulation writes its output (if None, uses stdout)
            working_dir: Working directory for the simulation command
        """
        self.command = command
        self.param_format = param_format
        self.output_format = output_format
        self.output_file = output_file
        self.working_dir = working_dir
    
    def _build_command(self, parameters: Dict[str, Any]) -> str:
        """
        Build the full command string with parameters.
        
        Args:
            parameters: Dictionary of parameter names and values
            
        Returns:
            Full command string with parameters
        """
        param_strings = []
        
        for name, value in parameters.items():
            param_str = self.param_format.format(name=name, value=value)
            param_strings.append(param_str)
        
        return f"{self.command} {' '.join(param_strings)}"
    
    def run_simulation(self, parameters: Dict[str, Any]) -> pd.DataFrame:
        """
        Run the simulation with the given parameters and return results.
        
        Args:
            parameters: Dictionary of parameter names and values
            
        Returns:
            DataFrame containing simulation results
            
        Raises:
            subprocess.CalledProcessError: If the simulation command fails
        """
        cmd = self._build_command(parameters)
        
        if self.output_file:
            # Run simulation, writing to specified output file
            subprocess.run(
                cmd, 
                shell=True, 
                check=True,
                cwd=self.working_dir
            )
            return self._load_output(self.output_file)
        else:
            # Run simulation, capturing output directly
            result = subprocess.run(
                cmd,
                shell=True,
                check=True,
                capture_output=True,
                text=True,
                cwd=self.working_dir
            )
            
            # Save output to temporary file
            with tempfile.NamedTemporaryFile(
                mode='w+', 
                suffix=f'.{self.output_format}',
                delete=False
            ) as temp_file:
                temp_file.write(result.stdout)
                temp_file_path = temp_file.name
            
            try:
                return self._load_output(temp_file_path)
            finally:
                os.unlink(temp_file_path)
    
    def _load_output(self, file_path: str) -> pd.DataFrame:
        """
        Load simulation output from file.
        
        Args:
            file_path: Path to the output file
            
        Returns:
            DataFrame containing simulation results
        
        Raises:
            ValueError: If output format is not supported
        """
        if self.output_format.lower() == 'csv':
            return pd.read_csv(file_path)
        elif self.output_format.lower() == 'json':
            return pd.read_json(file_path)
        else:
            raise ValueError(f"Unsupported output format: {self.output_format}")
