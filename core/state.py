"""
Thermodynamic State Management
Educational note: A thermodynamic state is defined by two independent properties.
This class stores all properties for a specific point in the cycle.
"""

class ThermodynamicState:
    """Stores thermodynamic properties and uncertainty tracking for a cycle state."""
    def __init__(self, T=None, P=None, h=None, s=None, v=None, x=None, rho=None, note=""):
        self.T = T          # Temperature (K)
        self.P = P          # Pressure (Pa)
        self.h = h          # Enthalpy (J/kg)
        self.s = s          # Entropy (J/kg·K)
        self.v = v          # Specific volume (m³/kg)
        self.x = x          # Quality (0-1, -1 for supercritical, None for subcooled/superheated)
        self.rho = rho      # Density (kg/m³)
        self.note = note    # Description (e.g., "Boiler Exit")
        
        # Phase detection
        self.is_supercritical = False
        self.phase_label = "" # e.g., "Two-Phase", "Superheated Vapor"
        
        # Source tracing
        self.source = ""    # Reference for the specific calculation
        
        # Error tracking (for future uncertainty analysis integration)
        self.err = {'T': 0, 'P': 0, 'h': 0, 's': 0}

    def to_dict(self):
        """Converts properties to a dictionary for JSON/CSV export."""
        return {
            'T': self.T, 'P': self.P, 'h': self.h, 
            's': self.s, 'v': self.v, 'x': self.x, 
            'rho': self.rho, 'note': self.note,
            'is_supercritical': self.is_supercritical,
            'phase': self.phase_label,
            'source': self.source
        }

    def __repr__(self):
        return f"State({self.note}: T={self.T:.2f}K, P={self.P/1e6:.3f}MPa)"
