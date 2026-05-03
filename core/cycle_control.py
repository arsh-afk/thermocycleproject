"""
Cycle Control and Variable Selection Logic
Centralized module to manage input constraints and validation rules.
Engineering Principle: Ensures that all user inputs are within physically 
valid domains and adhere to the State Postulate requirements.
"""

class CycleControl:
    """
    Manages metadata for thermodynamic variables and restricts UI options 
    to valid parameters for each specific cycle type.
    """
    
    # Global metadata for variables: Units and physical bounds.
    VAR_METADATA = {
        'P_max': {'label': 'Max Pressure', 'unit': 'MPa', 'min': 0.001, 'max': 50.0, 'default': 15.0},
        'T_max': {'label': 'Max Temperature', 'unit': '°C', 'min': 10.0, 'max': 1500.0, 'default': 550.0},
        'P_min': {'label': 'Min Pressure', 'unit': 'MPa', 'min': 0.001, 'max': 10.0, 'default': 0.01},
        'T_min': {'label': 'Min Temperature', 'unit': '°C', 'min': 5.0, 'max': 500.0, 'default': 35.0},
        'h_max': {'label': 'Max Enthalpy', 'unit': 'kJ/kg', 'min': 100.0, 'max': 5000.0, 'default': 3400.0},
        's_max': {'label': 'Max Entropy', 'unit': 'kJ/kg·K', 'min': 1.0, 'max': 10.0, 'default': 6.5},
        'x_boiler': {'label': 'Boiler Exit Quality', 'unit': '', 'min': 0.0, 'max': 1.0, 'default': 1.0},
        'q_in': {'label': 'Heat Input', 'unit': 'kJ/kg', 'min': 10.0, 'max': 10000.0, 'default': 3000.0},
        'w_net': {'label': 'Net Work', 'unit': 'kJ/kg', 'min': 10.0, 'max': 5000.0, 'default': 1000.0},
        'efficiency': {'label': 'Thermal Efficiency', 'unit': '%', 'min': 1.0, 'max': 99.0, 'default': 40.0},
        'r': {'label': 'Compression Ratio', 'unit': '', 'min': 1.1, 'max': 30.0, 'default': 8.0},
        'rc': {'label': 'Cutoff Ratio', 'unit': '', 'min': 1.0, 'max': 10.0, 'default': 2.0},
        'rp': {'label': 'Pressure Ratio', 'unit': '', 'min': 1.0, 'max': 10.0, 'default': 1.5},
        'P_low': {'label': 'Evaporator Pressure', 'unit': 'MPa', 'min': 0.01, 'max': 2.0, 'default': 0.14},
        'P_high': {'label': 'Condenser Pressure', 'unit': 'MPa', 'min': 0.1, 'max': 10.0, 'default': 0.8},
        'epsilon': {'label': 'Regen Effectiveness', 'unit': '', 'min': 0.0, 'max': 1.0, 'default': 0.8},
        'y_cogen': {'label': 'Cogen Fraction', 'unit': '', 'min': 0.0, 'max': 1.0, 'default': 0.2},
        'P_cogen': {'label': 'Cogen Pressure', 'unit': 'MPa', 'min': 0.01, 'max': 5.0, 'default': 0.5},
    }

    # Cycle-specific valid variables: Filtered to show only relevant options in the GUI.
    CYCLE_VARS = {
        'rankine': ['P_max', 'T_max', 'P_min', 'T_min', 'h_max', 's_max', 'x_boiler', 'q_in', 'w_net', 'efficiency', 'n_rh', 'n_fwh', 'y_cogen', 'P_cogen'],
        'brayton': ['P_max', 'P_min', 'T_max', 'T_min', 'q_in', 'w_net', 'efficiency', 'n_ic', 'n_rh', 'epsilon', 'mode'],
        'sco2': ['P_max', 'P_min', 'T_max', 'T_min', 'q_in', 'w_net', 'efficiency', 'split_frac', 'recup_eff'],
        'otto': ['r', 'T_max', 'P_min', 'T_min', 'q_in', 'w_net', 'efficiency'],
        'diesel': ['r', 'rc', 'T_max', 'P_min', 'T_min', 'q_in', 'w_net', 'efficiency'],
        'dual': ['r', 'rc', 'rp', 'T_min', 'P_min', 'efficiency'],
        'stirling': ['T_max', 'T_min', 'P_max', 'r', 'w_net'],
        'ericsson': ['T_max', 'T_min', 'P_max', 'P_min', 'w_net'],
        'refrigeration': ['P_low', 'P_high', 'type', 'T_source', 'T_env', 'T_ref', 'eta_c', 'dT_sh', 'dT_sc'],
        'combined': ['B_P_max', 'B_T_max', 'R_P_max', 'R_T_max', 'efficiency'],
    }

    @staticmethod
    def get_variables_for_cycle(cycle_key):
        """
        Returns the list of valid variable keys for a given cycle.
        Used by the GUI to dynamically build the input form.
        """
        return CycleControl.CYCLE_VARS.get(cycle_key, [])

    @staticmethod
    def get_metadata(var_key):
        """Returns physical bounds and units for a variable."""
        return CycleControl.VAR_METADATA.get(var_key, {})

    @staticmethod
    def validate_selection(selected_vars):
        """
        Enforces the rule that exactly TWO independent variables must be selected 
        to define the cycle's boundary states, consistent with the State Postulate.
        """
        if len(selected_vars) != 2:
            return False, "Select exactly TWO independent variables."
        return True, ""

    @staticmethod
    def apply_defaults(cycle_key, params):
        """Placeholder for logic to fill in non-essential defaults."""
        pass
