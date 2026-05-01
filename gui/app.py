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
import plotly.graph_objects as go
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
        
        html, body {{
            font-family: 'Inter', sans-serif;
            color: {TEXT_LIGHT};
        }}

        /* Streamlit components - be selective */
        [class*="st-"] {{
            color: {TEXT_LIGHT};
        }}

        .stApp {{
            background-color: {BG_DARK};
        }}

        .main {{
            background-color: {BG_DARK};
        }}

        :root {{
            color-scheme: dark;
            background-color: {BG_DARK};
        }}

        /* Specific input styling - avoid global selectors */
        .stNumberInput input,
        .stTextInput input,
        .stTextArea textarea,
        .stSelectbox select {{
            background-color: {CARD_DARK} !important;
            color: {TEXT_LIGHT} !important;
            border: 1px solid {BORDER_DARK} !important;
            border-radius: 12px !important;
            padding: 8px 12px !important;
            font-size: 14px !important;
            line-height: 1.4 !important;
            min-height: 20px !important;
            overflow: hidden !important;
            text-overflow: ellipsis !important;
            white-space: nowrap !important;
        }}

        .stNumberInput input:focus,
        .stTextInput input:focus,
        .stTextArea textarea:focus,
        .stSelectbox select:focus {{
            outline: 2px solid {ACCENT_CYAN} !important;
            outline-offset: 1px !important;
            box-shadow: 0 0 0 4px rgba(56, 189, 248, 0.16) !important;
            border-color: {ACCENT_CYAN} !important;
        }}

        /* Fix textarea multi-line */
        .stTextArea textarea {{
            white-space: pre-wrap !important;
            resize: vertical !important;
            min-height: 80px !important;
        }}

        /* Fix select dropdown arrow */
        .stSelectbox select {{
            appearance: auto !important;
            background-image: none !important;
            padding-right: 30px !important;
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
        
        /* Fix navbar and icon issues */
        .stApp header {{
            background-color: {BG_DARK} !important;
        }}

        /* Don't apply custom font to icons and special elements */
        .stApp header *,
        button svg,
        .stApp [data-testid*="icon"],
        .stApp [data-testid*="arrow"],
        .stApp [class*="icon"] {{
            font-family: inherit !important;
        }}

        /* Fix double arrow display */
        .stApp [data-testid="stSidebarNav"] button,
        .stApp header button {{
            font-family: inherit !important;
        }}

        /* Ensure icons remain visible */
        .stApp svg {{
            fill: currentColor !important;
        }}
        
        /* Slider styling */
        .stSidebar .stSlider div[data-baseweb="slider"] {{
            background-color: {CARD_DARK} !important;
        }}

        .stSidebar .stSlider [data-testid="stThumbValue"] {{
            background-color: {ACCENT_CYAN} !important;
            color: {BG_DARK} !important;
            font-weight: 600 !important;
        }}

        /* Fix text overflow in inputs */
        .stNumberInput input,
        .stTextInput input {{
            overflow: hidden !important;
            text-overflow: ellipsis !important;
            white-space: nowrap !important;
        }}

        /* Ensure proper spacing in sidebar */
        .stSidebar .stNumberInput,
        .stSidebar .stTextInput,
        .stSidebar .stSelectbox,
        .stSidebar .stMultiselect {{
            margin-bottom: 8px !important;
        }}

        /* Fix expander styling */
        .stSidebar .streamlit-expanderHeader {{
            background-color: {CARD_DARK} !important;
            border: 1px solid {BORDER_DARK} !important;
            border-radius: 8px !important;
            color: {TEXT_LIGHT} !important;
        }}

        .stSidebar .streamlit-expanderHeader:hover {{
            background-color: rgba(56, 189, 248, 0.08) !important;
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
            border-radius: 12px !important;
            border: 1px solid rgba(56, 189, 248, 0.4) !important;
            padding: 0.75rem 1.3rem !important;
            font-weight: 700 !important;
            transition: all 0.2s ease !important;
            width: 100%;
            box-shadow: 0 18px 38px rgba(56, 189, 248, 0.14) !important;
        }}
        
        .stButton>button:hover {{
            background-color: {ACCENT_AMBER} !important;
            color: {BG_DARK} !important;
            transform: translateY(-1px) scale(1.01);
            border-color: rgba(251, 180, 36, 0.5) !important;
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
            background-color: {CARD_DARK};
            border: 1px solid {BORDER_DARK};
            border-radius: 12px 12px 0 0;
            box-shadow: inset 0 0 0 1px rgba(255,255,255,0.05);
            padding: 6px;
        }}

        .stTabs [data-baseweb="tab"] {{
            height: 48px;
            white-space: pre-wrap;
            background-color: {CARD_DARK};
            border-radius: 8px 8px 0px 0px;
            gap: 1px;
            padding-top: 10px;
            padding-bottom: 10px;
            color: {TEXT_DIM};
            border: 1px solid transparent;
            transition: all 0.2s ease;
        }}

        .stTabs [data-baseweb="tab"]:hover {{
            background-color: rgba(56, 189, 248, 0.08);
        }}

        .stTabs [aria-selected="true"] {{
            color: {ACCENT_CYAN} !important;
            border-bottom-color: {ACCENT_CYAN} !important;
            background-color: {BG_DARK};
            box-shadow: inset 0 -3px 0 0 {ACCENT_CYAN};
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
        t1, t2, t3, t4 = st.tabs(["🏗️ Schematic", "📈 T-s Diagram", "📉 P-v Diagram", "⚡ Efficiency"])
        
        with t1:
            svg_buf = FlowChartGenerator.create_diagram(cycle_definition.get('name', selected_cycle_key.title()), cycle_obj.get_component_list(), states, metrics)
            b64 = base64.b64encode(svg_buf.getvalue()).decode('utf-8')
            st.markdown(f'<div style="background-color: {CARD_DARK}; padding: 24px; border-radius: 18px; display: flex; justify-content: center; border: 1px solid {BORDER_DARK}; box-shadow: 0 18px 40px rgba(0, 0, 0, 0.32); outline: 1px solid rgba(56, 189, 248, 0.12);"><img src="data:image/svg+xml;base64,{b64}" style="max-width: 100%; height: auto;"/></div>', unsafe_allow_html=True)

        with t2:
            st.plotly_chart(TSDiagram.create_plot(states, cycle_definition.get('name', selected_cycle_key.title()), fluid), use_container_width=True)
        
        with t3:
            st.plotly_chart(PVDiagram.create_plot(states, cycle_definition.get('name', selected_cycle_key.title()), fluid), use_container_width=True)

        with t4:
            st.markdown("### ⚡ Efficiency Breakdown")
            eff_type = st.radio(
                "Select efficiency type:",
                ["Thermal Efficiency", "Second Law Efficiency"],
                index=0,
                horizontal=True,
            )

            q_in = metrics.get('q_in', 0.0)
            q_out = metrics.get('q_out', 0.0)
            w_net = metrics.get('w_net', 0.0)
            thermal_eff = metrics.get('efficiency', 0.0)
            second_eff = metrics.get('second_law_efficiency', 0.0)

            if eff_type == "Thermal Efficiency":
                st.markdown(
                    fr"""
                    **Formula:** thermal efficiency = $\frac{{W_{{net}}}}{{Q_{{in}}}} \times 100\%$  
                    **Values:** $W_{{net}} = {w_net:.1f}\ \text{{kJ/kg}}$, $Q_{{in}} = {q_in:.1f}\ \text{{kJ/kg}}$  
                    **Result:** $\eta = {thermal_eff:.1f}\%$  
                    """,
                    unsafe_allow_html=True,
                )
                fig = go.Figure(
                    data=[
                        go.Bar(name='Useful Work', x=['Energy Flow'], y=[w_net], marker_color='#38bdf8', hovertemplate='W_net: %{y:.1f} kJ/kg'),
                        go.Bar(name='Rejected Heat', x=['Energy Flow'], y=[q_out], marker_color='#ffb703', hovertemplate='Q_out: %{y:.1f} kJ/kg'),
                    ]
                )
                fig.update_layout(
                    barmode='stack',
                    plot_bgcolor=BG_DARK,
                    paper_bgcolor=BG_DARK,
                    font_color=TEXT_LIGHT,
                    title='Energy balance for thermal efficiency',
                    xaxis_title='',
                    yaxis_title='kJ/kg',
                    legend_title_text='',
                )
                st.plotly_chart(fig, use_container_width=True)

            else:
                st.markdown(
                    fr"""
                    **Formula:** second law efficiency compares actual output to the ideal reversible limit.  
                    **Result:** {second_eff:.1f}\%  
                    """,
                    unsafe_allow_html=True,
                )
                st.info(
                    "Second Law Efficiency indicates how closely the cycle approaches the theoretical maximum work available under the same heat inputs."
                )

            with st.expander("How efficiency is calculated"):
                st.markdown(
                    f"""
                    - **Heat input** $Q_{{in}}$ is the total thermal energy added to the cycle.  
                    - **Work output** $W_{{net}}$ is the useful shaft work after subtracting pump and compressor losses.  
                    - **Rejected heat** $Q_{{out}} = Q_{{in}} - W_{{net}}$.  
                    - **Thermal efficiency** is the ratio of useful work to heat input, showing how effectively the cycle converts heat into work.  
                    - **Second law efficiency** is an advanced performance metric that includes irreversibilities and how far the cycle is from an ideal reversible process.
                    """,
                    unsafe_allow_html=True,
                )

            st.markdown("---")

        # State Point Table
        st.markdown("---")
        st.markdown("### 📝 Detailed State Point Analytics")

        temp_unit = col1 = col2 = col3 = col4 = None
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            temp_unit = st.selectbox("Temperature units", ["°C", "K", "°F"], index=0)
        with c2:
            press_unit = st.selectbox("Pressure units", ["MPa", "bar", "kPa"], index=0)
        with c3:
            enth_unit = st.selectbox("Enthalpy units", ["kJ/kg", "MJ/kg", "J/kg"], index=0)
        with c4:
            entro_unit = st.selectbox("Entropy units", ["kJ/kg·K", "J/kg·K"], index=0)

        def format_temperature(value, unit):
            if value is None:
                return ""
            if unit == "K":
                return f"{value:.2f}"
            if unit == "°F":
                return f"{(value - 273.15) * 9/5 + 32:.2f}"
            return f"{value - 273.15:.2f}"

        def format_pressure(value, unit):
            if value is None:
                return ""
            if unit == "bar":
                return f"{value / 1e5:.3f}"
            if unit == "kPa":
                return f"{value / 1e3:.1f}"
            return f"{value / 1e6:.3f}"

        def format_enthalpy(value, unit):
            if value is None:
                return ""
            if unit == "MJ/kg":
                return f"{value / 1e6:.3f}"
            if unit == "J/kg":
                return f"{value:.0f}"
            return f"{value / 1000:.1f}"

        def format_entropy(value, unit):
            if value is None:
                return ""
            if unit == "J/kg·K":
                return f"{value:.3f}"
            return f"{value / 1000:.3f}"

        headers = [
            ("Point", "State point number in the cycle sequence."),
            (f"T ({temp_unit})", "Temperature at the state point, describing heat level."),
            (f"P ({press_unit})", "Pressure at the state point, defining fluid compression."),
            (f"h ({enth_unit})", "Specific enthalpy indicates energy content per unit mass."),
            (f"s ({entro_unit})", "Specific entropy measures disorder and irreversibility."),
        ]

        row_tooltips = {
            "Point": "The sequential state number around the thermodynamic cycle.",
            "Temperature": "Temperature shows how hot or cold the working fluid is at this state.",
            "Pressure": "Pressure is the mechanical force per area in the working fluid.",
            "Enthalpy": "Enthalpy is the energy content per kilogram of fluid.",
            "Entropy": "Entropy is a measure of energy unavailable for work at this state.",
        }

        table_html = [
            f'<div style="overflow-x:auto; margin-top:1rem; border:1px solid {BORDER_DARK}; border-radius:14px; background:{CARD_DARK}; padding:12px;">',
            '<table style="width:100%; border-collapse: collapse; font-family: Inter, sans-serif; color: {TEXT_LIGHT};">'.replace('{TEXT_LIGHT}', TEXT_LIGHT),
            '<thead><tr>'
        ]

        for label, tooltip in headers:
            table_html.append(
                f'<th title="{tooltip}" style="text-align:left; padding:12px 14px; border-bottom:1px solid {BORDER_DARK}; font-size:0.95rem; color:{TEXT_LIGHT}; background:rgba(255,255,255,0.02);">{label}</th>'
            )
        table_html.append('</tr></thead><tbody>')

        for sid, st_obj in states.items():
            table_html.append('<tr>')
            table_html.append(f'<td title="{row_tooltips["Point"]}" style="padding:12px 14px; border-bottom:1px solid {BORDER_DARK};">{sid}</td>')
            table_html.append(
                f'<td title="{row_tooltips["Temperature"]}" style="padding:12px 14px; border-bottom:1px solid {BORDER_DARK};">{format_temperature(st_obj.T, temp_unit)}</td>'
            )
            table_html.append(
                f'<td title="{row_tooltips["Pressure"]}" style="padding:12px 14px; border-bottom:1px solid {BORDER_DARK};">{format_pressure(st_obj.P, press_unit)}</td>'
            )
            table_html.append(
                f'<td title="{row_tooltips["Enthalpy"]}" style="padding:12px 14px; border-bottom:1px solid {BORDER_DARK};">{format_enthalpy(st_obj.h, enth_unit)}</td>'
            )
            table_html.append(
                f'<td title="{row_tooltips["Entropy"]}" style="padding:12px 14px; border-bottom:1px solid {BORDER_DARK};">{format_entropy(st_obj.s, entro_unit)}</td>'
            )
            table_html.append('</tr>')

        table_html.append('</tbody></table></div>')
        st.markdown(''.join(table_html), unsafe_allow_html=True)

    except Exception as exc:
        logger.exception("Cycle execution failed")
        st.error(f"Solver Failure: {exc}")
else:
    st.info("💡 Define your cycle constraints in the sidebar and click **RUN ANALYSIS** to begin.")
    st.markdown(
        f"""
        <div style="background-color: {CARD_DARK}; padding: 34px; border-radius: 18px; border: 1px solid {BORDER_DARK}; text-align: center; box-shadow: 0 16px 36px rgba(0, 0, 0, 0.28); outline: 1px solid rgba(56, 189, 248, 0.12);">
            <p style="color: {TEXT_DIM}; font-size: 1.2rem; margin: 0;">Ready for simulation. Select a cycle architecture to view theoretical schematics.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
