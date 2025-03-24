"""
Tests for the Simulation Connector module.
"""

import pytest
import os
import tempfile
import pandas as pd
from unittest.mock import patch, MagicMock

from psuu.simulation_connector import SimulationConnector


def test_build_command():
    """Test building command strings with parameters."""
    connector = SimulationConnector(
        command="python -m model",
        param_format="--{name} {value}"
    )
    
    params = {
        "beta": 0.3,
        "gamma": 0.1,
        "population": 1000
    }
    
    cmd = connector._build_command(params)
    
    # Command should include all parameters
    assert "python -m model" in cmd
    assert "--beta 0.3" in cmd
    assert "--gamma 0.1" in cmd
    assert "--population 1000" in cmd


@patch("subprocess.run")
def test_run_simulation_with_output_file(mock_run):
    """Test running simulation with output file."""
    # Create a temporary CSV file with test data
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_file:
        temp_file.write("time,S,I,R\n0,990,10,0\n1,980,15,5\n")
        output_file = temp_file.name
    
    try:
        # Configure mock
        mock_run.return_value = MagicMock(returncode=0)
        
        # Create connector with output file
        connector = SimulationConnector(
            command="python -m model",
            output_format="csv",
            output_file=output_file
        )
        
        # Run simulation
        params = {"beta": 0.3, "gamma": 0.1}
        result = connector.run_simulation(params)
        
        # Verify command was called correctly
        mock_run.assert_called_once()
        assert isinstance(result, pd.DataFrame)
        assert list(result.columns) == ["time", "S", "I", "R"]
        assert len(result) == 2
    
    finally:
        # Clean up
        if os.path.exists(output_file):
            os.unlink(output_file)


@patch("subprocess.run")
def test_run_simulation_with_stdout(mock_run):
    """Test running simulation with output captured from stdout."""
    # Configure mock
    mock_process = MagicMock()
    mock_process.stdout = "time,S,I,R\n0,990,10,0\n1,980,15,5\n"
    mock_run.return_value = mock_process
    
    # Create connector without output file
    connector = SimulationConnector(
        command="python -m model",
        output_format="csv"
    )
    
    # Run simulation
    params = {"beta": 0.3, "gamma": 0.1}
    
    with patch("tempfile.NamedTemporaryFile", MagicMock()) as mock_temp:
        result = connector.run_simulation(params)
    
    # Verify command was called correctly
    mock_run.assert_called_once()
