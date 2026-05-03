"""
General Helper Utilities
Contains common thermodynamic functions and performance metric calculations.
SOURCE: Cengel, Thermodynamics: An Engineering Approach, Chapter 6.
"""
import numpy as np

def calculate_thermal_efficiency(w_net, q_in):
    """
    Calculates thermal efficiency: η_th = w_net / q_in.
    Engineering Principle: Represents the fraction of heat added that is converted to useful work.
    """
    if q_in == 0: return 0
    return (w_net / q_in) * 100

def get_carnot_efficiency(T_high, T_low):
    """
    Maximum theoretical (Carnot) efficiency: η_max = 1 - T_L / T_H.
    Engineering Principle: All temperatures must be in Kelvin (Absolute).
    No heat engine can be more efficient than a Carnot engine operating between the same T limits.
    """
    return (1 - T_low / T_high) * 100

class EESGenerator:
    """
    Utility for generating Engineering Equation Solver (EES) source code.
    Allows users to verify Python/CoolProp results against industry-standard EES logic.
    """
    
    @staticmethod
    def get_fluid_mapping(fluid):
        """Maps Python/CoolProp fluid names to EES standard names."""
        mapping = {
            'Water': 'Steam_IAPWS',
            'Air': 'Air',
            'CarbonDioxide': 'CarbonDioxide',
            'R134a': 'R134a',
            'Ammonia': 'Ammonia',
            'Helium': 'Helium'
        }
        return mapping.get(fluid, fluid)

    @staticmethod
    def generate_state_code(sid, state):
        """Generates EES code for a specific state point lookup."""
        fluid_ees = EESGenerator.get_fluid_mapping(state.fluid)
        T_c = state.T - 273.15
        P_mpa = state.P / 1e6
        
        code = f"\" --- State {sid} Lookup ---\"\n"
        code += f"T_{sid} = {T_c:.2f} [C]\n"
        code += f"P_{sid} = {P_mpa:.4f} [MPa]\n"
        code += f"h_{sid} = ENTHALPY({fluid_ees}, T=T_{sid}, P=P_{sid})\n"
        code += f"s_{sid} = ENTROPY({fluid_ees}, T=T_{sid}, P=P_{sid})\n"
        code += f"v_{sid} = VOLUME({fluid_ees}, T=T_{sid}, P=P_{sid})\n"
        
        explanation = (
            f"This EES code block defines the temperature (T) and pressure (P) for state point {sid}. "
            f"It then uses EES's built-in thermodynamic functions to retrieve enthalpy (h), entropy (s), "
            f"and specific volume (v) for '{fluid_ees}' using the IAPWS-IF97 formulation for water "
            "or the Span-Wagner equation of state for CO2."
        )
        return code, explanation

    @staticmethod
    def generate_performance_code(metrics, cycle_type):
        """Generates EES code for cycle-level efficiency and work."""
        w_net = metrics.get('w_net', 0)
        q_in = metrics.get('q_in', 0)
        
        code = f"\" --- {cycle_type} Performance Verification ---\"\n"
        code += f"W_net = {w_net:.2f} [kJ/kg]\n"
        code += f"Q_in = {q_in:.2f} [kJ/kg]\n"
        code += f"Efficiency = (W_net / Q_in) * 100\n"
        
        explanation = (
            f"This code calculates the overall thermal efficiency of the {cycle_type} cycle. "
            "It takes the net work output and total heat input (in kJ/kg) and applies the "
            "First Law of Thermodynamics for cycles: η = W_net / Q_in."
        )
        return code, explanation
