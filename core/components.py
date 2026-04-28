"""
Cycle Component Definitions
Educational note: Reusable components (turbines, pumps, heat exchangers) simplify 
cycle modeling and allow specific efficiency models per component.
"""
from utils.property_wrapper import PropertyWrapper

class Component:
    """Base class for all thermodynamic components."""
    def __init__(self, name):
        self.name = name

class Turbine(Component):
    """Energy extraction device (Turbine/Expander)."""
    def solve(self, state_in, P_out, eta_isen, fluid):
        """
        Solves expansion process.
        eta_isen: Isentropic efficiency (0-1).
        """
        # Ideal (isentropic) expansion
        state_out_ideal = PropertyWrapper.get_state(fluid, 'P', P_out, 'S', state_in.s, f"{self.name} Ideal")
        
        # Actual expansion
        h_actual = state_in.h - eta_isen * (state_in.h - state_out_ideal.h)
        state_out = PropertyWrapper.get_state(fluid, 'P', P_out, 'H', h_actual, f"{self.name} Actual")
        
        return state_out

class Compressor(Component):
    """Work input device for gases."""
    def solve(self, state_in, P_out, eta_isen, fluid):
        """Solves compression process."""
        # Ideal (isentropic) compression
        state_out_ideal = PropertyWrapper.get_state(fluid, 'P', P_out, 'S', state_in.s, f"{self.name} Ideal")
        
        # Actual compression
        h_actual = state_in.h + (state_out_ideal.h - state_in.h) / eta_isen
        state_out = PropertyWrapper.get_state(fluid, 'P', P_out, 'H', h_actual, f"{self.name} Actual")
        
        return state_out

class Pump(Component):
    """Work input device for liquids."""
    def solve(self, state_in, P_out, eta_isen, fluid):
        """Solves pumping process."""
        # Simple incompressible assumption for initial guess if needed, 
        # but we use full CoolProp for accuracy.
        state_out_ideal = PropertyWrapper.get_state(fluid, 'P', P_out, 'S', state_in.s, f"{self.name} Ideal")
        
        h_actual = state_in.h + (state_out_ideal.h - state_in.h) / eta_isen
        state_out = PropertyWrapper.get_state(fluid, 'P', P_out, 'H', h_actual, f"{self.name} Actual")
        
        return state_out

class HeatExchanger(Component):
    """Constant pressure heat transfer device."""
    def solve_exit(self, state_in, P_out, T_out, fluid):
        """Solves for exit state given exit T and P."""
        return PropertyWrapper.get_state(fluid, 'P', P_out, 'T', T_out, f"{self.name} Exit")
    
    def solve_sat_exit(self, state_in, P_out, x_out, fluid):
        """Solves for exit state given exit P and quality x."""
        return PropertyWrapper.get_state(fluid, 'P', P_out, 'Q', x_out, f"{self.name} Exit")
