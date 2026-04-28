# Flowchart Fix Instructions

## Problem Description
The current flowchart implementation in `visualization/flow_charts.py` does not properly adapt to different cycle types. It attempts to infer components from state property changes (e.g., pressure increase → compressor), but this leads to inaccurate or generic diagrams that don't reflect the specific cycle architecture. Additionally, the state points are not clearly correlated with the thermodynamic diagrams (T-S and P-V), and the styling is basic.

## Goals
1. **Cycle-Specific Diagrams**: The flowchart should change based on the selected cycle, using the `component_list` from `cycle_obj.get_component_list()` to draw appropriate components.
2. **State Point Correlation**: State points should be clearly labeled and positioned to align with the T-S and P-V diagrams for easy cross-referencing.
3. **Improved Styling**: Enhance visual appeal with better colors, fonts, layouts, and professional engineering standards.

## Steps to Fix

### 1. Update `FlowChartGenerator.create_diagram` Method
- **Input Parameters**: The method receives `cycle_type`, `component_list`, and `states`. Currently, `component_list` is ignored.
- **Use `component_list`**: Instead of inferring components from state changes, map the `component_list` to specific drawing functions.
  - Define a mapping from component names to drawing methods (e.g., "Turbine" → `draw_turbine`, "Compressor" → `draw_compressor`).
  - Position components sequentially around the diagram based on the list order.
- **State Point Positioning**: Use the same state keys as in the T-S and P-V diagrams. Position state points at the inlet/outlet of each component.
  - For each component in `component_list`, assign inlet and outlet states from `states`.
  - Ensure the layout is clockwise or standard engineering flow (e.g., heat addition → expansion → heat rejection → compression).

### 2. Component Mapping
Create a dictionary in `FlowChartGenerator` to map component names to drawing functions:
```python
COMPONENT_DRAWERS = {
    "Turbine": draw_turbine,
    "Compressor": draw_compressor,
    "Pump": draw_pump,
    "Boiler": lambda ax, x, y: draw_exchanger(ax, x, y, "BOILER", "#ffebee"),
    "Condenser": lambda ax, x, y: draw_exchanger(ax, x, y, "CONDENSER", "#e3f2fd"),
    "Heat Exchanger": lambda ax, x, y: draw_exchanger(ax, x, y, "HX", "#fff8e1"),
    # Add more as needed for each cycle
}
```
- For each cycle, ensure `get_component_list()` returns standardized names that match this mapping.

### 3. Layout Logic
- **Sequential Layout**: Instead of elliptical positioning, use a linear or rectangular layout where components are placed in order.
  - Example: Heat addition (left), Expansion (top), Heat rejection (right), Compression (bottom).
- **State Anchors**: Draw circles at state points with labels matching the state IDs (e.g., 1, 2, 3...).
- **Flow Arrows**: Draw arrows between consecutive states, colored by phase.

### 4. Correlation with Diagrams
- **Consistent Labeling**: Use the same state IDs in the flowchart as in T-S and P-V plots.
- **Tooltip or Hover**: If possible, add tooltips showing state properties (T, P, h, s).
- **Alignment**: Position the flowchart so that state 1 is at the bottom-left, matching typical cycle diagrams.

### 5. Styling Improvements
- **Colors**:
  - Use a professional color palette: Blues for cold/liquid, Reds for hot/vapor, Purples for supercritical.
  - Background: Light gray or white.
  - Components: Subtle fills with dark borders.
- **Fonts**: Use sans-serif fonts like Arial or Helvetica for readability. Bold for labels.
- **Sizing**: Increase figure size for better resolution. Use DPI=200 for crisp output.
- **Legend**: Expand the legend to include component types and phase colors.
- **Grid/Background**: Add a subtle grid or background pattern for engineering feel.
- **Arrows**: Use consistent arrow styles with phase-based coloring.

### 6. Testing and Validation
- **Per Cycle Testing**: Run the app for each cycle (Rankine, Brayton, sCO2, etc.) and verify the flowchart matches the expected components.
- **State Correlation**: Check that state points in the flowchart correspond to those in T-S and P-V diagrams.
- **Performance**: Ensure the SVG generation is fast and the output is scalable.

### 7. Additional Enhancements
- **Dynamic Scaling**: Adjust diagram size based on the number of components.
- **Error Handling**: If a component in `component_list` is not in `COMPONENT_DRAWERS`, log a warning and skip or use a default.
- **Config-Driven**: Optionally, load component drawings from a config file for extensibility.

## Files to Modify
- `visualization/flow_charts.py`: Main logic update.
- `core/base_cycle.py` or specific cycle files: Ensure `get_component_list()` returns accurate, standardized component names.
- `gui/app.py`: No changes needed, as it already passes the required parameters.

## Styling Guide for Flowcharts

To enhance the visual appeal and professionalism of the flowcharts, follow these guidelines:

### Color Palette
- **Background**: Use a light, neutral color like `#f9f9f9` or `#ffffff` for the figure background to avoid harsh whites.
- **Components**:
  - Compressors/Pumps: Light gray fill (`#f5f5f5`) with dark borders (`#333333`).
  - Turbines: Similar to compressors, with work arrows in black.
  - Heat Exchangers: Varied soft colors (e.g., `#ffebee` for boilers, `#e3f2fd` for condensers) to differentiate types.
- **Phase Colors**:
  - Liquid: Blue (`#0055cc`)
  - Vapor/Steam: Red (`#cc2200`)
  - Supercritical: Purple (`#9900cc`)
  - Two-Phase: Orange (`#ff7f0e`)
- **Text**: Dark gray (`#333333`) for readability.

### Fonts and Typography
- **Font Family**: Use sans-serif fonts like 'DejaVu Sans' or 'Arial' for modern, clean look.
- **Sizes**:
  - Title: 14pt, bold.
  - Component Labels: 8pt, bold.
  - State Labels: 9pt, bold.
  - Legend: 8-10pt.
- **Colors**: Black or dark gray for text to ensure contrast.

### Layout and Spacing
- **Figure Size**: 14x8 inches for better detail, DPI=200 for crisp output.
- **Component Positioning**: Use circular or elliptical layouts for cycles, ensuring even spacing.
- **State Points**: Circles with radius 2.5, white fill, dark border. Position them at logical flow points (e.g., component inlets/outlets).
- **Arrows**: Thick lines (lw=3) with phase-based colors, arrowheads for direction.

### Legend and Annotations
- **Legend Placement**: Bottom-right corner, with clear labels for phases.
- **Additional Elements**: Include a title at the top, and perhaps a scale or note if needed.
- **Z-Order**: Ensure state points (zorder=5) are above components and arrows.

### Best Practices
- **Consistency**: Match colors and styles with the T-S and P-V diagrams for coherence.
- **Scalability**: Use vector formats (SVG) for web display.
- **Accessibility**: High contrast for colors, clear labels.
- **Performance**: Optimize drawing to avoid slow rendering for complex cycles.

### Example Code Snippets
```python
# Set figure properties
fig, ax = plt.subplots(figsize=(14, 8), dpi=200, facecolor='#f9f9f9')
ax.set_xlim(0, 100)
ax.set_ylim(0, 60)
ax.axis('off')

# Draw components with consistent styling
# ... (as in the updated code)
```

This styling guide ensures the flowcharts are not only functional but also visually engaging and professional.