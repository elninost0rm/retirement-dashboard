import tkinter as tk
from tkinter import ttk, messagebox
import datetime

# =============================================================================
# Core financial engine (immediate pension if layoff age >= 49)
# =============================================================================
def calculate_scenario(inputs):
    brokerage = float(inputs['brokerage'])
    tsp = float(inputs['tsp'])
    broker_contrib = float(inputs['brokerage_contrib'])
    tsp_contrib = float(inputs['tsp_contrib'])
    base_spend = float(inputs['base_spend'])
    aca = float(inputs['aca'])
    medicare = float(inputs['medicare'])
    mortgage_save = float(inputs['mortgage_save'])
    new_job = float(inputs['new_job'])
    spouse_income = float(inputs['spouse'])
    ss_you = float(inputs['ss_you'])
    ss_spouse = float(inputs['ss_spouse'])
    high3 = float(inputs['high3'])
    yrs_service = int(inputs['yrs_service'])
    nominal_return = float(inputs['nominal_return'])
    inflation = float(inputs['inflation'])
    current_age = int(inputs['current_age'])
    layoff_age = int(inputs['layoff_age'])
    your_retire_age = int(inputs['your_retire_age'])
    spouse_retire_age = int(inputs['spouse_retire_age'])

    stress_enabled = bool(inputs.get('stress_enabled', False))
    if stress_enabled:
        stress_real_return = float(inputs.get('stress_real_return', 0.0)) / 100.0
        retirement_start = max(your_retire_age, spouse_retire_age - 3)
        stress_start_age = int(inputs.get('stress_start_age', retirement_start))
        stress_end_age = int(inputs.get('stress_end_age', retirement_start + 5))
    else:
        stress_real_return = None
        stress_start_age = 0
        stress_end_age = 0

    # Determine if pension is immediate (layoff at 49 or older)
    immediate_pension = layoff_age >= 49
    if immediate_pension:
        pension_start = layoff_age
        erosion_years = 0
    else:
        pension_start = 62
        erosion_years = 62 - layoff_age

    normal_real_return = (1 + nominal_return) / (1 + inflation) - 1
    nominal_pension = high3 * yrs_service * (0.01 if yrs_service < 20 else 0.011)
    # If immediate, no erosion; pension is already in "real" terms since it will be COLA'd
    real_pension = nominal_pension / ((1 + inflation) ** erosion_years) if erosion_years > 0 else nominal_pension

    current_year = datetime.datetime.now().year
    pay_off_year = 2049
    pay_off_month = 6
    end_age = 95
    tsp_access_age = 59.5

    yearly_data = []
    prev_someone_working = True
    min_total_portfolio = float('inf')
    min_total_age = 0
    min_brokerage_pre59 = float('inf')
    brokerage_failed_pre59 = False

    for age in range(current_age, end_age + 1):
        year = current_year + (age - current_age)
        spouse_current_age = age + 3

        # ----- Contributions & earned income -----
        your_income = 0
        if layoff_age <= age < your_retire_age:
            your_income = new_job
        spouse_earned = spouse_income if spouse_current_age < spouse_retire_age else 0
        earned_income = your_income + spouse_earned

        if age < layoff_age:
            brokerage += broker_contrib
            tsp += tsp_contrib
        elif layoff_age <= age and earned_income > 0:
            net = earned_income - base_spend
            brokerage += net

        # ----- Spending -----
        if year < pay_off_year or (year == pay_off_year and pay_off_month > 6):
            current_base = base_spend
        elif year == pay_off_year and pay_off_month <= 6:
            current_base = (6/12)*base_spend + (6/12)*(base_spend - mortgage_save)
        else:
            current_base = base_spend - mortgage_save

        someone_working = (spouse_current_age < spouse_retire_age) or (age < layoff_age)
        health_cost = 0 if someone_working else (aca if age < 65 else medicare)
        total_spend = current_base + health_cost

        # ----- Guaranteed income -----
        spouse_ss_start_age = 59
        spouse_ss = ss_spouse if age >= spouse_ss_start_age else 0
        your_ss = ss_you if age >= 62 else 0
        pension = real_pension if age >= pension_start else 0
        guaranteed_income = pension + your_ss + spouse_ss

        # ----- Withdrawals / surplus reinvestment -----
        base_note = ""
        both_retired = age >= max(your_retire_age, spouse_retire_age - 3)

        if both_retired:
            net_cashflow = guaranteed_income - total_spend
            if net_cashflow > 0:
                brokerage += net_cashflow
                base_note = f"Spend: ${total_spend:,.0f}, Gtd Inc: ${guaranteed_income:,.0f}, Surplus: ${net_cashflow:,.0f} reinvested"
            elif net_cashflow < 0:
                need = -net_cashflow
                from_brokerage = min(need, brokerage)
                brokerage -= from_brokerage
                need -= from_brokerage
                if need > 0 and age >= tsp_access_age:
                    from_tsp = min(need, tsp)
                    tsp -= from_tsp
                    need -= from_tsp
                if need > 0 and age < tsp_access_age:
                    brokerage_failed_pre59 = True
                base_note = f"Spend: ${total_spend:,.0f}, Gtd Inc: ${guaranteed_income:,.0f}, Net need: ${total_spend - guaranteed_income:,.0f}"
            else:
                base_note = f"Spend: ${total_spend:,.0f}, Gtd Inc: ${guaranteed_income:,.0f}, Net need: $0"
        else:
            if age < layoff_age:
                base_note = "Working (fed) – expenses covered"
            else:
                who = "both" if (your_income > 0 and spouse_earned > 0) else ("you" if your_income > 0 else "spouse")
                net = earned_income - base_spend
                if net >= 0:
                    flow = f"Surplus ${net:,.0f} added to brokerage"
                else:
                    flow = f"Deficit ${abs(net):,.0f} drawn from brokerage"
                base_note = f"Working ({who}) – {flow}"

        # Track minimum brokerage before TSP access
        if age < tsp_access_age:
            if brokerage < min_brokerage_pre59:
                min_brokerage_pre59 = brokerage

        # ----- Event highlights -----
        events = []
        if age == layoff_age:
            events.append("Layoff")
            if immediate_pension:
                events.append("Pension begins (immediate)")
        if age == your_retire_age:
            events.append("You retire")
        if spouse_current_age == spouse_retire_age:
            events.append("Spouse retires")
        if age == spouse_ss_start_age:
            events.append("Spouse SS begins")
        if age == 62:
            if not immediate_pension:
                events.append("Your pension & SS begin")
            else:
                events.append("Your SS begins (pension already active)")
        if age == 65:
            events.append("Medicare begins")
        if age == tsp_access_age:
            events.append("TSP penalty‑free access")
        if year == pay_off_year and pay_off_month <= 6:
            events.append("Mortgage paid off (Jun)")
        if not someone_working and prev_someone_working and age < 65:
            events.append("ACA coverage begins")
        if stress_enabled and stress_start_age <= age <= stress_end_age:
            events.append(f"STRESS: {stress_real_return*100:.0f}% real return")
        prev_someone_working = someone_working

        full_note = "; ".join(events) + " | " + base_note if events else base_note

        # ----- Grow balances with appropriate real return -----
        if stress_enabled and stress_start_age <= age <= stress_end_age:
            this_year_return = stress_real_return
        else:
            this_year_return = normal_real_return
        brokerage *= (1 + this_year_return)
        tsp *= (1 + this_year_return)

        total = round(brokerage + tsp)
        if total < min_total_portfolio:
            min_total_portfolio = total
            min_total_age = age

        yearly_data.append((age, round(brokerage), round(tsp), total, full_note))

    summary = (f"Minimum portfolio: ${min_total_portfolio:,} at age {min_total_age}",
               min_total_portfolio, min_total_age)
    extra_info = {
        'min_brokerage_pre59': min_brokerage_pre59 if min_brokerage_pre59 != float('inf') else 0,
        'brokerage_failed_pre59': brokerage_failed_pre59
    }
    return yearly_data, normal_real_return, layoff_age, your_retire_age, spouse_retire_age, summary, extra_info

# =============================================================================
# GUI application (unchanged UI, immediate pension logic baked in)
# =============================================================================
class RetirementApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Retirement Flexibility Calculator (Real $)")
        self.geometry("1200x950")
        self.resizable(True, True)

        self.default_entries = {
            "brokerage": 350000,
            "tsp": 280000,
            "brokerage_contrib": 30000,
            "tsp_contrib": 14000,
            "new_job": 32000,
            "spouse": 31200,
            "base_spend": 56400,
            "aca": 3792,
            "medicare": 10000,
            "mortgage_save": 9096,
            "ss_you": 18397,
            "ss_spouse": 13074,
            "high3": 110000,
            "yrs_service": 20,
        }
        self.default_sliders = {
            "current_age": 38,
            "layoff_age": 43,
            "your_retire_age": 53,
            "spouse_retire_age": 56,
            "nominal_return": 7.0,
            "inflation": 3.0,
        }
        self.stress_vars = {
            "stress_enabled": tk.BooleanVar(value=False),
            "stress_real_return": tk.StringVar(value="0"),
            "stress_start_age": tk.StringVar(value="53"),
            "stress_end_age": tk.StringVar(value="58"),
        }

        # --- Main scrollable canvas ---
        canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        self.scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas_window = canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(canvas_window, width=e.width))
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.configure(command=canvas.yview)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # --- Inputs Frame ---
        input_lf = ttk.LabelFrame(self.scrollable_frame, text="Adjustable Parameters", padding=10)
        input_lf.pack(fill="x", padx=10, pady=5)

        self.entries = {}
        entry_defs = [
            ("Brokerage Start", "brokerage", self.default_entries["brokerage"]),
            ("TSP Start", "tsp", self.default_entries["tsp"]),
            ("Brokerage Contrib", "brokerage_contrib", self.default_entries["brokerage_contrib"]),
            ("TSP Contrib", "tsp_contrib", self.default_entries["tsp_contrib"]),
            ("New Job Net", "new_job", self.default_entries["new_job"]),
            ("Spouse Net", "spouse", self.default_entries["spouse"]),
            ("Base Spending", "base_spend", self.default_entries["base_spend"]),
            ("ACA (after retire)", "aca", self.default_entries["aca"]),
            ("Medicare (per person)", "medicare", self.default_entries["medicare"]),
            ("Mortgage Savings", "mortgage_save", self.default_entries["mortgage_save"]),
            ("Your SS at 62", "ss_you", self.default_entries["ss_you"]),
            ("Spouse SS at 62", "ss_spouse", self.default_entries["ss_spouse"]),
            ("High-3 Salary", "high3", self.default_entries["high3"]),
            ("Years of Fed Service", "yrs_service", self.default_entries["yrs_service"]),
        ]

        mid = (len(entry_defs) + 1) // 2
        for i, (label, key, default) in enumerate(entry_defs[:mid]):
            ttk.Label(input_lf, text=label).grid(row=i, column=0, sticky="w", padx=5, pady=2)
            entry = ttk.Entry(input_lf, width=15)
            entry.insert(0, str(default))
            entry.grid(row=i, column=1, padx=5, pady=2)
            self.entries[key] = entry
        for i, (label, key, default) in enumerate(entry_defs[mid:]):
            ttk.Label(input_lf, text=label).grid(row=i, column=2, sticky="w", padx=5, pady=2)
            entry = ttk.Entry(input_lf, width=15)
            entry.insert(0, str(default))
            entry.grid(row=i, column=3, padx=5, pady=2)
            self.entries[key] = entry

        next_row = max(len(entry_defs[:mid]), len(entry_defs[mid:]))
        ttk.Separator(input_lf, orient='horizontal').grid(row=next_row, column=0, columnspan=4, sticky="ew", pady=5)
        next_row += 1

        slider_defs = [
            ("Your Current Age", "current_age", self.default_sliders["current_age"], 30, 50),
            ("Layoff Age", "layoff_age", self.default_sliders["layoff_age"], 40, 55),
            ("Your Retirement Age", "your_retire_age", self.default_sliders["your_retire_age"], 40, 62),
            ("Spouse Retirement Age", "spouse_retire_age", self.default_sliders["spouse_retire_age"], 40, 62),
            ("Nominal Return", "nominal_return", self.default_sliders["nominal_return"], 5.0, 10.0),
            ("Inflation", "inflation", self.default_sliders["inflation"], 1.0, 5.0),
        ]
        self.slider_vars = {}
        for idx, (label, key, default, from_, to_) in enumerate(slider_defs):
            row_offset = idx // 2
            col_offset = (idx % 2) * 3
            r = next_row + row_offset
            c = col_offset
            ttk.Label(input_lf, text=label).grid(row=r, column=c, sticky="w", padx=5)
            var = tk.DoubleVar(value=default)
            self.slider_vars[key] = var
            slider = ttk.Scale(input_lf, from_=from_, to=to_, variable=var, orient="horizontal",
                               length=130, command=lambda e, v=var, k=key: self.slider_update(v, k))
            slider.grid(row=r, column=c+1, sticky="ew", padx=5)
            val_label = ttk.Label(input_lf, text=f"{default:.1f}" if key in ("nominal_return","inflation") else f"{int(default)}")
            val_label.grid(row=r, column=c+2, padx=5)
            self.slider_vars[f"{key}_label"] = val_label

        # --- Stress Test Section (fields in one row) ---
        stress_frame = ttk.LabelFrame(self.scrollable_frame, text="Sequence‑of‑Returns Stress Test", padding=10)
        stress_frame.pack(fill="x", padx=10, pady=5)

        self.stress_check = ttk.Checkbutton(stress_frame, text="Enable Stress Test",
                                            variable=self.stress_vars["stress_enabled"],
                                            command=self.on_stress_toggle)
        self.stress_check.grid(row=0, column=0, columnspan=6, sticky="w", pady=5)

        ttk.Label(stress_frame, text="Real return during stress (%):").grid(row=1, column=0, sticky="w", padx=5)
        self.stress_return_entry = ttk.Entry(stress_frame, textvariable=self.stress_vars["stress_real_return"], width=8)
        self.stress_return_entry.grid(row=1, column=1, padx=5)

        ttk.Label(stress_frame, text="Stress Start Age:").grid(row=1, column=2, sticky="w", padx=5)
        self.stress_start_entry = ttk.Entry(stress_frame, textvariable=self.stress_vars["stress_start_age"], width=8)
        self.stress_start_entry.grid(row=1, column=3, padx=5)

        ttk.Label(stress_frame, text="Stress End Age:").grid(row=1, column=4, sticky="w", padx=5)
        self.stress_end_entry = ttk.Entry(stress_frame, textvariable=self.stress_vars["stress_end_age"], width=8)
        self.stress_end_entry.grid(row=1, column=5, padx=5)

        for entry in [self.stress_return_entry, self.stress_start_entry, self.stress_end_entry]:
            entry.bind("<Return>", lambda e: self.run())
            entry.bind("<FocusOut>", lambda e: self.run())

        # Stress banner
        self.stress_banner = tk.Label(self.scrollable_frame, text="", font=("Arial", 10, "bold"),
                                      fg="white", bg="red", anchor="center")

        # Buttons
        btn_frame = ttk.Frame(self.scrollable_frame)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Calculate", command=self.run).pack(side="left", padx=10)
        ttk.Button(btn_frame, text="Reset to Default", command=self.reset_defaults).pack(side="left", padx=10)
        ttk.Button(btn_frame, text="Quit", command=self.destroy).pack(side="left", padx=10)

        # --- Summary + Minimum Portfolio Row ---
        summary_frame = ttk.Frame(self.scrollable_frame)
        summary_frame.pack(fill="x", padx=10, pady=(10, 0))

        self.summary_var = tk.StringVar(value="Scenario: Layoff at -, You retire -, Spouse retires - | Real return = -")
        self.summary_label = ttk.Label(summary_frame, textvariable=self.summary_var, font=("Arial", 11, "bold"))
        self.summary_label.pack(side="left")

        right_info_frame = ttk.Frame(summary_frame)
        right_info_frame.pack(side="right")

        self.min_label = ttk.Label(right_info_frame, text="Minimum portfolio: ---", font=("Arial", 11, "bold"), foreground="darkred")
        self.min_label.pack(anchor="e")

        self.warning_label = ttk.Label(right_info_frame, text="", font=("Arial", 10, "bold"), foreground="red")
        self.warning_label.pack(anchor="e", pady=(2, 0))

        # Treeview
        tree_frame = ttk.Frame(self.scrollable_frame)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.tree = ttk.Treeview(tree_frame, columns=("Age", "Brokerage", "TSP", "Total", "Notes"), show="headings", height=20)
        self.tree.heading("Age", text="Age")
        self.tree.heading("Brokerage", text="Brokerage")
        self.tree.heading("TSP", text="TSP")
        self.tree.heading("Total", text="Total")
        self.tree.heading("Notes", text="Details")
        self.tree.column("Age", width=50, anchor="center")
        self.tree.column("Brokerage", width=140, anchor="e")
        self.tree.column("TSP", width=140, anchor="e")
        self.tree.column("Total", width=140, anchor="e")
        self.tree.column("Notes", width=450, anchor="w")
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)

    def on_stress_toggle(self):
        self.run()

    def slider_update(self, var, key):
        label = self.slider_vars[f"{key}_label"]
        if key in ("nominal_return","inflation"):
            label.config(text=f"{var.get():.1f}")
        else:
            label.config(text=f"{int(var.get())}")

    def reset_defaults(self):
        for key, entry in self.entries.items():
            entry.delete(0, tk.END)
            entry.insert(0, str(self.default_entries[key]))
        for key, default in self.default_sliders.items():
            var = self.slider_vars[key]
            var.set(default)
            label = self.slider_vars[f"{key}_label"]
            if key in ("nominal_return","inflation"):
                label.config(text=f"{default:.1f}")
            else:
                label.config(text=f"{int(default)}")
        self.stress_vars["stress_enabled"].set(False)
        self.stress_vars["stress_real_return"].set("0")
        self.stress_vars["stress_start_age"].set("53")
        self.stress_vars["stress_end_age"].set("58")
        self.stress_banner.pack_forget()
        self.summary_var.set("Scenario: Layoff at -, You retire -, Spouse retires - | Real return = -")
        self.min_label.config(text="Minimum portfolio: ---")
        self.warning_label.config(text="")
        for row in self.tree.get_children():
            self.tree.delete(row)

    def collect_inputs(self):
        inputs = {}
        for key, entry in self.entries.items():
            try:
                if key == "yrs_service":
                    inputs[key] = int(entry.get())
                else:
                    inputs[key] = float(entry.get())
            except:
                messagebox.showerror("Input Error", f"Invalid numeric value for {key}")
                return None
        for key, var in self.slider_vars.items():
            if key.endswith("_label"):
                continue
            if key in ("current_age", "layoff_age", "your_retire_age", "spouse_retire_age"):
                inputs[key] = int(var.get())
            else:
                inputs[key] = var.get() / 100.0
        if inputs['layoff_age'] > inputs['your_retire_age']:
            messagebox.showerror("Input Error", "Layoff age cannot be later than your retirement age.")
            return None
        if inputs['current_age'] >= inputs['layoff_age']:
            messagebox.showerror("Input Error", "Current age must be less than layoff age.")
            return None

        inputs['stress_enabled'] = self.stress_vars["stress_enabled"].get()
        try:
            inputs['stress_real_return'] = float(self.stress_vars["stress_real_return"].get())
            inputs['stress_start_age'] = int(self.stress_vars["stress_start_age"].get())
            inputs['stress_end_age'] = int(self.stress_vars["stress_end_age"].get())
            if inputs['stress_enabled'] and inputs['stress_start_age'] >= inputs['stress_end_age']:
                raise ValueError("Start age must be less than end age.")
        except ValueError as e:
            messagebox.showerror("Invalid", f"Stress ages invalid: {e}")
            return None
        return inputs

    def run(self):
        inputs = self.collect_inputs()
        if not inputs:
            return
        try:
            result = calculate_scenario(inputs)
            yearly_data, real_ret, layoff, your_ret, spouse_ret, summary, extra_info = result
        except Exception as e:
            messagebox.showerror("Calculation Error", str(e))
            return

        if inputs.get('stress_enabled', False):
            ret = inputs.get('stress_real_return', 0)
            start = inputs.get('stress_start_age', 0)
            end = inputs.get('stress_end_age', 0)
            banner_text = f"⚠ STRESS TEST ACTIVE: {ret:.0f}% real return from age {start} to {end}"
            self.stress_banner.config(text=banner_text, bg="red", fg="white")
            self.stress_banner.pack(before=self.summary_label.master, fill="x", padx=10, pady=(5, 0))
        else:
            self.stress_banner.pack_forget()

        stress_info = ""
        if inputs.get('stress_enabled', False):
            stress_info = f" (Stress: {inputs['stress_real_return']:.0f}% real, ages {inputs['stress_start_age']}-{inputs['stress_end_age']})"
        self.summary_var.set(f"Scenario: Layoff at {layoff}, You retire at {your_ret}, Spouse retires at {spouse_ret} | Real return = {real_ret:.4%}{stress_info}")

        min_total_text = f"Minimum portfolio: ${summary[1]:,} at age {summary[2]}"
        self.min_label.config(text=min_total_text)

        if extra_info['brokerage_failed_pre59']:
            self.warning_label.config(text="⚠ WARNING: Brokerage depleted before TSP access (age 59½)!")
        else:
            self.warning_label.config(text="")

        for row in self.tree.get_children():
            self.tree.delete(row)
        for item in yearly_data:
            if isinstance(item, tuple) and len(item) == 5:
                age, b, t, tot, note = item
                self.tree.insert("", "end", values=(age, f"${b:,}", f"${t:,}", f"${tot:,}", note))

        if summary:
            self.tree.insert("", "end", values=("", "", "", "", ""))
            min_text_row = f"MINIMUM PORTFOLIO: ${summary[1]:,} at age {summary[2]}"
            self.tree.insert("", "end", values=("", "", "", "", min_text_row), tags=("summary",))
            self.tree.tag_configure("summary", background="#ffffcc")

if __name__ == "__main__":
    app = RetirementApp()
    app.mainloop()