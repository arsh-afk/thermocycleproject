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

from core.cycle_control import CycleControl
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

# Modern Dark Theme Palette
BG_DARK = "#0f172a"
CARD_DARK = "#1e293b"
SIDEBAR_DARK = "#020617"
ACCENT_CYAN = "#38bdf8"
ACCENT_AMBER = "#fbbf24"
TEXT_LIGHT = "#f8fafc"
TEXT_DIM = "#94a3b8"
BORDER_DARK = "#334155"

st.markdown(
    f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Roboto+Mono&display=swap');
        
        html, body, [class*="st-"] {{
            font-family: 'Inter', sans-serif;
            color: {TEXT_LIGHT};
        }}
        
        .stApp {{
            background-color: {BG_DARK};
        }}
        
        .main {{
            background-color: {BG_DARK};
        }}
        
        /* Metric Cards Styling */
        div[data-testid="stMetric"] {{
            background-color: {CARD_DARK};
            padding: 20px;
            border-radius: 12px;
            border: 1px solid {BORDER_DARK};
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
            transition: all 0.2s ease;
        }}
        
        div[data-testid="stMetric"]:hover {{
            transform: translateY(-2px);
            border-color: {ACCENT_CYAN};
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.4);
        }}
        
        div[data-testid="stMetricValue"] {{
            color: {ACCENT_CYAN} !important;
            font-size: 1.8rem;
            font-weight: 700;
        }}
        
        div[data-testid="stMetricLabel"] {{
            color: {TEXT_DIM} !important;
            font-size: 0.8rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.1em;
        }}
        
        /* Sidebar Styling */
        section[data-testid="stSidebar"] {{
            background-color: {SIDEBAR_DARK};
            border-right: 1px solid {BORDER_DARK};
        }}
        
        section[data-testid="stSidebar"] .stText, 
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] .stMarkdown,
        section[data-testid="stSidebar"] p {{
            color: {TEXT_LIGHT} !important;
        }}
        
        /* Sidebar Inputs */
        .stSelectbox, .stMultiSelect, .stNumberInput, .stSlider {{
            background-color: {CARD_DARK} !important;
            border-radius: 8px !important;
        }}
        
        /* Header and Titles */
        h1, h2, h3, h4 {{
            color: {TEXT_LIGHT};
            font-weight: 700;
            letter-spacing: -0.02em;
        }}
        
        .hero-section {{
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
            padding: 2.5rem 2rem;
            border-radius: 16px;
            border: 1px solid {BORDER_DARK};
            margin-bottom: 2rem;
            position: relative;
            overflow: hidden;
        }}
        
        .hero-section::after {{
            content: "";
            position: absolute;
            top: 0; right: 0; bottom: 0; left: 0;
            background-image: radial-gradient(circle at 2px 2px, rgba(56, 189, 248, 0.05) 1px, transparent 0);
            background-size: 24px 24px;
        }}
        
        .hero-title {{
            font-size: 2.2rem;
            margin: 0;
            color: {TEXT_LIGHT} !important;
        }}
        
        .hero-subtitle {{
            font-size: 1rem;
            color: {TEXT_DIM};
            margin-top: 0.5rem;
        }}
        
        /* Buttons */
        .stButton>button {{
            background-color: {ACCENT_CYAN} !important;
            color: {BG_DARK} !important;
            border-radius: 8px !important;
            border: none !important;
            padding: 0.6rem 1.2rem !important;
            font-weight: 700 !important;
            transition: all 0.2s ease !important;
            width: 100%;
        }}
        
        .stButton>button:hover {{
            background-color: {ACCENT_AMBER} !important;
            transform: scale(1.02);
        }}
        
        /* Dataframes & Tables */
        .stDataFrame {{
            background-color: {CARD_DARK};
            border-radius: 12px;
            border: 1px solid {BORDER_DARK};
        }}
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 24px;
            background-color: transparent;
        }}
        
        .stTabs [data-baseweb="tab"] {{
            height: 50px;
            white-space: pre-wrap;
            background-color: transparent;
            border-radius: 4px 4px 0px 0px;
            gap: 1px;
            padding-top: 10px;
            padding-bottom: 10px;
            color: {TEXT_DIM};
        }}

        .stTabs [aria-selected="true"] {{
            color: {ACCENT_CYAN} !important;
            border-bottom-color: {ACCENT_CYAN} !important;
        }}
        
        /* Mono fonts */
        code, .mono {{
            font-family: 'Roboto Mono', monospace !important;
            color: {ACCENT_AMBER};
        }}

        hr {{
            border-color: {BORDER_DARK} !important;
        }}
        
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

# --- SIDEBAR CONTROLS ---
with st.sidebar:
    st.markdown(f"<h2 style='color: {ACCENT_CYAN}; margin-bottom: 0;'>THERMO</h2><h4 style='margin-top: 0; color: {TEXT_DIM};'>Cycle Explorer Pro</h4>", unsafe_allow_html=True)
    st.markdown("---")
    
    cycle_keys = list(cfg['cycles'].keys()) if cfg['cycles'] else ["rankine"]
    selected_cycle_key = st.selectbox(
        "Cycle Architecture",
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

    fluid = st.selectbox("Working Fluid", options=available_fluids)

    st.markdown("### 📐 Thermodynamic Spec")
    available_vars = CycleControl.get_variables_for_cycle(selected_cycle_key)
    selected_vars = st.multiselect(
        "Active Constraints",
        options=available_vars,
        default=available_vars[:2] if len(available_vars) >= 2 else [],
        format_func=lambda x: f"{CycleControl.get_metadata(x).get('label', x)}",
        help="Pick exactly two independent properties."
    )

    is_valid, error_msg = CycleControl.validate_selection(selected_vars)
    if not is_valid:
        st.error(f"⚠️ {error_msg}")
        solve_disabled = True
    else:
        solve_disabled = False

    params = {}
    for var_key in selected_vars:
        meta = CycleControl.get_metadata(var_key)
        params[var_key] = st.number_input(
            f"{meta['label']} ({meta['unit']})",
            min_value=float(meta['min']),
            max_value=float(meta['max']),
            value=float(meta['default']),
            step=0.1,
            key=f"input_{var_key}"
        )

    st.markdown("### ⚙️ Component Configuration")
    if selected_cycle_key == 'rankine':
        params['n_rh'] = st.number_input("Reheat Stages", 0, 10, cycle_definition.get('defaults', {}).get('n_rh', 1))
        params['n_fwh'] = st.number_input("Feedwater Heaters", 0, 10, cycle_definition.get('defaults', {}).get('n_fwh', 2))
    elif selected_cycle_key == 'brayton':
        params['n_ic'] = st.number_input("Intercooler Stages", 0, 5, cycle_definition.get('defaults', {}).get('n_ic', 1))
        params['n_rh'] = st.number_input("Reheat Stages", 0, 5, cycle_definition.get('defaults', {}).get('n_rh', 0))
    elif selected_cycle_key == 'sco2':
        params['split_frac'] = st.slider("Split Fraction", 0.05, 0.60, 0.35)
        params['recup_eff'] = st.slider("Recup Effectiveness", 0.5, 0.99, 0.95)
    
    with st.expander("ℹ️ Help & Documentation"):
        st.markdown("""
        **Getting Started**
        1. Select a **Cycle Architecture**.
        2. Pick **TWO** independent variables.
        3. Click **RUN ANALYSIS**.
        """)
    
    st.markdown("---")
    execute_btn = st.button("🚀 RUN ANALYSIS", type="primary", disabled=solve_disabled)

# --- MAIN CONTENT ---
st.markdown(
    f"""
    <div class="hero-section">
        <h1 class="hero-title">{cycle_definition.get('name', selected_cycle_key.title())}</h1>
        <p class="hero-subtitle">High-fidelity thermodynamic simulation and performance analysis.</p>
    </div>
    """,
    unsafe_allow_html=True
)

if execute_btn:
    try:
        cycle_factory = {
            'rankine': RankineCycle,
            'sco2': sCO2Cycle,
            'brayton': BraytonCycle,
            'otto': OttoCycle,
            'diesel': DieselCycle,
            'stirling': StirlingCycle,
            'ericsson': EricssonCycle,
        }
        
        cycle_cls = cycle_factory.get(selected_cycle_key)
        cycle_obj = cycle_cls() if selected_cycle_key == 'sco2' else cycle_cls(fluid)
        
        with st.spinner("Processing thermodynamic states..."):
            states = cycle_obj.solve_with_targets(params)
            metrics = cycle_obj.calculate_performance()

        # Metrics Row
        st.markdown("### 🏁 Performance Dashboard")
        c1, c2, c3, c4 = st.columns(4)
        eff = metrics.get('efficiency', 0.0)
        c1.metric("Thermal Efficiency", f"{eff:.2f}%", f"{eff-42:.1f}% vs Target")
        c2.metric("2nd Law Eff.", f"{metrics.get('second_law_efficiency', 0.0):.1f}%")
        c3.metric("Net Work Output", f"{metrics.get('w_net', 0.0):.1f} kJ/kg")
        c4.metric("Entropy Gen", f"{metrics.get('s_gen', 0.0):.4f} J/kg·K")

        # Visualization Tabs
        st.markdown("---")
        t1, t2, t3 = st.tabs(["🏗️ Schematic", "📈 T-s Diagram", "📉 P-v Diagram"])
        
        with t1:
            svg_buf = FlowChartGenerator.create_diagram(cycle_definition.get('name', selected_cycle_key.title()), cycle_obj.get_component_list(), states, metrics)
            b64 = base64.b64encode(svg_buf.getvalue()).decode('utf-8')
            st.markdown(f'<div style="background-color: white; padding: 20px; border-radius: 12px; display: flex; justify-content: center;"><img src="data:image/svg+xml;base64,{b64}" style="max-width: 100%; height: auto;"/></div>', unsafe_allow_html=True)

        with t2:
            st.plotly_chart(TSDiagram.create_plot(states, cycle_definition.get('name', selected_cycle_key.title()), fluid), use_container_width=True)
        
        with t3:
            st.plotly_chart(PVDiagram.create_plot(states, cycle_definition.get('name', selected_cycle_key.title()), fluid), use_container_width=True)

        # State Point Table
        st.markdown("---")
        st.markdown("### 📝 Detailed State Point Analytics")
        state_rows = []
        for sid, st_obj in states.items():
            row = st_obj.to_dict()
            row['Point'] = sid
            row['T (°C)'] = f"{row['T'] - 273.15:.2f}"
            row['P (MPa)'] = f"{row['P'] / 1e6:.3f}"
            row['h (kJ/kg)'] = f"{row['h'] / 1000:.1f}"
            row['s (kJ/kg·K)'] = f"{row['s'] / 1000:.3f}"
            state_rows.append(row)
        st.dataframe(state_rows, use_container_width=True)

    except Exception as exc:
        logger.exception("Cycle execution failed")
        st.error(f"Solver Failure: {exc}")
else:
    st.info("💡 Define your cycle constraints in the sidebar and click **RUN ANALYSIS** to begin.")
    st.markdown(
        f"""
        <div style="background-color: {CARD_DARK}; padding: 30px; border-radius: 12px; border: 1px solid {BORDER_DARK}; text-align: center;">
            <p style="color: {TEXT_DIM}; font-size: 1.2rem;">Ready for simulation. Select a cycle architecture to view theoretical schematics.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
