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

    @abstractmethod
    def solve(self, params):
        """Main entry point to solve the cycle state points."""
        pass

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
