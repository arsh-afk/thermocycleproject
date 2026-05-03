"""
Refrigeration Cycle Solver
Educational note: Standard vapor-compression, gas refrigeration, cascade, and absorption models.
SOURCE: Cengel, Thermodynamics: An Engineering Approach, Chapter 11.
"""
from core.base_cycle import BaseCycle
from core.components import Compressor, Turbine

class RefrigerationCycle(BaseCycle):
    """
    Versatile Refrigeration Cycle solver supporting multiple configurations.
    Engineering Principle: Refrigeration cycles move heat from a low-temperature region
    to a high-temperature region, requiring a net work input (W_in).
    Performance is measured by the Coefficient of Performance (COP).
    """
    def __init__(self, fluid="R134a"):
        """
        Initializes the refrigeration cycle.
        
        Args:
            fluid (str): Refrigerant (e.g., 'R134a', 'Ammonia', 'R22').
        """
        super().__init__(fluid)
        self.compressor = Compressor("Compressor")
        self.turbine = Turbine("Expansion Turbine")

    def solve(self, params):
        """
        Routes the solver to the appropriate refrigeration model.
        
        Engineering Principle: 
        1. Vapor-compression: Most common, uses a phase-change fluid.
        2. Gas refrigeration: Used in aircraft cooling, stays in gas phase.
        3. Cascade: Two cycles coupled to achieve very low temperatures.
        """
        self.clear_states()
        
        cycle_type = params.get('type', 'vapor_compression')
        
        if cycle_type == 'vapor_compression':
            return self._solve_vapor_compression(params)
        elif cycle_type == 'gas_refrigeration':
            return self._solve_gas_refrigeration(params)
        elif cycle_type == 'cascade':
            return self._solve_cascade(params)
        elif cycle_type == 'multistage':
            return self._solve_multistage(params)
        elif cycle_type == 'absorption':
            return self._solve_absorption(params)
        else:
            self.errors.append(f"Unknown refrigeration cycle type: {cycle_type}")
            return {}

    def _solve_vapor_compression(self, params):
        """
        Ideal or Realistic Vapor-Compression Refrigeration Cycle.
        Processes: 1-2 Comp, 2-3 Condensation, 3-4 Expansion (Isenthalpic), 4-1 Evaporation.
        """
        defaults = {
            'P_low': 0.14 * 1e6,
            'P_high': 0.8 * 1e6,
            'eta_c': 1.0, # Isentropic efficiency
            'dT_sh': 0.0, # Superheat at evaporator exit
            'dT_sc': 0.0, # Subcooling at condenser exit
        }
        current = defaults.copy()
        if 'P_low' in params: current['P_low'] = params['P_low'] * 1e6
        if 'P_high' in params: current['P_high'] = params['P_high'] * 1e6
        if 'eta_c' in params: current['eta_c'] = params['eta_c']
        if 'dT_sh' in params: current['dT_sh'] = params['dT_sh']
        if 'dT_sc' in params: current['dT_sc'] = params['dT_sc']
        
        # State 1: Evaporator Exit / Compressor Inlet
        st1_sat = self.get_state('P', current['P_low'], 'Q', 1)
        if current['dT_sh'] > 0:
            # Superheating improves compressor safety by ensuring no liquid droplets.
            self.states[1] = self.get_state('P', current['P_low'], 'T', st1_sat.T + current['dT_sh'], "Evap Exit (SH)")
        else:
            self.states[1] = st1_sat
            self.states[1].note = "Evap Exit (Sat Vap)"
            
        # State 2: Compressor Exit
        self.states[2] = self.compressor.solve(self.states[1], current['P_high'], current['eta_c'], self.fluid)
        
        # State 3: Condenser Exit / Expansion Valve Inlet
        st3_sat = self.get_state('P', current['P_high'], 'Q', 0)
        if current['dT_sc'] > 0:
            # Subcooling increases the cooling capacity (q_L).
            self.states[3] = self.get_state('P', current['P_high'], 'T', st3_sat.T - current['dT_sc'], "Cond Exit (SC)")
        else:
            self.states[3] = st3_sat
            self.states[3].note = "Cond Exit (Sat Liq)"
            
        # State 4: Expansion Valve Exit / Evaporator Inlet
        # Process 3-4 is Isenthalpic (h4 = h3) for a throttling valve.
        self.states[4] = self.get_state('P', current['P_low'], 'H', self.states[3].h, "Expansion Exit")
        self._mode = 'vapor_compression'
        self.T_hot = st3_sat.T
        self.T_cold = st1_sat.T
        return self.states

    def _solve_gas_refrigeration(self, params):
        """
        Reverse Brayton Cycle for gas refrigeration.
        Uses a turbine instead of an expansion valve to recover work and reach lower temperatures.
        """
        defaults = {
            'P_low': 0.1 * 1e6, 'P_high': 0.4 * 1e6, 'T_min': 250.0, 'T_max': 300.0,
        }
        current = defaults.copy()
        if 'P_low' in params: current['P_low'] = params['P_low'] * 1e6
        if 'P_high' in params: current['P_high'] = params['P_high'] * 1e6
        
        self.states[1] = self.get_state('P', current['P_low'], 'T', current['T_min'], "Comp Inlet")
        self.states[2] = self.compressor.solve(self.states[1], current['P_high'], params.get('eta_c', 1.0), self.fluid)
        self.states[3] = self.get_state('P', current['P_high'], 'T', current['T_max'], "Turb Inlet")
        self.states[4] = self.turbine.solve(self.states[3], current['P_low'], params.get('eta_t', 1.0), self.fluid)
        self._mode = 'gas_refrigeration'
        self.T_hot = current['T_max']
        self.T_cold = current['T_min']
        return self.states

    def _solve_cascade(self, params):
        """
        Couples two cycles at different pressure/temperature levels.
        The evaporator of the high-temp cycle cools the condenser of the low-temp cycle.
        """
        P_mid = params.get('P_mid', 0.4) * 1e6
        params_A = params.copy()
        params_B = params.copy()
        params_A['P_low'] = P_mid / 1e6
        params_B['P_high'] = P_mid / 1e6
        
        self.cycle_A = RefrigerationCycle(self.fluid)
        self.cycle_B = RefrigerationCycle(self.fluid)
        self.cycle_A.solve(params_A)
        self.cycle_B.solve(params_B)
        
        # Energy balance for the intermediate heat exchanger:
        # m_A * (h_A1 - h_A4) = m_B * (h_B2 - h_B3)
        h_B2, h_B3 = self.cycle_B.states[2].h, self.cycle_B.states[3].h
        h_A1, h_A4 = self.cycle_A.states[1].h, self.cycle_A.states[4].h
        self.m_ratio = (h_B2 - h_B3) / (h_A1 - h_A4)
        
        # Flatten states for visualization
        for sid, st in self.cycle_A.states.items():
            self.states[f"A{sid}"] = st
        for sid, st in self.cycle_B.states.items():
            self.states[f"B{sid}"] = st
            
        self._mode = 'cascade'
        return self.states

    def _solve_multistage(self, params):
        """
        Vapor-compression with a flash chamber for intercooling.
        Improves efficiency by removing vapor before the evaporator.
        """
        P_low = params.get('P_low', 0.14) * 1e6
        P_mid = params.get('P_mid', 0.4) * 1e6
        P_high = params.get('P_high', 1.0) * 1e6
        eta_c = params.get('eta_c', 1.0)
        
        self.states[1] = self.get_state('P', P_low, 'Q', 1, "LP Comp In")
        self.states[2] = self.compressor.solve(self.states[1], P_mid, eta_c, self.fluid)
        self.states[3] = self.get_state('P', P_mid, 'Q', 1, "Flash Vap")
        
        st5 = self.get_state('P', P_high, 'Q', 0, "Cond Out")
        self.states[5] = st5
        st6 = self.get_state('P', P_mid, 'H', st5.h, "Flash In")
        self.states[6] = st6
        x_flash = st6.x
        
        # Mixing of LP compressor exit and flash vapor
        h9 = (1 - x_flash) * self.states[2].h + x_flash * self.states[3].h
        self.states[9] = self.get_state('P', P_mid, 'H', h9, "HP Comp In")
        self.states[4] = self.compressor.solve(self.states[9], P_high, eta_c, self.fluid)
        self.states[7] = self.get_state('P', P_mid, 'Q', 0, "Flash Liq")
        self.states[8] = self.get_state('P', P_low, 'H', self.states[7].h, "Evap In")
        
        self._mode = 'multistage'
        self._x_flash = x_flash
        self.T_hot = st5.T
        self.T_cold = self.states[1].T
        return self.states

    def _solve_absorption(self, params):
        """
        Absorption refrigeration uses heat instead of work as the primary energy source.
        Analyzed here via maximum theoretical COP based on source/sink temperatures.
        """
        self.T_source = params.get('T_source', 150.0) + 273.15
        self.T_env = params.get('T_env', 25.0) + 273.15
        self.T_ref = params.get('T_ref', -10.0) + 273.15
        self._mode = 'absorption'
        return {}

    def calculate_performance(self):
        """
        Calculates COP and cooling capacity.
        Engineering Principle: COP_R = Useful Cooling / Work Input.
        """
        if not self.states and getattr(self, '_mode', '') != 'absorption':
            return {}
            
        mode = getattr(self, '_mode', 'vapor_compression')
        
        # We need a fallback q_in and q_out and T_hot and T_cold for generic exergy destruction
        T_hot = getattr(self, 'T_hot', 300.0)
        T_cold = getattr(self, 'T_cold', 250.0)
        
        if mode == 'cascade':
            met_A = self.cycle_A.calculate_performance()
            met_B = self.cycle_B.calculate_performance()
            w_net_in = self.m_ratio * met_A['w_net_in'] + met_B['w_net_in']
            q_L = met_B['q_L']
            cop_r = q_L / w_net_in if w_net_in > 0 else 0
            
            s_gen = self.calculate_entropy_generation(w_net_in*1000 + q_L*1000, T_hot, q_L*1000, T_cold) # Appx
            x_dest = self.calculate_exergy_destruction(s_gen)
            
            self.metrics = {'COP_R': cop_r, 'w_net_in': w_net_in, 'q_L': q_L, 'mass_ratio_A_B': self.m_ratio, 'x_dest': x_dest/1000 if x_dest else None}
        elif mode == 'multistage':
            x = self._x_flash
            h1, h2, h4, h8, h9 = self.states[1].h, self.states[2].h, self.states[4].h, self.states[8].h, self.states[9].h
            q_L = (1 - x) * (h1 - h8)
            w_in = (1 - x) * (h2 - h1) + (h4 - h9)
            cop_r = q_L / w_in if w_in > 0 else 0
            s_gen = self.calculate_entropy_generation(w_in + q_L, T_hot, q_L, T_cold)
            x_dest = self.calculate_exergy_destruction(s_gen)
            self.metrics = {'COP_R': cop_r, 'w_net_in': w_in / 1000, 'q_L': q_L / 1000, 'x_dest': x_dest/1000 if x_dest else None}
        elif mode == 'absorption':
            T0, Ts, TL = self.T_env, self.T_source, self.T_ref
            # Engineering Principle: Max COP_abs = (1 - T0/Ts) * (TL/(T0-TL))
            cop_max = (1 - T0 / Ts) * (TL / (T0 - TL)) if (Ts > T0 and T0 > TL) else 0
            self.metrics = {'COP_max': cop_max, 'T_source': Ts-273.15, 'T_env': T0-273.15, 'T_ref': TL-273.15}
        else:
            h1, h2, h3, h4 = self.states[1].h, self.states[2].h, self.states[3].h, self.states[4].h
            q_L = h1 - h4
            q_H = h2 - h3
            if mode == 'vapor_compression': w_net_in = h2 - h1
            else: w_net_in = (h2 - h1) - (h3 - h4)
            cop_r = q_L / w_net_in if w_net_in > 0 else 0
            s_gen = self.calculate_entropy_generation(q_H, T_hot, q_L, T_cold)
            x_dest = self.calculate_exergy_destruction(s_gen)
            self.metrics = {'COP_R': cop_r, 'q_L': q_L/1000, 'w_net_in': w_net_in/1000, 'x_dest': x_dest/1000 if x_dest else None}
            
        return self.metrics

    def validate_inputs(self, params):
        """Ensures that the condenser pressure is higher than the evaporator pressure."""
        p_low = params.get('P_low', 0.14)
        p_high = params.get('P_high', 0.8)
        if p_low >= p_high: 
            self.errors.append("High pressure must be greater than low pressure.")
        return len(self.errors) == 0

    def get_component_list(self):
        """Returns visual component names based on the active mode."""
        mode = getattr(self, '_mode', '')
        if mode == 'vapor_compression':
            return ["Compressor", "Condenser", "Expansion Valve", "Evaporator"]
        elif mode == 'gas_refrigeration':
            return ["Compressor", "Heat Exchanger (High)", "Turbine", "Heat Exchanger (Low)"]
        elif mode == 'cascade':
            return ["Cycle A Comp", "Cycle A Cond", "Inter-stage HX", "Cycle B Comp", "Cycle B Evap"]
        elif mode == 'multistage':
            return ["LP Comp", "Flash Chamber", "HP Comp", "Condenser", "Expansion Valve", "Evaporator"]
        return ["Refrigeration System"]
