import pytest
from utils.property_wrapper import PropertyWrapper


def test_get_state_saturated_water():
    state = PropertyWrapper.get_state('Water', 'P', 101325, 'Q', 0)
    assert state is not None
    assert pytest.approx(state.T, rel=1e-3) == 373.15
    assert state.x == 0
    assert state.phase_label in {'Two-Phase', 'Single-Phase'}
