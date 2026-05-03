"""
Otto Cycle Solver
Educational note: Standard spark-ignition engine model.
States: 1-Intake (BDC), 2-Compression (TDC), 3-Heat Addition (TDC), 4-Expansion (BDC).

Engineering Principle: The Otto cycle idealizes the constant-volume heat addition
and rejection processes of a gasoline engine. Efficiency = 1 - 1/r^(k-1).
SOURCE: Cengel, Thermodynamics: An Engineering Approach, Chapter 9.
"""
from core.base_cycle import BaseCycle


class OttoCycle(BaseCycle):
    """Air-standard Otto cycle solver (spark-ignition engine model)."""

    def __init__(self, fluid="Air"):
        super().__init__(fluid)

    def solve(self, params):
        """
        Solves the four-state Otto cycle.
        Processes:
          1-2: Isentropic Compression
          2-3: Constant-Volume Heat Addition (Isochoric)
          3-4: Isentropic Expansion
          4-1: Constant-Volume Heat Rejection (Isochoric)
        """
        self.clear_states()

        defaults = {
            'r': 8.0,
            'T_min': 25.0 + 273.15,
            'P_min': 0.1 * 1e6,
            'T_max': 1500.0 + 273.15,
        }

        current = defaults.copy()
        if 'r' in params: current['r'] = params['r']
        if 'T_min' in params: current['T_min'] = params['T_min'] + 273.15
        if 'P_min' in params: current['P_min'] = params['P_min'] * 1e6
        if 'T_max' in params: current['T_max'] = params['T_max'] + 273.15

        r = current['r']
        T1 = current['T_min']
        P1 = current['P_min']
        T3 = current['T_max']

        # State 1: Intake at BDC (Bottom Dead Centre)
        self.states[1] = self.get_state('P', P1, 'T', T1, "Intake BDC")

        # State 2: End of isentropic compression (TDC)
        v2 = self.states[1].v / r
        self.states[2] = self.get_state('V', v2, 'S', self.states[1].s, "Compression TDC")

        # State 3: After constant-volume heat addition (TDC)
        self.states[3] = self.get_state('V', v2, 'T', T3, "Combustion TDC")

        # State 4: End of isentropic expansion (BDC)
        v4 = self.states[3].v * r
        self.states[4] = self.get_state('V', v4, 'S', self.states[3].s, "Expansion BDC")

        return self.states

    def calculate_performance(self):
        """
        Calculates Otto cycle performance.
        Uses internal energy (u = h - P*v) for constant-volume processes.
        """
        if not self.states:
            return {}

        def get_u(st):
            """Internal energy from enthalpy: u = h - P*v"""
            return st.h - st.P * st.v

        u1 = get_u(self.states[1])
        u2 = get_u(self.states[2])
        u3 = get_u(self.states[3])
        u4 = get_u(self.states[4])

        w_net = (u3 - u4) - (u2 - u1)
        q_in = u3 - u2
        q_out = u4 - u1
        T_hot = self.states[3].T
        T_cold = self.states[1].T
        efficiency = (w_net / q_in) * 100 if q_in > 0 else 0
        s_gen = self.calculate_entropy_generation(q_in, T_hot, q_out, T_cold)
        sl_eff = self.calculate_second_law_efficiency(efficiency, T_hot, T_cold)

        self.metrics = {
            'efficiency': efficiency,
            'w_net': w_net / 1000,
            'q_in': q_in / 1000,
            'q_out': q_out / 1000,
            's_gen': s_gen,
            'second_law_efficiency': sl_eff,
        }
        return self.metrics

    def validate_inputs(self, params):
        errors = []
        r = params.get('r', 8.0)
        t_max = params.get('T_max', 1500.0)
        t_min = params.get('T_min', 25.0)

        if r <= 1:
            errors.append("Compression ratio must be greater than 1.")
        if t_max <= t_min:
            errors.append("T_max must be greater than T_min.")
        return errors

    def get_component_list(self):
        return ["Intake", "Compression", "Combustion", "Expansion"]
