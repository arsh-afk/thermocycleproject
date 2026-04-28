"""
Water Additive Mixture Corrections
Educational note: These are simplified correction models based on published engineering tables.
Full mixture thermodynamics (e.g., NRTL) is beyond this tool's scope.
Sources: Olsson et al. (2014), ASHRAE 2021, Ibrahim & Klein (1993).
"""

import numpy as np

class WaterAdditives:
    """Correction factors for water-based solutions."""
    
    @staticmethod
    def get_corrections(additive_name, concentration):
        """
        Returns correction functions for a specific additive.
        concentration: wt% or vol% as specified in YAML.
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
            # SOURCE: Olsson et al. (2014) - Fig 5
            # Approx boiling point elevation: dT = 0.0123*wt%^2 + 1.85*wt%
            return {
                'bp_elevation': lambda T: 0.0123 * concentration**2 + 1.85 * concentration,
                'rho_mult': lambda T: 1.0 + 0.01 * concentration, # Approx 1% increase per wt%
                'cp_mult': lambda T: 1.0 - 0.005 * concentration, # Approx 0.5% decrease per wt%
                'source': "Olsson et al. (2014) - NaOH solution properties"
            }
            
        if additive_name == "Water + LiBr":
            # SOURCE: ASHRAE Handbook Fundamentals (2021) - Table 32
            return {
                'bp_elevation': lambda T: 0.02 * concentration**2 + 2.0 * concentration, # High elevation
                'rho_mult': lambda T: 1.0 + 0.015 * concentration, # Denser than NaOH
                'cp_mult': lambda T: 1.0 - 0.008 * concentration,
                'source': "ASHRAE 2021 - LiBr solution properties"
            }
            
        if additive_name == "Water + Ammonia":
            # SOURCE: Ibrahim & Klein (1993) - Ammonia-water mixtures
            # This is zeotropic, so we use a simplified bubble point depression
            return {
                'bp_elevation': lambda T: -0.5 * concentration, # Depression
                'rho_mult': lambda T: 1.0 - 0.002 * concentration, # Lighter
                'cp_mult': lambda T: 1.0 + 0.003 * concentration,
                'source': "Ibrahim & Klein (1993) - Ammonia-water mixture"
            }
            
        if additive_name in ["Water + Ethylene Glycol", "Water + Propylene Glycol"]:
            # SOURCE: ASHRAE 2021 - Glycol properties
            return {
                'bp_elevation': lambda T: 0.05 * concentration, # Minimal elevation
                'rho_mult': lambda T: 1.0 + 0.001 * concentration,
                'cp_mult': lambda T: 1.0 - 0.004 * concentration,
                'source': "ASHRAE 2021 - Glycol solution properties"
            }
            
        return None
