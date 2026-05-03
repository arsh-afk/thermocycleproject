from core.base_cycle import BaseCycle
from core.components import Compressor, Turbine

class BraytonCycle(BaseCycle):
    """
    Refactored Template-Based Brayton Cycle Solver.
    Supports simple and regenerative configurations.
    """
    VALID_FLUIDS = ['Air', 'Nitrogen', 'Helium', 'Argon', 'Neon']

    def __init__(self, fluid="Air"):
        if fluid not in self.VALID_FLUIDS:
            raise ValueError(f"Brayton cycle restricted to non-condensable gases: {self.VALID_FLUIDS}")
        super().__init__(fluid)
        self.compressor = Compressor("Compressor")
        self.turbine = Turbine("Turbine")
        self.active_template = 'brayton_simple'

    def solve(self, params):
        """
        Routes to the appropriate sub-solver based on params['template'].
        Unified signature: solve(params) — consistent with all other cycles.
        """
        self.clear_states()
        template_key = params.get('template', 'brayton_simple')
        self.active_template = template_key
        if template_key == 'brayton_simple':
            return self._solve_simple(params)
        elif template_key == 'brayton_regen':
            return self._solve_regen(params)
        raise ValueError(f"Unknown template: {template_key}")

    def _solve_simple(self, p):
        # 1: Inlet
        st1 = self.get_state('P', 101325, 'T', p['T_min'], "Comp Inlet")
        # 2: Compressor outlet
        P_high = st1.P * p['rp']
        st2 = self.compressor.solve(st1, P_high, 0.85, self.fluid)
        # 3: Turbine inlet
        st3 = self.get_state('P', P_high, 'T', p['T_max'], "Turb Inlet")
        # 4: Turbine exit
        st4 = self.turbine.solve(st3, st1.P, 0.90, self.fluid)

        self.states = {1: st1, 2: st2, 3: st3, 4: st4}
        self.T_hot, self.T_cold = st3.T, st1.T
        self._q_in = st3.h - st2.h
        self._w_turbines = st3.h - st4.h
        self._w_pumps = st2.h - st1.h # w_comp
        return self.states

    def _solve_regen(self, p):
        # 1: Comp Inlet
        st1 = self.get_state('P', 101325, 'T', 300, "Comp Inlet")
        P_high = st1.P * p['rp']
        # 2: Comp Exit
        st2 = self.compressor.solve(st1, P_high, 0.85, self.fluid)
        # 4: Turb Inlet
        st4 = self.get_state('P', P_high, 'T', p['T_max'], "Turb Inlet")
        # 5: Turb Exit
        st5 = self.turbine.solve(st4, st1.P, 0.90, self.fluid)
        
        # Regeneration: h3 = h2 + eps * (h5 - h2)
        h3 = st2.h + p['epsilon'] * (st5.h - st2.h)
        st3 = self.get_state('P', P_high, 'H', h3, "Combustor Inlet")
        
        self.states = {1: st1, 2: st2, 3: st3, 4: st4, 5: st5}
        self.T_hot, self.T_cold = st4.T, st1.T
        self._q_in = st4.h - st3.h
        self._w_turbines = st4.h - st5.h
        self._w_pumps = st2.h - st1.h
        return self.states

    def validate_inputs(self, params):
        if params.get('T_max') and params.get('T_min'):
            if params['T_max'] <= params['T_min']:
                self.errors.append("Maximum temperature must be greater than minimum temperature.")
        if params.get('rp'):
            if params['rp'] <= 1.0:
                self.errors.append("Pressure ratio must be greater than 1.")
        return len(self.errors) == 0

    def get_component_list(self):
        if self.active_template == 'brayton_simple': return ["Compressor", "Combustor", "Turbine"]
        if self.active_template == 'brayton_regen': return ["Compressor", "Regenerator (Cold)", "Combustor", "Turbine", "Regenerator (Hot)"]
        return []

    def calculate_performance(self):
        w_net = self._w_turbines - self._w_pumps
        efficiency = (w_net / self._q_in) * 100 if self._q_in > 0 else 0
        q_out = self._q_in - w_net
        s_gen = self.calculate_entropy_generation(self._q_in, self.T_hot, q_out, self.T_cold)
        x_dest = self.calculate_exergy_destruction(s_gen)
        sl_eff = self.calculate_second_law_efficiency(efficiency, self.T_hot, self.T_cold)
        
        return {
            'efficiency': efficiency,
            'w_net': w_net / 1000,
            'q_in': self._q_in / 1000,
            'x_dest': x_dest / 1000 if x_dest else 0,
            'second_law_efficiency': sl_eff
        }
