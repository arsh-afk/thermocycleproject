"""
Stirling Cycle Solver
Educational note: Theoretical closed cycle with isothermal compression/expansion
and constant-volume regeneration. Matches Carnot efficiency with ideal regeneration.
"""
from core.base_cycle import BaseCycle
import numpy as np

class StirlingCycle(BaseCycle):
    def __init__(self, fluid="Air"):
        super().__init__(fluid)
        
    def solve(self, params):
        self.clear_states()
        T_hot = params['T_max'] + 273.15
        T_cold = params['T_min'] + 273.15
        P_max = params['P_max'] * 1e6
        r = params.get('r', 2.0)
        
        # State 3: Peak P and T (End of constant volume heating)
        self.states[3] = self.get_state('P', P_max, 'T', T_hot, "Heating Exit")
        
        # State 4: Isothermal Expansion
        v4 = self.states[3].v * r
        self.states[4] = self.get_state('V', v4, 'T', T_hot, "Expansion Exit")
        
        # State 1: Constant Volume Cooling
        v1 = v4
        self.states[1] = self.get_state('V', v1, 'T', T_cold, "Cooling Exit")
        
        # State 2: Isothermal Compression
        v2 = self.states[3].v
        self.states[2] = self.get_state('V', v2, 'T', T_cold, "Compression Exit")
        
        return self.states

    def calculate_performance(self):
        if not self.states: return {}
        T_H = self.states[3].T
        T_C = self.states[1].T
        
        q_in = T_H * (self.states[4].s - self.states[3].s)
        q_out = T_C * (self.states[1].s - self.states[2].s)
        w_net = q_in - q_out
        
        # Ideal Efficiency = 1 - Tc/Th
        return {
            'efficiency': (1 - T_C/T_H) * 100,
            'w_net': w_net / 1000,
            'q_in': q_in / 1000
        }

    def validate_inputs(self, params):
        return []

    def get_component_list(self):
        return ["Isothermal Compression", "Regeneration", "Isothermal Expansion", "Regeneration"]
