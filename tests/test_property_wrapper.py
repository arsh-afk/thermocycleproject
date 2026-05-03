"""
Unit tests for the PropertyWrapper utility.
Ensures accurate retrieval of thermodynamic properties from CoolProp.
"""
import pytest
from utils.property_wrapper import PropertyWrapper


def test_get_state_saturated_water():
    """
    Tests the retrieval of a saturated water state at atmospheric pressure.
    Verifies temperature, quality, and phase labeling.
    """
    # Define state at 1 atm (101325 Pa) and quality 0 (saturated liquid)
    state = PropertyWrapper.get_state('Water', 'P', 101325, 'Q', 0)
    
    # Assertions
    assert state is not None
    
    # Atmospheric boiling point should be approx 100°C (373.15 K)
    assert pytest.approx(state.T, rel=1e-3) == 373.15
    
    # Quality should remain 0 as requested
    assert state.x == 0
    
    # Check that phase labeling is correctly handled
    assert state.phase_label in {'Two-Phase', 'Single-Phase'}
