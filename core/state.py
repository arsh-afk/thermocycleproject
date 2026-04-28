"""
Thermodynamic State Management
Educational note: A thermodynamic state is defined by two independent properties.
This class stores all properties for a specific point in the cycle.
"""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ThermodynamicState:
    T: Optional[float] = None  # Temperature (K)
    P: Optional[float] = None  # Pressure (Pa)
    h: Optional[float] = None  # Enthalpy (J/kg)
    s: Optional[float] = None  # Entropy (J/kg·K)
    v: Optional[float] = None  # Specific volume (m³/kg)
    x: Optional[float] = None  # Quality (0-1, -1 for supercritical, None for subcooled/superheated)
    rho: Optional[float] = None  # Density (kg/m³)
    note: str = ""
    is_supercritical: bool = False
    phase_label: str = ""
    source: str = ""
    err: dict = field(default_factory=lambda: {'T': 0, 'P': 0, 'h': 0, 's': 0})

    def to_dict(self):
        """Converts properties to a dictionary for JSON/CSV export."""
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
        if self.T is None or self.P is None:
            return f"State({self.note})"
        return f"State({self.note}: T={self.T:.2f}K, P={self.P/1e6:.3f}MPa)"
