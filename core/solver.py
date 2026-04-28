"""
Convergence Solvers
Educational note: Complex cycles with recuperators or multiple feedwater heaters 
require iterative methods to find mass flow splits or temperature balances.
"""
import numpy as np

class Solver:
    """Numerical solver utilities for cycle convergence."""
    
    @staticmethod
    def bisection(func, a, b, tol=1e-5, max_iter=100):
        """Standard bisection method for root finding."""
        fa = func(a)
        if fa * func(b) > 0:
            return (a + b) / 2 # Fallback
            
        for _ in range(max_iter):
            c = (a + b) / 2
            fc = func(c)
            if abs(fc) < tol:
                return c
            if fa * fc < 0:
                b = c
            else:
                a = c
                fa = fc
        return (a + b) / 2

    @staticmethod
    def fixed_point(func, x0, tol=1e-5, max_iter=100):
        """Fixed point iteration for temperature/mass balances."""
        x = x0
        for _ in range(max_iter):
            x_new = func(x)
            if abs(x_new - x) < tol:
                return x_new
            x = x_new
        return x
