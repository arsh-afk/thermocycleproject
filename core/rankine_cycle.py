from core.base_cycle import BaseCycle
from core.components import Turbine, Pump, HeatExchanger, MixingChamber, ThrottlingValve

class RankineCycle(BaseCycle):
    """
    Refactored Template-Based Rankine Cycle Solver.
    """
    def __init__(self, fluid="Water"):
        super().__init__(fluid)
        self.turbine = Turbine("Turbine")
        self.pump = Pump("Pump")
        self.boiler = HeatExchanger("Boiler")
        self.mixer = MixingChamber("Open FWH")
        self.valve = ThrottlingValve("Valve")
        self.active_template = 'rankine_basic'

    def solve(self, params):
        """
        Routes to the appropriate sub-solver based on params['template'].
        Unified signature: solve(params) — consistent with all other cycles.
        """
        self.clear_states()
        template_key = params.get('template', 'rankine_basic')
        self.active_template = template_key
        if template_key == 'rankine_basic':
            return self._solve_basic(params)
        elif template_key == 'rankine_reheat':
            return self._solve_reheat(params)
        elif template_key == 'rankine_open_fwh':
            return self._solve_open_fwh(params)
        raise ValueError(f"Unknown template: {template_key}")


    def _solve_basic(self, p):
        # 1-2: Pump
        st1 = self.get_state('P', p['P_min']*1e6, 'Q', 0, "Pump Inlet")
        st2 = self.pump.solve(st1, p['P_max']*1e6, 0.85, self.fluid)
        # 2-3: Boiler
        st3 = self.get_state('P', p['P_max']*1e6, 'T', p['T_max']+273.15, "Turbine Inlet")
        # 3-4: Turbine
        st4 = self.turbine.solve(st3, p['P_min']*1e6, 0.90, self.fluid)
        
        self.states = {1: st1, 2: st2, 3: st3, 4: st4}
        self.T_hot, self.T_cold = st3.T, st1.T
        self._q_in = st3.h - st2.h
        self._w_turbines = st3.h - st4.h
        self._w_pumps = st2.h - st1.h
        return self.states

    def _solve_reheat(self, p):
        # 1-2: Pump
        st1 = self.get_state('P', p['P_min']*1e6, 'Q', 0, "Pump Inlet")
        st2 = self.pump.solve(st1, p['P_max']*1e6, 0.85, self.fluid)
        # 2-3: Boiler
        st3 = self.get_state('P', p['P_max']*1e6, 'T', p['T_max']+273.15, "HP Turbine Inlet")
        # 3-4: HP Turbine
        st4 = self.turbine.solve(st3, p['P_rh']*1e6, 0.90, self.fluid)
        # 4-5: Reheater
        st5 = self.get_state('P', p['P_rh']*1e6, 'T', p['T_max']+273.15, "LP Turbine Inlet")
        # 5-6: LP Turbine
        st6 = self.turbine.solve(st5, p['P_min']*1e6, 0.90, self.fluid)

        self.states = {1: st1, 2: st2, 3: st3, 4: st4, 5: st5, 6: st6}
        self.T_hot, self.T_cold = st3.T, st1.T
        self._q_in = (st3.h - st2.h) + (st5.h - st4.h)
        self._w_turbines = (st3.h - st4.h) + (st5.h - st6.h)
        self._w_pumps = st2.h - st1.h
        return self.states

    def _solve_open_fwh(self, p):
        # State 1: Condenser exit
        st1 = self.get_state('P', p['P_min']*1e6, 'Q', 0, "Cond. Pump Inlet")
        # State 2: Cond. pump exit to FWH pressure
        st2 = self.pump.solve(st1, p['P_ext']*1e6, 0.85, self.fluid)
        # State 5: Boiler exit
        st5 = self.get_state('P', p['P_max']*1e6, 'T', p['T_max']+273.15, "Turbine Inlet")
        # State 6: Extraction
        st6 = self.turbine.solve(st5, p['P_ext']*1e6, 0.90, self.fluid)
        # State 7: Turbine exit
        st7 = self.turbine.solve(st5, p['P_min']*1e6, 0.90, self.fluid)
        
        # Mass balance on Open FWH: y*h6 + (1-y)*h2 = h3 (sat liquid at P_ext)
        st3 = self.get_state('P', p['P_ext']*1e6, 'Q', 0, "Feed Pump Inlet")
        y = (st3.h - st2.h) / (st6.h - st2.h)
        
        # State 4: Feed pump exit
        st4 = self.pump.solve(st3, p['P_max']*1e6, 0.85, self.fluid)

        self.states = {1: st1, 2: st2, 3: st3, 4: st4, 5: st5, 6: st6, 7: st7}
        self.T_hot, self.T_cold = st5.T, st1.T
        self._q_in = st5.h - st4.h
        self._w_turbines = (st5.h - st6.h) + (1-y)*(st6.h - st7.h)
        self._w_pumps = (1-y)*(st2.h - st1.h) + (st4.h - st3.h)
        return self.states

    def validate_inputs(self, params):
        if params.get('P_max') and params.get('P_min'):
            if params['P_max'] <= params['P_min']:
                self.errors.append("Maximum pressure must be greater than minimum pressure.")
        return len(self.errors) == 0

    def get_component_list(self):
        if self.active_template == 'rankine_basic': return ["Pump", "Boiler", "Turbine", "Condenser"]
        if self.active_template == 'rankine_reheat': return ["Pump", "Boiler", "HP Turbine", "Reheater", "LP Turbine", "Condenser"]
        if self.active_template == 'rankine_open_fwh': return ["Cond. Pump", "Open FWH", "Feed Pump", "Boiler", "Turbine", "Condenser"]
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
