"""
Modular Gas Brayton Cycle Solver
Educational note: Gas turbines use intercooling and reheating to approximate 
the Ericsson cycle (isothermal compression/expansion), which maximizes efficiency.
SOURCE: Textbooks benchmarks for Gas Turbine Cycles.
"""
from core.base_cycle import BaseCycle
from core.components import Turbine, Compressor

class BraytonCycle(BaseCycle):
    """Modular Brayton Cycle with N-stages."""
    
    VALID_FLUIDS = ['Air', 'Nitrogen', 'Helium', 'Argon', 'Neon']
    
    def __init__(self, fluid="Air"):
        if fluid not in self.VALID_FLUIDS:
            raise ValueError(f"Brayton cycle restricted to non-condensable gases: {self.VALID_FLUIDS}")
        super().__init__(fluid)
        self.compressor = Compressor("Compressor")
        self.turbine = Turbine("Turbine")
        
    def solve(self, params):
        self.clear_states()
        P_min = params['P_min'] * 1e6
        P_max = params['P_max'] * 1e6
        T_min = params['T_min'] + 273.15
        T_max = params['T_max'] + 273.15
        n_ic = max(0, int(params.get('n_ic', 0)))
        n_rh = max(0, int(params.get('n_rh', 0)))
        eta_c, eta_t = 0.85, 0.90
        self.T_hot = T_max
        self.T_cold = T_min
        
        self._w_comp = 0.0
        self._w_turb = 0.0
        self._q_in = 0.0

        st_in = self.get_state('P', P_min, 'T', T_min, "Main Intake")
        self.states[1] = st_in
        
        pr_stage_c = (P_max / P_min) ** (1 / max(1, n_ic + 1))
        for i in range(n_ic + 1):
            p_out = st_in.P * pr_stage_c
            st_out = self.compressor.solve(st_in, p_out, eta_c, self.fluid)
            self.states[len(self.states)+1] = st_out
            self._w_comp += st_out.h - st_in.h
            
            if i < n_ic:
                st_in = self.get_state('P', p_out, 'T', T_min, f"Intercooler {i+1} Exit")
                self.states[len(self.states)+1] = st_in
        
        pr_stage_t = (P_max / P_min) ** (1 / max(1, n_rh + 1))
        t_in = self.get_state('P', P_max, 'T', T_max, "Combustor Exit")
        self.states[len(self.states)+1] = t_in
        self._q_in += t_in.h - st_out.h
        
        for i in range(n_rh + 1):
            p_out = t_in.P / pr_stage_t
            st_out = self.turbine.solve(t_in, p_out, eta_t, self.fluid)
            self.states[len(self.states)+1] = st_out
            self._w_turb += t_in.h - st_out.h
            
            if i < n_rh:
                t_in = self.get_state('P', p_out, 'T', T_max, f"Reheater {i+1} Exit")
                self.states[len(self.states)+1] = t_in
                self._q_in += t_in.h - st_out.h
        
        return self.states

    def calculate_performance(self):
        if not self.states:
            return {}
        w_net = self._w_turb - self._w_comp
        q_in = self._q_in
        efficiency = (w_net / q_in) * 100 if q_in > 0 else 0
        last_state = self.states[max(self.states)]
        q_out = last_state.h - self.states[1].h
        s_gen = self.calculate_entropy_generation(q_in, self.T_hot, q_out, self.T_cold)
        sl_eff = self.calculate_second_law_efficiency(efficiency, self.T_hot, self.T_cold)
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
        if params['P_min'] >= params['P_max']:
            errors.append("P_max must be greater than P_min.")
        if params['T_min'] >= params['T_max']:
            errors.append("T_max must be greater than T_min.")
        if params.get('n_ic', 0) < 0:
            errors.append("Intercooler stages cannot be negative.")
        if params.get('n_rh', 0) < 0:
            errors.append("Reheat stages cannot be negative.")
        return errors

    def get_component_list(self):
        return ["Compressors", "Intercoolers", "Combustor", "Turbines", "Reheaters"]
