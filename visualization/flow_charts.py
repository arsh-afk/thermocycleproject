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
        "Reheater": lambda ax, x, y: FlowChartGenerator.draw_exchanger(ax, x, y, "RH", "#c8e6c9"),
        "FWH": lambda ax, x, y: FlowChartGenerator.draw_exchanger(ax, x, y, "FWH", "#e8f5e8"),
        "Feedwater Heater": lambda ax, x, y: FlowChartGenerator.draw_exchanger(ax, x, y, "FWH", "#e8f5e8"),
        "Recuperator": lambda ax, x, y: FlowChartGenerator.draw_exchanger(ax, x, y, "RECUP", "#d1c4e9"),
        "Regenerator": lambda ax, x, y: FlowChartGenerator.draw_exchanger(ax, x, y, "REGEN", "#fce4ec"),
        "Cooler": lambda ax, x, y: FlowChartGenerator.draw_exchanger(ax, x, y, "COOL", "#bbdefb"),
        "Exhaust": lambda ax, x, y: FlowChartGenerator.draw_exchanger(ax, x, y, "EXH", "#f5f5f5"),
        "Intake": lambda ax, x, y: FlowChartGenerator.draw_exchanger(ax, x, y, "INTAKE", "#f5f5f5"),
        "Compression": lambda ax, x, y: FlowChartGenerator.draw_compressor(ax, x, y),
        "Combustion": lambda ax, x, y: FlowChartGenerator.draw_exchanger(ax, x, y, "COMB", "#ffcc80"),
        "Expansion": lambda ax, x, y: FlowChartGenerator.draw_turbine(ax, x, y),
        # Default for unknown
        "default": lambda ax, x, y: FlowChartGenerator.draw_exchanger(ax, x, y, "COMP", "#f5f5f5"),
    }

    @staticmethod
    def get_phase_color(state):
        """Determines line color based on thermodynamic state."""
        if state.is_supercritical: return FlowChartGenerator.PHASE_COLORS['supercritical']
        if state.x is not None and 0 <= state.x <= 1: return FlowChartGenerator.PHASE_COLORS['two-phase']
        if (state.x is not None and state.x > 1) or state.phase_label == "Superheated": return FlowChartGenerator.PHASE_COLORS['vapor']
        return FlowChartGenerator.PHASE_COLORS['liquid']

    @staticmethod
    def draw_turbine(ax, x, y, size=6):
        """Draws converging trapezoid for expansion."""
        # Inlet (wider) at left, outlet (narrower) at right
        path = [[x-size/2, y+size/1.5], [x-size/2, y-size/1.5], 
                [x+size/2, y-size/2.5], [x+size/2, y+size/2.5]]
        poly = patches.Polygon(path, fc="#f5f5f5", ec="#333333", lw=1.5, zorder=3)
        ax.add_patch(poly)
        ax.text(x, y, "TURBINE", ha='center', va='center', fontsize=7, fontweight='bold', color='#333')
        # Work Arrow
        ax.annotate('', xy=(x, y+size), xytext=(x, y+size/2), arrowprops=dict(arrowstyle='<->', color='black', lw=1.5))

    @staticmethod
    def draw_compressor(ax, x, y, size=6):
        """Draws diverging trapezoid for compression."""
        # Inlet (narrower) at left, outlet (wider) at right
        path = [[x-size/2, y+size/2.5], [x-size/2, y-size/2.5], 
                [x+size/2, y-size/1.5], [x+size/2, y+size/1.5]]
        poly = patches.Polygon(path, fc="#f5f5f5", ec="#333333", lw=1.5, zorder=3)
        ax.add_patch(poly)
        ax.text(x, y, "COMP", ha='center', va='center', fontsize=7, fontweight='bold', color='#333')

    @staticmethod
    def draw_pump(ax, x, y, size=3):
        """Draws circular pump symbol."""
        circ = patches.Circle((x, y), size, fc="#f5f5f5", ec="#333333", lw=1.5, zorder=3)
        ax.add_patch(circ)
        ax.text(x, y, "P", ha='center', va='center', fontsize=8, fontweight='bold', color='#333')

    @staticmethod
    def draw_exchanger(ax, x, y, label, color="#fff8e1", w=10, h=6):
        """Draws rectangular heat exchanger/boiler."""
        box = patches.FancyBboxPatch((x-w/2, y-h/2), w, h, boxstyle="round,pad=0.1", 
                                    fc=color, ec="#333333", lw=1.5, zorder=3)
        ax.add_patch(box)
        ax.text(x, y, label, ha='center', va='center', fontsize=8, fontweight='bold', color='#333')

    # Cycle-specific layout functions
    CYCLE_LAYOUTS = {
        'rankine': lambda comps, states: FlowChartGenerator.layout_rankine(comps, states),
        'brayton': lambda comps, states: FlowChartGenerator.layout_brayton(comps, states),
        'sco2': lambda comps, states: FlowChartGenerator.layout_sco2(comps, states),
        'otto': lambda comps, states: FlowChartGenerator.layout_otto(comps, states),
        'diesel': lambda comps, states: FlowChartGenerator.layout_diesel(comps, states),
        'stirling': lambda comps, states: FlowChartGenerator.layout_stirling(comps, states),
        'ericsson': lambda comps, states: FlowChartGenerator.layout_ericsson(comps, states),
    }

    CYCLE_ALIASES = {
        'supercritical co2': 'sco2',
        'co2': 'sco2',
        'sco2': 'sco2',
        'rankine': 'rankine',
        'brayton': 'brayton',
        'otto': 'otto',
        'diesel': 'diesel',
        'stirling': 'stirling',
        'ericsson': 'ericsson',
    }

    @staticmethod
    def normalize_cycle_type(cycle_type):
        key = cycle_type.lower()
        if key in FlowChartGenerator.CYCLE_LAYOUTS:
            return key
        for alias, mapped in FlowChartGenerator.CYCLE_ALIASES.items():
            if alias in key:
                return mapped
        for layout_key in FlowChartGenerator.CYCLE_LAYOUTS:
            if layout_key in key:
                return layout_key
        return None

    @staticmethod
    def layout_generic(comps, states):
        """Generic layout for unknown cycles."""
        positions = {'components': {}, 'states': {}}
        connections = []
        annotations = []
        
        n_comp = len(comps)
        sorted_states = sorted(states.keys())
        
        # Simple horizontal layout
        for i, comp in enumerate(comps):
            x = 20 + i * (60 / max(1, n_comp - 1))
            positions['components'][comp] = (x, 35)
        
        # Place states between components
        for i, state_id in enumerate(sorted_states):
            comp_idx = i % n_comp
            x = 20 + comp_idx * (60 / max(1, n_comp - 1))
            positions['states'][state_id] = (x - 3, 25)
            
            # Connect to next state
            next_i = (i + 1) % len(sorted_states)
            next_id = sorted_states[next_i]
            connections.append((state_id, next_id, ""))
        
        return positions, connections, annotations

    @staticmethod
    def layout_rankine(comps, states):
        """Rankine cycle layout: Pump → FWH → Boiler → Turbine → Condenser loop."""
        positions = {'components': {}, 'states': {}}
        connections = []
        annotations = []

        pump_names = [c for c in comps if 'pump' in c.lower()]
        fwh_names = [c for c in comps if 'fwh' in c.lower()]
        turbine_names = [c for c in comps if 'turbine' in c.lower()]
        reheater_names = [c for c in comps if 'reheater' in c.lower()]
        condenser_names = [c for c in comps if 'condenser' in c.lower()]
        boiler_names = [c for c in comps if 'boiler' in c.lower()]

        if condenser_names:
            positions['components'][condenser_names[0]] = (20, 52)
        if boiler_names:
            positions['components'][boiler_names[0]] = (78, 35)
        for i, pump in enumerate(pump_names):
            positions['components'][pump] = (20 + i * 12, 18)
        for i, fwh in enumerate(fwh_names):
            positions['components'][fwh] = (36 + i * 12, 18)
        for i, turbine in enumerate(turbine_names):
            positions['components'][turbine] = (80, 52 - i * 8)
        for i, reheater in enumerate(reheater_names):
            positions['components'][reheater] = (68, 45 - i * 8)
        if not condenser_names:
            positions['components']['Condenser'] = (20, 52)
        if not boiler_names:
            positions['components']['Boiler'] = (78, 35)

        sorted_states = sorted(states.keys())
        rankine_state_positions = [
            (20, 40),  # condenser out
            (30, 20),  # pump exit
            (42, 20),  # FWH exit / feedwater path
            (55, 20),  # feedwater pump exit to boiler
            (70, 35),  # boiler exit
            (80, 48),  # turbine exit
            (70, 54),  # reheater path
            (40, 55),  # high-side return
            (25, 45),  # return to condenser
        ]
        for idx, state_id in enumerate(sorted_states):
            if idx < len(rankine_state_positions):
                positions['states'][state_id] = rankine_state_positions[idx]
            else:
                positions['states'][state_id] = (20 + ((idx - len(rankine_state_positions)) % 4) * 12, 28 + ((idx - len(rankine_state_positions)) // 4) * 10)

        for i in range(len(sorted_states)):
            current_id = sorted_states[i]
            next_id = sorted_states[(i + 1) % len(sorted_states)]
            connections.append((current_id, next_id, ""))

        for state_id, st in states.items():
            if state_id in positions['states']:
                x, y = positions['states'][state_id]
                temp = f"{st.T - 273.15:.0f}°C" if st.T else ""
                press = f"{st.P / 1e6:.1f}MPa" if st.P else ""
                info = f"{temp}\n{press}".strip()
                if info:
                    annotations.append(((x, y - 7), info, '#666'))

        for i in range(len(sorted_states)):
            current_id = sorted_states[i]
            next_id = sorted_states[(i + 1) % len(sorted_states)]
            if current_id in positions['states'] and next_id in positions['states']:
                current_st = states[current_id]
                next_st = states[next_id]
                delta_h = next_st.h - current_st.h if next_st.h and current_st.h else 0
                comp_idx = i % len(comps)
                comp_name = comps[comp_idx].lower()
                annotation_pos = (positions['states'][current_id][0] + 4, positions['states'][current_id][1] + 4)
                if 'turb' in comp_name and delta_h < 0:
                    annotations.append((annotation_pos, f"W={abs(delta_h)/1000:.0f}kJ/kg", '#2E8B57'))
                elif 'pump' in comp_name and delta_h > 0:
                    annotations.append((annotation_pos, f"W={delta_h/1000:.0f}kJ/kg", '#DC143C'))
                elif 'fwh' in comp_name and delta_h < 0:
                    annotations.append((annotation_pos, f"Q={abs(delta_h)/1000:.0f}kJ/kg", '#4169E1'))
                elif 'boiler' in comp_name and delta_h > 0:
                    annotations.append((annotation_pos, f"Q={delta_h/1000:.0f}kJ/kg", '#FF6347'))
                elif 'condenser' in comp_name and delta_h < 0:
                    annotations.append((annotation_pos, f"Q={abs(delta_h)/1000:.0f}kJ/kg", '#4169E1'))

        return positions, connections, annotations

    @staticmethod
    def layout_brayton(comps, states):
        """Brayton cycle layout: Compressor → Intercooler → Combustor → Turbine → Cooler/Exhaust."""
        positions = {'components': {}, 'states': {}}
        connections = []
        annotations = []

        comp_names = [c for c in comps if 'compressor' in c.lower()]
        ic_names = [c for c in comps if 'intercooler' in c.lower()]
        turbine_names = [c for c in comps if 'turbine' in c.lower()]
        reheater_names = [c for c in comps if 'reheater' in c.lower()]
        cooler_names = [c for c in comps if 'cooler' in c.lower() or 'exhaust' in c.lower()]
        regenerator_names = [c for c in comps if 'regenerator' in c.lower() or 'recuperator' in c.lower()]

        for i, comp in enumerate(comp_names):
            positions['components'][comp] = (18 + i * 14, 22)
        for i, ic in enumerate(ic_names):
            positions['components'][ic] = (32 + i * 14, 22)
        positions['components']['Combustor'] = (58, 38)
        for i, turbine in enumerate(turbine_names):
            positions['components'][turbine] = (80, 46 - i * 8)
        for i, reheater in enumerate(reheater_names):
            positions['components'][reheater] = (68, 50 - i * 8)
        if regenerator_names:
            positions['components'][regenerator_names[0]] = (50, 52)
        if cooler_names:
            positions['components'][cooler_names[0]] = (78, 22)

        sorted_states = sorted(states.keys())
        brayton_state_positions = [
            (15, 30),  # inlet
            (32, 22),  # compressor exit
            (48, 22),  # intercooler exit
            (60, 38),  # combustor exit
            (80, 46),  # turbine exit
            (80, 28),  # cooler/exhaust exit
            (55, 52),  # regenerator hot side
            (25, 35),  # return path
        ]
        for idx, state_id in enumerate(sorted_states):
            if idx < len(brayton_state_positions):
                positions['states'][state_id] = brayton_state_positions[idx]
            else:
                positions['states'][state_id] = (20 + ((idx - len(brayton_state_positions)) % 4) * 12, 30)

        for i in range(len(sorted_states)):
            current_id = sorted_states[i]
            next_id = sorted_states[(i + 1) % len(sorted_states)]
            connections.append((current_id, next_id, ""))

        for state_id, st in states.items():
            if state_id in positions['states']:
                x, y = positions['states'][state_id]
                temp = f"{st.T - 273.15:.0f}°C" if st.T else ""
                press = f"{st.P / 1e6:.1f}MPa" if st.P else ""
                annotations.append(((x, y - 7), f"{temp}\n{press}".strip(), '#666'))

        return positions, connections, annotations

    @staticmethod
    def layout_sco2(comps, states):
        """sCO2 recompression cycle layout with recuperators and recompressor"""
        positions = {'components': {}, 'states': {}}
        connections = []
        annotations = []
        
        # Component positions for recompression sCO2 cycle
        positions['components'] = {
            'Main Compressor': (15, 20),
            'LTR': (45, 25),
            'HTR': (45, 45),
            'Primary Heater': (75, 50),
            'Turbine': (85, 55),
            'Recompressor': (25, 45),
            'Mixer': (35, 35),
            'Flow Split': (65, 35),
        }
        
        # State positions for recompression sCO2 cycle (10 states typical)
        sorted_states = sorted(states.keys())
        sco2_state_positions = [
            (10, 30),   # Main comp inlet
            (20, 20),   # Main comp exit
            (30, 20),   # Recompressor inlet (after mixer)
            (30, 45),   # Recompressor exit
            (40, 45),   # HTR cold exit
            (60, 50),   # Primary heater exit
            (90, 50),   # Turbine exit
            (70, 45),   # HTR hot exit
            (70, 25),   # LTR hot exit
            (50, 20),   # LTR cold exit / back to main comp
        ]
        
        for idx, state_id in enumerate(sorted_states):
            if idx < len(sco2_state_positions):
                positions['states'][state_id] = sco2_state_positions[idx]
            else:
                # Handle additional states if any
                positions['states'][state_id] = (20 + ((idx - len(sco2_state_positions)) % 4) * 12, 30)
        
        # Connections in cycle order
        for i in range(len(sorted_states)):
            current_id = sorted_states[i]
            next_id = sorted_states[(i + 1) % len(sorted_states)]
            connections.append((current_id, next_id, ""))
        
        return positions, connections, annotations

    @staticmethod
    def layout_otto(comps, states):
        """Otto cycle layout: Compression → Heat Addition → Expansion → Heat Rejection"""
        positions = {'components': {}, 'states': {}}
        connections = []
        annotations = []
        
        # Otto cycle is typically shown as a piston/cylinder
        positions['components'] = {
            'Compression': (30, 25),
            'Heat Addition': (70, 35),
            'Expansion': (70, 55),
            'Heat Rejection': (30, 55),
        }
        
        # State positions
        sorted_states = sorted(states.keys())
        if len(sorted_states) >= 4:
            positions['states'] = {
                sorted_states[0]: (20, 35),   # Intake
                sorted_states[1]: (40, 25),   # Compression end
                sorted_states[2]: (80, 35),   # Heat addition end
                sorted_states[3]: (80, 55),   # Expansion end
            }
        
        # Connections
        for i in range(len(sorted_states)):
            current_id = sorted_states[i]
            next_id = sorted_states[(i + 1) % len(sorted_states)]
            connections.append((current_id, next_id, ""))
        
        # Add state annotations with thermodynamic properties
        for state_id, st in states.items():
            if state_id in positions['states']:
                x, y = positions['states'][state_id]
                temp = f"{st.T - 273.15:.0f}°C" if st.T else ""
                press = f"{st.P / 1e5:.1f}bar" if st.P else ""
                info = f"{temp}\n{press}".strip()
                if info:
                    annotations.append(((x, y - 7), info, '#666'))
        
        # Add process annotations
        for i in range(len(sorted_states)):
            current_id = sorted_states[i]
            next_id = sorted_states[(i + 1) % len(sorted_states)]
            if current_id in positions['states'] and next_id in positions['states']:
                current_st = states[current_id]
                next_st = states[next_id]
                delta_u = next_st.u - current_st.u if next_st.u and current_st.u else 0
                annotation_pos = (positions['states'][current_id][0] + 4, positions['states'][current_id][1] + 4)
                if i == 0:  # Compression
                    annotations.append((annotation_pos, f"W_c={abs(delta_u)/1000:.0f}kJ/kg", '#DC143C'))
                elif i == 1:  # Heat addition
                    annotations.append((annotation_pos, f"Q_in={abs(delta_u)/1000:.0f}kJ/kg", '#FF6347'))
                elif i == 2:  # Expansion
                    annotations.append((annotation_pos, f"W_e={abs(delta_u)/1000:.0f}kJ/kg", '#2E8B57'))
                elif i == 3:  # Heat rejection
                    annotations.append((annotation_pos, f"Q_out={abs(delta_u)/1000:.0f}kJ/kg", '#4169E1'))
        
        return positions, connections, annotations

    @staticmethod
    def layout_diesel(comps, states):
        """Diesel cycle layout - similar to Otto but with different heat addition"""
        return FlowChartGenerator.layout_otto(comps, states)  # Similar layout

    @staticmethod
    def layout_stirling(comps, states):
        """Stirling cycle layout - isothermal compression and expansion"""
        positions = {'components': {}, 'states': {}}
        connections = []
        annotations = []
        
        positions['components'] = {
            'Compression': (25, 25),
            'Heat Addition': (75, 35),
            'Expansion': (75, 55),
            'Heat Rejection': (25, 55),
        }
        
        # State positions
        sorted_states = sorted(states.keys())
        if len(sorted_states) >= 4:
            positions['states'] = {
                sorted_states[0]: (15, 35),
                sorted_states[1]: (35, 25),
                sorted_states[2]: (85, 35),
                sorted_states[3]: (85, 55),
            }
        
        # Connections
        for i in range(len(sorted_states)):
            current_id = sorted_states[i]
            next_id = sorted_states[(i + 1) % len(sorted_states)]
            connections.append((current_id, next_id, ""))
        
        # Add state annotations
        for state_id, st in states.items():
            if state_id in positions['states']:
                x, y = positions['states'][state_id]
                temp = f"{st.T - 273.15:.0f}°C" if st.T else ""
                press = f"{st.P / 1e5:.1f}bar" if st.P else ""
                info = f"{temp}\n{press}".strip()
                if info:
                    annotations.append(((x, y - 7), info, '#666'))
        
        # Add process annotations
        for i in range(len(sorted_states)):
            current_id = sorted_states[i]
            next_id = sorted_states[(i + 1) % len(sorted_states)]
            if current_id in positions['states'] and next_id in positions['states']:
                current_st = states[current_id]
                next_st = states[next_id]
                delta_h = next_st.h - current_st.h if next_st.h and current_st.h else 0
                annotation_pos = (positions['states'][current_id][0] + 4, positions['states'][current_id][1] + 4)
                if i == 0:  # Isothermal compression
                    annotations.append((annotation_pos, f"W_c={abs(delta_h)/1000:.0f}kJ/kg", '#DC143C'))
                elif i == 1:  # Isothermal heating
                    annotations.append((annotation_pos, f"Q_in={abs(delta_h)/1000:.0f}kJ/kg", '#FF6347'))
                elif i == 2:  # Isothermal expansion
                    annotations.append((annotation_pos, f"W_e={abs(delta_h)/1000:.0f}kJ/kg", '#2E8B57'))
                elif i == 3:  # Isothermal cooling
                    annotations.append((annotation_pos, f"Q_out={abs(delta_h)/1000:.0f}kJ/kg", '#4169E1'))
        
        return positions, connections, annotations

    @staticmethod
    def layout_ericsson(comps, states):
        """Ericsson cycle layout - isothermal processes"""
        return FlowChartGenerator.layout_brayton(comps, states)  # Similar to Brayton

    @staticmethod
    def create_diagram(cycle_type, component_list, states, metrics=None):
        """
        Procedurally maps components and states for cycle-specific diagrams with process information.
        """
        # Set figure properties with a neutral background
        fig, ax = plt.subplots(figsize=(16, 10), dpi=200, facecolor='#f9f9f9')
        ax.set_xlim(0, 100)
        ax.set_ylim(0, 60)
        ax.axis('off')

        # Get cycle-specific layout using normalized cycle name or alias
        cycle_key = FlowChartGenerator.normalize_cycle_type(cycle_type)
        layout_func = FlowChartGenerator.CYCLE_LAYOUTS.get(cycle_key, FlowChartGenerator.layout_generic)
        positions, connections, annotations = layout_func(component_list, states)

        # Draw components
        for comp_name, (x, y) in positions['components'].items():
            drawer_key = "default"
            # Match the most specific key first
            for key in sorted(FlowChartGenerator.COMPONENT_DRAWERS.keys(), key=len, reverse=True):
                if key.lower() in comp_name.lower():
                    drawer_key = key
                    break
            
            drawer = FlowChartGenerator.COMPONENT_DRAWERS.get(drawer_key)
            drawer(ax, x, y)

        # Draw state points and connections
        sorted_states = sorted(states.keys())
        for i, state_id in enumerate(sorted_states):
            st = states[state_id]
            x, y = positions['states'][state_id]
            
            # Draw state anchor with phase color
            color = FlowChartGenerator.get_phase_color(st)
            circ = patches.Circle((x, y), 3.5, fc="white", ec=color, lw=2.5, zorder=5)
            ax.add_patch(circ)
            ax.text(x, y, str(state_id), ha='center', va='center', fontsize=10, fontweight='bold', color='#333')

        # Draw flow connections
        for start_id, end_id, label in connections:
            if start_id in positions['states'] and end_id in positions['states']:
                p1 = positions['states'][start_id]
                p2 = positions['states'][end_id]
                color = FlowChartGenerator.get_phase_color(states[start_id])
                
                # Draw line with arrow
                ax.annotate('', xy=p2, xytext=p1,
                            arrowprops=dict(arrowstyle='-|>,head_width=0.5,head_length=0.8', 
                                          color=color, lw=4, shrinkA=10, shrinkB=10, zorder=2))
                
                # Add process label if provided
                if label:
                    mid_x, mid_y = (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2
                    ax.text(mid_x, mid_y + 2, label, ha='center', va='bottom', 
                           fontsize=8, fontweight='bold', color='#333', 
                           bbox=dict(boxstyle="round,pad=0.2", facecolor="white", alpha=0.8))

        # Add annotations
        for (x, y), text, color in annotations:
            ax.text(x, y, text, ha='center', va='center', fontsize=8, 
                   fontweight='bold', color=color, 
                   bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.9))

        # Title with metrics
        title = f"{cycle_type} - System Architecture"
        if metrics:
            eff = metrics.get('efficiency', 0)
            w_net = metrics.get('w_net', 0)
            title += f" | η = {eff:.1f}% | W_net = {w_net:.0f} kJ/kg"
        
        ax.text(50, 58, title, ha='center', fontweight='bold', fontsize=14, color='#333')

        # Enhanced Legend
        lax = fig.add_axes([0.02, 0.05, 0.25, 0.25])
        lax.axis('off')
        lax.text(0, 0.9, "Phases:", fontsize=10, fontweight='bold', color='#333')
        lax.text(0.1, 0.7, "─ Vapor/Steam", color=FlowChartGenerator.PHASE_COLORS['vapor'], fontsize=8, fontweight='bold')
        lax.text(0.1, 0.5, "─ Liquid", color=FlowChartGenerator.PHASE_COLORS['liquid'], fontsize=8, fontweight='bold')
        lax.text(0.1, 0.3, "─ Supercritical", color=FlowChartGenerator.PHASE_COLORS['supercritical'], fontsize=8, fontweight='bold')
        lax.text(0.1, 0.1, "─ Two-Phase", color=FlowChartGenerator.PHASE_COLORS['two-phase'], fontsize=8, fontweight='bold')

        # Process Information Legend
        if metrics:
            rix = fig.add_axes([0.75, 0.05, 0.22, 0.25])
            rix.axis('off')
            rix.text(0, 0.9, "Cycle Metrics:", fontsize=10, fontweight='bold', color='#333')
            rix.text(0.1, 0.7, f"η = {metrics.get('efficiency', 0):.1f}%", fontsize=8, color='#333')
            rix.text(0.1, 0.5, f"W_net = {metrics.get('w_net', 0):.0f} kJ/kg", fontsize=8, color='#333')
            rix.text(0.1, 0.3, f"Q_in = {metrics.get('q_in', 0):.0f} kJ/kg", fontsize=8, color='#333')
            rix.text(0.1, 0.1, f"Q_out = {metrics.get('q_out', 0):.0f} kJ/kg", fontsize=8, color='#333')

        buf = io.BytesIO()
        plt.savefig(buf, format='svg', bbox_inches='tight', transparent=True)
        plt.close(fig)
        return buf
