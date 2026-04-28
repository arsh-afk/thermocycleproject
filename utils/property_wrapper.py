"""
CoolProp Wrapper for Thermodynamic Properties
Handles unit conversions (Internal SI) and physical boundary protection.
Grounded in Span-Wagner (CO2) and IAPWS-IF97 (Water) via CoolProp.
"""
import CoolProp.CoolProp as CP
from core.state import ThermodynamicState

class PropertyWrapper:
    """Centralized property calculation engine with safety checks."""
    
    @staticmethod
    def get_state(fluid, prop1, val1, prop2, val2, note=""):
        """
        Retrieves state from CoolProp with physical boundary validation.
        Internal units: T(K), P(Pa), H(J/kg), S(J/kgK), D(kg/m3).
        """
        try:
            # SOURCE: Fundamental Physical Boundaries check
            # Prevent calling CoolProp for CO2 at pressures below triple point (0.518 MPa)
            if fluid == "CO2":
                P_val = None
                if prop1.upper() == 'P': P_val = val1
                elif prop2.upper() == 'P': P_val = val2
                
                if P_val is not None and P_val < 518000:
                    raise ValueError(f"Pressure {P_val/1e6:.3f} MPa is below CO2 Triple Point (0.518 MPa).")

            # Map input codes to CoolProp format
            p1 = 'Q' if prop1.upper() == 'X' else prop1.upper()
            p2 = 'Q' if prop2.upper() == 'X' else prop2.upper()
            
            T = CP.PropsSI('T', p1, val1, p2, val2, fluid)
            P = CP.PropsSI('P', p1, val1, p2, val2, fluid)
            h = CP.PropsSI('H', p1, val1, p2, val2, fluid)
            s = CP.PropsSI('S', p1, val1, p2, val2, fluid)
            rho = CP.PropsSI('D', p1, val1, p2, val2, fluid)
            
            state = ThermodynamicState(T=T, P=P, h=h, s=s, rho=rho, v=1/rho, note=note)
            
            # Quality detection
            try:
                x = CP.PropsSI('Q', p1, val1, p2, val2, fluid)
                state.x = x
            except:
                state.x = -1 
            
            # Supercritical detection
            # SOURCE: CoolProp critical property constants
            T_crit = CP.PropsSI('T_CRITICAL', fluid)
            P_crit = CP.PropsSI('P_CRITICAL', fluid)
            if T > T_crit and P > P_crit:
                state.is_supercritical = True
                state.phase_label = "Supercritical"
            elif state.x >= 0 and state.x <= 1:
                state.phase_label = "Two-Phase"
            else:
                state.phase_label = "Single-Phase"
                
            return state
            
        except Exception as e:
            # Educational note: Meaningful errors help students understand phase limits.
            raise ValueError(f"Thermodynamic Boundary Error [{fluid}]: {str(e)}")

    @staticmethod
    def get_fluid_constants(fluid):
        return {
            'T_crit': CP.PropsSI('T_CRITICAL', fluid),
            'P_crit': CP.PropsSI('P_CRITICAL', fluid),
            'P_min': CP.PropsSI('P_TRIPLE', fluid) if fluid != 'Air' else 0.05e6,
            'T_min': CP.PropsSI('TTRIPLE', fluid) if fluid != 'Air' else 60.0
        }
