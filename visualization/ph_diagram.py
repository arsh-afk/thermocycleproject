"""
P-h Diagram Visualization Module
Educational note: Pressure-Enthalpy diagrams allow clear visualization of work 
input/output and heat addition/rejection.
"""
import plotly.graph_objects as go
import numpy as np

class PHDiagram:
    """Generates interactive P-h diagrams using Plotly."""
    
    @staticmethod
    def create_plot(states, cycle_name, fluid_name):
        fig = go.Figure()
        
        # Enthalpy in kJ/kg, Pressure in MPa
        h_vals = [st.h/1000 for st in states.values()]
        P_vals = [st.P/1e6 for st in states.values()]
        
        # Close loop
        h_vals.append(h_vals[0])
        P_vals.append(P_vals[0])
        
        fig.add_trace(go.Scatter(
            x=h_vals, y=P_vals,
            mode='lines+markers',
            name='Cycle Path',
            line=dict(color='orange', width=2),
            marker=dict(size=8)
        ))
        
        fig.update_layout(
            title=f"P-h Diagram: {cycle_name} ({fluid_name})",
            xaxis_title="Specific Enthalpy (kJ/kg)",
            yaxis_title="Pressure (MPa)",
            yaxis_type="log", # Educational note: Log scale is standard for P in P-h diagrams.
            template="plotly_dark",
            height=600
        )
        
        return fig
