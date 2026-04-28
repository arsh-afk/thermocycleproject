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
        
    def get_component_list(self):
        components = []
        n_ic = getattr(self, '_n_ic_used', 0)
        n_rh = getattr(self, '_n_rh_used', 0)
        
        for i in range(n_ic + 1):
            components.append(f"Compressor {i+1}")
            if i < n_ic:
                components.append(f"Intercooler {i+1}")
                
        components.append("Combustor")
        
        for i in range(n_rh + 1):
            components.append(f"Turbine {i+1}")
            if i < n_rh:
                components.append(f"Reheater {i+1}")
                
        components.append("Cooler/Exhaust")
        return components

    def solve(self, params):
        self.clear_states()
        P_min = params['P_min'] * 1e6
        P_max = params['P_max'] * 1e6
        T_min = params['T_min'] + 273.15
        T_max = params['T_max'] + 273.15
        n_ic = max(0, int(params.get('n_ic', 0)))
        n_rh = max(0, int(params.get('n_rh', 0)))
        
        self._n_ic_used = n_ic
        self._n_rh_used = n_rh
        
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
