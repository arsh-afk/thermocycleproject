"""
Otto Cycle Solver
Educational note: Standard spark-ignition engine model.
States: 1-Intake (BDC), 2-Compression (TDC), 3-Heat Addition (TDC), 4-Expansion (BDC).
"""
from core.base_cycle import BaseCycle

class OttoCycle(BaseCycle):
    def __init__(self, fluid="Air"):
        super().__init__(fluid)
        
    def solve(self, params):
        self.clear_states()
        
        # Mapping UI keys and providing defaults
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
        
        self.states[1] = self.get_state('P', P1, 'T', T1, "Intake BDC")
        
        v2 = self.states[1].v / r
        self.states[2] = self.get_state('V', v2, 'S', self.states[1].s, "Compression TDC")
        
        self.states[3] = self.get_state('V', v2, 'T', T3, "Combustion TDC")
        
        v4 = self.states[3].v * r
        self.states[4] = self.get_state('V', v4, 'S', self.states[3].s, "Expansion BDC")
        
        return self.states

    def calculate_performance(self):
        if not self.states:
            return {}

        def get_u(st):
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

        return {
            'efficiency': efficiency,
            'w_net': w_net / 1000,
            'q_in': q_in / 1000,
            'q_out': q_out / 1000,
            's_gen': s_gen,
            'second_law_efficiency': sl_eff,
        }

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
