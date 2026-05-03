"""
Thermodynamic State Management
Educational note: The State Postulate (Cengel, Ch 1) states that the thermodynamic state 
of a simple compressible system is completely specified by two independent, intensive properties.
This class stores all properties for a specific point in the cycle.
"""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ThermodynamicState:
    """
    Object representing a unique thermodynamic point.
    Internal units follow SI: T(K), P(Pa), h(J/kg), s(J/kg·K).
    """
    T: Optional[float] = None  # Temperature (K)
    P: Optional[float] = None  # Pressure (Pa)
    h: Optional[float] = None  # Enthalpy (J/kg) - Energy content per unit mass
    s: Optional[float] = None  # Entropy (J/kg·K) - Measure of molecular disorder
    v: Optional[float] = None  # Specific volume (m³/kg) - Inverse of density
    x: Optional[float] = None  # Quality (0-1): Ratio of vapor mass to total mass
    rho: Optional[float] = None  # Density (kg/m³)
    note: str = "" # Description of the state (e.g., 'Turbine Inlet')
    is_supercritical: bool = False # Flag for states above the critical point
    phase_label: str = "" # Label: 'Single-Phase', 'Two-Phase', or 'Supercritical'
    source: str = "" # Data source (e.g., 'CoolProp', 'IAPWS')
    fluid: str = "" # Fluid name (e.g., 'Water', 'Air')
    err: dict = field(default_factory=lambda: {'T': 0, 'P': 0, 'h': 0, 's': 0})

    @property
    def u(self):
        """Internal energy (J/kg): u = h - P*v. Computed on demand."""
        if self.h is not None and self.P is not None and self.v is not None:
            return self.h - self.P * self.v
        return None

    def to_dict(self):
        """
        Converts properties to a dictionary for JSON/CSV export or UI display.
        Useful for students to extract data for external analysis in Excel/MATLAB.
        """
        return {
            'T': self.T,
            'P': self.P,
            'h': self.h,
            's': self.s,
            'v': self.v,
            'x': self.x,
            'rho': self.rho,
            'note': self.note,
            'is_supercritical': self.is_supercritical,
            'phase': self.phase_label,
            'source': self.source,
        }

    def __repr__(self):
        """Readable string representation of the state for debugging and logging."""
        if self.T is None or self.P is None:
            return f"State({self.note})"
        return f"State({self.note}: T={self.T:.2f}K, P={self.P/1e6:.3f}MPa)"
