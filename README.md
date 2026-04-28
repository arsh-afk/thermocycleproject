# Thermodynamic Cycle Project

ThermoCycleProject is an educational engineering toolkit for analyzing and visualizing thermodynamic power cycles. The repository includes core cycle solvers, property wrapper utilities, interactive visualization, and a Streamlit-based UI.

## Features
- Cycle solvers for Rankine, Brayton, sCO2, Otto, Diesel, Stirling, and Ericsson configurations.
- CoolProp-backed thermodynamic state calculation.
- Interactive plots for T-s and P-v diagrams.
- Config-driven cycle and fluid selection.
- Basic validation and benchmark data for trusted comparison.

## Getting Started

### Install dependencies
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

> Note: `requirements.txt` now includes `matplotlib`, which is required for the flow chart visualization.

### Run the Streamlit app
```bash
cd /workspaces/thermocycleproject
python -m streamlit run gui/app.py
```

### Run tests
```bash
pytest -q
```

## Package installation
Install the project in editable mode for development:
```bash
pip install -e .
```

## Project structure
- `core/` - Cycle models, solver utilities, and component definitions.
- `utils/` - Property wrapper and helper utilities.
- `config/` - YAML-driven cycle, fluid, and heat source metadata.
- `gui/` - Streamlit application interface.
- `visualization/` - Plot and PFD generation logic.
- `analysis/` - Higher-level economic and exergy analysis modules.
- `validation/` - Benchmark data and validation resources.
- `tests/` - Unit test suite.

## Notes
- The UI validates cycle inputs and uses configuration metadata wherever possible.
- The app currently supports `CO2` for sCO2, and non-condensable gases for Brayton cycle variants.

## Contributing
1. Create a feature branch.
2. Add or update tests for new code.
3. Run `pytest -q` before opening a pull request.
