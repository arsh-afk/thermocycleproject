"""
CoolProp Wrapper for Thermodynamic Properties
Handles unit conversions (Internal SI) and physical boundary protection.
Grounded in Span-Wagner (CO2) and IAPWS-IF97 (Water) via CoolProp.
SOURCE: CoolProp Documentation and IAPWS standards.
"""
import logging

import CoolProp.CoolProp as CP
from core.state import ThermodynamicState

logger = logging.getLogger(__name__)

class PropertyWrapper:
    """
    Centralized property calculation engine with safety checks.
    Engineering Principle: Thermodynamic properties are inter-related.
    Given any two independent intensive properties, all other properties can be determined.
    """

    @staticmethod
    def get_state(fluid, prop1, val1, prop2, val2, note=""):
        """
        Retrieves a full thermodynamic state from CoolProp using two inputs.
        Internal units are SI: T(K), P(Pa), H(J/kg), S(J/kgK), D(kg/m3).
        
        Args:
            fluid (str): The fluid name (e.g., 'Water', 'CO2').
            prop1, val1: First property key (e.g., 'P') and value.
            prop2, val2: Second property key (e.g., 'T') and value.
            note (str): Descriptive label for the state.
            
        Engineering Principle: The State Postulate.
        Note: Pressure 'P' and Temperature 'T' are NOT independent in the two-phase region.
        In such cases, 'P' and Quality 'X' or 'T' and Quality 'X' must be used.
        """
        def map_prop(p, v):
            """Internal mapping of property keys to CoolProp standard."""
            p = p.upper()
            if p == 'X': return 'Q', v # Quality
            if p == 'V': return 'D', 1.0 / v # Specific Volume to Density
            return p, v

        p1, v1 = map_prop(prop1, val1)
        p2, v2 = map_prop(prop2, val2)

        # Safety Check for CO2 (Dry Ice boundary)
        if fluid == 'CO2':
            P_val = v1 if p1 == 'P' else (v2 if p2 == 'P' else None)
            if P_val is not None and P_val < 518000:
                raise ValueError(f"Pressure {P_val/1e6:.3f} MPa is below CO2 triple point (0.518 MPa).")

        try:
            # Query CoolProp for core properties
            T = CP.PropsSI('T', p1, v1, p2, v2, fluid)
            P = CP.PropsSI('P', p1, v1, p2, v2, fluid)
            h = CP.PropsSI('H', p1, v1, p2, v2, fluid)
            s = CP.PropsSI('S', p1, v1, p2, v2, fluid)
            rho = CP.PropsSI('D', p1, v1, p2, v2, fluid)
        except Exception as exc:
            logger.exception("CoolProp state calculation failed")
            # Provide helpful range information for debugging non-physical inputs
            limits = PropertyWrapper.get_fluid_limits(fluid)
            limit_str = ""
            if limits:
                limit_str = f"\nValid ranges for {fluid}:\n"
                for prop, (min_val, max_val) in [('T', (limits.get('T_min'), limits.get('T_max'))),
                                                ('P', (limits.get('P_min'), limits.get('P_max'))),
                                                ('H', (limits.get('H_min'), limits.get('H_max'))),
                                                ('S', (limits.get('S_min'), limits.get('S_max')))]:
                    if min_val is not None and max_val is not None:
                        limit_str += f"  {prop}: {min_val:.2e} to {max_val:.2e}\n"
            raise ValueError(f"Thermodynamic calculation failed for {fluid} with {p1}={val1}, {p2}={val2}: {exc}{limit_str}") from exc

        # Construct the state object
        state = ThermodynamicState(T=T, P=P, h=h, s=s, rho=rho, v=(1.0 / rho if rho else None), note=note, fluid=fluid)

        # Attempt to get Quality (X/Q)
        try:
            state.x = CP.PropsSI('Q', p1, val1, p2, val2, fluid)
        except Exception:
            # CoolProp throws exception for quality in subcooled or superheated regions
            state.x = -1 # Convention for single-phase

        # Phase Identification
        T_crit = CP.PropsSI('T_CRITICAL', fluid)
        P_crit = CP.PropsSI('P_CRITICAL', fluid)
        if T > T_crit and P > P_crit:
            state.is_supercritical = True
            state.phase_label = 'Supercritical'
        elif 0 <= state.x <= 1:
            state.phase_label = 'Two-Phase'
        else:
            state.phase_label = 'Single-Phase'

        return state

    @staticmethod
    def get_fluid_limits(fluid):
        """
        Retrieves the valid property ranges for the specified fluid.
        Helps prevent out-of-bounds errors in iterative solvers.
        """
        limits = {}
        limit_keys = [
            ('T_min', 'T_MIN'), ('T_max', 'T_MAX'),
            ('P_min', 'P_MIN'), ('P_max', 'P_MAX'),
            ('H_min', 'HMASS_MIN'), ('H_max', 'HMASS_MAX'),
            ('S_min', 'SMASS_MIN'), ('S_max', 'SMASS_MAX'),
        ]
        for limit_name, cp_key in limit_keys:
            try:
                limits[limit_name] = CP.PropsSI(cp_key, fluid)
            except Exception:
                pass 
        return limits

    @staticmethod
    def get_fluid_constants(fluid):
        """
        Returns critical and triple point constants for a fluid.
        Triple point defines the lower limit of the fluid's validity in the database.
        """
        try:
            return {
                'T_crit': CP.PropsSI('T_CRITICAL', fluid),
                'P_crit': CP.PropsSI('P_CRITICAL', fluid),
                'P_min': CP.PropsSI('P_TRIPLE', fluid) if fluid != 'Air' else 0.05e6,
                'T_min': CP.PropsSI('TTRIPLE', fluid) if fluid != 'Air' else 60.0,
            }
        except Exception as exc:
            logger.exception("Failed to read fluid constants for %s", fluid)
            raise ValueError(f"Unable to retrieve constants for fluid {fluid}: {exc}") from exc
