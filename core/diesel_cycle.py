"""
Diesel Cycle Solver
Educational note: Standard compression-ignition engine model.
States: 1-Intake (BDC), 2-Compression (TDC), 3-Heat Addition (Constant P), 4-Expansion (BDC).
"""
from core.base_cycle import BaseCycle

class DieselCycle(BaseCycle):
    def __init__(self, fluid="Air"):
        super().__init__(fluid)
        
    def solve(self, params):
        self.clear_states()
        
        # Mapping UI keys and providing defaults
        defaults = {
            'r': 16.0,
            'rc': 2.0,
            'T_min': 25.0 + 273.15,
            'P_min': 0.1 * 1e6,
        }
        
        current = defaults.copy()
        if 'r' in params: current['r'] = params['r']
        if 'rc' in params: current['rc'] = params['rc']
        if 'T_min' in params: current['T_min'] = params['T_min'] + 273.15
        if 'P_min' in params: current['P_min'] = params['P_min'] * 1e6
        
        r = current['r']
        rc = current['rc']
        T1 = current['T_min']
        P1 = current['P_min']
        
        self.states[1] = self.get_state('P', P1, 'T', T1, "Intake BDC")
        
        v2 = self.states[1].v / r
        self.states[2] = self.get_state('V', v2, 'S', self.states[1].s, "Compression TDC")
        
        v3 = v2 * rc
        self.states[3] = self.get_state('P', self.states[2].P, 'V', v3, "Combustion Exit")
        
        v4 = self.states[1].v
        self.states[4] = self.get_state('V', v4, 'S', self.states[3].s, "Expansion BDC")
        
        return self.states

    def calculate_performance(self):
        if not self.states:
            return {}

        def get_u(st):
            return st.h - st.P * st.v

        u1 = get_u(self.states[1])
        u2 = get_u(self.states[2])
        u4 = get_u(self.states[4])
        h2 = self.states[2].h
        h3 = self.states[3].h

        q_in = h3 - h2
        q_out = u4 - u1
        w_net = q_in - q_out
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
        r = params.get('r', 16.0)
        rc = params.get('rc', 2.0)
        if r <= 1:
            errors.append("Compression ratio must be greater than 1.")
        if rc <= 1:
            errors.append("Cutoff ratio must be greater than 1.")
        return errors

    def get_component_list(self):
        return ["Intake", "Compression", "Combustion", "Expansion"]
