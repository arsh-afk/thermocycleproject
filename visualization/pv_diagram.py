"""
P-v Diagram Visualization Module
Educational note: Pressure-Volume diagrams are fundamental for understanding work (integral of Pdv).
SOURCE: Standard thermodynamic plot conventions.
"""
import plotly.graph_objects as go
import numpy as np
import CoolProp.CoolProp as CP

class PVDiagram:
    """Generates interactive P-v diagrams with saturation curves."""
    
    @staticmethod
    def create_plot(states, cycle_name, fluid_name):
        fig = go.Figure()
        
        # 1. Plot Saturation Dome (Log-Log)
        try:
            T_crit = CP.PropsSI('TCRIT', fluid_name)
            T_trip = CP.PropsSI('TTRIPLE', fluid_name)
            T_range = np.linspace(T_trip + 0.1, T_crit - 0.1, 100)
            
            # SOURCE: CoolProp dynamic property retrieval
            v_liq = [1.0/CP.PropsSI('D', 'T', t, 'Q', 0, fluid_name) for t in T_range]
            v_vap = [1.0/CP.PropsSI('D', 'T', t, 'Q', 1, fluid_name) for t in T_range]
            P_c = [CP.PropsSI('P', 'T', t, 'Q', 0, fluid_name)/1e6 for t in T_range]
            
            fig.add_trace(go.Scatter(
                x=v_liq + v_vap[::-1], y=P_c + P_c[::-1],
                fill='toself', fillcolor='rgba(255, 165, 0, 0.05)',
                line=dict(color='rgba(255, 165, 0, 0.3)', dash='dash', width=1),
                name=f'{fluid_name} Saturation Dome'
            ))
        except:
            pass

        # 2. Plot Cycle Path
        sorted_keys = sorted(states.keys())
        v_vals = [states[k].v for k in sorted_keys]
        P_vals = [states[k].P/1e6 for k in sorted_keys]
        
        # Close loop
        v_vals.append(v_vals[0]); P_vals.append(P_vals[0])
        
        fig.add_trace(go.Scatter(
            x=v_vals, y=P_vals,
            mode='lines+markers+text',
            text=[str(k) for k in sorted_keys] + [""],
            textposition="top center",
            name='Cycle Path',
            line=dict(color='orange', width=2),
            marker=dict(size=8, color='white')
        ))
        
        fig.update_layout(
            title=f"P-v Diagram: {cycle_name}",
            xaxis_title="Specific Volume (m³/kg)",
            yaxis_title="Pressure (MPa)",
            xaxis_type="log", # SOURCE: Standard log-log scale for P-v
            yaxis_type="log",
            template="plotly_dark",
            height=600
        )
        
        return fig
