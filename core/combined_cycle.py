"""
Combined Gas-Vapor Power Cycle Solver
Educational note: A Brayton (Gas) cycle topping a Rankine (Vapor) cycle.
The high-temperature exhaust from the gas turbine is used to generate steam in a 
Heat Recovery Steam Generator (HRSG).
SOURCE: Cengel, Thermodynamics: An Engineering Approach, Chapter 10.
"""
from core.base_cycle import BaseCycle
from core.brayton_cycle import BraytonCycle
from core.rankine_cycle import RankineCycle

class CombinedCycle(BaseCycle):
    """
    Combined Cycle solver.
    Engineering Principle: The combined cycle exploits the high-temperature heat addition 
    of the Brayton cycle and the low-temperature heat rejection of the Rankine cycle,
    resulting in an overall thermal efficiency higher than either individual cycle.
    """
    def __init__(self):
        """Initializes the combined cycle with Air (Brayton) and Water (Rankine)."""
        super().__init__("Air + Water")
        self.brayton = BraytonCycle("Air")
        self.rankine = RankineCycle("Water")

    def solve(self, params):
        """
        Solves the combined cycle by coupling the gas and vapor stages.
        
        Engineering Principle: 
        The energy rejected by the gas cycle is absorbed by the vapor cycle:
        m_gas * (h_gas_exit - h_gas_stack) = m_steam * (h_steam_exit - h_feedwater).
        This defines the mass ratio (m_gas / m_steam).
        """
        self.clear_states()
        
        # Parameters for Brayton part
        brayton_params = {
            'P_min': params.get('B_P_min', 0.1),
            'P_max': params.get('B_P_max', 1.2),
            'T_min': params.get('B_T_min', 25.0),
            'T_max': params.get('B_T_max', 1100.0),
        }
        
        # Parameters for Rankine part
        rankine_params = {
            'P_min': params.get('R_P_min', 0.01),
            'P_max': params.get('R_P_max', 10.0),
            'T_max': params.get('R_T_max', 450.0),
        }
        
        # Solve Brayton first: Provides the 'source' heat for the Rankine part.
        self.brayton.solve(brayton_params)
        b_metrics = self.brayton.calculate_performance()
        
        # Solve Rankine: The 'bottoming' cycle.
        self.rankine.solve(rankine_params)
        r_metrics = self.rankine.calculate_performance()
        
        # Pinch-Point Analysis for HRSG
        # Gas enters at T_gas_in (Brayton turbine exit) and leaves at T_stack.
        # Steam enters at T_feed (Rankine pump exit) and leaves at T_steam_out (Boiler exit).
        # Pinch point usually occurs where water reaches saturation (T_sat).
        st_gas_in = self.brayton.states[max(self.brayton.states)] # Actually it's turbine exit, but let's say state before cooler
        # Find the actual gas turbine exit state
        for sid, st in self.brayton.states.items():
            if st.note and "Turbine" in st.note and "Exit" in st.note:
                st_gas_in = st
                break
        
        st_steam_out = self.rankine.states[2] # Boiler exit
        st_feed = self.rankine.states[1] # Technically pump exit or FWH exit, but let's use the last fw state
        for sid, st in self.rankine.states.items():
            if st.note == "Boiler Exit":
                st_steam_out = st
            elif st.note and "Boiler Inlet" in st.note:
                st_feed = st
        
        # We need the saturation state of water at P_max
        st_sat_water = self.rankine.get_state('P', rankine_params['P_max']*1e6, 'Q', 0)
        
        # Determine the maximum steam flow allowed by the pinch point (e.g. 10 K)
        pinch_delta = 10.0
        # Energy balance from gas inlet to pinch point:
        # m_gas * Cp_gas * (T_gas_in - (T_sat_water + pinch_delta)) = m_steam * (h_steam_out - h_sat_water)
        # Approximate Cp_gas = 1050 J/kgK
        Cp_gas = 1050.0
        
        T_gas_in = st_gas_in.T
        T_sat = st_sat_water.T
        h_steam_out = st_steam_out.h
        h_sat_water = st_sat_water.h
        
        # Maximum m_steam / m_gas
        m_ratio_inv = (Cp_gas * (T_gas_in - (T_sat + pinch_delta))) / max(h_steam_out - h_sat_water, 1e-6)
        
        if m_ratio_inv <= 0:
            self.errors.append("Pinch-point violation: Gas turbine exhaust is too cold to generate this steam.")
            m_ratio = 1.0
        else:
            m_ratio = 1.0 / m_ratio_inv
        
        # Now calculate T_stack based on full energy balance
        # m_gas * Cp_gas * (T_gas_in - T_stack) = m_steam * (h_steam_out - h_feedwater)
        q_in_R = r_metrics['q_in'] * 1000 # J/kg_steam
        T_stack = T_gas_in - (q_in_R / (m_ratio * Cp_gas))
        
        if T_stack < st_feed.T + pinch_delta:
            # Secondary pinch point violation at the cold end. Adjust m_ratio.
            T_stack = st_feed.T + pinch_delta
            m_ratio = q_in_R / (Cp_gas * (T_gas_in - T_stack))
            
        self.m_ratio = m_ratio
        self.T_stack = T_stack
        
        # Total performance per unit mass of steam
        # Engineering Principle: w_total = w_net_R + (m_gas/m_steam) * w_net_B
        w_net_B = b_metrics['w_net'] * 1000
        w_net_R = r_metrics['w_net'] * 1000
        q_in_B = b_metrics['q_in'] * 1000
        
        self._w_net = m_ratio * w_net_B + w_net_R
        self._q_in = m_ratio * q_in_B
        
        # Store combined states for visualization with prefixes (B for Brayton, R for Rankine)
        for sid, st in self.brayton.states.items():
            self.states[f"B{sid}"] = st
        for sid, st in self.rankine.states.items():
            self.states[f"R{sid}"] = st
        
        return self.states

    def calculate_performance(self):
        """Calculates the overall thermal efficiency of the combined cycle."""
        if not self._q_in:
            return {}
            
        # η_combined = W_net,total / Q_in,total
        efficiency = (self._w_net / self._q_in) * 100
        
        self.metrics = {
            'efficiency': efficiency,
            'w_net': self._w_net / 1000,
            'q_in': self._q_in / 1000,
            'mass_ratio_gas_steam': self.m_ratio,
            'brayton_efficiency': self.brayton.metrics['efficiency'],
            'rankine_efficiency': self.rankine.metrics['efficiency'],
        }
        return self.metrics

    def validate_inputs(self, params):
        """Validation is handled by sub-cycles (Brayton and Rankine)."""
        # We can delegate to sub-cycles if needed, but for now just return True
        return len(self.errors) == 0

    def get_component_list(self):
        """Returns the sequence of components across both cycles and the HRSG coupler."""
        comps = []
        for c in self.brayton.get_component_list():
            comps.append(f"Brayton {c}")
        comps.append("HRSG (Heat Recovery Steam Generator)")
        for c in self.rankine.get_component_list():
            comps.append(f"Rankine {c}")
        return comps
