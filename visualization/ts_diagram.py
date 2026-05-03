"""
T-s Diagram Visualization Module
Educational note: Temperature-Entropy (T-s) diagrams are essential for analyzing heat 
engines and refrigeration cycles. The area under the path on a T-s diagram represents 
the heat transfer during internally reversible processes.

Features:
1. Dynamic saturation dome generation for any fluid supported by CoolProp.
2. Sequential cycle path plotting with state point markers.
3. Interactive Plotly interface with dark theme optimization.
"""
import logging
import plotly.graph_objects as go
import numpy as np
import CoolProp.CoolProp as CP

logger = logging.getLogger(__name__)

class TSDiagram:
    """
    Generates interactive T-s diagrams with saturation domes.
    Enables visual validation of isentropic transitions and phase changes.
    """
    
    @staticmethod
    def create_plot(states, cycle_name, fluid_name):
        """
        Creates a Plotly figure representing the cycle on a T-s plane.
        
        Args:
            states (dict): Dictionary of thermodynamic State objects.
            cycle_name (str): Name of the cycle for the plot title.
            fluid_name (str): Name of the working fluid (e.g., 'Water', 'R134a').
            
        Returns:
            plotly.graph_objects.Figure: The interactive plot.
        """
        fig = go.Figure()
        
        # 1. Plot Saturation Dome
        # The dome defines the phase boundaries (liquid, two-phase, vapor).
        # We retrieve properties from the triple point to the critical point.
        try:
            T_crit = CP.PropsSI('TCRIT', fluid_name)
            T_trip = CP.PropsSI('TTRIPLE', fluid_name)
            # Create a temperature range for the dome
            T_range = np.linspace(T_trip + 0.1, T_crit - 0.1, 100)
            
            # Saturated liquid line (Q=0) and Saturated vapor line (Q=1)
            # Entropy is converted to kJ/kgK for standard engineering units.
            s_liq = [CP.PropsSI('S', 'T', t, 'Q', 0, fluid_name)/1000 for t in T_range]
            s_vap = [CP.PropsSI('S', 'T', t, 'Q', 1, fluid_name)/1000 for t in T_range]
            T_c = [t - 273.15 for t in T_range] # Convert Kelvin to Celsius for axis
            
            # Add the dome to the plot as a shaded region
            fig.add_trace(go.Scatter(
                x=s_liq + s_vap[::-1], y=T_c + T_c[::-1],
                fill='toself', fillcolor='rgba(100, 100, 100, 0.1)',
                line=dict(color='rgba(150, 150, 150, 0.5)', dash='dash', width=1),
                name=f'{fluid_name} Saturation Dome',
                hoverinfo='skip'
            ))
        except Exception as exc:
            logger.debug("Unable to plot saturation dome for %s: %s", fluid_name, exc)

        # 2. Plot Cycle Path
        # States are plotted in numerical/key order.
        sorted_keys = sorted(states.keys())
        s_vals = [states[k].s/1000 for k in sorted_keys]
        T_vals = [states[k].T - 273.15 for k in sorted_keys]
        
        # Close the cycle loop by returning to the first state
        s_plot = s_vals + [s_vals[0]]
        T_plot = T_vals + [T_vals[0]]
        
        # Plot the path with markers and labels for each state point
        fig.add_trace(go.Scatter(
            x=s_plot, y=T_plot,
            mode='lines+markers+text',
            text=[str(k) for k in sorted_keys] + [""],
            textposition="top center",
            name='Cycle Path',
            line=dict(color='#2ca8ff', width=3), # Branded Cool Cyan
            marker=dict(size=10, color='white', line=dict(color='#0f1f3d', width=2)),
            hovertemplate="<b>State %{text}</b><br>s: %{x:.4f} kJ/kgK<br>T: %{y:.2f} °C<extra></extra>"
        ))
        
        # 3. Configure Layout
        # Optimized for integration into the dark-themed Streamlit dashboard.
        fig.update_layout(
            title=dict(
                text=f"<b>T-s Diagram: {cycle_name}</b>",
                font=dict(size=20, color='#f8fafc')
            ),
            xaxis_title="Specific Entropy (kJ/kg·K)",
            yaxis_title="Temperature (°C)",
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=600,
            hovermode="closest",
            margin=dict(l=40, r=40, t=60, b=40),
            xaxis=dict(gridcolor='#334155', zerolinecolor='#334155'),
            yaxis=dict(gridcolor='#334155', zerolinecolor='#334155')
        )
        
        return fig
