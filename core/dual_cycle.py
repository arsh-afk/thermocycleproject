"""
Dual Cycle Solver
Educational note: A more realistic model for internal combustion engines that
combines features of both the Otto and Diesel cycles.
Heat addition is split between constant-volume (isochoric) and constant-pressure (isobaric) processes.
SOURCE: Cengel, Thermodynamics: An Engineering Approach, Chapter 9.
"""
from core.base_cycle import BaseCycle

class DualCycle(BaseCycle):
    """
    Ideal Dual Cycle solver.
    Engineering Principle: Real engines do not follow pure Otto or Diesel cycles.
    The Dual cycle uses a pressure ratio (rp) for the constant-volume part and
    a cutoff ratio (rc) for the constant-pressure part of heat addition.
    """
    def __init__(self, fluid="Air"):
        """
        Initializes the Dual cycle.
        
        Args:
            fluid (str): Working fluid, typically 'Air'.
        """
        super().__init__(fluid)
        
    def solve(self, params):
        """
        Solves for the five states of the ideal Dual cycle.
        
        Engineering Principle:
        1-2: Isentropic compression.
        2-X: Constant-volume heat addition (Pressure ratio rp).
        X-3: Constant-pressure heat addition (Cutoff ratio rc).
        3-4: Isentropic expansion.
        4-1: Constant-volume heat rejection.
        """
        self.clear_states()
        
        # Defaults
        defaults = {
            'r': 16.0,   # Compression ratio (v1/v2)
            'rc': 1.2,  # Cutoff ratio (v3/vx)
            'rp': 1.5,  # Pressure ratio (Px/P2)
            'T_min': 25.0 + 273.15,
            'P_min': 0.1 * 1e6,
        }
        
        current = defaults.copy()
        if 'r' in params: current['r'] = params['r']
        if 'rc' in params: current['rc'] = params['rc']
        if 'rp' in params: current['rp'] = params['rp']
        if 'T_min' in params: current['T_min'] = params['T_min'] + 273.15
        if 'P_min' in params: current['P_min'] = params['P_min'] * 1e6
        
        r = current['r']
        rc = current['rc']
        rp = current['rp']
        T1 = current['T_min']
        P1 = current['P_min']
        
        # State 1: Intake BDC
        self.states[1] = self.get_state('P', P1, 'T', T1, "Intake BDC")
        
        # State 2: Compression TDC
        v2 = self.states[1].v / r
        # Isentropic Compression: s2 = s1
        self.states[2] = self.get_state('V', v2, 'S', self.states[1].s, "Compression TDC")
        
        # State X: End of Constant Volume Heat Addition
        # Process 2-X: Volume is constant (vX = v2). Pressure increases by rp.
        Px = self.states[2].P * rp
        self.states['X'] = self.get_state('P', Px, 'V', v2, "Constant V Heat Addition")
        
        # State 3: End of Constant Pressure Heat Addition
        # Process X-3: Pressure is constant (P3 = PX). Volume increases by rc.
        v3 = v2 * rc
        self.states[3] = self.get_state('P', Px, 'V', v3, "Constant P Heat Addition")
        
        # State 4: End of Isentropic Expansion (BDC)
        v4 = self.states[1].v
        # Isentropic Expansion: s4 = s3
        self.states[4] = self.get_state('V', v4, 'S', self.states[3].s, "Expansion BDC")
        
        return self.states

    def calculate_performance(self):
        """
        Calculates thermal efficiency and work based on the First Law.
        Engineering Principle: q_in = q_in,v + q_in,p = (ux - u2) + (h3 - hx).
        """
        if not self.states:
            return {}

        def get_u(st):
            """Internal energy (u) helper: u = h - Pv."""
            return st.h - st.P * st.v

        u1 = get_u(self.states[1])
        u2 = get_u(self.states[2])
        ux = get_u(self.states['X'])
        u4 = get_u(self.states[4])
        hx = self.states['X'].h
        h3 = self.states[3].h

        # Heat Addition Part 1 (Constant Volume): q_in_v = ux - u2
        q_in_v = ux - u2
        # Heat Addition Part 2 (Constant Pressure): q_in_p = h3 - hx
        q_in_p = h3 - hx
        q_in = q_in_v + q_in_p
        
        # Heat Rejection (Constant Volume): q_out = u4 - u1
        q_out = u4 - u1
        w_net = q_in - q_out
        
        T_hot = self.states[3].T
        T_cold = self.states[1].T
        efficiency = (w_net / q_in) * 100 if q_in > 0 else 0
        
        # Second Law Analysis
        s_gen = self.calculate_entropy_generation(q_in, T_hot, q_out, T_cold)
        x_dest = self.calculate_exergy_destruction(s_gen)
        sl_eff = self.calculate_second_law_efficiency(efficiency, T_hot, T_cold)

        return {
            'efficiency': efficiency,
            'w_net': w_net / 1000,
            'q_in': q_in / 1000,
            'q_out': q_out / 1000,
            's_gen': s_gen,
            'x_dest': x_dest / 1000 if x_dest else None,
            'second_law_efficiency': sl_eff,
        }

    def validate_inputs(self, params):
        """Validates compression, cutoff, and pressure ratios."""
        errors = []
        r = params.get('r', 16.0)
        rc = params.get('rc', 1.2)
        rp = params.get('rp', 1.5)
        if r <= 1:
            errors.append("Compression ratio must be greater than 1.")
        if rc < 1:
            errors.append("Cutoff ratio must be at least 1.")
        if rp < 1:
            errors.append("Pressure ratio must be at least 1.")
        return errors

    def get_component_list(self):
        """Returns the sequence of idealized processes in the Dual cycle."""
        return ["Compression", "Combustion (V)", "Combustion (P)", "Expansion", "Exhaust"]
