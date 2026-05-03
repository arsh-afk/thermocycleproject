"""
Benchmark Data for Validation
Educational note: Validation against peer-reviewed research ensures model accuracy.
Data sources include Dostal (2004) and Sandia Labs for sCO2.

This module provides reference data sets from established literature 
to verify the correctness of the thermodynamic solvers implemented 
in this project.
"""

# Dictionary containing reference design points and expected outcomes 
# for various thermodynamic cycles.
BENCHMARKS = {
    'sco2_recompression': {
        'source': 'Dostal (2004) - sCO2 Brayton Cycles for Nuclear Reactors',
        'design_point': {
            'T_max': 550.0, # Max temperature at turbine inlet (°C)
            'P_high': 25.0, # Compressor outlet pressure (MPa)
            'P_low': 7.6,   # Compressor inlet pressure (MPa)
            'efficiency': 45.3 # Expected thermal efficiency (%)
        }
    },
    'rankine_standard': {
        'source': 'IAPWS-IF97 Reference / Thermodynamics Textbooks',
        'design_point': {
            'T_max': 550.0, # Superheat temperature (°C)
            'P_high': 15.0, # Boiler pressure (MPa)
            'P_low': 0.01,  # Condenser pressure (MPa)
            'efficiency': 40.5 # Approximate theoretical efficiency (%)
        }
    }
}
