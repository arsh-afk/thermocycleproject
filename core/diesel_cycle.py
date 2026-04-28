"""
Diesel Cycle Solver
Educational note: Standard compression-ignition engine model.
States: 1-Intake (BDC), 2-Compression (TDC), 3-Heat Addition (Constant P), 4-Expansion (BDC).
"""
from core.base_cycle import BaseCycle
import numpy as np

class DieselCycle(BaseCycle):
    def __init__(self, fluid="Air"):
        super().__init__(fluid)
        
    def solve(self, params):
        self.clear_states()
        r = params['r']
        rc = params['rc'] # Cutoff ratio
        T1 = params.get('T_min', 25) + 273.15
        P1 = params.get('P_min', 0.1) * 1e6
        
        # State 1
        self.states[1] = self.get_state('P', P1, 'T', T1, "Intake BDC")
        
        # State 2: Compression
        v2 = self.states[1].v / r
        self.states[2] = self.get_state('V', v2, 'S', self.states[1].s, "Compression TDC")
        
        # State 3: Combustion (Constant P)
        v3 = v2 * rc
        self.states[3] = self.get_state('P', self.states[2].P, 'V', v3, "Combustion Exit")
        
        # State 4: Expansion
        v4 = self.states[1].v
        self.states[4] = self.get_state('V', v4, 'S', self.states[3].s, "Expansion BDC")
        
        return self.states

    def calculate_performance(self):
        if not self.states: return {}
        def get_u(st): return st.h - st.P * st.v
        
        u1, u2, u4 = get_u(self.states[1]), get_u(self.states[2]), get_u(self.states[4])
        h2, h3 = self.states[2].h, self.states[3].h
        
        q_in = h3 - h2
        q_out = u4 - u1
        w_net = q_in - q_out
        
        return {
            'efficiency': (w_net / q_in) * 100 if q_in > 0 else 0,
            'w_net': w_net / 1000,
            'q_in': q_in / 1000
        }

    def validate_inputs(self, params):
        return []

    def get_component_list(self):
        return ["Intake", "Compression", "Combustion", "Expansion"]
