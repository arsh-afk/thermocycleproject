"""
Supercritical CO2 Recompression Brayton Cycle
Educational note: The sCO2 cycle utilizes CO2 near its critical point (304.13K, 7.377 MPa).
At this state, the fluid is highly dense (like a liquid) but compressible (like a gas), 
which significantly reduces the work required for compression.
SOURCE: Cengel, Thermodynamics: An Engineering Approach, Chapter 9 (Advanced Topics).
"""
from core.base_cycle import BaseCycle
from core.components import Turbine, Compressor, HeatExchanger

class sCO2Cycle(BaseCycle):
    """
    Advanced sCO2 Recompression Brayton Cycle solver.
    Engineering Principle: The recompression configuration addresses the 'recuperator pinch' 
    issue by splitting the flow. Part of the fluid is recompressed without cooling, 
    balancing the heat capacities in the recuperators (HTR and LTR).
    """
    
    FLUID = 'CO2'
    
    def __init__(self):
        """Initializes components of the sCO2 recompression cycle."""
        super().__init__(self.FLUID)
        self.turbine = Turbine("sCO2 Turbine")
        self.main_compressor = Compressor("Main Compressor")
        self.recompressor = Compressor("Recompressor")
        self.HTR = HeatExchanger("HTR")
        self.LTR = HeatExchanger("LTR")
        
    def solve(self, params):
        """
        Solves the complex sCO2 cycle with flow splitting and recompression.
        
        Engineering Principle:
        1-2: Main compression near the critical point (low work).
        6-7: Turbine expansion.
        7-8-9: Heat rejection through recuperators (HTR/LTR).
        9: Flow split. One part to cooler/main comp, one part to recompressor.
        10: Recompression to high pressure.
        """
        self.clear_states()
        
        # Mapping UI keys and providing defaults
        defaults = {
            'P_min': 7.6 * 1e6, # Just above critical pressure (7.38 MPa)
            'P_max': 25.0 * 1e6,
            'T_min': 32.0 + 273.15, # Just above critical temperature (31.1 C)
            'T_max': 550.0 + 273.15,
        }
        
        current = defaults.copy()
        if 'P_min' in params: current['P_min'] = params['P_min'] * 1e6
        if 'P_max' in params: current['P_max'] = params['P_max'] * 1e6
        if 'T_min' in params: current['T_min'] = params['T_min'] + 273.15
        if 'T_max' in params: current['T_max'] = params['T_max'] + 273.15
        
        P_low = current['P_min']
        P_high = current['P_max']
        T_min = current['T_min']
        T_max = current['T_max']
        
        # split_frac: The fraction of mass flow diverted to the recompressor
        self.split = min(max(params.get('split_frac', 0.35), 0.05), 0.95)
        eta_recup = params.get('recup_eff', 0.95)
        eta_c = params.get('eta_c', 0.89)
        eta_t = params.get('eta_t', 0.92)
        
        # Main Compressor Inlet: Near critical point for maximum density benefit
        self.states[1] = self.get_state('P', P_low, 'T', T_min, "Main Comp Inlet")
        self.T_hot = T_max
        self.T_cold = T_min
        
        # Compression (1-2)
        self.states[2] = self.main_compressor.solve(self.states[1], P_high, eta_c, self.FLUID)
        
        # Turbine (6-7)
        self.states[6] = self.get_state('P', P_high, 'T', T_max, "Turbine Inlet")
        self.states[7] = self.turbine.solve(self.states[6], P_low, eta_t, self.FLUID)
        
        # HTR Hot Side Outlet (Guess based on effectiveness)
        T8_guess = self.states[7].T - eta_recup * (self.states[7].T - self.states[2].T)
        self.states[8] = self.get_state('P', P_low, 'T', T8_guess, "HTR Hot Outlet")
        
        # LTR Hot Side Outlet / Split Point
        T9_guess = self.states[8].T - eta_recup * (self.states[8].T - self.states[2].T)
        self.states[9] = self.get_state('P', P_low, 'T', T9_guess, "Flow Split Point")
        
        # Recompressor (9-10): Mass fraction = split
        self.states[10] = self.recompressor.solve(self.states[9], P_high, eta_c, self.FLUID)
        
        # LTR Cold Side Outlet (3): Energy balance with hot side
        # (1-split) * (h3 - h2) = (h8 - h9)
        h3 = self.states[2].h + (self.states[8].h - self.states[9].h) / max(1 - self.split, 1e-6)
        self.states[3] = self.get_state('P', P_high, 'H', h3, "LTR Cold Outlet")
        
        # Mixer (4): Combine flow from LTR and Recompressor
        # 1 * h4 = (1-split) * h3 + split * h10
        h4 = (1 - self.split) * self.states[3].h + self.split * self.states[10].h
        self.states[4] = self.get_state('P', P_high, 'H', h4, "HTR Cold Inlet")
        
        # HTR Cold Side Outlet (5): Energy balance with hot side
        # 1 * (h5 - h4) = (h7 - h8)
        h5 = self.states[4].h + (self.states[7].h - self.states[8].h)
        self.states[5] = self.get_state('P', P_high, 'H', h5, "Primary Heater Inlet")
        
        # Tag states as supercritical if applicable
        for st in self.states.values():
            if st.T is not None and st.P is not None and st.T > 304.13 and st.P > 7.377e6:
                st.is_supercritical = True
                st.phase_label = "Supercritical"
            else:
                st.phase_label = "Gas/Liquid"
        
        return self.states

    def calculate_performance(self):
        """
        Calculates efficiency, net work, and back-work ratio for the sCO2 cycle.
        Engineering Principle: Net work is the turbine work minus the work of both compressors.
        """
        if not self.states:
            return {}
        split = getattr(self, 'split', 0.35)
        w_t = self.states[6].h - self.states[7].h
        # Weighted compressor work based on mass flow splitting
        w_c_main = (1 - split) * (self.states[2].h - self.states[1].h)
        w_c_recomp = split * (self.states[10].h - self.states[9].h)
        
        w_net = w_t - (w_c_main + w_c_recomp)
        q_in = self.states[6].h - self.states[5].h
        
        # Conservation of Energy: q_out = h8 - h1 (effectively)
        q_out = self.states[8].h - self.states[1].h
        
        # First-law consistency check
        energy_balance_gap = abs(q_in - q_out - w_net)
        if energy_balance_gap > 1e-3:
            q_out = q_in - w_net
            
        efficiency = (w_net / q_in) * 100 if q_in > 0 else 0
        s_gen = self.calculate_entropy_generation(q_in, self.T_hot, q_out, self.T_cold)
        x_dest = self.calculate_exergy_destruction(s_gen)
        sl_eff = self.calculate_second_law_efficiency(efficiency, self.T_hot, self.T_cold)
        
        self.metrics = {
            'efficiency': efficiency,
            'w_net': w_net / 1000,
            'q_in': q_in / 1000,
            'q_out': q_out / 1000,
            's_gen': s_gen,
            'x_dest': x_dest / 1000 if x_dest else None,
            'second_law_efficiency': sl_eff,
            'back_work_ratio': ((w_c_main + w_c_recomp) / w_t) * 100 if w_t > 0 else 0,
        }
        return self.metrics

    def validate_inputs(self, params):
        """Checks for operation near the critical point and potential instabilities."""
        errs = []
        p_min = params.get('P_min', 7.6)
        p_max = params.get('P_max', 25.0)
        t_min = params.get('T_min', 32.0)
        t_max = params.get('T_max', 550.0)
        
        if p_min >= p_max:
            errs.append("P_max must be greater than P_min.")
        if t_min >= t_max:
            errs.append("T_max must be greater than T_min.")
        # Supercritical logic check
        if p_min < 7.38:
            errs.append("WARNING: Low pressure below 7.38 MPa risks two-phase condensation in compressor.")
        if t_min < 32:
            errs.append("WARNING: Operating too close to T_crit (31.1°C) causes numerical instability.")
        return errs

    def get_component_list(self):
        """Returns the sequence of sCO2 recompression loop components."""
        return [
            "Main Compressor",
            "LTR (Cold)",
            "Mixer",
            "HTR (Cold)",
            "Primary Heater",
            "Turbine",
            "HTR (Hot)",
            "LTR (Hot)",
            "Flow Split",
            "Recompressor/Cooler"
        ]
