from core.rankine_cycle import RankineCycle


def test_rankine_cycle_baseline():
    cycle = RankineCycle()
    params = {
        'P_min': 0.01,
        'P_max': 15.0,
        'T_max': 550.0,
        'n_rh': 0,
        'n_fwh': 0
    }

    states = cycle.solve(params)
    metrics = cycle.calculate_performance()

    assert states
    assert metrics['efficiency'] >= 0
    assert metrics['w_net'] >= 0
    assert metrics['q_in'] > 0
