"""
Unit tests for the RankineCycle implementation.
Validates the thermodynamic solver and performance metric calculations.
"""
from core.rankine_cycle import RankineCycle


def test_rankine_cycle_baseline():
    """
    Tests a basic Rankine cycle simulation with typical power plant parameters.
    Verifies that the solver completes and returns physically meaningful metrics.
    """
    cycle = RankineCycle()
    
    # Standard baseline parameters
    params = {
        'P_min': 0.01,   # 10 kPa (Condenser Pressure)
        'P_max': 15.0,   # 15 MPa (Boiler Pressure)
        'T_max': 550.0,  # 550 °C (Turbine Inlet Temperature)
        'n_rh': 0,       # No Reheat
        'n_fwh': 0       # No Feedwater Heaters
    }

    # Execute simulation
    states = cycle.solve('rankine_basic', params)
    metrics = cycle.calculate_performance()

    # Basic validity checks
    assert states, "Solver should return a dictionary of state points"
    assert metrics['efficiency'] >= 0, "Efficiency cannot be negative"
    assert metrics['w_net'] >= 0, "Net work output should be positive for a power cycle"
    assert metrics['q_in'] > 0, "Heat input must be positive"
