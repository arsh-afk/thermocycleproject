"""
Otto Cycle Solver
Educational note: Standard spark-ignition engine model.
States: 1-Intake (BDC), 2-Compression (TDC), 3-Heat Addition (TDC), 4-Expansion (BDC).
"""
from core.base_cycle import BaseCycle
import numpy as np

class OttoCycle(BaseCycle):
    def __init__(self, fluid="Air"):
        super().__init__(fluid)
        
    def solve(self, params):
        self.clear_states()
        r = params['r']
        T1 = params.get('T_min', 25) + 273.15
        P1 = params.get('P_min', 0.1) * 1e6
        T3 = params['T_max'] + 273.15
        
        # State 1: Intake (BDC)
        self.states[1] = self.get_state('P', P1, 'T', T1, "Intake BDC")
        
        # State 2: Compression (Isentropic)
        v2 = self.states[1].v / r
        self.states[2] = self.get_state('V', v2, 'S', self.states[1].s, "Compression TDC")
        
        # State 3: Combustion (Constant Volume)
        self.states[3] = self.get_state('V', v2, 'T', T3, "Combustion TDC")
        
        # State 4: Expansion (Isentropic)
        v4 = self.states[3].v * r
        self.states[4] = self.get_state('V', v4, 'S', self.states[3].s, "Expansion BDC")
        
        return self.states

    def calculate_performance(self):
        if not self.states: return {}
        # u is not currently in state, but can be calculated h - Pv
        # u = h - Pv
        def get_u(st): return st.h - st.P * st.v
        
        u1, u2, u3, u4 = get_u(self.states[1]), get_u(self.states[2]), get_u(self.states[3]), get_u(self.states[4])
        
        w_net = (u3 - u4) - (u2 - u1)
        q_in = u3 - u2
        
        return {
            'efficiency': (w_net / q_in) * 100 if q_in > 0 else 0,
            'w_net': w_net / 1000,
            'q_in': q_in / 1000
        }

    def validate_inputs(self, params):
        return []

    def get_component_list(self):
        return ["Intake", "Compression", "Combustion", "Expansion"]
