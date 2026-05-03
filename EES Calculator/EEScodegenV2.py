import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys

def install_package(package):
    try:
        __import__(package)
    except ImportError:
        print(f"Installing {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Auto-install required libraries
install_package("iapws")
install_package("pyperclip")
install_package("CoolProp")
install_package("scipy")

import pyperclip
from iapws import IAPWS97
from CoolProp.CoolProp import PropsSI
from scipy.interpolate import interp1d, interp2d, CubicSpline
import numpy as np

class ThermoCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Thermodynamic Property Calculator")
        self.root.geometry("600x800")
        self.root.resizable(False, False)
        
        self.fluid = tk.StringVar(value="Steam")
        self.pressure_unit = tk.StringVar(value="MPa")
        
        # Variables for EES code generation selection
        self.ees_vars = {
            'Temperature': tk.BooleanVar(value=True),
            'Pressure': tk.BooleanVar(value=True),
            'Entropy': tk.BooleanVar(value=True),
            'Enthalpy': tk.BooleanVar(value=True),
            'Quality': tk.BooleanVar(value=False),
            'Specific_Volume': tk.BooleanVar(value=False),
            'Internal_Energy': tk.BooleanVar(value=False)
        }
        
        self.vars = {
            'Temperature': tk.StringVar(),
            'Pressure': tk.StringVar(),
            'Entropy': tk.StringVar(),
            'Enthalpy': tk.StringVar(),
            'Quality': tk.StringVar(),
            'Specific_Volume': tk.StringVar(),
            'Internal_Energy': tk.StringVar()
        }
        
        self.units = {
            'Temperature': '°C',
            'Pressure': self.pressure_unit,
            'Entropy': 'kJ/kg·K',
            'Enthalpy': 'kJ/kg',
            'Quality': '-',
            'Specific_Volume': 'm³/kg',
            'Internal_Energy': 'kJ/kg'
        }
        
        # Initialize R-134a data tables from standard thermodynamic tables
        self.init_r134a_tables()
        
        self.create_ui()
        
    def init_r134a_tables(self):
        """
        Initialize R-134a saturation tables from standard thermodynamic data
        (Based on Cengel & Boles, Thermodynamics: An Engineering Approach, 9th ed.)
        Pressures in MPa, Temperatures in °C, h in kJ/kg, s in kJ/kg·K, v in m³/kg, u in kJ/kg
        """
        # Saturation pressure table (excerpt with key points)
        self.r134a_psat = np.array([
            0.06, 0.08, 0.10, 0.12, 0.14, 0.16, 0.18, 0.20, 0.24, 0.28,
            0.32, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 1.00, 1.20, 1.40
        ])
        
        # Corresponding saturation temperatures
        self.r134a_tsat = np.array([
            -37.07, -31.21, -26.43, -22.36, -18.80, -15.62, -12.73, -10.09, -5.38, -1.25,
            2.48, 8.93, 15.71, 21.55, 26.72, 31.31, 35.51, 39.37, 46.29, 52.43
        ])
        
        # Saturated liquid enthalpy
        self.r134a_hf = np.array([
            3.14, 10.42, 16.29, 21.32, 25.77, 29.78, 33.45, 36.84, 43.11, 48.79,
            54.02, 63.62, 73.33, 81.51, 88.82, 95.47, 101.61, 107.32, 117.79, 127.25
        ])
        
        # Saturated vapor enthalpy
        self.r134a_hg = np.array([
            206.12, 209.46, 211.98, 214.01, 215.68, 217.11, 218.34, 219.41, 221.24, 222.71,
            223.90, 225.86, 227.53, 228.79, 229.76, 230.50, 231.06, 231.46, 231.97, 232.21
        ])
        
        # Saturated liquid entropy
        self.r134a_sf = np.array([
            0.0135, 0.0447, 0.0678, 0.0869, 0.1034, 0.1180, 0.1312, 0.1431, 0.1645, 0.1832,
            0.2002, 0.2304, 0.2615, 0.2870, 0.3091, 0.3290, 0.3471, 0.3638, 0.3941, 0.4217
        ])
        
        # Saturated vapor entropy
        self.r134a_sg = np.array([
            0.9520, 0.9444, 0.9395, 0.9354, 0.9320, 0.9290, 0.9264, 0.9241, 0.9202, 0.9169,
            0.9140, 0.9092, 0.9046, 0.9007, 0.8973, 0.8942, 0.8915, 0.8890, 0.8844, 0.8803
        ])
        
        # Saturated liquid specific volume (m³/kg)
        self.r134a_vf = np.array([
            0.0007094, 0.0007140, 0.0007185, 0.0007228, 0.0007269, 0.0007308, 0.0007346, 0.0007383,
            0.0007453, 0.0007520, 0.0007584, 0.0007706, 0.0007867, 0.0008024, 0.0008179,
            0.0008332, 0.0008485, 0.0008639, 0.0008951, 0.0009274
        ])
        
        # Saturated vapor specific volume (m³/kg)
        self.r134a_vg = np.array([
            0.31108, 0.23753, 0.19255, 0.16212, 0.14014, 0.12355, 0.11041, 0.09987, 0.08390,
            0.07205, 0.06295, 0.05008, 0.04015, 0.03313, 0.02798, 0.02405, 0.02096, 0.01850,
            0.01466, 0.01189
        ])
        
        # Saturated liquid internal energy
        self.r134a_uf = np.array([
            3.13, 10.37, 16.21, 21.20, 25.62, 29.60, 33.24, 36.61, 42.83, 48.47,
            53.66, 63.19, 72.83, 80.95, 88.22, 94.82, 100.92, 106.59, 116.98, 126.38
        ])
        
        # Saturated vapor internal energy
        self.r134a_ug = np.array([
            188.18, 190.83, 192.94, 194.59, 195.94, 197.08, 198.06, 198.92, 200.46, 201.70,
            202.71, 204.32, 205.76, 206.91, 207.86, 208.63, 209.26, 209.76, 210.51, 211.05
        ])
        
        # Create interpolation functions
        self.r134a_interp_tsat = interp1d(self.r134a_psat, self.r134a_tsat, kind='cubic', fill_value='extrapolate')
        self.r134a_interp_psat = interp1d(self.r134a_tsat, self.r134a_psat, kind='cubic', fill_value='extrapolate')
        
        # For superheated tables, we'll use CoolProp but with offset correction
        # The offset is determined by matching saturation data
        self.calc_r134a_offset()
        
    def calc_r134a_offset(self):
        """Calculate offset between CoolProp and standard tables at a reference point"""
        try:
            # Use 0.12 MPa, saturated liquid as reference
            p_ref = 0.12e6  # Pa
            t_ref = PropsSI('T', 'P', p_ref, 'Q', 0, 'R134a') - 273.15  # °C
            h_coolprop = PropsSI('H', 'P', p_ref, 'Q', 0, 'R134a') / 1000  # kJ/kg
            s_coolprop = PropsSI('S', 'P', p_ref, 'Q', 0, 'R134a') / 1000  # kJ/kg·K
            
            # Find standard values at this pressure
            idx = np.argmin(np.abs(self.r134a_psat - 0.12))
            h_standard = self.r134a_hf[idx]  # 21.32 kJ/kg
            s_standard = self.r134a_sf[idx]  # 0.0869 kJ/kg·K
            
            self.h_offset = h_standard - h_coolprop
            self.s_offset = s_standard - s_coolprop
            self.u_offset = self.h_offset  # Approximate same offset for internal energy
            
        except:
            # Default offsets if calculation fails
            self.h_offset = -152.0
            self.s_offset = -0.65
            self.u_offset = -152.0
        
    def get_r134a_sat_property(self, pressure, quality, property_type):
        """
        Get saturated property by interpolating in the tables
        pressure: MPa
        quality: 0 to 1
        property_type: 'h', 's', 'v', 'u'
        """
        # Clamp pressure to table bounds
        p = max(self.r134a_psat[0], min(pressure, self.r134a_psat[-1]))
        
        # Find interpolation indices
        if p <= self.r134a_psat[0]:
            idx = 0
            frac = 0
        elif p >= self.r134a_psat[-1]:
            idx = len(self.r134a_psat) - 2
            frac = 1
        else:
            idx = np.searchsorted(self.r134a_psat, p) - 1
            frac = (p - self.r134a_psat[idx]) / (self.r134a_psat[idx+1] - self.r134a_psat[idx])
        
        # Get liquid and vapor values
        if property_type == 'h':
            f = self.r134a_hf[idx] + frac * (self.r134a_hf[idx+1] - self.r134a_hf[idx])
            g = self.r134a_hg[idx] + frac * (self.r134a_hg[idx+1] - self.r134a_hg[idx])
        elif property_type == 's':
            f = self.r134a_sf[idx] + frac * (self.r134a_sf[idx+1] - self.r134a_sf[idx])
            g = self.r134a_sg[idx] + frac * (self.r134a_sg[idx+1] - self.r134a_sg[idx])
        elif property_type == 'v':
            f = self.r134a_vf[idx] + frac * (self.r134a_vf[idx+1] - self.r134a_vf[idx])
            g = self.r134a_vg[idx] + frac * (self.r134a_vg[idx+1] - self.r134a_vg[idx])
        elif property_type == 'u':
            f = self.r134a_uf[idx] + frac * (self.r134a_uf[idx+1] - self.r134a_uf[idx])
            g = self.r134a_ug[idx] + frac * (self.r134a_ug[idx+1] - self.r134a_ug[idx])
        else:
            return None
        
        return f + quality * (g - f)
    
    def get_r134a_tsat(self, pressure):
        """Get saturation temperature for given pressure (MPa)"""
        p = max(self.r134a_psat[0], min(pressure, self.r134a_psat[-1]))
        return float(self.r134a_interp_tsat(p))
    
    def get_r134a_psat(self, temperature):
        """Get saturation pressure for given temperature (°C)"""
        t = max(self.r134a_tsat[0], min(temperature, self.r134a_tsat[-1]))
        return float(self.r134a_interp_psat(t))
        
    def create_ui(self):
        title = tk.Label(self.root, text="Thermodynamic Property Calculator", 
                        font=('Arial', 16, 'bold'))
        title.pack(pady=10)
        
        main_frame = tk.Frame(self.root)
        main_frame.pack(padx=20, pady=10, fill='both', expand=True)
        
        # Fluid selector
        fluid_frame = tk.Frame(main_frame)
        fluid_frame.pack(fill='x', pady=(0, 5))
        tk.Label(fluid_frame, text="Fluid:").pack(side='left')
        fluid_combo = ttk.Combobox(fluid_frame, textvariable=self.fluid, 
                                   values=["Steam", "R-134a"], width=15, state="readonly")
        fluid_combo.pack(side='left', padx=5)
        fluid_combo.bind("<<ComboboxSelected>>", self.on_fluid_change)
        
        # Unit selector
        unit_frame = tk.Frame(main_frame)
        unit_frame.pack(fill='x', pady=(0, 10))
        tk.Label(unit_frame, text="Pressure Unit:").pack(side='left')
        unit_combo = ttk.Combobox(unit_frame, textvariable=self.pressure_unit, 
                                  values=["MPa", "kPa"], width=8, state="readonly")
        unit_combo.pack(side='left', padx=5)
        unit_combo.bind("<<ComboboxSelected>>", self.update_unit_labels)
        
        input_label = tk.Label(main_frame, text="Known Properties (enter 2):", 
                              font=('Arial', 10, 'bold'))
        input_label.pack(anchor='w', pady=(0, 5))
        
        self.entries = {}
        self.unit_labels = {}
        
        for prop in ['Temperature', 'Pressure', 'Entropy', 'Enthalpy', 'Quality']:
            frame = tk.Frame(main_frame)
            frame.pack(fill='x', pady=2)
            
            lbl = tk.Label(frame, text=f"{prop}:", width=12, anchor='e')
            lbl.pack(side='left')
            
            entry = tk.Entry(frame, textvariable=self.vars[prop], width=15)
            entry.pack(side='left', padx=5)
            self.entries[prop] = entry
            
            unit_text = self.units[prop].get() if prop == 'Pressure' else self.units[prop]
            unit_lbl = tk.Label(frame, text=unit_text, width=10, anchor='w')
            unit_lbl.pack(side='left')
            self.unit_labels[prop] = unit_lbl
        
        btn_frame = tk.Frame(main_frame)
        btn_frame.pack(pady=15)
        
        calc_btn = tk.Button(btn_frame, text="Calculate", command=self.calculate,
                            bg='#4CAF50', fg='white', width=12, font=('Arial', 10, 'bold'))
        calc_btn.pack(side='left', padx=5)
        
        clear_btn = tk.Button(btn_frame, text="Clear", command=self.clear,
                             width=12)
        clear_btn.pack(side='left', padx=5)
        
        # EES Code button with variable selection
        ees_frame = tk.LabelFrame(main_frame, text="EES Code Options", font=('Arial', 9))
        ees_frame.pack(fill='x', pady=10)
        
        # Checkboxes for EES variables
        ees_check_frame = tk.Frame(ees_frame)
        ees_check_frame.pack(fill='x', padx=5, pady=5)
        
        col = 0
        for prop in ['Temperature', 'Pressure', 'Entropy', 'Enthalpy', 
                     'Quality', 'Specific_Volume', 'Internal_Energy']:
            chk = tk.Checkbutton(ees_check_frame, text=prop, variable=self.ees_vars[prop])
            chk.grid(row=col//4, column=col%4, sticky='w', padx=5)
            col += 1
        
        copy_btn = tk.Button(ees_frame, text="Generate EES Code", command=self.copy_ees,
                            width=15, bg='#2196F3', fg='white')
        copy_btn.pack(pady=5)
        
        output_label = tk.Label(main_frame, text="Calculated Properties:", 
                               font=('Arial', 10, 'bold'))
        output_label.pack(anchor='w', pady=(10, 5))
        
        self.outputs = {}
        for prop in ['Temperature', 'Pressure', 'Entropy', 'Enthalpy', 
                     'Quality', 'Specific_Volume', 'Internal_Energy']:
            frame = tk.Frame(main_frame)
            frame.pack(fill='x', pady=2)
            
            lbl = tk.Label(frame, text=f"{prop}:", width=12, anchor='e')
            lbl.pack(side='left')
            
            val_lbl = tk.Label(frame, text="--", width=15, anchor='w', 
                              bg='#f0f0f0', relief='sunken')
            val_lbl.pack(side='left', padx=5)
            self.outputs[prop] = val_lbl
            
            unit_text = self.units[prop].get() if prop == 'Pressure' else self.units[prop]
            unit_lbl = tk.Label(frame, text=unit_text, width=10, anchor='w')
            unit_lbl.pack(side='left')
        
        self.status = tk.Label(self.root, text="Select fluid, enter 2 properties and click Calculate", 
                              bd=1, relief='sunken', anchor='w')
        self.status.pack(side='bottom', fill='x')
    
    def on_fluid_change(self, event=None):
        self.clear()
        fluid = self.fluid.get()
        self.status.config(text=f"Fluid changed to {fluid}. Enter 2 properties and click Calculate.")
        
    def update_unit_labels(self, event=None):
        unit = self.pressure_unit.get()
        self.unit_labels['Pressure'].config(text=unit)
        for prop in ['Pressure']:
            if prop in self.outputs:
                output_frame = self.outputs[prop].master
                children = output_frame.winfo_children()
                if len(children) >= 3:
                    children[2].config(text=unit)
        
    def get_inputs(self):
        inputs = {}
        for prop in ['Temperature', 'Pressure', 'Entropy', 'Enthalpy', 'Quality']:
            val = self.vars[prop].get().strip()
            if val:
                try:
                    num_val = float(val)
                    if prop == 'Pressure':
                        # Store always in MPa internally
                        if self.pressure_unit.get() == 'kPa':
                            num_val = num_val / 1000.0
                    inputs[prop] = num_val
                except ValueError:
                    messagebox.showerror("Error", f"Invalid number for {prop}")
                    return None
        return inputs
    
    def calculate_steam(self, inputs):
        """Calculate using IAPWS97 for steam"""
        kwargs = {}
        
        if 'Temperature' in inputs:
            kwargs['T'] = inputs['Temperature'] + 273.15
        if 'Pressure' in inputs:
            kwargs['P'] = inputs['Pressure']
        if 'Entropy' in inputs:
            kwargs['s'] = inputs['Entropy']
        if 'Enthalpy' in inputs:
            kwargs['h'] = inputs['Enthalpy']
        if 'Quality' in inputs:
            kwargs['x'] = inputs['Quality']
        
        steam = IAPWS97(**kwargs)
        
        return {
            'Temperature': steam.T - 273.15,
            'Pressure': steam.P,
            'Entropy': steam.s,
            'Enthalpy': steam.h,
            'Quality': steam.x if steam.x is not None else (0 if steam.region == 4 else 1),
            'Specific_Volume': steam.v,
            'Internal_Energy': steam.u
        }
    
    def calculate_r134a(self, inputs):
        """
        Calculate R-134a properties using table lookup for saturation states
        and CoolProp with offset correction for superheated states
        """
        props = list(inputs.keys())
        if len(props) < 2:
            raise Exception("Need at least 2 properties")
        
        # Determine state and calculate properties
        P = inputs.get('Pressure')
        T = inputs.get('Temperature')
        x = inputs.get('Quality')
        h = inputs.get('Enthalpy')
        s = inputs.get('Entropy')
        
        # Case 1: Pressure and Quality given (saturation state)
        if P is not None and x is not None:
            if x < 0 or x > 1:
                raise Exception("Quality must be between 0 and 1")
            
            T_sat = self.get_r134a_tsat(P)
            h_val = self.get_r134a_sat_property(P, x, 'h')
            s_val = self.get_r134a_sat_property(P, x, 's')
            v_val = self.get_r134a_sat_property(P, x, 'v')
            u_val = self.get_r134a_sat_property(P, x, 'u')
            
            return {
                'Temperature': T_sat,
                'Pressure': P,
                'Entropy': s_val,
                'Enthalpy': h_val,
                'Quality': x,
                'Specific_Volume': v_val,
                'Internal_Energy': u_val
            }
        
        # Case 2: Temperature and Quality given (saturation state)
        elif T is not None and x is not None:
            if x < 0 or x > 1:
                raise Exception("Quality must be between 0 and 1")
            
            P_sat = self.get_r134a_psat(T)
            h_val = self.get_r134a_sat_property(P_sat, x, 'h')
            s_val = self.get_r134a_sat_property(P_sat, x, 's')
            v_val = self.get_r134a_sat_property(P_sat, x, 'v')
            u_val = self.get_r134a_sat_property(P_sat, x, 'u')
            
            return {
                'Temperature': T,
                'Pressure': P_sat,
                'Entropy': s_val,
                'Enthalpy': h_val,
                'Quality': x,
                'Specific_Volume': v_val,
                'Internal_Energy': u_val
            }
        
        # Case 3: Pressure and Temperature given
        elif P is not None and T is not None:
            T_sat = self.get_r134a_tsat(P)
            
            # Check if saturated (within 0.1°C tolerance)
            if abs(T - T_sat) < 0.1:
                # Saturated state - need quality, assume saturated liquid (x=0)
                x = 0
                h_val = self.get_r134a_sat_property(P, x, 'h')
                s_val = self.get_r134a_sat_property(P, x, 's')
                v_val = self.get_r134a_sat_property(P, x, 'v')
                u_val = self.get_r134a_sat_property(P, x, 'u')
                
                return {
                    'Temperature': T_sat,
                    'Pressure': P,
                    'Entropy': s_val,
                    'Enthalpy': h_val,
                    'Quality': x,
                    'Specific_Volume': v_val,
                    'Internal_Energy': u_val
                }
            elif T > T_sat:
                # Superheated vapor - use CoolProp with offset correction
                return self.calc_r134a_superheated(P, T, x=None)
            else:
                # Subcooled liquid - approximate as saturated liquid at same T
                P_sat = self.get_r134a_psat(T)
                x = 0
                h_val = self.get_r134a_sat_property(P_sat, x, 'h')
                s_val = self.get_r134a_sat_property(P_sat, x, 's')
                v_val = self.get_r134a_sat_property(P_sat, x, 'v')
                u_val = self.get_r134a_sat_property(P_sat, x, 'u')
                
                return {
                    'Temperature': T,
                    'Pressure': P,
                    'Entropy': s_val,
                    'Enthalpy': h_val,
                    'Quality': 0,  # Subcooled
                    'Specific_Volume': v_val,
                    'Internal_Energy': u_val
                }
        
        # Case 4: Pressure and Enthalpy given
        elif P is not None and h is not None:
            # Check saturation properties at this pressure
            hf = self.get_r134a_sat_property(P, 0, 'h')
            hg = self.get_r134a_sat_property(P, 1, 'h')
            T_sat = self.get_r134a_tsat(P)
            
            if h < hf:
                # Subcooled liquid
                return {
                    'Temperature': T_sat - 5,  # Approximate
                    'Pressure': P,
                    'Entropy': self.get_r134a_sat_property(P, 0, 's'),
                    'Enthalpy': h,
                    'Quality': 0,
                    'Specific_Volume': self.get_r134a_sat_property(P, 0, 'v'),
                    'Internal_Energy': self.get_r134a_sat_property(P, 0, 'u')
                }
            elif h > hg:
                # Superheated - use CoolProp
                return self.calc_r134a_superheated(P=P, h=h)
            else:
                # Two-phase mixture
                x = (h - hf) / (hg - hf)
                return {
                    'Temperature': T_sat,
                    'Pressure': P,
                    'Entropy': self.get_r134a_sat_property(P, x, 's'),
                    'Enthalpy': h,
                    'Quality': x,
                    'Specific_Volume': self.get_r134a_sat_property(P, x, 'v'),
                    'Internal_Energy': self.get_r134a_sat_property(P, x, 'u')
                }
        
        # Case 5: Pressure and Entropy given
        elif P is not None and s is not None:
            sf = self.get_r134a_sat_property(P, 0, 's')
            sg = self.get_r134a_sat_property(P, 1, 's')
            T_sat = self.get_r134a_tsat(P)
            
            if s < sf:
                # Subcooled
                return {
                    'Temperature': T_sat - 5,
                    'Pressure': P,
                    'Entropy': s,
                    'Enthalpy': self.get_r134a_sat_property(P, 0, 'h'),
                    'Quality': 0,
                    'Specific_Volume': self.get_r134a_sat_property(P, 0, 'v'),
                    'Internal_Energy': self.get_r134a_sat_property(P, 0, 'u')
                }
            elif s > sg:
                # Superheated
                return self.calc_r134a_superheated(P=P, s=s)
            else:
                # Two-phase
                x = (s - sf) / (sg - sf)
                return {
                    'Temperature': T_sat,
                    'Pressure': P,
                    'Entropy': s,
                    'Enthalpy': self.get_r134a_sat_property(P, x, 'h'),
                    'Quality': x,
                    'Specific_Volume': self.get_r134a_sat_property(P, x, 'v'),
                    'Internal_Energy': self.get_r134a_sat_property(P, x, 'u')
                }
        
        else:
            raise Exception("Property combination not supported. Use: P+x, T+x, P+T, P+h, or P+s")
    
    def calc_r134a_superheated(self, P=None, T=None, h=None, s=None, x=None):
        """
        Calculate superheated properties using CoolProp with offset correction
        """
        fluid_name = "R134a"
        
        try:
            # Determine input pair for CoolProp
            if P is not None and T is not None:
                T_k = T + 273.15
                P_pa = P * 1e6
                # Get properties from CoolProp
                h_cool = PropsSI('H', 'P', P_pa, 'T', T_k, fluid_name) / 1000
                s_cool = PropsSI('S', 'P', P_pa, 'T', T_k, fluid_name) / 1000
                v_cool = 1 / PropsSI('D', 'P', P_pa, 'T', T_k, fluid_name)
                u_cool = PropsSI('U', 'P', P_pa, 'T', T_k, fluid_name) / 1000
                
            elif P is not None and h is not None:
                # Convert h to CoolProp reference
                h_cool_input = (h - self.h_offset) * 1000
                P_pa = P * 1e6
                T_k = PropsSI('T', 'P', P_pa, 'H', h_cool_input, fluid_name)
                s_cool = PropsSI('S', 'P', P_pa, 'H', h_cool_input, fluid_name) / 1000
                v_cool = 1 / PropsSI('D', 'P', P_pa, 'H', h_cool_input, fluid_name)
                u_cool = PropsSI('U', 'P', P_pa, 'H', h_cool_input, fluid_name) / 1000
                T = T_k - 273.15
                
            elif P is not None and s is not None:
                s_cool_input = (s - self.s_offset) * 1000
                P_pa = P * 1e6
                T_k = PropsSI('T', 'P', P_pa, 'S', s_cool_input, fluid_name)
                h_cool = PropsSI('H', 'P', P_pa, 'S', s_cool_input, fluid_name) / 1000
                v_cool = 1 / PropsSI('D', 'P', P_pa, 'S', s_cool_input, fluid_name)
                u_cool = PropsSI('U', 'P', P_pa, 'S', s_cool_input, fluid_name) / 1000
                T = T_k - 273.15
                
            else:
                raise Exception("Invalid superheated calculation inputs")
            
            # Apply offset correction to get standard reference values
            h_std = h_cool + self.h_offset if 'h_cool' in locals() else None
            s_std = s_cool + self.s_offset if 's_cool' in locals() else None
            u_std = u_cool + self.u_offset
            
            # If we didn't calculate h or s above, get them now
            if h_std is None:
                h_std = h_cool + self.h_offset
            if s_std is None:
                s_std = s_cool + self.s_offset
            
            return {
                'Temperature': T,
                'Pressure': P,
                'Entropy': s_std,
                'Enthalpy': h_std,
                'Quality': 1,  # Superheated
                'Specific_Volume': v_cool,
                'Internal_Energy': u_std
            }
            
        except Exception as e:
            raise Exception(f"Superheated calculation failed: {str(e)}")
    
    def calculate(self):
        inputs = self.get_inputs()
        if not inputs:
            return
        
        count = len(inputs)
        
        if count < 2:
            self.status.config(text="Error: Need exactly 2 independent properties")
            return
        
        try:
            fluid = self.fluid.get()
            
            if fluid == "Steam":
                results = self.calculate_steam(inputs)
            else:  # R-134a
                results = self.calculate_r134a(inputs)
            
            # Display results
            for prop, val in results.items():
                if val is not None:
                    if prop == 'Quality':
                        if isinstance(val, str):
                            text = val
                        else:
                            text = f"{val:.4f}"
                    elif prop == 'Pressure':
                        val_mpa = val
                        if self.pressure_unit.get() == 'kPa':
                            text = f"{val_mpa * 1000:.4f}"
                        else:
                            text = f"{val_mpa:.6f}"
                    else:
                        text = f"{val:.4f}"
                else:
                    text = "N/A"
                self.outputs[prop].config(text=text)
            
            self.status.config(text=f"Calculation successful ({fluid})")
            
        except Exception as e:
            self.status.config(text=f"Error: {str(e)[:60]}")
            messagebox.showerror("Calculation Error", str(e))
    
    def clear(self):
        for var in self.vars.values():
            var.set('')
        for lbl in self.outputs.values():
            lbl.config(text='--')
        self.status.config(text="Enter 2 properties and click Calculate")
    
    def copy_ees(self):
        inputs = self.get_inputs()
        if not inputs or len(inputs) < 2:
            messagebox.showerror("Error", "Need valid calculation first")
            return
        
        fluid = self.fluid.get()
        fluid_ees = "Steam" if fluid == "Steam" else "R134a"
        
        ees_vars_map = {
            'Temperature': 't',
            'Pressure': 'p',
            'Entropy': 's',
            'Enthalpy': 'h',
            'Quality': 'x',
            'Specific_Volume': 'v',
            'Internal_Energy': 'u'
        }
        
        unit = self.pressure_unit.get()
        
        # Build EES code
        lines = []
        
        # Add known inputs
        known = list(inputs.keys())[:2]
        for prop in known:
            var = ees_vars_map[prop]
            val = self.vars[prop].get().strip()
            
            if prop == 'Temperature':
                lines.append(f"{var} = {val} [C]")
            elif prop == 'Pressure':
                if unit == 'kPa':
                    lines.append(f"{var} = {val} [kPa]")
                else:
                    lines.append(f"{var} = {val} [MPa]")
            elif prop == 'Entropy':
                lines.append(f"{var} = {val} [kJ/kg-K]")
            elif prop == 'Enthalpy':
                lines.append(f"{var} = {val} [kJ/kg]")
            elif prop == 'Quality':
                lines.append(f"{var} = {val}")
        
        # Add lookup call for selected output variables
        lookup = ", ".join([f"{ees_vars_map[p]}={ees_vars_map[p]}" for p in known])
        
        # Get selected variables to calculate
        selected_outputs = [p for p, var in self.ees_vars.items() 
                          if var.get() and p not in known]
        
        for prop in selected_outputs:
            var = ees_vars_map[prop]
            if prop == 'Temperature':
                lines.append(f"{var} = Temperature({fluid_ees}, {lookup}) [C]")
            elif prop == 'Pressure':
                if unit == 'kPa':
                    lines.append(f"{var} = Pressure({fluid_ees}, {lookup}) [kPa]")
                else:
                    lines.append(f"{var} = Pressure({fluid_ees}, {lookup}) [MPa]")
            elif prop == 'Entropy':
                lines.append(f"{var} = Entropy({fluid_ees}, {lookup}) [kJ/kg-K]")
            elif prop == 'Enthalpy':
                lines.append(f"{var} = Enthalpy({fluid_ees}, {lookup}) [kJ/kg]")
            elif prop == 'Quality':
                lines.append(f"{var} = Quality({fluid_ees}, {lookup})")
            elif prop == 'Specific_Volume':
                lines.append(f"{var} = Volume({fluid_ees}, {lookup}) [m^3/kg]")
            elif prop == 'Internal_Energy':
                lines.append(f"{var} = IntEnergy({fluid_ees}, {lookup}) [kJ/kg]")
        
        code = "\n".join(lines)
        
        try:
            pyperclip.copy(code)
            self.status.config(text="EES code copied to clipboard!")
        except:
            messagebox.showinfo("EES Code", code)

if __name__ == "__main__":
    root = tk.Tk()
    app = ThermoCalculator(root)
    root.mainloop()