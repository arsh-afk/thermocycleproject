"""
Base Cycle Abstract Class
Educational note: All thermodynamic power cycles share common principles of heat addition,
work extraction, and heat rejection. This base class enforces a consistent interface.
"""
from abc import ABC, abstractmethod
from utils.property_wrapper import PropertyWrapper

class BaseCycle(ABC):
    """Abstract interface for all cycle solvers."""
    
    def __init__(self, fluid="Water"):
        self.fluid = fluid
        self.states = {} # Dictionary of state_id: ThermodynamicState
        self.metrics = {} # Cycle performance results
        self.errors = [] # Input validation errors

    def clear_states(self):
        """Resets the cycle state dictionary and metrics."""
        self.states = {}
        self.metrics = {}
        self.errors = []

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
        return PropertyWrapper.get_state(self.fluid, prop1, val1, prop2, val2, note)

    def calculate_work(self, h_in, h_out):
        """Work per unit mass: w = h_in - h_out (Positive for turbines)."""
        return h_in - h_out

    def calculate_heat(self, h_in, h_out):
        """Heat per unit mass: q = h_out - h_in (Positive for heat addition)."""
        return h_out - h_in
