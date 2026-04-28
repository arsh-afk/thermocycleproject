# Website Design Guide

## Goal
Create a modern, professional interface that feels like a thermodynamics engineering tool. The website should communicate scientific rigor while remaining approachable, with clear visuals, structured layouts, and a polished data-driven experience.

## Visual Tone
- **Modern Engineering**: Clean, high-contrast layouts with a cool palette, subtle gradients, and minimal clutter.
- **Scientific Confidence**: Use technical typography, iconography, and data-first presentation to reflect the precision of thermodynamic analysis.
- **Accessible and Inviting**: Keep navigation intuitive and controls clear to support both students and engineers.

## Color Palette
- **Primary Colors**:
  - Deep navy: `#0f1f3d`
  - Cool cyan: `#2ca8ff`
  - Warm amber: `#ffaa00`
- **Secondary Colors**:
  - Slate gray: `#4b5f7a`
  - Soft white: `#f8fbff`
  - Charcoal: `#1f2a38`
- **Status Colors**:
  - Success: `#22c55e`
  - Warning: `#f59e0b`
  - Error: `#ef4444`

## Typography
- **Primary font**: Sans-serif, modern and professional. Prefer `Inter`, `Roboto`, or `Segoe UI`.
- **Headings**: Uppercase or small-caps for section headers with strong letter spacing.
- **Body text**: Clear and readable, 16px minimum.
- **Monospace**: Use for thermodynamic labels, equations, and state variables.

## Layout and Structure
- **Hero/Title Section**: Large page heading with a supporting subtitle like "Explore power cycles with thermodynamic precision." Use a subtle geometric background or a faint schematic overlay.
- **Sidebar**: Sticky control panel with grouped inputs, tooltips, and advanced options hidden behind collapsible sections.
- **Main content**: Split into three areas:
  1. Diagram & chart canvas
  2. Key metric summary cards
  3. Statepoint analytics and toggles
- **Responsive grid**: Use columns that adapt from desktop to tablet/mobile while preserving readability.

## Components
### Navigation and Header
- Minimal top bar with brand name, cycle selector, and a small help icon.
- Use a subtle shadow or border to separate the header from content.

### Metrics Cards
- Display core metrics in cards with concise labels:
  - Thermal Efficiency
  - Second-Law Efficiency
  - Entropy Generation
  - Net Work Output
  - Heat Input / Rejection
- Use iconography or small sparkline accents for visual hierarchy.
- Keep cards consistent with soft backgrounds and rounded corners.

### Charts and Diagrams
- **Flowchart panel**: Large, centered. Prefer vector SVG output with a light chart background.
- **T-S and P-V diagrams**: Use polished plotly charts with branded color palettes.
- **Statepoint table**: Present as a compact, clearly labeled grid.

### Controls and Inputs
- Group related inputs with labeled sections: "Cycle Parameters", "Component Settings", "Advanced Options".
- Use sliders, dropdowns, and numeric inputs with concise helper text.
- Add inline validation states for invalid or inconsistent values.
- Keep action buttons prominent: e.g. "Run Analysis" with a strong accent color.

## Interaction and Feedback
- **Microcopy**: Provide short, actionable help text for cycles and parameters.
- **Hover states**: Highlight cards and chart elements on hover.
- **Success/alert feedback**: Use color-coded banners for results or warnings.
- **Loading states**: Show a clean spinner overlay while the solver runs.

## Branding and Imagery
- **Thermodynamics motif**: Incorporate subtle references to heat, pressure, and state diagrams in iconography or backgrounds.
- **Illustrative icons**: Use schematic-like icons for pumps, turbines, boilers, and heat exchangers.
- **Subtle gradients**: Apply soft blue-to-cyan gradients in panel headers or hero backgrounds.

## UI Styling Recommendations
- **Cards**: White or very light background, rounded corners, soft shadow, strong border contrast.
- **Buttons**: Primary action uses accent blue; secondary uses slate gray.
- **Inputs**: Clean borders, slight inset shadows, spacing for readability.
- **Text**: Use color hierarchy: dark text for labels, medium for secondary text, accent for values.
- **Divider lines**: Use thin lines and spacing rather than thick separations.

## Accessibility
- Ensure sufficient contrast for all text and icon colors.
- Use at least 16px body font and clear spacing.
- Provide keyboard-friendly controls and semantic UI elements.
- Add alternative labels or descriptions for interactive elements.

## Example Page Flow
1. **Top hero**: Title, short description, current cycle selector.
2. **Sidebar**: Parameter controls, heat source select, advanced options.
3. **Main dashboard**:
   - Flowchart and schematic display
   - Metrics summary row
   - T-S / P-V diagrams
   - Statepoint table and diagnostics
4. **Footer or info panel**: Quick thermodynamics notes, data source, and cycle definitions.

## Implementation Notes
- Reuse the site’s existing CSS injection in `gui/app.py` with refined styles.
- Keep the core layout simple while using modern spacing and typography.
- Avoid overly noisy visuals; prioritize clarity and scientific precision.

## Design Principles
- **Precision first**: Every widget should feel engineered, not decorative.
- **Modern simplicity**: Use clean spacing and minimal visual noise.
- **Technical polish**: Charts and cards should feel like an analyst’s workspace.
- **Contextual clarity**: Users should immediately understand what each metric and diagram means.

This guide is intended to turn the ThermoCycle website into a modern, polished thermodynamics tool that feels both technical and approachable.