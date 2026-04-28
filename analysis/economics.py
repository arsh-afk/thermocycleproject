"""
Economic Analysis Module
Educational note: LCOE (Levelized Cost of Energy) allows comparing different power sources
with varying capital costs and fuel prices.
"""

class EconomicAnalyzer:
    """Calculates LCOE and simple payback period."""
    
    def calculate_lcoe(self, capex, om_fixed, fuel_cost, power_mw, cf=0.85, disc_rate=0.07, life=30):
        """
        LCOE = (CAPEX * CRF + O&M_fixed) / (8760 * CF * Power) + Fuel_unit_cost
        """
        # Capital Recovery Factor
        crf = (disc_rate * (1 + disc_rate)**life) / ((1 + disc_rate)**life - 1)
        
        annual_gen_mwh = 8760 * cf * power_mw
        lcoe = (capex * crf + om_fixed) / annual_gen_mwh + fuel_cost
        
        return lcoe
