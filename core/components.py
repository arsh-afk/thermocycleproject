"""
Cycle Component Definitions
Educational note: Reusable components (turbines, pumps, heat exchangers) simplify 
cycle modeling and allow specific efficiency models per component.

Engineering Principle: Each component is treated as a steady-flow control volume.
The First Law (Energy Balance) and Second Law (Isentropic Efficiency) are applied
to determine exit states from inlet conditions.
"""
from utils.property_wrapper import PropertyWrapper

class Component:
    """
    Base class for all thermodynamic components.
    Provides a common naming structure for cycle elements.
    """
    def __init__(self, name):
        """
        Initializes a component with a name.
        
        Args:
            name (str): Identifier for the component (e.g., 'High Pressure Turbine').
        """
        self.name = name

class Turbine(Component):
    """
    Energy extraction device (Turbine/Expander).
    Engineering Principle: Turbines produce work by expanding a fluid from high to low pressure.
    """
    def solve(self, state_in, P_out, eta_isen, fluid):
        """
        Solves the expansion process through the turbine.
        
        Args:
            state_in (ThermodynamicState): The state of the fluid at the turbine inlet.
            P_out (float): The desired exit pressure (Pa).
            eta_isen (float): Isentropic efficiency (0.0 to 1.0).
            fluid (str): The working fluid.
            
        Returns:
            ThermodynamicState: The actual exit state.
            
        Engineering Principle: 
        1. Calculate isentropic exit enthalpy (h_s) where s_exit = s_in.
        2. Calculate actual exit enthalpy (h_a) using: h_a = h_in - η_t * (h_in - h_s).
        """
        # Ideal (isentropic) expansion: Process 1-2s (constant entropy)
        state_out_ideal = PropertyWrapper.get_state(fluid, 'P', P_out, 'S', state_in.s, f"{self.name} Ideal")
        
        # Actual expansion: Process 1-2a (accounting for internal irreversibilities)
        h_actual = state_in.h - eta_isen * (state_in.h - state_out_ideal.h)
        state_out = PropertyWrapper.get_state(fluid, 'P', P_out, 'H', h_actual, f"{self.name} Actual")
        
        return state_out

class Compressor(Component):
    """
    Work input device for gases.
    Engineering Principle: Compressors increase gas pressure, requiring work input.
    """
    def solve(self, state_in, P_out, eta_isen, fluid):
        """
        Solves the compression process.
        
        Engineering Principle:
        Actual work is greater than isentropic work: h_a = h_in + (h_s - h_in) / η_c.
        """
        # Ideal (isentropic) compression: s_out = s_in
        state_out_ideal = PropertyWrapper.get_state(fluid, 'P', P_out, 'S', state_in.s, f"{self.name} Ideal")
        
        # Actual compression
        h_actual = state_in.h + (state_out_ideal.h - state_in.h) / eta_isen
        state_out = PropertyWrapper.get_state(fluid, 'P', P_out, 'H', h_actual, f"{self.name} Actual")
        
        return state_out

class Pump(Component):
    """
    Work input device for liquids.
    Engineering Principle: Pumps increase the pressure of incompressible or slightly 
    compressible liquids. Work input is typically small compared to turbines.
    """
    def solve(self, state_in, P_out, eta_isen, fluid):
        """
        Solves the pumping process.
        
        Engineering Principle: For liquids, work is often approximated as v*ΔP,
        but here we use full property data (h_a = h_in + (h_s - h_in) / η_p).
        """
        # Ideal (isentropic) compression
        state_out_ideal = PropertyWrapper.get_state(fluid, 'P', P_out, 'S', state_in.s, f"{self.name} Ideal")
        
        h_actual = state_in.h + (state_out_ideal.h - state_in.h) / eta_isen
        state_out = PropertyWrapper.get_state(fluid, 'P', P_out, 'H', h_actual, f"{self.name} Actual")
        
        return state_out

class HeatExchanger(Component):
    """
    Heat transfer device (Boilers, Condensers, Recuperators).
    Engineering Principle: Accounts for pressure drops if specified.
    """
    def solve_exit(self, state_in, P_out_nominal, T_out, fluid, pressure_drop=0.0):
        """
        Solves for the exit state given temperature and nominal pressure.
        Applies a pressure drop (Pa) if specified.
        """
        P_actual = P_out_nominal - pressure_drop
        return PropertyWrapper.get_state(fluid, 'P', P_actual, 'T', T_out, f"{self.name} Exit")
    
    def solve_sat_exit(self, state_in, P_out_nominal, x_out, fluid, pressure_drop=0.0):
        """
        Solves for the exit state at a specific quality (x).
        Applies a pressure drop (Pa) if specified.
        """
        P_actual = P_out_nominal - pressure_drop
        return PropertyWrapper.get_state(fluid, 'P', P_actual, 'Q', x_out, f"{self.name} Exit")

class Nozzle(Component):
    """
    Kinetic energy conversion device (increases velocity at the expense of pressure).
    Engineering Principle: Isentropic expansion is used to calculate exit velocity.
    Steady-Flow Energy Equation: h_in + (V_in^2)/2 = h_out + (V_out^2)/2
    """
    def solve(self, state_in, P_out, eta_n, fluid, V_in=0.0):
        """
        Solves the nozzle expansion to find exit state and velocity.
        """
        # Ideal isentropic expansion
        state_out_s = PropertyWrapper.get_state(fluid, 'P', P_out, 'S', state_in.s, f"{self.name} Ideal")
        # Actual exit enthalpy based on nozzle efficiency
        h_actual = state_in.h - eta_n * (state_in.h - state_out_s.h)
        state_out = PropertyWrapper.get_state(fluid, 'P', P_out, 'H', h_actual, f"{self.name} Actual")
        
        # Calculate exit velocity (assuming V_in is small if not provided)
        V_out = (2 * (state_in.h - h_actual) + V_in**2)**0.5
        return state_out, V_out

class Diffuser(Component):
    """
    Kinetic energy conversion device (decreases velocity to increase pressure).
    Engineering Principle: Converts kinetic energy into enthalpy/pressure.
    """
    def solve(self, state_in, V_in, V_out, eta_d, fluid):
        """
        Solves the diffuser compression to find exit state.
        """
        # Actual enthalpy increase from kinetic energy change
        h_actual = state_in.h + (V_in**2 - V_out**2) / 2
        
        # Determine ideal enthalpy change to find exit pressure
        h_ideal = state_in.h + (h_actual - state_in.h) * eta_d
        
        # Iterate or use approximation for exit state.
        # For simplicity, we find the pressure that matches h_ideal at constant entropy,
        # then find actual state at P_out and h_actual.
        # In reality, this requires an iterative or reverse lookup solver in CoolProp.
        # Approximating by looking up state at ideal h and s:
        # Note: D_in = V_in. If it's a gas, Cp ~ const.
        # Let's do a simple temperature rise approximation for ideal gas if needed, or
        # try to use CoolProp. CoolProp supports (H, S) inputs.
        state_out_ideal = PropertyWrapper.get_state(fluid, 'H', h_ideal, 'S', state_in.s, f"{self.name} Ideal")
        P_out = state_out_ideal.P
        state_out = PropertyWrapper.get_state(fluid, 'P', P_out, 'H', h_actual, f"{self.name} Actual")
        return state_out

class MixingChamber(Component):
    """
    Device where two or more fluid streams mix to form a single exit stream.
    Engineering Principle: Based on conservation of mass and energy.
    Σ(m_in * h_in) = m_out * h_out
    """
    def solve(self, inlets, P_out, fluid):
        """
        Solves for the exit state of a mixing chamber.
        
        Args:
            inlets (list): List of tuples (state, mass_fraction).
            P_out (float): Pressure of the mixing chamber (Pa).
            fluid (str): Working fluid.
        """
        total_mh = sum(st.h * m for st, m in inlets)
        total_m = sum(m for st, m in inlets)
        h_exit = total_mh / total_m
        return PropertyWrapper.get_state(fluid, 'P', P_out, 'H', h_exit, f"{self.name} Exit")

class ThrottlingValve(Component):
    """
    Pressure reducing device (Expansion Valve / PRV).
    Engineering Principle: Throttling is an isenthalpic process (h_in = h_out).
    """
    def solve(self, state_in, P_out, fluid):
        """
        Solves for the exit state after throttling.
        """
        return PropertyWrapper.get_state(fluid, 'P', P_out, 'H', state_in.h, f"{self.name} Exit")

class FlashChamber(Component):
    """
    Separation device for two-phase mixtures.
    Engineering Principle: Saturated liquid and vapor are separated at constant pressure.
    """
    def solve(self, state_in):
        """
        Returns the saturated liquid and saturated vapor states.
        
        Returns:
            tuple: (Sat Liquid State, Sat Vapor State, Quality x)
        """
        fluid = state_in.fluid
        P = state_in.P
        st_liq = PropertyWrapper.get_state(fluid, 'P', P, 'Q', 0, f"{self.name} Liquid")
        st_vap = PropertyWrapper.get_state(fluid, 'P', P, 'Q', 1, f"{self.name} Vapor")
        return st_liq, st_vap, state_in.x

class ClosedFeedwaterHeater(Component):
    """
    Non-contact heat exchanger for Rankine cycles.
    Engineering Principle: Heat is transferred from extracted steam to feedwater
    without mixing. Exit states are governed by TTD and DCA.
    """
    def __init__(self, name, ttd=2.8, dca=5.6):
        """
        Args:
            ttd (float): Terminal Temperature Difference (T_sat_steam - T_fw_out).
            dca (float): Drain Cooler Approach (T_drain_out - T_fw_in).
        """
        super().__init__(name)
        self.ttd = ttd
        self.dca = dca

    def solve(self, st_fw_in, st_steam_ext, P_fw_out, fluid):
        """
        Solves for the exit states of the feedwater and the steam drain.
        """
        # Saturated temperature of the extracted steam at its pressure
        st_sat_steam = PropertyWrapper.get_state(fluid, 'P', st_steam_ext.P, 'Q', 1)
        
        # Feedwater Exit Temperature: T_fw_out = T_sat_steam - TTD
        T_fw_out = st_sat_steam.T - self.ttd
        st_fw_out = PropertyWrapper.get_state(fluid, 'P', P_fw_out, 'T', T_fw_out, f"{self.name} FW Exit")
        
        # Drain Exit Temperature: T_drain = T_fw_in + DCA
        T_drain = st_fw_in.T + self.dca
        st_drain = PropertyWrapper.get_state(fluid, 'P', st_steam_ext.P, 'T', T_drain, f"{self.name} Drain Exit")
        
        return st_fw_out, st_drain
