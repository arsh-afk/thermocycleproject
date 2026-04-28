"""
Thermodynamic Cycle Calculator Pro v2.0
Monolithic Single-Page Professional Interface
AURAK Project 2026 Educational Tool
"""
import streamlit as st
import yaml
import os
import sys
import numpy as np
import CoolProp.CoolProp as CP
import base64

# Add project root to path
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_path not in sys.path:
    sys.path.append(root_path)

from core.rankine_cycle import RankineCycle
from core.sco2_cycle import sCO2Cycle
from core.brayton_cycle import BraytonCycle
from core.otto_cycle import OttoCycle
from core.diesel_cycle import DieselCycle
from core.stirling_cycle import StirlingCycle
from core.ericsson_cycle import EricssonCycle

from visualization.ts_diagram import TSDiagram
from visualization.pv_diagram import PVDiagram
from visualization.flow_charts import FlowChartGenerator

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Thermo Cycle Explorer Pro", page_icon="🔥", layout="wide")

st.markdown("""
<style>
    .stMetric { background-color: #1a1c23; padding: 15px; border-radius: 10px; border: 1px solid #444; }
    .stProgress > div > div > div > div { background-color: #2ecc71; }
    .sidebar .sidebar-content { width: 450px; }
    .block-container { padding-top: 1rem; }
</style>
""", unsafe_allow_html=True)

# --- CONFIG LOADING ---
@st.cache_data
def load_config():
    config = {'cycles': {}, 'fluids': {}, 'heat_sources': {}}
    config_dir = os.path.join(root_path, "config")
    try:
        for f in ["cycles.yaml", "fluids.yaml", "heat_sources.yaml"]:
            with open(os.path.join(config_dir, f), "r") as file:
                config[f.replace(".yaml", "")] = yaml.safe_load(file)
    except: pass
    return config

cfg = load_config()

# --- SIDEBAR: DESIGN SPECIFICATION ---
st.sidebar.title("🔥 System Design")

# 1. Architecture & Fluid
cycle_options = ["Rankine Cycle", "sCO2 Recompression", "Brayton Cycle", "Otto Cycle", "Diesel Cycle", "Stirling Cycle", "Ericsson Cycle"]
cycle_type = st.sidebar.selectbox("Architecture", options=cycle_options, index=0)

# Fluid Logic
fluid_map = {
    "Rankine Cycle": ["Water", "Ammonia", "R134a", "R245fa", "Isobutane"],
    "sCO2 Recompression": ["CO2"],
    "Brayton Cycle": ["Air", "Helium", "Nitrogen", "Argon"],
}
fluid_list = fluid_map.get(cycle_type, ["Air"])
fluid = st.sidebar.selectbox("Working Fluid", options=fluid_list)

# 2. Independent Variables Specification (Gibbs Phase Rule)
st.sidebar.subheader("📐 Thermodynamic Spec")
st.sidebar.caption("Per Gibbs Phase Rule, select exactly TWO variables.")

# Variable Meta with Procedural Constraint Logic
# SOURCE: Standard engineering limits
vars_meta = {
    'P_max': {'label': 'Max Pressure (MPa)', 'min': 0.1, 'max': 35.0, 'val': 15.0, 'step': 0.5},
    'T_max': {'label': 'Max Temperature (°C)', 'min': 100, 'max': 750, 'val': 550, 'step': 10},
    'P_min': {'label': 'Min Pressure (MPa)', 'min': 0.001, 'max': 1.0, 'val': 0.01, 'step': 0.001},
    'T_min': {'label': 'Min Temperature (°C)', 'min': 10, 'max': 100, 'val': 35, 'step': 1}
}

if "sco2" in cycle_type.lower():
    vars_meta['P_min'] = {'label': 'Min Pressure (MPa)', 'min': 7.4, 'max': 10.0, 'val': 7.6, 'step': 0.05}
    vars_meta['P_max'] = {'label': 'Max Pressure (MPa)', 'min': 10.0, 'max': 35.0, 'val': 25.0, 'step': 0.5}

col_spec1, col_spec2 = st.sidebar.columns(2)
selected_vars = []

# Spec 1 Selection
with col_spec1:
    spec1_key = st.selectbox("Primary Property", options=["P_max", "P_min", "T_max"], index=0)
    selected_vars.append(spec1_key)

# Procedural Limit for Spec 2 based on Spec 1
# SOURCE: Boiling Point Elevation / Saturation boundaries
try:
    if spec1_key == "P_max":
        T_sat = CP.PropsSI('T', 'P', vars_meta['P_max']['val']*1e6, 'Q', 0, fluid) - 273.15
        T_min_allowed = T_sat + 10.0
    else:
        T_min_allowed = 100.0
except: T_min_allowed = 100.0

with col_spec2:
    spec2_key = st.selectbox("Secondary Property", options=["T_max", "P_min", "T_min"], index=0)
    selected_vars.append(spec2_key)

if spec1_key == spec2_key:
    st.sidebar.error("Select two DIFFERENT variables.")
    solve_disabled = True
else:
    solve_disabled = False

# Inputs for selected variables
params = {}
st.sidebar.markdown("---")
for k in selected_vars:
    meta = vars_meta[k]
    # Linked Slider + Number Input for precision
    st.sidebar.write(f"**{meta['label']}**")
    s_val = st.sidebar.slider(meta['label'], meta['min'], meta['max'], meta['val'], step=meta['step'], key=f"sld_{k}", label_visibility="collapsed")
    n_val = st.sidebar.number_input(meta['label'], value=float(s_val), step=float(meta['step']), key=f"num_{k}", label_visibility="collapsed")
    params[k] = n_val

# Non-selected parameters get default values
for k in vars_meta:
    if k not in params: params[k] = vars_meta[k]['val']

# 3. Scalability
st.sidebar.subheader("🏗️ Cycle Scalability")
params['n_rh'] = st.sidebar.number_input("Reheat Stages", 0, 10, 1)
params['n_fwh'] = st.sidebar.number_input("Feedwater Heaters", 0, 10, 2) if "Rankine" in cycle_type else 0

# --- MAIN AREA ---
st.title(f"📊 {cycle_type} Analysis Dashboard")

if st.sidebar.button("🚀 EXECUTE SIMULATION", type="primary", use_container_width=True, disabled=solve_disabled):
    try:
        # Factory Logic
        if "Rankine" in cycle_type: cycle_obj = RankineCycle(fluid)
        elif "sCO2" in cycle_type: cycle_obj = sCO2Cycle()
        elif "Brayton" in cycle_type: cycle_obj = BraytonCycle(fluid)
        elif "Otto" in cycle_type: cycle_obj = OttoCycle(fluid)
        elif "Diesel" in cycle_type: cycle_obj = DieselCycle(fluid)
        elif "Stirling" in cycle_type: cycle_obj = StirlingCycle(fluid)
        elif "Ericsson" in cycle_type: cycle_obj = EricssonCycle(fluid)
        else: raise ValueError(f"Unknown cycle type: {cycle_type}")
        
        with st.spinner("Processing thermodynamic property matrix..."):
            states = cycle_obj.solve(params)
            metrics = cycle_obj.calculate_performance()
        
        if states:
            # 1. Spatially Accurate PFD
            st.subheader("🔗 System Architecture Flow-Chart")
            comp_list = cycle_obj.get_component_list()
            svg_buf = FlowChartGenerator.create_diagram(cycle_type, comp_list, states)
            # Display SVG in Streamlit
            svg_bytes = svg_buf.getvalue()
            b64 = base64.b64encode(svg_bytes).decode('utf-8')
            st.markdown(f'<div style="background-color: white; padding: 10px; border-radius: 5px; overflow-x: auto;"><img src="data:image/svg+xml;base64,{b64}"/></div>', unsafe_allow_html=True)
            
            # 2. Key Metrics
            mcol1, mcol2, mcol3, mcol4 = st.columns(4)
            eff = metrics.get('efficiency', 0)
            mcol1.metric("Thermal Efficiency", f"{eff:.2f}%", delta=f"{eff-42:.1f}% vs Target")
            with mcol1:
                if eff >= 42: st.success("✅ Target ≥42% Met")
                else: st.error("❌ Below 42% Target")
            mcol2.metric("Net Work", f"{metrics.get('w_net', 0):.1f} kJ/kg")
            mcol3.metric("Mass Flow @ 100MW", f"{100000 / (metrics.get('w_net', 1) or 1):.2f} kg/s")
            mcol4.metric("Fluid", fluid)

            # 3. Diagrams
            st.subheader("📈 Thermodynamic Correlation Diagrams")
            dcol1, dcol2 = st.columns(2)
            with dcol1: st.plotly_chart(TSDiagram.create_plot(states, cycle_type, fluid), use_container_width=True)
            with dcol2: st.plotly_chart(PVDiagram.create_plot(states, cycle_type, fluid), use_container_width=True)
            
            # 4. State Table
            st.subheader("📝 State Point Analytics")
            state_data = []
            for sid, st_obj in states.items():
                d = st_obj.to_dict()
                d['Point'] = sid
                d['T (°C)'] = f"{d['T']-273.15:.2f}"
                d['P (MPa)'] = f"{d['P']/1e6:.3f}"
                d['h (kJ/kg)'] = f"{d['h']/1000:.1f}"
                d['s (kJ/kg·K)'] = f"{d['s']/1000:.3f}"
                state_data.append(d)
            st.dataframe(state_data, use_container_width=True)

    except Exception as e:
        st.error(f"Solver Failure: {str(e)}")
else:
    st.info("👈 Use the specification panel to define state and click SOLVE.")
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/c/ca/T-s_Rankine_cycle.svg/1024px-T-s_Rankine_cycle.svg.png", width=600)
