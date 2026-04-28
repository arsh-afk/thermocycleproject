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
        Procedurally maps states to components and draws the loop.
        states: dict of state_id: ThermodynamicState
        """
        # Determine scaling based on component count
        n = len(states)
        fig, ax = plt.subplots(figsize=(12, 7), dpi=150)
        ax.set_xlim(0, 100); ax.set_ylim(0, 60)
        ax.axis('off')

        # SOURCE: Topology Mapping
        # Standard power loop layout logic
        # 1. Heating (Left) 2. Expansion (Top) 3. Cooling (Right) 4. Compression (Bottom)
        
        # We classify states based on P and T trends to assign coordinates
        # Simplified: Use standard clockwise mapping for N components
        sorted_keys = sorted(states.keys())
        n_pts = len(sorted_keys)
        
        # Calculate ellipse/rectangle coordinates
        t = np.linspace(0, 2*np.pi, n_pts, endpoint=False)
        # Flip to clockwise starting from bottom left
        t = -t + np.pi*1.2
        coords = {k: (50 + 35*np.cos(ti), 30 + 20*np.sin(ti)) for k, ti in zip(sorted_keys, t)}

        # Draw Components and Lines
        for i in range(n_pts):
            k1 = sorted_keys[i]
            k2 = sorted_keys[(i + 1) % n_pts]
            p1, p2 = coords[k1], coords[k2]
            st1, st2 = states[k1], states[k2]
            
            # 1. Determine Component Type based on P, T changes
            mx, my = (p1[0]+p2[0])/2, (p1[1]+p2[1])/2
            
            # Logic: P increase -> Pump/Comp, T increase -> Boiler/Heat
            if st2.P > st1.P * 1.1:
                if st1.x == 0 or st1.phase_label == "Liquid":
                    FlowChartGenerator.draw_pump(ax, mx, my)
                else:
                    FlowChartGenerator.draw_compressor(ax, mx, my)
            elif st2.h < st1.h * 0.9:
                FlowChartGenerator.draw_turbine(ax, mx, my)
            elif st2.T > st1.T + 10:
                FlowChartGenerator.draw_exchanger(ax, mx, my, "HEAT ADD", "#ffebee")
            elif st2.T < st1.T - 10:
                FlowChartGenerator.draw_exchanger(ax, mx, my, "COOLER", "#e3f2fd")

            # 2. Draw Flow Line with Phase Coloring
            color = FlowChartGenerator.get_phase_color(st1)
            ax.annotate('', xy=p2, xytext=p1,
                        arrowprops=dict(arrowstyle='-|>,head_width=0.3,head_length=0.5', 
                                      color=color, lw=2.5, shrinkA=5, shrinkB=5))

            # 3. Draw State Anchor (Circle)
            # Positioned at the START of each component inlet
            circ = patches.Circle(p1, 2.0, fc="white", ec="#333333", lw=1, zorder=5)
            ax.add_patch(circ)
            ax.text(p1[0], p1[1], str(k1), ha='center', va='center', fontsize=8, fontweight='bold')

        # Title Block
        ax.text(50, 58, f"{cycle_type} - Procedural Flow Schematic", ha='center', fontweight='bold', fontsize=12)
        
        # Legend
        lax = fig.add_axes([0.8, 0.05, 0.15, 0.15])
        lax.axis('off')
        lax.text(0, 0.8, "─ Vapor/Steam", color=FlowChartGenerator.PHASE_COLORS['vapor'], fontsize=7, fontweight='bold')
        lax.text(0, 0.5, "─ Liquid Phase", color=FlowChartGenerator.PHASE_COLORS['liquid'], fontsize=7, fontweight='bold')
        lax.text(0, 0.2, "─ Supercritical", color=FlowChartGenerator.PHASE_COLORS['supercritical'], fontsize=7, fontweight='bold')

        buf = io.BytesIO()
        plt.savefig(buf, format='svg', bbox_inches='tight', transparent=True)
        plt.close(fig)
        return buf
