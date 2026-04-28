"""
Thermodynamic Cycle Calculator Pro v2.0
Monolithic Single-Page Professional Interface
AURAK Project 2026 Educational Tool
"""
import base64
import logging
import os
import sys

import CoolProp.CoolProp as CP
import streamlit as st
import yaml

# Add project root to path for local package imports.
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_path not in sys.path:
    sys.path.append(root_path)

from core.brayton_cycle import BraytonCycle
from core.diesel_cycle import DieselCycle
from core.ericsson_cycle import EricssonCycle
from core.otto_cycle import OttoCycle
from core.rankine_cycle import RankineCycle
from core.sco2_cycle import sCO2Cycle
from core.stirling_cycle import StirlingCycle
from visualization.flow_charts import FlowChartGenerator
from visualization.pv_diagram import PVDiagram
from visualization.ts_diagram import TSDiagram

logger = logging.getLogger(__name__)

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Thermo Cycle Explorer Pro", page_icon="🔥", layout="wide")

st.markdown(
    """
    <style>
        .stMetric { background-color: #1a1c23; padding: 15px; border-radius: 10px; border: 1px solid #444; }
        .stProgress > div > div > div > div { background-color: #2ecc71; }
        .sidebar .sidebar-content { width: 450px; }
        .block-container { padding-top: 1rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

@st.cache_data
def load_config():
    config = {'cycles': {}, 'fluids': {}, 'heat_sources': {}}
    config_dir = os.path.join(root_path, "config")
    for filename in ["cycles.yaml", "fluids.yaml", "heat_sources.yaml"]:
        try:
            with open(os.path.join(config_dir, filename), "r", encoding="utf-8") as handle:
                config[filename.replace(".yaml", "")] = yaml.safe_load(handle) or {}
        except FileNotFoundError:
            logger.warning("Missing configuration file: %s", filename)
        except yaml.YAMLError as exc:
            logger.error("Invalid YAML in %s: %s", filename, exc)
    return config

cfg = load_config()

cycle_keys = list(cfg['cycles'].keys()) if cfg['cycles'] else ["rankine"]
selected_cycle_key = st.sidebar.selectbox(
    "Architecture",
    options=cycle_keys,
    format_func=lambda key: cfg['cycles'][key]['name'] if key in cfg['cycles'] else key.title(),
    index=0,
)
cycle_definition = cfg['cycles'].get(selected_cycle_key, {})

available_fluids = [
    name for name, data in cfg['fluids'].items()
    if selected_cycle_key in data.get('common_cycles', [])
]
if not available_fluids:
    available_fluids = list(cfg['fluids'].keys())

fluid = st.sidebar.selectbox("Working Fluid", options=available_fluids)

st.sidebar.subheader("📐 Thermodynamic Spec")
st.sidebar.caption("Select exactly two independent variables.")

vars_meta = {
    'P_max': {'label': 'Max Pressure (MPa)', 'min': 0.1, 'max': 35.0, 'val': 15.0, 'step': 0.5},
    'T_max': {'label': 'Max Temperature (°C)', 'min': 100, 'max': 750, 'val': 550, 'step': 10},
    'P_min': {'label': 'Min Pressure (MPa)', 'min': 0.001, 'max': 1.0, 'val': 0.01, 'step': 0.001},
    'T_min': {'label': 'Min Temperature (°C)', 'min': 10, 'max': 100, 'val': 35, 'step': 1},
}

if "sco2" in selected_cycle_key:
    vars_meta['P_min'] = {'label': 'Min Pressure (MPa)', 'min': 7.4, 'max': 10.0, 'val': 7.6, 'step': 0.05}
    vars_meta['P_max'] = {'label': 'Max Pressure (MPa)', 'min': 10.0, 'max': 35.0, 'val': 25.0, 'step': 0.5}

selected_vars = st.sidebar.multiselect(
    "Independent variables",
    options=list(vars_meta.keys()),
    default=["P_max", "T_max"],
    help="Pick exactly two independent state variables for the cycle solver.",
)

if len(selected_vars) != 2:
    st.sidebar.error("Please select exactly two independent variables.")
    solve_disabled = True
else:
    solve_disabled = False

params = {key: float(meta['val']) for key, meta in vars_meta.items()}
for selected_var in selected_vars:
    meta = vars_meta[selected_var]
    params[selected_var] = st.sidebar.number_input(
        meta['label'],
        min_value=float(meta['min']),
        max_value=float(meta['max']),
        value=float(meta['val']),
        step=float(meta['step']),
        key=f"num_{selected_var}",
    )

if selected_cycle_key == 'rankine':
    params['n_rh'] = st.sidebar.number_input(
        "Reheat Stages",
        min_value=0,
        max_value=10,
        value=cycle_definition.get('defaults', {}).get('n_rh', 1),
        step=1,
    )
    params['n_fwh'] = st.sidebar.number_input(
        "Feedwater Heaters",
        min_value=0,
        max_value=10,
        value=cycle_definition.get('defaults', {}).get('n_fwh', 2),
        step=1,
    )
elif selected_cycle_key == 'brayton':
    params['n_ic'] = st.sidebar.number_input(
        "Intercooler Stages",
        min_value=0,
        max_value=5,
        value=cycle_definition.get('defaults', {}).get('n_ic', 1),
        step=1,
    )
    params['n_rh'] = st.sidebar.number_input(
        "Reheat Stages",
        min_value=0,
        max_value=5,
        value=cycle_definition.get('defaults', {}).get('n_rh', 0),
        step=1,
    )
elif selected_cycle_key == 'sco2':
    params['split_frac'] = st.sidebar.slider(
        "Recompression Split Fraction",
        min_value=0.05,
        max_value=0.60,
        value=cycle_definition.get('defaults', {}).get('split_frac', 0.35),
        step=0.01,
    )
    params['recup_eff'] = st.sidebar.slider(
        "Recuperator Effectiveness",
        min_value=0.5,
        max_value=0.99,
        value=cycle_definition.get('defaults', {}).get('recup_eff', 0.95),
        step=0.01,
    )
    params['eta_c'] = st.sidebar.slider(
        "Compressor Efficiency",
        min_value=0.7,
        max_value=0.95,
        value=cycle_definition.get('defaults', {}).get('eta_c', 0.89),
        step=0.01,
    )
    params['eta_t'] = st.sidebar.slider(
        "Turbine Efficiency",
        min_value=0.7,
        max_value=0.95,
        value=cycle_definition.get('defaults', {}).get('eta_t', 0.92),
        step=0.01,
    )

heat_source_options = list(cfg['heat_sources'].keys())
if heat_source_options:
    params['heat_source'] = st.sidebar.selectbox("Primary Heat Source", heat_source_options)

cycle_factory = {
    'rankine': RankineCycle,
    'sco2': sCO2Cycle,
    'brayton': BraytonCycle,
    'otto': OttoCycle,
    'diesel': DieselCycle,
    'stirling': StirlingCycle,
    'ericsson': EricssonCycle,
}

st.title(f"📊 {cycle_definition.get('name', selected_cycle_key.title())} Analysis Dashboard")

if st.sidebar.button("🚀 EXECUTE SIMULATION", type="primary", use_container_width=True, disabled=solve_disabled):
    try:
        cycle_cls = cycle_factory.get(selected_cycle_key)
        if cycle_cls is None:
            raise ValueError(f"Unsupported cycle: {selected_cycle_key}")

        cycle_obj = cycle_cls() if selected_cycle_key == 'sco2' else cycle_cls(fluid)
        validation_messages = cycle_obj.validate_inputs(params)
        for message in validation_messages:
            st.warning(message)

        with st.spinner("Processing thermodynamic state properties..."):
            states = cycle_obj.solve(params)
            metrics = cycle_obj.calculate_performance()

        if not states:
            st.error("Cycle solver returned no state points.")
        else:
            st.subheader("🔗 System Architecture Flow-Chart")
            svg_buf = FlowChartGenerator.create_diagram(
                cycle_definition.get('name', selected_cycle_key.title()),
                cycle_obj.get_component_list(),
                states,
            )
            svg_bytes = svg_buf.getvalue()
            b64 = base64.b64encode(svg_bytes).decode('utf-8')
            st.markdown(
                f'<div style="background-color: white; padding: 10px; border-radius: 5px; overflow-x: auto;"><img src="data:image/svg+xml;base64,{b64}"/></div>',
                unsafe_allow_html=True,
            )

            st.subheader("📈 Thermodynamic Correlation Diagrams")
            c1, c2 = st.columns(2)
            with c1:
                st.plotly_chart(TSDiagram.create_plot(states, cycle_definition.get('name', selected_cycle_key.title()), fluid), use_container_width=True)
            with c2:
                st.plotly_chart(PVDiagram.create_plot(states, cycle_definition.get('name', selected_cycle_key.title()), fluid), use_container_width=True)

            st.subheader("📝 State Point Analytics")
            state_rows = []
            for sid, state_obj in states.items():
                row = state_obj.to_dict()
                row['Point'] = sid
                row['T (°C)'] = f"{row['T'] - 273.15:.2f}" if row['T'] else None
                row['P (MPa)'] = f"{row['P'] / 1e6:.3f}" if row['P'] else None
                row['h (kJ/kg)'] = f"{row['h'] / 1000:.1f}" if row['h'] else None
                row['s (kJ/kg·K)'] = f"{row['s'] / 1000:.3f}" if row['s'] else None
                state_rows.append(row)
            st.dataframe(state_rows, use_container_width=True)

            metric_cols = st.columns(4)
            efficiency = metrics.get('efficiency', 0.0)
            metric_cols[0].metric("Thermal Efficiency", f"{efficiency:.2f}%", delta=f"{efficiency - 42:.1f}% vs Target")
            metric_cols[1].metric("Second-Law Efficiency", f"{metrics.get('second_law_efficiency', 0.0):.2f}%")
            metric_cols[2].metric("Entropy Generation", f"{metrics.get('s_gen', 0.0):.4f} J/kg·K")
            metric_cols[3].metric("Net Work", f"{metrics.get('w_net', 0.0):.1f} kJ/kg")

            extra_cols = st.columns(3)
            extra_cols[0].metric("Heat Input", f"{metrics.get('q_in', 0.0):.1f} kJ/kg")
            extra_cols[1].metric("Heat Rejection", f"{metrics.get('q_out', 0.0):.1f} kJ/kg")
            extra_cols[2].metric("Working Fluid", fluid)

            if efficiency >= 42.0:
                st.success("✅ Target ≥42% Met")
            else:
                st.info("⚠️ Below the 42% efficiency target")

    except Exception as exc:
        logger.exception("Cycle execution failed")
        st.error(f"Solver Failure: {exc}")
else:
    st.info("👈 Use the sidebar to define the cycle specification and click EXECUTE SIMULATION.")
    st.image(
        "https://upload.wikimedia.org/wikipedia/commons/thumb/c/ca/T-s_Rankine_cycle.svg/1024px-T-s_Rankine_cycle.svg.png",
        width=600,
    )
