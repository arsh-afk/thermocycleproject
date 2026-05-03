"""
Base Cycle Abstract Class
Educational note: All thermodynamic power cycles share common principles of heat addition,
work extraction, and heat rejection. This base class enforces a consistent interface.

Engineering Principle: The First Law of Thermodynamics for a cycle states that the net heat
transfer is equal to the net work output (ΣQ = ΣW). This base class provides the 
structure to verify this balance across various cycle implementations.
"""
from abc import ABC, abstractmethod

class BaseCycle(ABC):
    """
    Abstract interface for all cycle solvers.
    Defines the standard workflow: input validation -> solving states -> performance calculation.
    """
    
    def __init__(self, fluid="Water"):
        """
        Initializes the base cycle with a working fluid and empty results containers.
        
        Args:
            fluid (str): The working fluid used in the cycle (e.g., 'Water', 'Air', 'CO2').
        """
        self.fluid = fluid
        self.states = {}  # Dictionary of state_id: ThermodynamicState
        self.metrics = {}  # Cycle performance results (efficiency, work, heat)
        self.errors = []  # List of input validation errors
        self.entropy_generation = 0.0 # Total entropy generated in the cycle (S_gen)
        self.second_law_efficiency = None # Comparison to Carnot efficiency

    def clear_states(self):
        """
        Resets the cycle state dictionary and metrics to prepare for a new simulation.
        Ensures that previous results do not interfere with new calculations.
        """
        self.states = {}
        self.metrics = {}
        self.errors = []
        self.entropy_generation = 0.0
        self.second_law_efficiency = None

    def solve_with_targets(self, params):
        """
        Handles iterative solving if targets like efficiency, w_net, or q_in are provided.
        Otherwise, falls back to normal solve.
        
        This reflects engineering design scenarios where a specific performance target
        (e.g., a 40% efficient plant) is the starting point rather than the fixed inputs.
        """
        targets = {k: params[k] for k in params if k in ['efficiency', 'w_net', 'q_in']}
        if not targets:
            return self.solve(params)
        
        # Iterative design approach: Vary one parameter to meet a specific performance target.
        # For simplicity, we choose T_max or P_max as the iteration variable.
        from core.solver import Solver
        
        target_key = list(targets.keys())[0]
        target_val = targets[target_key]
        
        # Decide which variable to vary based on which is NOT fixed by the user.
        iter_var = 'T_max'
        if 'T_max' in params:
            iter_var = 'P_max'
            
        def objective(x):
            """Objective function for the solver: target_value - calculated_value."""
            test_params = params.copy()
            test_params[iter_var] = x
            # Remove targets from test_params to avoid infinite recursion
            for t in targets: test_params.pop(t)
            
            self.solve(test_params)
            metrics = self.calculate_performance()
            
            if target_key == 'efficiency':
                return metrics.get('efficiency', 0.0) - target_val
            elif target_key == 'w_net':
                return metrics.get('w_net', 0.0) - target_val
            elif target_key == 'q_in':
                return metrics.get('q_in', 0.0) - target_val
            return 0.0

        # Define search range based on iter_var for bisection method
        if iter_var == 'T_max':
            low, high = 100.0, 1500.0 # Standard temperature range in Kelvin
        else:
            low, high = 0.1, 50.0 # Standard pressure range in MPa
            
        result = Solver.bisection(objective, low, high)
        
        # Final solve with the optimized value found by bisection
        final_params = params.copy()
        final_params[iter_var] = result
        for t in targets: final_params.pop(t)
        return self.solve(final_params)

    @abstractmethod
    def calculate_performance(self):
        """
        Calculates efficiency, power output, and other metrics.
        Must be implemented by specific cycle subclasses (e.g., Rankine, Otto).
        """
        pass

    @abstractmethod
    def validate_inputs(self, params):
        """
        Checks for physically realistic parameter ranges.
        Prevents non-physical solutions (e.g., T_max < T_min).
        """
        pass

    @abstractmethod
    def get_component_list(self):
        """
        Returns ordered list of component names for schematic/flow chart visualization.
        Subclasses that support multiple templates should read self.active_template internally.
        """
        pass

    def get_state(self, prop1, val1, prop2, val2, note=""):
        """
        Utility to get a thermodynamic state using the cycle's fluid.
        Uses the PropertyWrapper to interface with CoolProp/IAPWS data.
        """
        from utils.property_wrapper import PropertyWrapper
        return PropertyWrapper.get_state(self.fluid, prop1, val1, prop2, val2, note)

    def calculate_work(self, h_in, h_out):
        """
        Calculates work per unit mass: w = h_in - h_out.
        Follows the standard convention: Work done BY the system (turbine) is positive.
        """
        return h_in - h_out

    def calculate_heat(self, h_in, h_out):
        """
        Calculates heat per unit mass: q = h_out - h_in.
        Follows the standard convention: Heat added TO the system (boiler/combustor) is positive.
        """
        return h_out - h_in

    def calculate_entropy_generation(self, q_in, T_hot, q_out, T_cold):
        """
        Computes entropy generation for a steady cycle per unit mass (S_gen).
        Based on the Clausius Inequality: S_gen = Σ(Q_out/T_out) - Σ(Q_in/T_in) >= 0.
        Note: T_hot and T_cold must be absolute temperatures (Kelvin).
        """
        if q_in is None or q_out is None or T_hot is None or T_cold is None:
            return None
        if T_hot <= 0 or T_cold <= 0:
            return None
        # Engineering Principle: Entropy generation is a measure of irreversibility.
        s_gen = q_out / T_cold - q_in / T_hot
        return max(s_gen, 0.0) # S_gen cannot be negative according to the Second Law

    def calculate_exergy_destruction(self, s_gen, T_0=298.15):
        """
        Calculates Exergy Destruction (X_dest) = T_0 * S_gen.
        T_0 is the dead state (environment) temperature in Kelvin.
        """
        if s_gen is None:
            return None
        return T_0 * s_gen

    def calculate_second_law_efficiency(self, efficiency, T_hot, T_cold):
        """
        Returns second-law efficiency (η_II) relative to the Carnot cycle.
        η_II = η_thermal / η_Carnot.
        This provides insight into how much of the maximum possible work is actually achieved.
        """
        if efficiency is None or T_hot <= T_cold or T_hot <= 0 or T_cold <= 0:
            return None
        # η_Carnot = 1 - T_L / T_H
        carnot = 1.0 - T_cold / T_hot
        if carnot <= 0:
            return None
        return max(0.0, min(100.0, (efficiency / 100.0) / carnot * 100.0))
