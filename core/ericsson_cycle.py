"""
Ericsson Cycle Solver
Educational note: Similar to Stirling but with constant-pressure regeneration
(isobaric heating/cooling instead of isochoric). Achieves Carnot efficiency with ideal regeneration.

Engineering Principle: Two isothermal processes (heat addition/rejection at T_H, T_C)
and two isobaric processes (heat exchange via regenerator). η = 1 - T_C/T_H = η_Carnot.
SOURCE: Cengel, Thermodynamics: An Engineering Approach, Chapter 9.
"""
from core.base_cycle import BaseCycle


class EricssonCycle(BaseCycle):
    """Ericsson cycle solver — ideal gas cycle with isothermal processes and constant-pressure regeneration."""

    def __init__(self, fluid="Air"):
        super().__init__(fluid)

    def solve(self, params):
        """
        Solves the four-state Ericsson cycle.
        Processes:
          1-2: Isothermal Compression at P_max (heat rejected at T_C)
          2-3: Isobaric Heating (regenerator absorbs heat from hot exhaust)
          3-4: Isothermal Expansion at P_min (heat added at T_H)
          4-1: Isobaric Cooling (regenerator releases heat)
        """
        self.clear_states()

        defaults = {
            'T_max': 800.0 + 273.15,
            'T_min': 25.0 + 273.15,
            'P_max': 10.0 * 1e6,
            'P_min': 0.1 * 1e6,
        }

        current = defaults.copy()
        if 'T_max' in params: current['T_max'] = params['T_max'] + 273.15
        if 'T_min' in params: current['T_min'] = params['T_min'] + 273.15
        if 'P_max' in params: current['P_max'] = params['P_max'] * 1e6
        if 'P_min' in params: current['P_min'] = params['P_min'] * 1e6

        T_hot = current['T_max']
        T_cold = current['T_min']
        P_max = current['P_max']
        P_min = current['P_min']

        # State 3: Start of isothermal expansion (high T, high P)
        self.states[3] = self.get_state('P', P_max, 'T', T_hot, "Heating Exit")

        # State 4: End of isothermal expansion (high T, low P)
        self.states[4] = self.get_state('P', P_min, 'T', T_hot, "Expansion Exit")

        # State 1: End of isobaric cooling (low T, low P)
        self.states[1] = self.get_state('P', P_min, 'T', T_cold, "Cooling Exit")

        # State 2: End of isothermal compression (low T, high P)
        self.states[2] = self.get_state('P', P_max, 'T', T_cold, "Compression Exit")

        return self.states

    def calculate_performance(self):
        """
        Calculates Ericsson cycle performance.
        For ideal Ericsson: η = Carnot efficiency.
        """
        if not self.states:
            return {}

        T_H = self.states[3].T
        T_C = self.states[1].T

        # Isothermal heat transfer: Q = T * ΔS
        q_in = T_H * (self.states[4].s - self.states[3].s)
        q_out = T_C * (self.states[1].s - self.states[2].s)
        w_net = q_in - q_out
        efficiency = (1 - T_C / T_H) * 100 if T_H > 0 else 0
        s_gen = self.calculate_entropy_generation(q_in, T_H, q_out, T_C)
        sl_eff = self.calculate_second_law_efficiency(efficiency, T_H, T_C)

        self.metrics = {
            'efficiency': efficiency,
            'w_net': w_net / 1000,
            'q_in': q_in / 1000,
            'q_out': q_out / 1000,
            's_gen': s_gen,
            'second_law_efficiency': sl_eff,
        }
        return self.metrics

    def validate_inputs(self, params):
        errors = []
        p_min = params.get('P_min', 0.1)
        p_max = params.get('P_max', 10.0)
        t_min = params.get('T_min', 25.0)
        t_max = params.get('T_max', 800.0)

        if p_min >= p_max:
            errors.append("P_max must be greater than P_min.")
        if t_min >= t_max:
            errors.append("T_max must be greater than T_min.")
        return errors

    def get_component_list(self):
        return ["Isothermal Compression", "Regeneration", "Isothermal Expansion", "Regeneration"]
