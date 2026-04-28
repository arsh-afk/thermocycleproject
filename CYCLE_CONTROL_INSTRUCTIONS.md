# Cycle Control and Variable Selection Instructions

## Objective
Enable users to manipulate cycle calculations through multiple input modes while protecting the solver from invalid or over-constrained thermodynamic requests. The interface should allow control over properties such as enthalpy, temperature, pressure, work output, and heat input, but only provide valid combinations and prevent fake results.

## Core Principles
- **Two independent properties only**: For any cycle solve, users may specify exactly two independent variables. This keeps the system solvable and avoids over-constraining the calculation.
- **Thermodynamic validity**: Input combinations must obey the rules of the underlying cycle and real fluid behavior. Reject invalid pairs or show warnings if the combination is physically impossible.
- **Consistent solution path**: User inputs should map to a solver path that uses the cycle model’s existing equations, not ad hoc guesses.
- **Guardrails, not freedom**: Provide flexibility, but constrain choices so the solver remains robust and outputs realistic thermodynamic values.

## Supported Variable Types
Allow users to choose any of the following properties as inputs, depending on the cycle:
- Pressure (`P`) at key state points
- Temperature (`T`) at key state points
- Enthalpy (`h`) at key state points
- Entropy (`s`) at key state points
- Heat input (`q_in`)
- Heat rejection (`q_out`)
- Work output (`w_net`, `w_t`, `w_c`)
- State-specific variables such as quality (`x`) for two-phase states

## User Interaction Modes
### 1. Parameter Selection Mode
- The user chooses which two properties to fix before solving.
- Example for Rankine: `P_boiler` and `T_boiler`, or `P_condenser` and `T_condenser`.
- The application then computes the remaining states and performance metrics.

### 2. Result-Driven Mode
- Let the user specify a desired target such as `thermal efficiency` or `work output`.
- This mode should map to iterative solver adjustments rather than direct variable overrides.
- Treat target values as goals, not independent constraints.

### 3. Mixed Mode with Safety Checks
- Allow a primary state and secondary performance target, but internally validate that only two independent equations are used.
- For example, user may specify `P_high` and `T_high` plus request a specific `work_output`; the solver may then compute the rest only if the cycle is still deterministically defined.

## Implementation Guidance
### A. Cycle-Specific Constraint Panels
Each cycle should expose its own valid input set. Examples:
- **Rankine**: `P_high`, `P_low`, `T_high`, `T_low`, `x_low`, `x_high`
- **Brayton**: `P_ratio`, `T_turbine_inlet`, `eta_comp`, `eta_turbine`
- **sCO2**: `P_high`, `P_low`, `T_max`, `T_min`, `split_frac`, `recup_eff`
- **Otto/Diesel**: `compression_ratio`, `T_max`, `T_min`, `eta_combustion`

### B. Two-Variable Enforcement
- Present the available property fields in the UI.
- Allow the user to select exactly two fields as active inputs.
- Disable or hide remaining fields until two are selected.
- If the user selects more than two, show an error and prevent execution.

### C. Valid Input Combination Rules
- Only allow input pairs that are truly independent. For example, `P_high` and `P_ratio` are not independent.
- Do not allow both a state property and a dependent cycle result in the active pair (e.g., `q_in` and `efficiency` should not both be active inputs unless the solver explicitly supports that mode).
- Reject combinations known to be thermodynamically invalid for the selected cycle (e.g., `T_low > T_high` in Rankine).

### D. Solver Integration
- Use the cycle solver’s existing state-based methods for all variable calculations.
- When a user supplies properties at one or more state points, compute the remaining state points through the cycle model.
- Keep the computation path deterministic: solve the cycle from the selected independent pair using the same equation path used by the model.

### E. Behavior for Derived Variables
- Derived variables such as heat input, heat rejection, and net work should be output only after the core cycle states are solved.
- Do not allow the user to directly set derived variables as one of the two independent inputs unless the solver explicitly supports a compatible equation set.
- If direct target control is desired, treat it as a secondary goal with solver guidance rather than a primary input.

## Example Workflow for Rankine
1. User chooses Rankine cycle.
2. UI displays valid input fields: `P_boiler`, `T_boiler`, `P_condenser`, `T_condenser`, `x_condenser`, `x_evaporator`.
3. User selects two fields: `P_boiler` and `T_boiler`.
4. Application uses the Rankine solver to compute the remaining state points and outputs `q_in`, `q_out`, `w_net`, efficiency, entropy generation, etc.
5. If the selected pair is invalid, the app presents a clear warning and prevents execution.

## Error Handling and Feedback
- **Validation before solve**: Check the selected pair, the numeric ranges, and cycle-specific consistency rules.
- **Clear warnings**: If the user chooses an invalid combination, explain why it is invalid and which properties are allowed.
- **Solver protection**: Prevent execution when the inputs would force the solver to extrapolate outside valid thermodynamic regions.
- **Fallback guidance**: Suggest valid alternative pairs if the user selection is not accepted.

## UI Recommendations
- Display the active input pair clearly at the top of the solver panel.
- Use toggle chips or checkbox selection for the two independent variables.
- Show a small summary card titled `Constraint Mode` with the chosen properties.
- Provide a `Reset to Default Constraints` button for quick recovery.

## Thermodynamic Safety Rules
- Ensure `T_high > T_low` where applicable.
- Ensure `P_high > P_low` for pressure-driven cycles.
- Prevent unrealistic `x` or quality values outside `[0, 1]`.
- Keep fluid state requests within the supported envelope of the property library.
- Use entropy generation and second-law efficiency as sanity checks for outputs.

## Notes for Developers
- Centralize variable selection logic in one module so all cycles use the same two-variable enforcement rules.
- Keep cycle solvers agnostic of the UI; the UI should translate user choices into property constraints.
- Add tests that verify valid and invalid variable pair selection per cycle.
- Document the supported variable pairs for each cycle in the config or cycle metadata.

## Desired Result
The project should let users explore the cycle in multiple ways, while still respecting thermodynamic constraints and the solver’s internal consistency. Exactly two independent properties should define each solve, and the app should never accept or produce inputs that would generate fake or non-physical results.