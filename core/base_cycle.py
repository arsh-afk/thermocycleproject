"""
Base Cycle Abstract Class
Educational note: All thermodynamic power cycles share common principles of heat addition,
work extraction, and heat rejection. This base class enforces a consistent interface.
"""
from abc import ABC, abstractmethod

class BaseCycle(ABC):
    """Abstract interface for all cycle solvers."""
    
    def __init__(self, fluid="Water"):
        self.fluid = fluid
        self.states = {}  # Dictionary of state_id: ThermodynamicState
        self.metrics = {}  # Cycle performance results
        self.errors = []  # Input validation errors
        self.entropy_generation = 0.0
        self.second_law_efficiency = None

    def clear_states(self):
        """Resets the cycle state dictionary and metrics."""
        self.states = {}
        self.metrics = {}
        self.errors = []
        self.entropy_generation = 0.0
        self.second_law_efficiency = None

    def solve_with_targets(self, params):
        """
        Handles iterative solving if targets like efficiency, w_net, or q_in are provided.
        Otherwise, falls back to normal solve.
        """
        targets = {k: params[k] for k in params if k in ['efficiency', 'w_net', 'q_in']}
        if not targets:
            return self.solve(params)
        
        # If we have targets, we need to iterate on a 'free' variable to hit them.
        # For simplicity, we choose T_max or P_max as the iteration variable.
        from core.solver import Solver
        
        target_key = list(targets.keys())[0]
        target_val = targets[target_key]
        
        # We need to decide which variable to vary. 
        # If P_max is fixed by user, vary T_max. If T_max is fixed, vary P_max.
        # If neither is fixed, vary T_max.
        iter_var = 'T_max'
        if 'T_max' in params:
            iter_var = 'P_max'
            
        def objective(x):
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

        # Define search range based on iter_var
        if iter_var == 'T_max':
            low, high = 100.0, 1500.0
        else:
            low, high = 0.1, 50.0
            
        result = Solver.bisection(objective, low, high)
        
        # Final solve with the found value
        final_params = params.copy()
        final_params[iter_var] = result
        for t in targets: final_params.pop(t)
        return self.solve(final_params)

    @abstractmethod
    def calculate_performance(self):
        """Calculates efficiency, power output, and other metrics."""
        pass

    @abstractmethod
    def validate_inputs(self, params):
        """Checks for physically realistic parameter ranges."""
        pass

    @abstractmethod
    def get_component_list(self):
        """Returns ordered list of component names for schematic."""
        pass

    def get_state(self, prop1, val1, prop2, val2, note=""):
        """Utility to get state using cycle's fluid."""
        from utils.property_wrapper import PropertyWrapper
        return PropertyWrapper.get_state(self.fluid, prop1, val1, prop2, val2, note)

    def calculate_work(self, h_in, h_out):
        """Work per unit mass: w = h_in - h_out (Positive for turbines)."""
        return h_in - h_out

    def calculate_heat(self, h_in, h_out):
        """Heat per unit mass: q = h_out - h_in (Positive for heat addition)."""
        return h_out - h_in

    def calculate_entropy_generation(self, q_in, T_hot, q_out, T_cold):
        """Computes entropy generation for a steady cycle per unit mass."""
        if q_in is None or q_out is None or T_hot is None or T_cold is None:
            return None
        if T_hot <= 0 or T_cold <= 0:
            return None
        s_gen = q_out / T_cold - q_in / T_hot
        return max(s_gen, 0.0)

    def calculate_second_law_efficiency(self, efficiency, T_hot, T_cold):
        """Returns second-law efficiency relative to Carnot."""
        if efficiency is None or T_hot <= T_cold or T_hot <= 0 or T_cold <= 0:
            return None
        carnot = 1.0 - T_cold / T_hot
        if carnot <= 0:
            return None
        return max(0.0, min(100.0, (efficiency / 100.0) / carnot * 100.0))
