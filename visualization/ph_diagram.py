"""
P-h Diagram Visualization Module
Educational note: Pressure-Enthalpy (P-h) diagrams allow clear visualization of work 
input/output and heat addition/rejection. They are particularly common in 
refrigeration and heat pump analysis.
"""
import plotly.graph_objects as go
import numpy as np

class PHDiagram:
    """
    Generates interactive Pressure-Enthalpy (P-h) diagrams using Plotly.
    """
    
    @staticmethod
    def create_plot(states, cycle_name, fluid_name):
        """
        Creates a Plotly figure representing the cycle on a P-h coordinate system.
        
        Args:
            states: Dict of State objects representing the cycle state points.
            cycle_name: String name of the cycle for the title.
            fluid_name: String name of the working fluid.
            
        Returns:
            plotly.graph_objects.Figure: The generated P-h plot.
        """
        fig = go.Figure()
        
        # Convert values to standard engineering units: Enthalpy in kJ/kg, Pressure in MPa
        h_vals = [st.h/1000 for st in states.values()]
        P_vals = [st.P/1e6 for st in states.values()]
        
        # Close the cycle loop by connecting the last point back to the first
        h_vals.append(h_vals[0])
        P_vals.append(P_vals[0])
        
        # Plot the cycle path with markers at state points
        fig.add_trace(go.Scatter(
            x=h_vals, y=P_vals,
            mode='lines+markers',
            name='Cycle Path',
            line=dict(color='orange', width=2),
            marker=dict(size=8),
            hovertemplate='h: %{x:.1f} kJ/kg<br>P: %{y:.3f} MPa<extra></extra>'
        ))
        
        # Standard engineering layout for P-h diagrams
        fig.update_layout(
            title=f"P-h Diagram: {cycle_name} ({fluid_name})",
            xaxis_title="Specific Enthalpy (kJ/kg)",
            yaxis_title="Pressure (MPa)",
            # Educational note: Logarithmic scale for pressure is standard in engineering 
            # P-h diagrams to represent wide pressure ranges clearly.
            yaxis_type="log", 
            template="plotly_dark",
            height=600,
            hovermode="closest"
        )
        
        return fig
