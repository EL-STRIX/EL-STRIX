"""End-to-End Pipeline tests."""

import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../scripts")))

import main


def test_full_pipeline_execution(mocker):
    """Test the complete execution of EL-STRIX phases."""
    # Mock initialize dependencies
    mocker.patch("main.initialize")
    
    # Mock Phase Executions 
    mock_run_phase_02 = mocker.patch("main.run_phase_02")
    mock_run_phase_03 = mocker.patch("main.run_phase_03")
    mock_run_phase_04 = mocker.patch("main.run_phase_04")
    mock_run_phase_05 = mocker.patch("main.run_phase_05")
    mock_run_phase_06 = mocker.patch("main.run_phase_06")
    mock_run_phase_07 = mocker.patch("main.run_phase_07")
    
    # Run the main pipeline
    try:
        main.main()
    except Exception as e:
        pytest.fail(f"Pipeline execution failed: {e}")
        
    # Verify all phases were called
    mock_run_phase_02.assert_called_once()
    mock_run_phase_03.assert_called_once()
    mock_run_phase_04.assert_called_once()
    mock_run_phase_05.assert_called_once()
    mock_run_phase_06.assert_called_once()
    mock_run_phase_07.assert_called_once()

def test_pipeline_failure_handling(mocker):
    """Test pipeline gracefully exits on fatal phase error."""
    mocker.patch("main.initialize")
    mocker.patch("main.run_phase_02", side_effect=SystemExit(1))
    
    with pytest.raises(SystemExit):
        main.main()
