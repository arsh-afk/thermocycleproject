"""
Professional Rankine Cycle Solver
Educational note: Supports arbitrary N-stages of reheat and FWH.
SOURCE: IAPWS-IF97 (Water) and CoolProp backends.
"""
from core.base_cycle import BaseCycle
from core.components import Turbine, Pump, HeatExchanger
from core.water_additives import WaterAdditives
import numpy as np

class RankineCycle(BaseCycle):
    def __init__(self, fluid="Water", additive="Pure Water", concentration=0.0):
        super().__init__(fluid)
        self.turbine = Turbine("Steam Turbine")
        self.pump = Pump("Feed Pump")
        self.boiler = HeatExchanger("Boiler")
        self.corrections = WaterAdditives.get_corrections(additive, concentration)

    def solve(self, params):
        self.clear_states()
        P_min = params['P_min'] * 1e6
        P_max = params['P_max'] * 1e6
        T_max = params['T_max'] + 273.15
        n_rh = params.get('n_rh', 0)
        n_fwh = params.get('n_fwh', 0)
        eta_p, eta_t = 0.85, 0.90

        # Initialize tracking variables for accurate metrics
        self._w_pumps = 0.0
        self._w_turbines = 0.0
        self._q_in = 0.0

        # SOURCE: Standard FWH pressure selection - Equal Saturation Temperature increments
        st1 = self.get_state('P', P_min, 'Q', 0, "Condenser Out")
        T_cond = st1.T
        st_boil_sat = self.get_state('P', P_max, 'Q', 0)
        T_boil_sat = st_boil_sat.T if st_boil_sat else 647.1 
            
        dT = (T_boil_sat - T_cond) / (n_fwh + 1)
        fwh_pressures = [self.get_state('T', T_cond + i*dT, 'Q', 0).P for i in range(1, n_fwh + 1)]

        # --- SEQUENTIAL STATE MAPPING (for PFD Correlation) ---
        # State 1: Condenser Exit
        self.states[1] = st1
        
        # 1. Pumping Path (States 1 -> 2 -> 3...)
        p_in = self.states[1]
        for i in range(n_fwh + 1):
            p_target = fwh_pressures[i] if i < n_fwh else P_max
            st_out = self.pump.solve(p_in, p_target, eta_p, self.fluid)
            st_out.note = f"Pump {i+1} Exit"
            self.states[len(self.states)+1] = st_out
            self._w_pumps += (st_out.h - p_in.h)
            
            if i < n_fwh:
                p_in = self.get_state('P', p_target, 'Q', 0, f"FWH {i+1} Exit")
                self.states[len(self.states)+1] = p_in
        
        # 2. Boiler Heating
        st_boil = self.get_state('P', P_max, 'T', T_max, "Boiler Exit")
        self.states[len(self.states)+1] = st_boil
        self._q_in += (st_boil.h - st_out.h)
        
        # 3. Turbine Expansion Path
        pr_stage = (P_max / P_min) ** (1 / (n_rh + 1))
        t_in = st_boil
        for i in range(n_rh + 1):
            p_out = P_max / (pr_stage ** (i+1)) if i < n_rh else P_min
            st_out = self.turbine.solve(t_in, p_out, eta_t, self.fluid)
            st_out.note = f"Turbine {i+1} Exit"
            self.states[len(self.states)+1] = st_out
            self._w_turbines += (t_in.h - st_out.h)
            
            if i < n_rh:
                t_in = self.get_state('P', p_out, 'T', T_max, f"Reheat {i+1} Exit")
                self.states[len(self.states)+1] = t_in
                self._q_in += (t_in.h - st_out.h)
        
        return self.states

    def calculate_performance(self):
        if not self.states: return {}
        w_net = self._w_turbines - self._w_pumps
        return {
            'efficiency': (w_net / self._q_in) * 100 if self._q_in > 0 else 0,
            'w_net': w_net / 1000,
            'q_in': self._q_in / 1000
        }

    def validate_inputs(self, params): return []
    def get_component_list(self): return ["Pumps", "Boiler", "Turbines", "Condenser"]
