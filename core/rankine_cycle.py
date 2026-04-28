"""
Professional Rankine Cycle Solver
Educational note: Supports arbitrary N-stages of reheat and FWH.
SOURCE: IAPWS-IF97 (Water) and CoolProp backends.
"""
from core.base_cycle import BaseCycle
from core.components import Turbine, Pump, HeatExchanger
from core.water_additives import WaterAdditives

class RankineCycle(BaseCycle):
    def __init__(self, fluid="Water", additive="Pure Water", concentration=0.0):
        super().__init__(fluid)
        self.turbine = Turbine("Steam Turbine")
        self.pump = Pump("Feed Pump")
        self.boiler = HeatExchanger("Boiler")
        self.corrections = WaterAdditives.get_corrections(additive, concentration)

    def get_component_list(self):
        # We need to return exactly the same number of components as there are state changes.
        # Flow is: Condenser -> Pump -> FWH -> Pump -> FWH -> Boiler -> Turbine -> Reheater -> Turbine -> Condenser
        components = []
        n_rh = getattr(self, '_n_rh_used', 0)
        n_fwh = getattr(self, '_n_fwh_used', 0)
        
        for i in range(n_fwh + 1):
            components.append(f"Pump {i+1}")
            if i < n_fwh:
                components.append(f"FWH {i+1}")
                
        components.append("Boiler")
        
        for i in range(n_rh + 1):
            components.append(f"Turbine {i+1}")
            if i < n_rh:
                components.append(f"Reheater {i+1}")
                
        components.append("Condenser")
        return components

    def solve(self, params):
        self.clear_states()
        P_min = params['P_min'] * 1e6
        P_max = params['P_max'] * 1e6
        T_max = params['T_max'] + 273.15
        n_rh = max(0, int(params.get('n_rh', 0)))
        n_fwh = max(0, int(params.get('n_fwh', 0)))
        
        self._n_rh_used = n_rh
        self._n_fwh_used = n_fwh
        
        eta_p, eta_t = 0.85, 0.90
        self.T_hot = T_max
        self.T_cold = None

        self._w_pumps = 0.0
        self._w_turbines = 0.0
        self._q_in = 0.0

        st1 = self.get_state('P', P_min, 'Q', 0, "Condenser Out")
        T_cond = st1.T
        st_boil_sat = self.get_state('P', P_max, 'Q', 0)
        T_boil_sat = st_boil_sat.T if st_boil_sat else 647.1

        dT = (T_boil_sat - T_cond) / max(1, n_fwh + 1)
        fwh_pressures = [self.get_state('T', T_cond + i * dT, 'Q', 0).P for i in range(1, n_fwh + 1)]

        self.states[1] = st1
        self.T_cold = st1.T
        p_in = self.states[1]
        for i in range(n_fwh + 1):
            p_target = fwh_pressures[i] if i < n_fwh else P_max
            st_out = self.pump.solve(p_in, p_target, eta_p, self.fluid)
            st_out.note = f"Pump {i+1} Exit"
            self.states[len(self.states) + 1] = st_out
            self._w_pumps += st_out.h - p_in.h

            if i < n_fwh:
                p_in = self.get_state('P', p_target, 'Q', 0, f"FWH {i+1} Exit")
                self.states[len(self.states) + 1] = p_in

        st_boil = self.get_state('P', P_max, 'T', T_max, "Boiler Exit")
        self.states[len(self.states) + 1] = st_boil
        self._q_in += st_boil.h - st_out.h

        pr_stage = (P_max / P_min) ** (1 / max(1, n_rh + 1))
        t_in = st_boil
        for i in range(n_rh + 1):
            p_out = P_max / (pr_stage ** (i + 1)) if i < n_rh else P_min
            st_out = self.turbine.solve(t_in, p_out, eta_t, self.fluid)
            st_out.note = f"Turbine {i+1} Exit"
            self.states[len(self.states) + 1] = st_out
            self._w_turbines += t_in.h - st_out.h

            if i < n_rh:
                t_in = self.get_state('P', p_out, 'T', T_max, f"Reheat {i+1} Exit")
                self.states[len(self.states) + 1] = t_in
                self._q_in += t_in.h - st_out.h

        return self.states

    def calculate_performance(self):
        if not self.states:
            return {}
        w_net = self._w_turbines - self._w_pumps
        efficiency = (w_net / self._q_in) * 100 if self._q_in > 0 else 0
        last_state = self.states[max(self.states)]
        q_out = last_state.h - self.states[1].h
        s_gen = self.calculate_entropy_generation(self._q_in, self.T_hot, q_out, self.T_cold)
        sl_eff = self.calculate_second_law_efficiency(efficiency, self.T_hot, self.T_cold)
        self.metrics = {
            'efficiency': efficiency,
            'w_net': w_net / 1000,
            'q_in': self._q_in / 1000,
            'q_out': q_out / 1000,
            's_gen': s_gen,
            'second_law_efficiency': sl_eff,
        }
        return self.metrics

    def validate_inputs(self, params):
        errors = []
        if params['P_min'] >= params['P_max']:
            errors.append("P_max must be greater than P_min.")
        if params['T_max'] <= 0:
            errors.append("T_max must be a positive temperature.")
        if params.get('n_rh', 0) < 0:
            errors.append("Reheat stages cannot be negative.")
        if params.get('n_fwh', 0) < 0:
            errors.append("Feedwater heater count cannot be negative.")
        return errors
