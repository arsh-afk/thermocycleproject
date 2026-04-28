"""
Stirling Cycle Solver
Educational note: Theoretical closed cycle with isothermal compression/expansion
and constant-volume regeneration. Matches Carnot efficiency with ideal regeneration.
"""
from core.base_cycle import BaseCycle

class StirlingCycle(BaseCycle):
    def __init__(self, fluid="Air"):
        super().__init__(fluid)
        
    def solve(self, params):
        self.clear_states()
        
        # Mapping UI keys and providing defaults
        defaults = {
            'T_max': 800.0 + 273.15,
            'T_min': 25.0 + 273.15,
            'P_max': 10.0 * 1e6,
            'r': 2.0,
        }
        
        current = defaults.copy()
        if 'T_max' in params: current['T_max'] = params['T_max'] + 273.15
        if 'T_min' in params: current['T_min'] = params['T_min'] + 273.15
        if 'P_max' in params: current['P_max'] = params['P_max'] * 1e6
        if 'r' in params: current['r'] = params['r']
        
        T_hot = current['T_max']
        T_cold = current['T_min']
        P_max = current['P_max']
        r = current['r']
        
        self.states[3] = self.get_state('P', P_max, 'T', T_hot, "Heating Exit")
        
        v4 = self.states[3].v * r
        self.states[4] = self.get_state('V', v4, 'T', T_hot, "Expansion Exit")
        
        v1 = v4
        self.states[1] = self.get_state('V', v1, 'T', T_cold, "Cooling Exit")
        
        v2 = self.states[3].v
        self.states[2] = self.get_state('V', v2, 'T', T_cold, "Compression Exit")
        
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
        t_max = params.get('T_max', 800.0)
        t_min = params.get('T_min', 25.0)
        r = params.get('r', 2.0)
        
        if t_max <= t_min:
            errors.append("T_max must be greater than T_min.")
        if r <= 1:
            errors.append("Expansion ratio must be greater than 1.")
        return errors

    def get_component_list(self):
        return ["Isothermal Compression", "Regeneration", "Isothermal Expansion", "Regeneration"]
