"""
Cycle Optimization Module
Educational note: Finding optimal pressure ratios or mass splits to maximize efficiency.
Uses SLSQP algorithm to handle constraints.
"""
from scipy.optimize import minimize

class CycleOptimizer:
    """Provides optimization wrappers for cycle parameters."""
    
    def optimize_efficiency(self, cycle_obj, initial_params, param_bounds, constraints=None):
        """
        Maximizes cycle efficiency by minimizing the negative efficiency.
        """
        def objective(x_values):
            params = {name: value for name, value in zip(initial_params.keys(), x_values)}
            cycle_obj.solve(params)
            metrics = cycle_obj.calculate_performance()
            return -metrics.get('efficiency', 0)

        x0 = [initial_params[name] for name in initial_params]
        result = minimize(objective, x0, bounds=param_bounds, constraints=constraints or [], method='SLSQP')
        return result
