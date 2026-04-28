"""
Cycle Control and Variable Selection Logic
Centralized module to manage input constraints and validation rules.
"""

class CycleControl:
    """Manages which variables are valid for each cycle and enforces the 'two-variable' rule."""
    
    # Global metadata for variables
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
    }

    # Cycle-specific valid variables
    CYCLE_VARS = {
        'rankine': ['P_max', 'T_max', 'P_min', 'T_min', 'h_max', 's_max', 'x_boiler', 'q_in', 'w_net', 'efficiency'],
        'brayton': ['P_max', 'P_min', 'T_max', 'T_min', 'q_in', 'w_net', 'efficiency'],
        'sco2': ['P_max', 'P_min', 'T_max', 'T_min', 'q_in', 'w_net', 'efficiency'],
        'otto': ['r', 'T_max', 'P_min', 'T_min', 'q_in', 'w_net', 'efficiency'],
        'diesel': ['r', 'rc', 'T_max', 'P_min', 'T_min', 'q_in', 'w_net', 'efficiency'],
        'stirling': ['T_max', 'T_min', 'P_max', 'r', 'w_net'],
        'ericsson': ['T_max', 'T_min', 'P_max', 'P_min', 'w_net'],
    }

    @staticmethod
    def get_variables_for_cycle(cycle_key):
        """Returns the list of valid variables for a given cycle."""
        return CycleControl.CYCLE_VARS.get(cycle_key, [])

    @staticmethod
    def get_metadata(var_key):
        """Returns metadata for a variable."""
        return CycleControl.VAR_METADATA.get(var_key, {})

    @staticmethod
    def validate_selection(selected_vars):
        """Enforces the 'exactly two variables' rule."""
        if len(selected_vars) != 2:
            return False, "Select exactly TWO independent variables."
        
        # Check for independence (e.g., P_max and P_ratio are not independent - if we had P_ratio)
        # For now, most of our variables are independent enough for initial state definition.
        
        return True, ""

    @staticmethod
    def apply_defaults(cycle_key, params):
        """Fills in default values for variables not in params, based on cycle config."""
        # This will be used by the solver to get full set of parameters
        from core.base_cycle import BaseCycle
        # In practice, this should probably be handled by the cycle object itself 
        # using its own defaults from config/cycles.yaml
        pass
