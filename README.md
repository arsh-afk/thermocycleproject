# Thermodynamic Cycle Explorer Pro 2.0

## 🚀 How to Run
Streamlit applications cannot be run like standard Python scripts. You must use the Streamlit runner:

1. **Open your terminal** in the `thermo_cycle_calc` directory.
2. **Execute the following command:**
   ```powershell
   python -m streamlit run gui/app.py
   ```
   *(If you are using a specific Python version, use: `C:/Python314/python.exe -m streamlit run gui/app.py`)*

## 📐 The Two-Variable Rule (Gibbs Phase Rule)
This tool strictly follows thermodynamic laws. For any cycle, you must specify **exactly TWO** independent variables (e.g., $P_{max}$ and $T_{max}$). 

- Use the **checkboxes** in the sidebar to select which two variables you want to control.
- Once exactly two are checked, the **EXECUTE SIMULATION** button will become active.
- All other variables will be automatically calculated based on your specifications and fluid physics.

## 🧪 Simulation Features
- **Spatially Accurate PFDs:** Flow charts that match real plant topology.
- **CoolProp Integration:** Real gas properties for 10+ working fluids.
- **N-Component Scalability:** Up to 10 stages of reheating/intercooling.
- **Target Tracking:** Real-time feedback on the **≥42% efficiency target**.
