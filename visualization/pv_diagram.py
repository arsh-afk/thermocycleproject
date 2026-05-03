"""
P-v Diagram Visualization Module
Educational note: Pressure-Volume (P-v) diagrams are fundamental for understanding 
work transfer (integral of P dv). The area enclosed by the cycle on a P-v diagram 
represents the net work output per unit mass.
SOURCE: Standard thermodynamic plot conventions.
"""
import logging
import plotly.graph_objects as go
import numpy as np
import CoolProp.CoolProp as CP

logger = logging.getLogger(__name__)

class PVDiagram:
    """
    Generates interactive Pressure-Volume (P-v) diagrams with saturation curves.
    """
    
    @staticmethod
    def create_plot(states, cycle_name, fluid_name):
        """
        Creates a Plotly figure representing the cycle on a P-v coordinate system.
        
        Args:
            states: Dict of State objects representing the cycle state points.
            cycle_name: String name of the cycle for the title.
            fluid_name: String name of the working fluid.
            
        Returns:
            plotly.graph_objects.Figure: The generated P-v plot.
        """
        fig = go.Figure()
        
        # 1. Plot Saturation Dome (Liquid-Vapor envelope)
        # The dome defines the phase boundaries where the fluid exists as a mixture.
        try:
            T_crit = CP.PropsSI('TCRIT', fluid_name)
            T_trip = CP.PropsSI('TTRIPLE', fluid_name)
            # Create a range of temperatures from triple point to critical point
            T_range = np.linspace(T_trip + 0.1, T_crit - 0.1, 100)
            
            # Retrieve saturation properties using CoolProp
            v_liq = [1.0/CP.PropsSI('D', 'T', t, 'Q', 0, fluid_name) for t in T_range]
            v_vap = [1.0/CP.PropsSI('D', 'T', t, 'Q', 1, fluid_name) for t in T_range]
            P_c = [CP.PropsSI('P', 'T', t, 'Q', 0, fluid_name)/1e6 for t in T_range]
            
            # Add the saturation dome to the plot
            fig.add_trace(go.Scatter(
                x=v_liq + v_vap[::-1], y=P_c + P_c[::-1],
                fill='toself', fillcolor='rgba(255, 165, 0, 0.05)',
                line=dict(color='rgba(255, 165, 0, 0.3)', dash='dash', width=1),
                name=f'{fluid_name} Saturation Dome',
                hoverinfo='skip'
            ))
        except Exception as exc:
            logger.debug("Unable to plot P-v saturation dome for %s: %s", fluid_name, exc)

        # 2. Plot Cycle Path
        # Connect the state points in the order they occur in the cycle.
        sorted_keys = sorted(states.keys())
        v_vals = [states[k].v for k in sorted_keys]
        P_vals = [states[k].P/1e6 for k in sorted_keys]
        
        # Close the cycle loop by connecting the last point back to the first
        v_vals.append(v_vals[0]); P_vals.append(P_vals[0])
        
        fig.add_trace(go.Scatter(
            x=v_vals, y=P_vals,
            mode='lines+markers+text',
            text=[str(k) for k in sorted_keys] + [""],
            textposition="top center",
            name='Cycle Path',
            line=dict(color='#ffaa00', width=3), # Branded Warm Amber
            marker=dict(size=10, color='white', line=dict(color='#0f1f3d', width=2)),
            hovertemplate='v: %{x:.4f} m³/kg<br>P: %{y:.3f} MPa<extra></extra>'
        ))
        
        # Layout configuration for a professional engineering look
        fig.update_layout(
            title=dict(
                text=f"<b>P-v Diagram: {cycle_name}</b>",
                font=dict(size=20, color='#f8fafc')
            ),
            xaxis_title="Specific Volume (m³/kg)",
            yaxis_title="Pressure (MPa)",
            # Educational note: Log-Log scales are standard for P-v diagrams to 
            # effectively display changes over several orders of magnitude.
            xaxis_type="log",
            yaxis_type="log",
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=600,
            hovermode="x unified",
            margin=dict(l=40, r=40, t=60, b=40)
        )
        
        return fig
