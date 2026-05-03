"""
Thermodynamic Cycle Calculator Pro v3.1 — Merged Edition
AURAK Project 2026 Educational Tool

Merges:
  - New version: template-based sidebar, 🎲 randomizer, interactive state editor
  - Old version: P-V diagram tab, efficiency breakdown tab, unit-selector state table,
                 full cycle factory (Otto, Diesel, Stirling, Ericsson, sCO2, Refrigeration, Combined),
                 rich CSS (hover cards, animated tabs, button glow)
"""
import base64
import logging
import os
import sys
import random

import plotly.graph_objects as go
import streamlit as st
import yaml
import pandas as pd

root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_path not in sys.path:
    sys.path.append(root_path)

from core.rankine_cycle import RankineCycle
from core.brayton_cycle import BraytonCycle
from core.sco2_cycle import sCO2Cycle
from core.otto_cycle import OttoCycle
from core.diesel_cycle import DieselCycle
from core.stirling_cycle import StirlingCycle
from core.ericsson_cycle import EricssonCycle
from core.refrigeration_cycle import RefrigerationCycle
from core.combined_cycle import CombinedCycle
from visualization.flow_charts import FlowChartGenerator
from visualization.ts_diagram import TSDiagram
from visualization.pv_diagram import PVDiagram
from utils.helpers import EESGenerator

logger = logging.getLogger(__name__)

# --- PAGE CONFIG ---
st.set_page_config(page_title="Thermo Cycle Explorer Pro", page_icon="🔥", layout="wide")

BG_DARK = "#0f172a"
CARD_DARK = "#1e293b"
ACCENT_CYAN = "#38bdf8"
ACCENT_AMBER = "#fbbf24"
TEXT_LIGHT = "#f8fafc"
TEXT_DIM = "#94a3b8"
BORDER_DARK = "#334155"

st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Roboto+Mono&display=swap');
        html, body {{ font-family: 'Inter', sans-serif; color: {TEXT_LIGHT}; }}
        .stApp {{ background-color: {BG_DARK}; }}
        :root {{ color-scheme: dark; background-color: {BG_DARK}; }}
        .stNumberInput input, .stTextInput input, .stSelectbox select {{
            background-color: {CARD_DARK} !important; color: {TEXT_LIGHT} !important;
            border: 1px solid {BORDER_DARK} !important; border-radius: 12px !important;
            font-size: 14px !important;
        }}
        .stNumberInput input:focus, .stSelectbox select:focus {{
            outline: 2px solid {ACCENT_CYAN} !important;
            box-shadow: 0 0 0 4px rgba(56, 189, 248, 0.16) !important;
        }}
        div[data-testid="stMetric"] {{
            background-color: {CARD_DARK}; padding: 20px; border-radius: 12px;
            border: 1px solid {BORDER_DARK}; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.2);
            transition: all 0.2s ease;
        }}
        div[data-testid="stMetric"]:hover {{
            transform: translateY(-2px); border-color: {ACCENT_CYAN};
            box-shadow: 0 10px 15px -3px rgba(0,0,0,0.4);
        }}
        div[data-testid="stMetricValue"] {{ color: {ACCENT_CYAN} !important; font-size: 1.8rem; font-weight: 700; }}
        div[data-testid="stMetricLabel"] {{ color: {TEXT_DIM} !important; font-size: 0.8rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.1em; }}
        .stApp header {{ background-color: {BG_DARK} !important; }}
        h1, h2, h3, h4 {{ color: {TEXT_LIGHT}; font-weight: 700; letter-spacing: -0.02em; }}
        .hero-section {{
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
            padding: 2.5rem 2rem; border-radius: 16px; border: 1px solid {BORDER_DARK};
            margin-bottom: 2rem; position: relative; overflow: hidden;
        }}
        .hero-section::after {{
            content: ""; position: absolute; top: 0; right: 0; bottom: 0; left: 0;
            background-image: radial-gradient(circle at 2px 2px, rgba(56,189,248,0.05) 1px, transparent 0);
            background-size: 24px 24px;
        }}
        .hero-title {{ font-size: 2.2rem; margin: 0; color: {TEXT_LIGHT} !important; }}
        .hero-subtitle {{ font-size: 1rem; color: {TEXT_DIM}; margin-top: 0.5rem; }}
        .stButton>button {{
            background-color: {ACCENT_CYAN} !important; color: {BG_DARK} !important;
            border-radius: 12px !important; border: 1px solid rgba(56,189,248,0.4) !important;
            padding: 0.75rem 1.3rem !important; font-weight: 700 !important;
            transition: all 0.2s ease !important; width: 100%;
            box-shadow: 0 18px 38px rgba(56,189,248,0.14) !important;
        }}
        .stButton>button:hover {{
            background-color: {ACCENT_AMBER} !important; color: {BG_DARK} !important;
            transform: translateY(-1px) scale(1.01); border-color: rgba(251,180,36,0.5) !important;
        }}
        .stTabs [data-baseweb="tab-list"] {{
            gap: 24px; background-color: {CARD_DARK}; border: 1px solid {BORDER_DARK};
            border-radius: 12px 12px 0 0; padding: 6px;
        }}
        .stTabs [data-baseweb="tab"] {{
            height: 48px; background-color: {CARD_DARK}; border-radius: 8px 8px 0 0;
            color: {TEXT_DIM}; border: 1px solid transparent; transition: all 0.2s ease;
        }}
        .stTabs [data-baseweb="tab"]:hover {{ background-color: rgba(56,189,248,0.08); }}
        .stTabs [aria-selected="true"] {{
            color: {ACCENT_CYAN} !important; background-color: {BG_DARK};
            box-shadow: inset 0 -3px 0 0 {ACCENT_CYAN};
        }}
        code, .mono {{ font-family: 'Roboto Mono', monospace !important; color: {ACCENT_AMBER}; }}
        hr {{ border-color: {BORDER_DARK} !important; }}
    </style>
""", unsafe_allow_html=True)


@st.cache_data
def load_config():
    with open(os.path.join(root_path, "config", "cycles.yaml"), "r", encoding="utf-8") as h:
        return yaml.safe_load(h)

cfg = load_config()

# --- CYCLE FACTORY ---
CYCLE_FACTORY = {
    'rankine_basic':           (RankineCycle, 'Water'),
    'rankine_reheat':          (RankineCycle, 'Water'),
    'rankine_open_fwh':        (RankineCycle, 'Water'),
    'brayton_simple':          (BraytonCycle, 'Air'),
    'brayton_regen':           (BraytonCycle, 'Air'),
    'sco2_recompression':      (sCO2Cycle,    None),
    'otto_standard':           (OttoCycle,    'Air'),
    'diesel_standard':         (DieselCycle,  'Air'),
    'stirling_standard':       (StirlingCycle,'Air'),
    'ericsson_standard':       (EricssonCycle,'Air'),
    'refrigeration_ideal':     (RefrigerationCycle, 'R134a'),
    'combined_brayton_rankine':(CombinedCycle, None),
}

def randomize_param(template_key, param_key):
    spec = cfg[template_key]['required_inputs'][param_key]
    sk = f"in_{template_key}_{param_key}"
    if isinstance(spec['default'], int):
        st.session_state[sk] = random.randint(int(spec['min']), int(spec['max']))
    else:
        st.session_state[sk] = round(random.uniform(spec['min'], spec['max']), 2)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown(f"<h2 style='color:{ACCENT_CYAN};margin-bottom:0;'>THERMO</h2><h4 style='margin-top:0;color:{TEXT_DIM};'>Cycle Explorer Pro</h4>", unsafe_allow_html=True)
    st.markdown("---")

    categories = sorted(set(v['category'] for v in cfg.values()))
    selected_cat = st.selectbox("Cycle Category", options=categories)
    cat_templates = {k: v for k, v in cfg.items() if v['category'] == selected_cat}
    template_key = st.selectbox("Specific Template", options=list(cat_templates.keys()),
                                format_func=lambda x: cat_templates[x]['name'])
    template = cfg[template_key]

    st.markdown("### 📐 Required Inputs")
    params = {}
    for key, spec in template['required_inputs'].items():
        sk = f"in_{template_key}_{key}"
        if sk not in st.session_state:
            st.session_state[sk] = float(spec.get('default', 0.0))
        col1, col2 = st.columns([4, 1])
        with col1:
            params[key] = st.number_input(
                f"{spec['label']} ({spec['unit']})",
                min_value=float(spec['min']), max_value=float(spec['max']) * 2.0,
                key=sk
            )
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            st.button("🎲", key=f"dice_{sk}", help="Plausible Random Value",
                      on_click=randomize_param, args=(template_key, key))

    # Inject template key so solve(params) knows which sub-variant to use
    params['template'] = template_key

    execute_btn = st.button("🚀 RUN ANALYSIS", type="primary")

# --- HERO HEADER ---
arch = " → ".join(template.get("components", []))
st.markdown(f'<div class="hero-section"><h1 class="hero-title">{template["name"]}</h1><p class="hero-subtitle">Architecture: {arch}</p></div>', unsafe_allow_html=True)

# --- FORMAT HELPERS ---
def fmt_T(v, unit):
    if v is None: return ""
    if unit == "K": return f"{v:.2f}"
    if unit == "°F": return f"{(v-273.15)*9/5+32:.2f}"
    return f"{v-273.15:.2f}"

def fmt_P(v, unit):
    if v is None: return ""
    if unit == "bar": return f"{v/1e5:.3f}"
    if unit == "kPa": return f"{v/1e3:.1f}"
    return f"{v/1e6:.4f}"

def fmt_h(v, unit):
    if v is None: return ""
    if unit == "MJ/kg": return f"{v/1e6:.3f}"
    if unit == "J/kg": return f"{v:.0f}"
    return f"{v/1000:.2f}"

def fmt_s(v, unit):
    if v is None: return ""
    if unit == "J/kg·K": return f"{v:.3f}"
    return f"{v/1000:.4f}"

# --- MAIN EXECUTION ---
if execute_btn:
    st.session_state.run_analysis = True
    st.session_state.last_params = params.copy()

if st.session_state.get('run_analysis', False) and st.session_state.get('last_params') != params:
    st.session_state.run_analysis = False

if st.session_state.get('run_analysis', False) or 'override_states' in st.session_state:
    try:
        zeros = [spec['label'] for key, spec in template['required_inputs'].items()
                 if params.get(key, 0.0) == 0.0]
        if zeros and 'override_states' not in st.session_state:
            st.error(f"⚠️ Please provide valid inputs for: {', '.join(zeros)}. Use the 🎲 icons to quickly fill plausible data.")
        else:
            # Build cycle object
            cycle_cls, fluid = CYCLE_FACTORY.get(template_key, (None, None))
            if cycle_cls is None:
                st.error("Solver not yet available for this template.")
                st.stop()

            cycle_obj = cycle_cls() if fluid is None else cycle_cls(fluid)

            # Validation — normalize: some cycles return list[str], others return bool
            raw_errs = cycle_obj.validate_inputs(params)
            if isinstance(raw_errs, bool):
                errs = [] if raw_errs else getattr(cycle_obj, 'errors', ["Validation failed."])
            else:
                errs = list(raw_errs)
            if errs:
                for e in errs: st.error(f"❌ {e}")
                st.stop()

            if 'override_states' in st.session_state:
                # Initialize internal cycle parameters using original inputs first
                cycle_obj.solve(params)
                states = st.session_state.override_states
                cycle_obj.states = states
                metrics = cycle_obj.calculate_performance()
                st.warning("📊 Using manually edited state points.")
            else:
                if execute_btn or 'active_results' not in st.session_state:
                    with st.spinner("Solving thermodynamic states..."):
                        states = cycle_obj.solve(params)
                        metrics = cycle_obj.calculate_performance()
                        st.session_state.active_results = (states, metrics)
                else:
                    states, metrics = st.session_state.active_results

            # --- METRICS ROW ---
            st.markdown("### 🏁 Performance Dashboard")
            c1, c2, c3, c4 = st.columns(4)
            eff = metrics.get('efficiency', 0.0) or 0.0
            sl = metrics.get('second_law_efficiency', 0.0) or 0.0
            wn = metrics.get('w_net', 0.0) or 0.0
            sg = metrics.get('s_gen', metrics.get('x_dest', 0.0)) or 0.0
            c1.metric("Thermal Efficiency", f"{eff:.2f}%")
            c2.metric("2nd Law Efficiency", f"{sl:.1f}%")
            c3.metric("Net Work Output", f"{wn:.1f} kJ/kg")
            c4.metric("Entropy Gen / Exergy Dest", f"{sg:.4f}")

            # --- VISUALIZATIONS ---
            st.markdown("---")

            with st.container():
                st.markdown("### 🏗️ Schematic")
                try:
                    svg_buf = FlowChartGenerator.create_diagram(
                        template['name'], cycle_obj.get_component_list(), states, metrics)
                    b64 = base64.b64encode(svg_buf.getvalue()).decode()
                    st.markdown(f'<div style="background:{CARD_DARK};padding:24px;border-radius:18px;display:flex;justify-content:center;border:1px solid {BORDER_DARK};"><img src="data:image/svg+xml;base64,{b64}" style="max-width:100%;height:auto;"/></div>', unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Schematic error: {e}")

            st.markdown("---")
            with st.container():
                st.markdown("### 📈 T-s Diagram")
                try:
                    fig_ts = TSDiagram.create_plot(states, template['name'], fluid or 'CO2')
                    st.plotly_chart(fig_ts, use_container_width=True)
                except Exception as e:
                    st.warning(f"T-s diagram unavailable: {e}")

            st.markdown("---")
            with st.container():
                st.markdown("### 📉 P-v Diagram")
                try:
                    fig_pv = PVDiagram.create_plot(states, template['name'], fluid or 'CO2')
                    st.plotly_chart(fig_pv, use_container_width=True)
                except Exception as e:
                    st.warning(f"P-v diagram unavailable: {e}")

            st.markdown("---")
            with st.container():
                st.markdown("### ⚡ Efficiency Breakdown")
                q_in = metrics.get('q_in', 0.0) or 0.0
                q_out = metrics.get('q_out', q_in - wn)
                eff_type = st.radio("Select type:", ["Thermal Efficiency", "Second Law Efficiency"], horizontal=True)
                if eff_type == "Thermal Efficiency":
                    st.markdown(fr"""
                    **Formula:** $\eta = W_{{net}} / Q_{{in}} \times 100\%$  
                    **Values:** $W_{{net}} = {wn:.1f}\ \text{{kJ/kg}}$, $Q_{{in}} = {q_in:.1f}\ \text{{kJ/kg}}$  
                    **Result:** $\eta = {eff:.1f}\%$
                    """)
                    fig = go.Figure(data=[
                        go.Bar(name='Useful Work', x=['Energy Flow'], y=[wn], marker_color=ACCENT_CYAN),
                        go.Bar(name='Rejected Heat', x=['Energy Flow'], y=[q_out], marker_color=ACCENT_AMBER),
                    ])
                    fig.update_layout(barmode='stack', plot_bgcolor=BG_DARK, paper_bgcolor=BG_DARK,
                                      font_color=TEXT_LIGHT, title='Energy Balance', yaxis_title='kJ/kg')
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.markdown(f"**Second Law Efficiency** indicates how closely the cycle approaches the theoretical Carnot maximum.  \n**Result: {sl:.1f}%**")
                    st.info("A value of 100% would mean the cycle operates as a reversible Carnot engine between the same temperature limits.")

            st.markdown("---")
            with st.container():
                st.markdown("### 📝 State Points")
                # Unit selectors
                cu1, cu2, cu3, cu4 = st.columns(4)
                with cu1: temp_u = st.selectbox("Temperature", ["°C", "K", "°F"])
                with cu2: press_u = st.selectbox("Pressure", ["MPa", "bar", "kPa"])
                with cu3: enth_u = st.selectbox("Enthalpy", ["kJ/kg", "MJ/kg", "J/kg"])
                with cu4: entr_u = st.selectbox("Entropy", ["kJ/kg·K", "J/kg·K"])

                table_html = [
                    f'<div style="overflow-x:auto;margin-top:1rem;border:1px solid {BORDER_DARK};border-radius:14px;background:{CARD_DARK};padding:12px;">',
                    f'<table style="width:100%;border-collapse:collapse;color:{TEXT_LIGHT};">',
                    '<thead><tr>'
                ]
                for lbl in [f"Point", f"T ({temp_u})", f"P ({press_u})", f"h ({enth_u})", f"s ({entr_u})", "Phase", "Note"]:
                    table_html.append(f'<th style="text-align:left;padding:10px 14px;border-bottom:1px solid {BORDER_DARK};font-size:0.9rem;">{lbl}</th>')
                table_html.append('</tr></thead><tbody>')

                for sid, st_obj in states.items():
                    table_html.append('<tr>')
                    table_html.append(f'<td style="padding:10px 14px;border-bottom:1px solid {BORDER_DARK};">{sid}</td>')
                    table_html.append(f'<td style="padding:10px 14px;border-bottom:1px solid {BORDER_DARK};">{fmt_T(st_obj.T, temp_u)}</td>')
                    table_html.append(f'<td style="padding:10px 14px;border-bottom:1px solid {BORDER_DARK};">{fmt_P(st_obj.P, press_u)}</td>')
                    table_html.append(f'<td style="padding:10px 14px;border-bottom:1px solid {BORDER_DARK};">{fmt_h(st_obj.h, enth_u)}</td>')
                    table_html.append(f'<td style="padding:10px 14px;border-bottom:1px solid {BORDER_DARK};">{fmt_s(st_obj.s, entr_u)}</td>')
                    table_html.append(f'<td style="padding:10px 14px;border-bottom:1px solid {BORDER_DARK};">{getattr(st_obj,"phase_label","")}</td>')
                    table_html.append(f'<td style="padding:10px 14px;border-bottom:1px solid {BORDER_DARK};color:{TEXT_DIM};">{st_obj.note}</td>')
                    table_html.append('</tr>')

                table_html.append('</tbody></table></div>')
                st.markdown(''.join(table_html), unsafe_allow_html=True)

                st.markdown("---")
                st.markdown("#### ✏️ Interactive State Editor")
                data_rows = []
                for sid, st_obj in states.items():
                    data_rows.append({
                        "Point": sid, "T (K)": round(st_obj.T or 0, 2), "P (MPa)": round((st_obj.P or 0)/1e6, 4),
                        "h (kJ/kg)": round((st_obj.h or 0)/1000, 2), "s (kJ/kgK)": round((st_obj.s or 0)/1000, 4),
                        "Note": st_obj.note
                    })
                with st.form("editor_form"):
                    edited_df = st.data_editor(pd.DataFrame(data_rows), width='stretch',
                                               hide_index=True, disabled=["Point", "Note"])
                    if st.form_submit_button("🚀 RECALCULATE FROM TABLE"):
                        from core.state import ThermodynamicState
                        st.session_state.override_states = {
                            r["Point"]: ThermodynamicState(
                                T=r["T (K)"], P=r["P (MPa)"]*1e6, h=r["h (kJ/kg)"]*1000,
                                s=r["s (kJ/kgK)"]*1000, note=r["Note"], fluid=fluid or ""
                            ) for _, r in edited_df.iterrows()
                        }
                        st.rerun()
                if st.button("🧹 Reset Edits"):
                    if 'override_states' in st.session_state: del st.session_state.override_states
                    st.rerun()

    except Exception as exc:
        logger.exception("Cycle execution failed")
        st.error(f"❌ Solver Failure: {exc}")
else:
    st.info("💡 Pick a template and provide inputs in the sidebar, then click **🚀 RUN ANALYSIS**.")
    st.markdown(f"""
        <div style="background:{CARD_DARK};padding:34px;border-radius:18px;border:1px solid {BORDER_DARK};text-align:center;box-shadow:0 16px 36px rgba(0,0,0,0.28);">
            <p style="color:{TEXT_DIM};font-size:1.2rem;margin:0;">Ready for simulation. Select a cycle category and template to begin.</p>
        </div>
    """, unsafe_allow_html=True)
