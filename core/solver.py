"""
Convergence Solvers
Educational note: Complex cycles with recuperators or multiple feedwater heaters 
require iterative methods to find mass flow splits or temperature balances where 
explicit algebraic solutions are unavailable.
SOURCE: Numerical Methods for Engineers, Chapra.
"""
import numpy as np

class Solver:
    """
    Numerical solver utilities for thermodynamic cycle convergence.
    These methods are essential when cycle parameters depend on unknown states (e.g., Regeneration).
    """
    
    @staticmethod
    def bisection(func, a, b, tol=1e-5, max_iter=100):
        """
        Standard bisection method for root finding.
        Engineering Principle: Guarantees convergence if the root is bracketed.
        Used to find target pressures or temperatures to hit a desired efficiency/work.
        """
        fa = func(a)
        if fa * func(b) > 0:
            # If root is not bracketed, return midpoint as a fallback guess
            return (a + b) / 2
            
        for _ in range(max_iter):
            c = (a + b) / 2
            fc = func(c)
            if abs(fc) < tol:
                return c
            # Bisect the interval
            if fa * fc < 0:
                b = c
            else:
                a = c
                fa = fc
        return (a + b) / 2

    @staticmethod
    def fixed_point(func, x0, tol=1e-5, max_iter=100):
        """
        Fixed point iteration: x_{n+1} = f(x_n).
        Used for temperature/mass balances in regenerative cycles (e.g., sCO2).
        """
        x = x0
        for _ in range(max_iter):
            x_new = func(x)
            if abs(x_new - x) < tol:
                return x_new
            x = x_new
        return x
