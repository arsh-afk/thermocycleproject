"""
Ericsson Cycle Solver
Educational note: Similar to Stirling but with constant-pressure regeneration.
Matches Carnot efficiency with ideal regeneration.
"""
from core.base_cycle import BaseCycle

class EricssonCycle(BaseCycle):
    def __init__(self, fluid="Air"):
        super().__init__(fluid)
        
    def solve(self, params):
        self.clear_states()
        T_hot = params['T_max'] + 273.15
        T_cold = params['T_min'] + 273.15
        P_max = params['P_max'] * 1e6
        P_min = params['P_min'] * 1e6
        
        self.states[3] = self.get_state('P', P_max, 'T', T_hot, "Heating Exit")
        self.states[4] = self.get_state('P', P_min, 'T', T_hot, "Expansion Exit")
        self.states[1] = self.get_state('P', P_min, 'T', T_cold, "Cooling Exit")
        self.states[2] = self.get_state('P', P_max, 'T', T_cold, "Compression Exit")
        
        return self.states

    def calculate_performance(self):
        if not self.states:
            return {}
        T_H = self.states[3].T
        T_C = self.states[1].T
        
        q_in = T_H * (self.states[4].s - self.states[3].s)
        q_out = T_C * (self.states[1].s - self.states[2].s)
        w_net = q_in - q_out
        efficiency = (1 - T_C / T_H) * 100 if T_H > 0 else 0
        s_gen = self.calculate_entropy_generation(q_in, T_H, q_out, T_C)
        sl_eff = self.calculate_second_law_efficiency(efficiency, T_H, T_C)

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
        if params['P_min'] >= params['P_max']:
            errors.append("P_max must be greater than P_min.")
        if params['T_min'] >= params['T_max']:
            errors.append("T_max must be greater than T_min.")
        return errors

    def get_component_list(self):
        return ["Isothermal Compression", "Regeneration", "Isothermal Expansion", "Regeneration"]
