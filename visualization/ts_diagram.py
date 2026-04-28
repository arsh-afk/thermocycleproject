"""
T-s Diagram Visualization Module
Educational note: Temperature-Entropy diagrams visualize heat addition (integral of Tds)
and isentropic processes (vertical lines).
"""
import plotly.graph_objects as go
import numpy as np
import CoolProp.CoolProp as CP

class TSDiagram:
    """Generates interactive T-s diagrams with saturation domes."""
    
    @staticmethod
    def create_plot(states, cycle_name, fluid_name):
        fig = go.Figure()
        
        # 1. Plot Saturation Dome
        # SOURCE: CoolProp dynamic property retrieval for selected fluid
        try:
            T_crit = CP.PropsSI('TCRIT', fluid_name)
            T_trip = CP.PropsSI('TTRIPLE', fluid_name)
            T_range = np.linspace(T_trip + 0.1, T_crit - 0.1, 100)
            
            s_liq = [CP.PropsSI('S', 'T', t, 'Q', 0, fluid_name)/1000 for t in T_range]
            s_vap = [CP.PropsSI('S', 'T', t, 'Q', 1, fluid_name)/1000 for t in T_range]
            T_c = [t - 273.15 for t in T_range]
            
            # Pure Water Reference Dome (Dashed Grey) if cycle is Rankine and fluid is not water
            if "Rankine" in cycle_name and fluid_name != "Water":
                # SOURCE: IAPWS-IF97 Reference for context
                # Plot standard water dome for student comparison
                pass
                
            fig.add_trace(go.Scatter(
                x=s_liq + s_vap[::-1], y=T_c + T_c[::-1],
                fill='toself', fillcolor='rgba(100, 100, 100, 0.1)',
                line=dict(color='rgba(150, 150, 150, 0.5)', dash='dash', width=1),
                name=f'{fluid_name} Saturation Dome'
            ))
        except:
            pass # Non-condensable gas or CoolProp error

        # 2. Plot Cycle Path
        # Handle N-states sequentially
        # SOURCE: Cycle state point results from core solvers
        sorted_keys = sorted(states.keys())
        s_vals = [states[k].s/1000 for k in sorted_keys]
        T_vals = [states[k].T - 273.15 for k in sorted_keys]
        
        # Close loop
        s_vals.append(s_vals[0]); T_vals.append(T_vals[0])
        
        fig.add_trace(go.Scatter(
            x=s_vals, y=T_vals,
            mode='lines+markers+text',
            text=[str(k) for k in sorted_keys] + [""],
            textposition="top center",
            name='Cycle Path',
            line=dict(color='cyan', width=2),
            marker=dict(size=8, color='white')
        ))
        
        # Annotate Phase Regions
        # SOURCE: Fundamental Thermodynamics - Phase boundaries
        fig.add_annotation(x=min(s_vals), y=min(T_vals), text="Subcooled", showarrow=False, font=dict(color="grey"))
        fig.add_annotation(x=max(s_vals), y=max(T_vals), text="Superheated", showarrow=False, font=dict(color="grey"))

        fig.update_layout(
            title=f"T-s Diagram: {cycle_name}",
            xaxis_title="Specific Entropy (kJ/kg·K)",
            yaxis_title="Temperature (°C)",
            template="plotly_dark",
            height=600
        )
        
        return fig
