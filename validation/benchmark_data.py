"""
Benchmark Data for Validation
Educational note: Validation against peer-reviewed research ensures model accuracy.
Data sources include Dostal (2004) and Sandia Labs for sCO2.
"""

BENCHMARKS = {
    'sco2_recompression': {
        'source': 'Dostal (2004)',
        'design_point': {
            'T_max': 550.0, # C
            'P_high': 25.0, # MPa
            'P_low': 7.6, # MPa
            'efficiency': 45.3 # %
        }
    },
    'rankine_standard': {
        'source': 'IAPWS-IF97 Reference',
        'design_point': {
            'T_max': 550.0,
            'P_high': 15.0,
            'P_low': 0.01,
            'efficiency': 40.5
        }
    }
}
