"""
Professional Engineering PFD Generator - Node-Based Engine
Educational note: Uses Matplotlib to generate textbook-quality schematics.
Implements:
1. trapezoidal symbols for expansion/compression.
2. phase-based line coloring (Blue:Liquid, Red:Vapor, Purple:Supercritical).
3. sequential state point anchoring.
"""
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import io

class FlowChartGenerator:
    """Dynamic generator for professional engineering schematics."""
    
    # SOURCE: Professional engineering diagram color standards
    PHASE_COLORS = {
        'liquid': "#0055cc",
        'vapor': "#cc2200",
        'supercritical': "#9900cc",
        'two-phase': "#ff7f0e",
        'default': "#333333"
    }

    COMPONENT_DRAWERS = {
        "Turbine": lambda ax, x, y: FlowChartGenerator.draw_turbine(ax, x, y),
        "Turbines": lambda ax, x, y: FlowChartGenerator.draw_turbine(ax, x, y),
        "Compressor": lambda ax, x, y: FlowChartGenerator.draw_compressor(ax, x, y),
        "Compressors": lambda ax, x, y: FlowChartGenerator.draw_compressor(ax, x, y),
        "Main Comp": lambda ax, x, y: FlowChartGenerator.draw_compressor(ax, x, y),
        "Recompressor": lambda ax, x, y: FlowChartGenerator.draw_compressor(ax, x, y),
        "Recomp Comp": lambda ax, x, y: FlowChartGenerator.draw_compressor(ax, x, y),
        "Pump": lambda ax, x, y: FlowChartGenerator.draw_pump(ax, x, y),
        "Pumps": lambda ax, x, y: FlowChartGenerator.draw_pump(ax, x, y),
        "Boiler": lambda ax, x, y: FlowChartGenerator.draw_exchanger(ax, x, y, "BOILER", "#ffebee"),
        "Condenser": lambda ax, x, y: FlowChartGenerator.draw_exchanger(ax, x, y, "CONDENSER", "#e3f2fd"),
        "Heat Exchanger": lambda ax, x, y: FlowChartGenerator.draw_exchanger(ax, x, y, "HX", "#fff8e1"),
        "LTR": lambda ax, x, y: FlowChartGenerator.draw_exchanger(ax, x, y, "LTR", "#e8f5e8"),
        "HTR": lambda ax, x, y: FlowChartGenerator.draw_exchanger(ax, x, y, "HTR", "#f3e5f5"),
        "Primary Heater": lambda ax, x, y: FlowChartGenerator.draw_exchanger(ax, x, y, "HEATER", "#fff3e0"),
        "Regeneration": lambda ax, x, y: FlowChartGenerator.draw_exchanger(ax, x, y, "REGEN", "#fce4ec"),
        "Isothermal Compression": lambda ax, x, y: FlowChartGenerator.draw_compressor(ax, x, y),
        "Isothermal Expansion": lambda ax, x, y: FlowChartGenerator.draw_turbine(ax, x, y),
        "Combustor": lambda ax, x, y: FlowChartGenerator.draw_exchanger(ax, x, y, "COMB", "#ffcc80"),
        "Intercoolers": lambda ax, x, y: FlowChartGenerator.draw_exchanger(ax, x, y, "IC", "#b3e5fc"),
        "Reheaters": lambda ax, x, y: FlowChartGenerator.draw_exchanger(ax, x, y, "RH", "#c8e6c9"),
        # Default for unknown
        "default": lambda ax, x, y: FlowChartGenerator.draw_exchanger(ax, x, y, "COMP", "#f5f5f5"),
    }

    @staticmethod
    def get_phase_color(state):
        """Determines line color based on thermodynamic state."""
        if state.is_supercritical: return FlowChartGenerator.PHASE_COLORS['supercritical']
        if 0 <= state.x <= 1: return FlowChartGenerator.PHASE_COLORS['two-phase']
        if state.x > 1 or state.phase_label == "Superheated": return FlowChartGenerator.PHASE_COLORS['vapor']
        return FlowChartGenerator.PHASE_COLORS['liquid']

    @staticmethod
    def draw_turbine(ax, x, y, size=6):
        """Draws converging trapezoid for expansion."""
        # Inlet (wider) at left, outlet (narrower) at right
        path = [[x-size/2, y+size/1.5], [x-size/2, y-size/1.5], 
                [x+size/2, y-size/2.5], [x+size/2, y+size/2.5]]
        poly = patches.Polygon(path, fc="#f5f5f5", ec="#333333", lw=1.5, zorder=3)
        ax.add_patch(poly)
        ax.text(x, y, "TURBINE", ha='center', va='center', fontsize=7, fontweight='bold')
        # Work Arrow - Fixed style to valid Matplotlib '<->'
        ax.annotate('', xy=(x, y+size), xytext=(x, y+size/2), arrowprops=dict(arrowstyle='<->', color='black', lw=1.5))

    @staticmethod
    def draw_compressor(ax, x, y, size=6):
        """Draws diverging trapezoid for compression."""
        # Inlet (narrower) at left, outlet (wider) at right
        path = [[x-size/2, y+size/2.5], [x-size/2, y-size/2.5], 
                [x+size/2, y-size/1.5], [x+size/2, y+size/1.5]]
        poly = patches.Polygon(path, fc="#f5f5f5", ec="#333333", lw=1.5, zorder=3)
        ax.add_patch(poly)
        ax.text(x, y, "COMP", ha='center', va='center', fontsize=7, fontweight='bold')

    @staticmethod
    def draw_pump(ax, x, y, size=3):
        """Draws circular pump symbol."""
        circ = patches.Circle((x, y), size, fc="#f5f5f5", ec="#333333", lw=1.5, zorder=3)
        ax.add_patch(circ)
        ax.text(x, y, "P", ha='center', va='center', fontsize=8, fontweight='bold')

    @staticmethod
    def draw_exchanger(ax, x, y, label, color="#fff8e1", w=10, h=6):
        """Draws rectangular heat exchanger/boiler."""
        box = patches.FancyBboxPatch((x-w/2, y-h/2), w, h, boxstyle="round,pad=0.1", 
                                    fc=color, ec="#333333", lw=1.5, zorder=3)
        ax.add_patch(box)
        ax.text(x, y, label, ha='center', va='center', fontsize=8, fontweight='bold')

    @staticmethod
    def create_diagram(cycle_type, component_list, states):
        """
        Procedurally maps components and states for cycle-specific diagrams.
        component_list: list of component names in order.
        states: dict of state_id: ThermodynamicState
        """
        fig, ax = plt.subplots(figsize=(14, 8), dpi=200, facecolor='#f9f9f9')
        ax.set_xlim(0, 100)
        ax.set_ylim(0, 60)
        ax.axis('off')

        n_comp = len(component_list)
        n_states = len(states)
        sorted_states = sorted(states.keys())

        # Position components in a cycle: start from bottom-left, clockwise
        angles = np.linspace(np.pi/2, -3*np.pi/2, n_comp, endpoint=False)  # Start at top, go clockwise
        comp_positions = [(50 + 35*np.cos(a), 30 + 20*np.sin(a)) for a in angles]

        # Position state points midway between components
        state_angles = np.linspace(np.pi/2, -3*np.pi/2, n_states, endpoint=False)
        state_positions = [(50 + 40*np.cos(a), 30 + 25*np.sin(a)) for a in state_angles]

        # Draw components
        for i, comp in enumerate(component_list):
            x, y = comp_positions[i]
            drawer = FlowChartGenerator.COMPONENT_DRAWERS.get(comp, FlowChartGenerator.COMPONENT_DRAWERS["default"])
            drawer(ax, x, y)

        # Draw state points and connections
        for i, state_id in enumerate(sorted_states):
            st = states[state_id]
            p = state_positions[i]

            # Draw state anchor
            circ = patches.Circle(p, 2.5, fc="white", ec="#333333", lw=1.5, zorder=5)
            ax.add_patch(circ)
            ax.text(p[0], p[1], str(state_id), ha='center', va='center', fontsize=9, fontweight='bold', color='#333')

            # Draw flow arrow to next state
            next_i = (i + 1) % n_states
            next_p = state_positions[next_i]
            color = FlowChartGenerator.get_phase_color(st)
            ax.annotate('', xy=next_p, xytext=p,
                        arrowprops=dict(arrowstyle='-|>,head_width=0.4,head_length=0.6', 
                                      color=color, lw=3, shrinkA=8, shrinkB=8))

        # Title
        ax.text(50, 58, f"{cycle_type} - Flow Schematic", ha='center', fontweight='bold', fontsize=14, color='#333')

        # Enhanced Legend
        lax = fig.add_axes([0.75, 0.05, 0.2, 0.25])
        lax.axis('off')
        lax.text(0, 0.9, "Phases:", fontsize=10, fontweight='bold', color='#333')
        lax.text(0, 0.7, "─ Vapor/Steam", color=FlowChartGenerator.PHASE_COLORS['vapor'], fontsize=8)
        lax.text(0, 0.5, "─ Liquid", color=FlowChartGenerator.PHASE_COLORS['liquid'], fontsize=8)
        lax.text(0, 0.3, "─ Supercritical", color=FlowChartGenerator.PHASE_COLORS['supercritical'], fontsize=8)
        lax.text(0, 0.1, "─ Two-Phase", color=FlowChartGenerator.PHASE_COLORS['two-phase'], fontsize=8)

        buf = io.BytesIO()
        plt.savefig(buf, format='svg', bbox_inches='tight', transparent=True)
        plt.close(fig)
        return buf
