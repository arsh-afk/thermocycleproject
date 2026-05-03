"""
Water Additive Mixture Corrections
Educational note: These are simplified correction models based on published engineering tables.
In real power plants, additives like NaOH or Ammonia are used for pH control or to 
shift boiling points in specialized cycles.
Sources: Olsson et al. (2014), ASHRAE 2021.
"""

import numpy as np

class WaterAdditives:
    """
    Correction factors for water-based solutions.
    Engineering Principle: Adding a non-volatile solute to a solvent increases its 
    boiling point (Boiling Point Elevation) and modifies other properties.
    """
    
    @staticmethod
    def get_corrections(additive_name, concentration):
        """
        Returns correction functions for property multipliers and BP elevation.
        
        Args:
            additive_name (str): The chemical additive.
            concentration (float): Weight or volume percentage.
            
        Returns:
            dict: Lambdas for corrections (bp_elevation, density, heat capacity).
        """
        # Baseline: Pure Water
        if additive_name == "Pure Water" or concentration <= 0:
            return {
                'bp_elevation': lambda T: 0.0,
                'rho_mult': lambda T: 1.0,
                'cp_mult': lambda T: 1.0,
                'source': "IAPWS-IF97"
            }
            
        if additive_name == "Water + NaOH":
            # Boiling point elevation for Sodium Hydroxide solutions.
            return {
                'bp_elevation': lambda T: 0.0123 * concentration**2 + 1.85 * concentration,
                'rho_mult': lambda T: 1.0 + 0.01 * concentration,
                'cp_mult': lambda T: 1.0 - 0.005 * concentration,
                'source': "Olsson et al. (2014)"
            }
            
        if additive_name == "Water + LiBr":
            # Used in absorption refrigeration. High boiling point elevation.
            return {
                'bp_elevation': lambda T: 0.02 * concentration**2 + 2.0 * concentration,
                'rho_mult': lambda T: 1.0 + 0.015 * concentration,
                'cp_mult': lambda T: 1.0 - 0.008 * concentration,
                'source': "ASHRAE 2021"
            }
            
        if additive_name == "Water + Ammonia":
            # Zeotropic mixture. Concentration shifts the bubble point.
            return {
                'bp_elevation': lambda T: -0.5 * concentration, # Boiling point depression
                'rho_mult': lambda T: 1.0 - 0.002 * concentration,
                'cp_mult': lambda T: 1.0 + 0.003 * concentration,
                'source': "Ibrahim & Klein (1993)"
            }
            
        if additive_name in ["Water + Ethylene Glycol", "Water + Propylene Glycol"]:
            # Common antifreeze additives.
            return {
                'bp_elevation': lambda T: 0.05 * concentration,
                'rho_mult': lambda T: 1.0 + 0.001 * concentration,
                'cp_mult': lambda T: 1.0 - 0.004 * concentration,
                'source': "ASHRAE 2021"
            }
            
        return None
