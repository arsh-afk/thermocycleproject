"""
General Helper Utilities
Contains common thermodynamic functions and interpolation routines.
"""
import numpy as np

def calculate_thermal_efficiency(w_net, q_in):
    """Simple thermal efficiency: n = w_net / q_in."""
    if q_in == 0: return 0
    return (w_net / q_in) * 100

def get_carnot_efficiency(T_high, T_low):
    """Maximum theoretical efficiency: n = 1 - Tl / Th (T in K)."""
    return (1 - T_low / T_high) * 100
