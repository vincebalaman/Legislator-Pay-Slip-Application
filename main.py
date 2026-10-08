import calendar
import os
import re
from datetime import date
import tkinter as tk
from tkinter import ttk, messagebox
import database
from pdf_generator import generate_payslip_pdf


class PayslipApp(tk.Tk):
    COLORS = {
        "background": "#F3F6FB",
        "surface": "#FFFFFF",
        "navy": "#14243A",
        "text": "#1E293B",
        "muted": "#64748B",
        "border": "#DCE3ED",
        "accent": "#2563EB",
        "accent_hover": "#1D4ED8",
        "danger": "#B42318",
        "selected": "#DBEAFE",
    }

    def __init__(self):
        super().__init__()
        self.title("Legislator | Payroll")
        self.geometry("1220x900")
        self.minsize(1000, 700)
        self.configure(bg=self.COLORS["background"])

        database.init_db()
        self.selected_payslip_id = None
        self.selected_employee_db_id = None
        self._period_start = date.today()
        self.pay_period_var = tk.StringVar(
            self, value=self._format_pay_period(self._period_start)
        )

        self._configure_styles()
        self._build_ui()
        self.refresh_employees()
        self.refresh_payslips_list()

    def _configure_styles(self):
        style = ttk.Style(self)
        if "clam" in style.theme_names():
            style.theme_use("clam")

        background = self.COLORS["background"]
        surface = self.COLORS["surface"]
        text = self.COLORS["text"]
        muted = self.COLORS["muted"]
        border = self.COLORS["border"]
        accent = self.COLORS["accent"]

        style.configure(".", font=("Segoe UI", 10), foreground=text)
        style.configure("App.TFrame", background=background)
        style.configure("Card.TFrame", background=surface)
        style.configure("Header.TFrame", background=self.COLORS["navy"])
        style.configure(
            "HeaderTitle.TLabel", background=self.COLORS["navy"],
            foreground="#FFFFFF", font=("Segoe UI Semibold", 19),
        )
        style.configure(
            "HeaderSubtitle.TLabel", background=self.COLORS["navy"],
            foreground="#C6D2E1", font=("Segoe UI", 10),
        )
        style.configure(
            "PageTitle.TLabel", background=background,
            foreground=text, font=("Segoe UI Semibold", 17),
        )
        style.configure(
            "PageSubtitle.TLabel", background=background,
            foreground=muted, font=("Segoe UI", 10),
        )
        style.configure(
            "CardTitle.TLabel", background=surface,
            foreground=text, font=("Segoe UI Semibold", 12),
        )
        style.configure(
            "CardHint.TLabel", background=surface,
            foreground=muted, font=("Segoe UI", 9),
        )
        style.configure("TNotebook", background=background, borderwidth=0)
        style.configure(
            "TNotebook.Tab", padding=(18, 10),
            font=("Segoe UI Semibold", 10),
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", surface), ("!selected", background)],
            foreground=[("selected", accent), ("!selected", muted)],
        )
        style.configure("TLabel", background=surface, foreground=text)
        style.configure("TFrame", background=surface)
        style.configure(
            "TLabelframe", background=surface, bordercolor=border,
            relief="solid", borderwidth=1,
        )
        style.configure(
            "TLabelframe.Label", background=surface, foreground=text,
            font=("Segoe UI Semibold", 10),
        )
        style.configure(
            "TEntry", padding=(9, 7), fieldbackground=surface,
            bordercolor=border, lightcolor=border, darkcolor=border,
        )
        style.map("TEntry", bordercolor=[("focus", accent)])
        style.configure(
            "TCombobox", padding=(8, 6), fieldbackground=surface,
            bordercolor=border, arrowsize=13,
        )
        style.map(
            "TCombobox", fieldbackground=[("readonly", surface)],
            bordercolor=[("focus", accent)],
        )
        style.configure(
            "TButton", padding=(12, 8), background="#E8EEF6",
            bordercolor="#E8EEF6", font=("Segoe UI Semibold", 9),
        )
        style.map(
            "TButton",
            background=[("active", "#DCE5F0"), ("pressed", "#DCE5F0")],
        )
        style.configure(
            "Primary.TButton", background=accent,
            foreground="#FFFFFF", bordercolor=accent,
        )
        style.map(
            "Primary.TButton",
            background=[
                ("active", self.COLORS["accent_hover"]),
                ("pressed", self.COLORS["accent_hover"]),
            ],
            foreground=[("active", "#FFFFFF"), ("pressed", "#FFFFFF")],
        )
        style.configure(
            "Danger.TButton", background="#FDECEC",
            foreground=self.COLORS["danger"], bordercolor="#FDECEC",
        )
        style.map(
            "Danger.TButton",
            background=[("active", "#FBD5D5"), ("pressed", "#FBD5D5")],
        )
        style.configure(
            "Treeview", background=surface, fieldbackground=surface,
            foreground=text, rowheight=31, bordercolor=border,
            font=("Segoe UI", 9),
        )
        style.configure(
            "Treeview.Heading", background="#F1F5F9",
            foreground=muted, padding=(8, 9),
            font=("Segoe UI Semibold", 9), relief="flat",
        )
        style.map(
            "Treeview",
            background=[("selected", self.COLORS["selected"])],
            foreground=[("selected", text)],
        )

    def _build_ui(self):
        header = ttk.Frame(self, style="Header.TFrame", padding=(26, 18))
        header.pack(fill="x")
        ttk.Label(
            header, text="Legislator Payroll", style="HeaderTitle.TLabel"
        ).pack(anchor="w")
        ttk.Label(
            header,
            text="Manage employees, prepare payslips, and export clean PDF records.",
            style="HeaderSubtitle.TLabel",
        ).pack(anchor="w", pady=(3, 0))

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=18, pady=(10, 14))
        self.payslip_tab = ttk.Frame(
            self.notebook, style="App.TFrame", padding=14
        )
        self.notebook.add(self.payslip_tab, text="Payslips")
        self.employee_tab = ttk.Frame(
            self.notebook, style="App.TFrame", padding=14
        )
        self.notebook.add(self.employee_tab, text="Employees")

        self._build_payslip_tab()
        self._build_employee_tab()

    def _build_payslip_tab(self):
        page_heading = ttk.Frame(self.payslip_tab, style="App.TFrame")
        page_heading.pack(fill="x")
        ttk.Label(
            page_heading, text="Payslips", style="PageTitle.TLabel"
        ).pack(side="left", anchor="w")
        heading_actions = ttk.Frame(page_heading, style="App.TFrame")
        heading_actions.pack(side="right")
        ttk.Button(
            heading_actions, text="New", command=self.clear_payslip_form
        ).pack(side="left", padx=(0, 6))
        ttk.Button(
            heading_actions, text="Save", style="Primary.TButton",
            command=self.save_payslip_header,
        ).pack(side="left", padx=(0, 6))
        ttk.Button(
            heading_actions, text="Delete", style="Danger.TButton",
            command=self.delete_payslip,
        ).pack(side="left", padx=(0, 6))
        self.btn_generate_pdf = ttk.Button(
            page_heading,
            text="Generate PDF payslip",
            style="Primary.TButton",
            command=self.generate_pdf,
        )
        self.btn_generate_pdf.pack(side="right", padx=(12, 0))
        ttk.Label(
            self.payslip_tab,
            text="Create a pay record, add earnings, and keep your payroll history organized.",
            style="PageSubtitle.TLabel",
        ).pack(anchor="w", pady=(3, 8))

        content = ttk.Frame(self.payslip_tab, style="App.TFrame")
        content.pack(fill="both", expand=True)
        content.columnconfigure(0, weight=12, uniform="payslip")
        content.columnconfigure(1, weight=8, uniform="payslip")
        content.rowconfigure(0, weight=1)

        left_frame = ttk.Frame(content, style="App.TFrame")
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        right_frame = ttk.Frame(content, style="App.TFrame")
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        header_group = ttk.Frame(left_frame, style="Card.TFrame", padding=10)
        header_group.pack(fill="x", pady=(0, 8))
        ttk.Label(
            header_group, text="Payslip details", style="CardTitle.TLabel"
        ).grid(row=0, column=0, columnspan=2, sticky="w")
        header_group.columnconfigure(1, weight=1, uniform="field")
        header_group.columnconfigure(3, weight=1, uniform="field")

        ttk.Label(header_group, text="Employee").grid(
            row=2, column=0, sticky="w", pady=(0, 3)
        )
        ttk.Label(header_group, text="Pay period").grid(
            row=2, column=2, sticky="w", pady=(0, 3), padx=(12, 0)
        )
        self.combo_employee = ttk.Combobox(header_group, state="readonly")
        self.combo_employee.grid(row=3, column=0, columnspan=2, sticky="ew")
        period_frame = ttk.Frame(header_group, style="Card.TFrame")
        period_frame.grid(row=3, column=2, columnspan=2, sticky="ew", padx=(12, 0))
        period_frame.columnconfigure(0, weight=1)
        self.entry_pay_period = ttk.Entry(
            period_frame, textvariable=self.pay_period_var, state="readonly"
        )
        self.entry_pay_period.grid(row=0, column=0, sticky="ew", padx=(0, 7))
        ttk.Button(
            period_frame, text="Calendar", command=self.open_period_calendar
        ).grid(row=0, column=1)

        ttk.Label(header_group, text="Deductions").grid(
            row=4, column=0, sticky="w", pady=(9, 3)
        )
        ttk.Label(header_group, text="Remarks").grid(
            row=4, column=2, sticky="w", pady=(9, 3), padx=(12, 0)
        )
        self.entry_deductions = ttk.Entry(header_group)
        self.entry_deductions.insert(0, "0.0")
        self.entry_deductions.grid(
            row=5, column=0, columnspan=2, sticky="ew"
        )
        self.entry_remarks = ttk.Entry(header_group)
        self.entry_remarks.grid(
            row=5, column=2, columnspan=2, sticky="ew", padx=(12, 0)
        )

        items_group = ttk.Frame(left_frame, style="Card.TFrame", padding=12)
        items_group.pack(fill="both", expand=True)
        items_heading = ttk.Frame(items_group, style="Card.TFrame")
        items_heading.pack(fill="x")
        ttk.Label(
            items_heading, text="Earnings and line items", style="CardTitle.TLabel"
        ).pack(side="left", anchor="w")
        ttk.Button(
            items_heading, text="Remove selected", style="Danger.TButton",
            command=self.remove_line_item,
        ).pack(side="right")
        item_input_frame = ttk.Frame(items_group, style="Card.TFrame")
        item_input_frame.pack(fill="x", pady=(8, 10))
        item_input_frame.columnconfigure(1, weight=1)
        ttk.Label(item_input_frame, text="Description").grid(row=0, column=0)
        self.entry_item_desc = ttk.Entry(item_input_frame, width=12)
        self.entry_item_desc.grid(row=0, column=1, sticky="ew", padx=(5, 8))
        ttk.Label(item_input_frame, text="Amount").grid(row=0, column=2)
        self.entry_item_earnings = ttk.Entry(item_input_frame, width=8)
        self.entry_item_earnings.insert(0, "500.0")
        self.entry_item_earnings.grid(row=0, column=3, padx=(5, 8))
        ttk.Label(item_input_frame, text="Qty").grid(row=0, column=4)
        self.entry_item_freq = ttk.Entry(item_input_frame, width=5)
        self.entry_item_freq.insert(0, "1.0")
        self.entry_item_freq.grid(row=0, column=5, padx=(5, 8))
        ttk.Button(
            item_input_frame, text="Add item", style="Primary.TButton",
            command=self.add_line_item,
        ).grid(row=0, column=6)

        items_table = ttk.Frame(items_group, style="Card.TFrame")
        items_table.pack(fill="both", expand=True)
        items_table.rowconfigure(0, weight=1)
        items_table.columnconfigure(0, weight=1)
        self.tree_items = ttk.Treeview(
            items_table,
            columns=("ID", "Description", "Earnings", "Frequency", "Total"),
            show="headings",
            height=8,
        )
        for col, title in (
            ("ID", "ID"),
            ("Description", "Description"),
            ("Earnings", "Earnings"),
            ("Frequency", "Qty"),
            ("Total", "Total"),
        ):
            self.tree_items.heading(col, text=title)
        self.tree_items.column("ID", width=38, anchor="center", stretch=False)
        self.tree_items.column("Description", width=220, minwidth=160)
        self.tree_items.column("Earnings", width=74, anchor="e")
        self.tree_items.column("Frequency", width=50, anchor="center")
        self.tree_items.column("Total", width=80, anchor="e")
        self.tree_items.grid(row=0, column=0, sticky="nsew")
        items_scrollbar = tk.Scrollbar(
            items_table,
            orient="vertical",
            command=self.tree_items.yview,
            width=20,
            bg="#DCE3ED",
            troughcolor=self.COLORS["surface"],
            activebackground="#94A3B8",
            highlightthickness=0,
            bd=0,
            relief="flat",
        )
        items_scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree_items.configure(yscrollcommand=items_scrollbar.set)

        list_group = ttk.Frame(right_frame, style="Card.TFrame", padding=16)
        list_group.pack(fill="both", expand=True)
        ttk.Label(
            list_group, text="Payslip history", style="CardTitle.TLabel"
        ).pack(anchor="w")
        ttk.Label(
            list_group,
            text="Select a record to view or edit its details.",
            style="CardHint.TLabel",
        ).pack(anchor="w", pady=(2, 10))
        payslips_table = ttk.Frame(list_group, style="Card.TFrame")
        payslips_table.pack(fill="both", expand=True)
        payslips_table.rowconfigure(0, weight=1)
        payslips_table.columnconfigure(0, weight=1)
        self.tree_payslips = ttk.Treeview(
            payslips_table,
            columns=("ID", "Emp #", "Name", "Period", "Gross", "Net"),
            show="headings",
        )
        for col, title in (
            ("ID", "ID"),
            ("Emp #", "Employee"),
            ("Name", "Name"),
            ("Period", "Pay period"),
            ("Gross", "Gross"),
            ("Net", "Net"),
        ):
            self.tree_payslips.heading(col, text=title)
        self.tree_payslips.column("ID", width=40, anchor="center", stretch=False)
        self.tree_payslips.column("Emp #", width=64, anchor="center")
        self.tree_payslips.column("Name", width=120)
        self.tree_payslips.column("Period", width=125)
        self.tree_payslips.column("Gross", width=74, anchor="e")
        self.tree_payslips.column("Net", width=74, anchor="e")
        self.tree_payslips.grid(row=0, column=0, sticky="nsew")
        payslips_scrollbar = tk.Scrollbar(
            payslips_table,
            orient="vertical",
            command=self.tree_payslips.yview,
            width=20,
            bg="#DCE3ED",
            troughcolor=self.COLORS["surface"],
            activebackground="#94A3B8",
            highlightthickness=0,
            bd=0,
            relief="flat",
        )
        payslips_scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree_payslips.configure(yscrollcommand=payslips_scrollbar.set)
        self.tree_payslips.bind("<<TreeviewSelect>>", self.on_payslip_select)

    def _build_employee_tab(self):
        ttk.Label(
            self.employee_tab, text="Employees", style="PageTitle.TLabel"
        ).pack(anchor="w")
        ttk.Label(
            self.employee_tab,
            text="Maintain the employee details used on payslips.",
            style="PageSubtitle.TLabel",
        ).pack(anchor="w", pady=(3, 16))

        top_frame = ttk.Frame(self.employee_tab, style="Card.TFrame", padding=16)
        top_frame.pack(fill="x", pady=(0, 14))
        ttk.Label(
            top_frame, text="Employee details", style="CardTitle.TLabel"
        ).grid(row=0, column=0, columnspan=6, sticky="w", pady=(0, 10))
        for column in (1, 3, 5):
            top_frame.columnconfigure(column, weight=1)

        ttk.Label(top_frame, text="Employee code").grid(
            row=1, column=0, sticky="w", padx=(0, 8)
        )
        self.entry_emp_code = ttk.Entry(top_frame)
        self.entry_emp_code.grid(row=1, column=1, sticky="ew", padx=(0, 16))
        ttk.Label(top_frame, text="Full name").grid(
            row=1, column=2, sticky="w", padx=(0, 8)
        )
        self.entry_emp_name = ttk.Entry(top_frame)
        self.entry_emp_name.grid(row=1, column=3, sticky="ew", padx=(0, 16))
        ttk.Label(top_frame, text="Position").grid(
            row=1, column=4, sticky="w", padx=(0, 8)
        )
        self.entry_emp_pos = ttk.Entry(top_frame)
        self.entry_emp_pos.grid(row=1, column=5, sticky="ew")

        emp_btn_frame = ttk.Frame(top_frame, style="Card.TFrame")
        emp_btn_frame.grid(
            row=2, column=0, columnspan=6, sticky="ew", pady=(12, 0)
        )
        ttk.Button(
            emp_btn_frame, text="Save employee", style="Primary.TButton",
            command=self.save_employee,
        ).pack(side="left")
        ttk.Button(
            emp_btn_frame, text="Clear form", command=self.clear_employee_form
        ).pack(side="left", padx=(8, 0))
        ttk.Button(
            emp_btn_frame, text="Delete employee", style="Danger.TButton",
            command=self.delete_employee,
        ).pack(side="right")

        bottom_frame = ttk.Frame(self.employee_tab, style="Card.TFrame", padding=16)
        bottom_frame.pack(fill="both", expand=True)
        ttk.Label(
            bottom_frame, text="Employee directory", style="CardTitle.TLabel"
        ).pack(anchor="w")
        ttk.Label(
            bottom_frame,
            text="Select an employee to edit their information.",
            style="CardHint.TLabel",
        ).pack(anchor="w", pady=(2, 10))

        employees_table = ttk.Frame(bottom_frame, style="Card.TFrame")
        employees_table.pack(fill="both", expand=True)
        employees_table.rowconfigure(0, weight=1)
        employees_table.columnconfigure(0, weight=1)
        self.tree_employees = ttk.Treeview(
            employees_table,
            columns=("ID", "Emp Code", "Full Name", "Position"),
            show="headings",
        )
        self.tree_employees.heading("ID", text="ID")
        self.tree_employees.heading("Emp Code", text="Employee code")
        self.tree_employees.heading("Full Name", text="Full name")
        self.tree_employees.heading("Position", text="Position")
        self.tree_employees.column("ID", width=55, anchor="center", stretch=False)
        self.tree_employees.column("Emp Code", width=140, anchor="center")
        self.tree_employees.column("Full Name", width=300)
        self.tree_employees.column("Position", width=250)
        self.tree_employees.grid(row=0, column=0, sticky="nsew")
        employees_scrollbar = tk.Scrollbar(
            employees_table,
            orient="vertical",
            command=self.tree_employees.yview,
            width=20,
            bg="#DCE3ED",
            troughcolor=self.COLORS["surface"],
            activebackground="#94A3B8",
            highlightthickness=0,
            bd=0,
            relief="flat",
        )
        employees_scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree_employees.configure(yscrollcommand=employees_scrollbar.set)
        self.tree_employees.bind("<<TreeviewSelect>>", self.on_employee_select)

    @staticmethod
    def _format_pay_period(start_date):
        end_date = date.fromordinal(start_date.toordinal() + 6)
        start_month = calendar.month_abbr[start_date.month]
        end_month = calendar.month_abbr[end_date.month]
        if start_date.year == end_date.year and start_date.month == end_date.month:
            return f"{start_month}. {start_date.day}-{end_date.day}, {end_date.year}"
        if start_date.year == end_date.year:
            return (
                f"{start_month}. {start_date.day}-{end_month}. "
                f"{end_date.day}, {end_date.year}"
            )
        return (
            f"{start_month}. {start_date.day}, {start_date.year}-"
            f"{end_month}. {end_date.day}, {end_date.year}"
        )

    @staticmethod
    def _parse_pay_period_start(period):
        match = re.fullmatch(
            r"([A-Za-z]{3})\.?\s+(\d{1,2})(?:,\s*(\d{4}))?"
            r"-(?:([A-Za-z]{3})\.?\s*)?(\d{1,2}),\s*(\d{4})",
            period.strip(),
        )
        if not match:
            return None
        start_month, start_day, start_year, _, _, end_year = match.groups()
        month_number = next(
            (
                number for number in range(1, 13)
                if calendar.month_abbr[number].lower() == start_month.lower()
            ),
            None,
        )
        if month_number is None:
            return None
        try:
            return date(int(start_year or end_year), month_number, int(start_day))
        except ValueError:
            return None

    def _set_period_start(self, start_date):
        self._period_start = start_date
        self.pay_period_var.set(self._format_pay_period(start_date))

    def open_period_calendar(self):
        selected_date = self._period_start or date.today()
        year, month = selected_date.year, selected_date.month
        popup = tk.Toplevel(self)
        popup.title("Choose pay period")
        popup.transient(self)
        popup.resizable(False, False)
        popup.configure(bg=self.COLORS["surface"])
        popup.grab_set()

        calendar_frame = ttk.Frame(popup, style="Card.TFrame", padding=14)
        calendar_frame.pack(fill="both", expand=True)
        month_label = ttk.Label(
            calendar_frame, style="CardTitle.TLabel", anchor="center"
        )
        month_label.grid(row=0, column=1, sticky="ew", padx=8, pady=(0, 10))
        calendar_frame.columnconfigure(1, weight=1)

        def change_month(delta):
            nonlocal year, month
            month += delta
            if month < 1:
                year -= 1
                month = 12
            elif month > 12:
                year += 1
                month = 1
            render_month()

        ttk.Button(
            calendar_frame, text="<", width=3, command=lambda: change_month(-1)
        ).grid(row=0, column=0, sticky="w", pady=(0, 10))
        ttk.Button(
            calendar_frame, text=">", width=3, command=lambda: change_month(1)
        ).grid(row=0, column=2, sticky="e", pady=(0, 10))

        def choose_day(day):
            self._set_period_start(date(year, month, day))
            popup.destroy()

        def render_month():
            month_label.configure(text=f"{calendar.month_name[month]} {year}")
            for child in calendar_frame.grid_slaves():
                if int(child.grid_info()["row"]) > 0:
                    child.destroy()
            for column, weekday in enumerate(("Mo", "Tu", "We", "Th", "Fr", "Sa", "Su")):
                ttk.Label(
                    calendar_frame, text=weekday, style="CardHint.TLabel",
                    anchor="center",
                ).grid(row=1, column=column, sticky="ew", padx=2, pady=(0, 5))
            for row, week in enumerate(calendar.monthcalendar(year, month), start=2):
                for column, day in enumerate(week):
                    if day:
                        ttk.Button(
                            calendar_frame,
                            text=str(day),
                            width=4,
                            command=lambda selected_day=day: choose_day(selected_day),
                        ).grid(row=row, column=column, padx=2, pady=2, sticky="ew")

        render_month()
        popup.update_idletasks()
        x = self.entry_pay_period.winfo_rootx()
        y = self.entry_pay_period.winfo_rooty() + self.entry_pay_period.winfo_height()
        popup.geometry(f"+{x}+{y}")
        popup.focus_set()

    # =========================================================================
    # LOGIC & DATABASE CONTROLLERS
    # =========================================================================

    # --- Employee Controllers ---
    def refresh_employees(self):
        conn = database.get_connection()
        conn.row_factory = database.sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM employees ORDER BY employee_id DESC")
        rows = cursor.fetchall()
        conn.close()

        # Update Treeview
        for item in self.tree_employees.get_children():
            self.tree_employees.delete(item)

        self.emp_lookup = {}
        combo_values = []
        for r in rows:
            self.tree_employees.insert("", "end", values=(r["employee_id"], r["emp_code"], r["full_name"], r["position"]))
            label = f"#{r['emp_code']} - {r['full_name']}"
            combo_values.append(label)
            self.emp_lookup[label] = r["employee_id"]

        self.combo_employee["values"] = combo_values

    def save_employee(self):
        code = self.entry_emp_code.get().strip()
        name = self.entry_emp_name.get().strip()
        pos = self.entry_emp_pos.get().strip()

        if not code or not name or not pos:
            messagebox.showwarning("Validation Error", "All employee fields are required.")
            return

        conn = database.get_connection()
        cursor = conn.cursor()
        try:
            if self.selected_employee_db_id:
                cursor.execute(
                    "UPDATE employees SET emp_code = ?, full_name = ?, position = ? WHERE employee_id = ?",
                    (code, name, pos, self.selected_employee_db_id)
                )
            else:
                cursor.execute(
                    "INSERT INTO employees (emp_code, full_name, position) VALUES (?, ?, ?)",
                    (code, name, pos)
                )
            conn.commit()
            messagebox.showinfo("Success", "Employee saved successfully!")
            self.clear_employee_form()
            self.refresh_employees()
        except database.sqlite3.IntegrityError:
            messagebox.showerror("Error", f"Employee Code '{code}' already exists.")
        finally:
            conn.close()

    def delete_employee(self):
        if not self.selected_employee_db_id:
            messagebox.showwarning("Selection Error", "Please select an employee to delete.")
            return

        if messagebox.askyesno("Confirm Delete", "Deleting an employee will also delete all associated payslips. Proceed?"):
            conn = database.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM employees WHERE employee_id = ?", (self.selected_employee_db_id,))
            conn.commit()
            conn.close()
            self.clear_employee_form()
            self.refresh_employees()
            self.refresh_payslips_list()

    def on_employee_select(self, event):
        selected = self.tree_employees.selection()
        if not selected:
            return
        item = self.tree_employees.item(selected[0])
        val = item["values"]
        self.selected_employee_db_id = val[0]

        self.entry_emp_code.delete(0, tk.END)
        self.entry_emp_code.insert(0, val[1])
        self.entry_emp_name.delete(0, tk.END)
        self.entry_emp_name.insert(0, val[2])
        self.entry_emp_pos.delete(0, tk.END)
        self.entry_emp_pos.insert(0, val[3])

    def clear_employee_form(self):
        self.selected_employee_db_id = None
        self.entry_emp_code.delete(0, tk.END)
        self.entry_emp_name.delete(0, tk.END)
        self.entry_emp_pos.delete(0, tk.END)

    # --- Payslip Controllers ---
    def refresh_payslips_list(self):
        conn = database.get_connection()
        conn.row_factory = database.sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM v_payslip_totals ORDER BY payslip_id DESC")
        rows = cursor.fetchall()
        conn.close()

        for item in self.tree_payslips.get_children():
            self.tree_payslips.delete(item)

        for r in rows:
            self.tree_payslips.insert(
                "",
                "end",
                values=(
                    r["payslip_id"],
                    r["emp_code"],
                    r["full_name"],
                    r["pay_period"],
                    f"{r['gross_total']:,.2f}",
                    f"{r['net_pay']:,.2f}"
                )
            )

    def save_payslip_header(self):
        emp_label = self.combo_employee.get()
        period = self.entry_pay_period.get().strip()

        try:
            deductions = float(self.entry_deductions.get().strip() or 0.0)
        except ValueError:
            messagebox.showerror("Validation Error", "Deductions must be a valid number.")
            return

        remarks = self.entry_remarks.get().strip()

        if not emp_label or emp_label not in self.emp_lookup:
            messagebox.showwarning("Validation Error", "Please select a valid employee.")
            return

        if not period:
            messagebox.showwarning("Validation Error", "Pay period is required.")
            return

        employee_id = self.emp_lookup[emp_label]

        conn = database.get_connection()
        cursor = conn.cursor()

        try:
            if self.selected_payslip_id:
                cursor.execute(
                    """
                    UPDATE payslips 
                    SET employee_id = ?, pay_period = ?, deductions = ?, remarks = ?
                    WHERE payslip_id = ?
                    """,
                    (employee_id, period, deductions, remarks, self.selected_payslip_id)
                )
            else:
                cursor.execute(
                    """
                    INSERT INTO payslips (employee_id, pay_period, deductions, remarks)
                    VALUES (?, ?, ?, ?)
                    """,
                    (employee_id, period, deductions, remarks)
                )
                self.selected_payslip_id = cursor.lastrowid

            conn.commit()
            messagebox.showinfo("Success", f"Payslip #{self.selected_payslip_id} saved.")
            self.refresh_payslips_list()
            self.load_payslip_details(self.selected_payslip_id)
        except database.sqlite3.IntegrityError:
            messagebox.showerror("Duplicate Error", "A payslip for this employee and pay period already exists.")
        finally:
            conn.close()

    def delete_payslip(self):
        if not self.selected_payslip_id:
            messagebox.showwarning("Selection Error", "No payslip selected to delete.")
            return

        if messagebox.askyesno("Confirm Delete", f"Delete payslip #{self.selected_payslip_id}?"):
            conn = database.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM payslips WHERE payslip_id = ?", (self.selected_payslip_id,))
            conn.commit()
            conn.close()
            self.clear_payslip_form()
            self.refresh_payslips_list()

    def on_payslip_select(self, event):
        selected = self.tree_payslips.selection()
        if not selected:
            return
        item = self.tree_payslips.item(selected[0])
        payslip_id = item["values"][0]
        self.load_payslip_details(payslip_id)

    def load_payslip_details(self, payslip_id):
        self.selected_payslip_id = payslip_id
        conn = database.get_connection()
        conn.row_factory = database.sqlite3.Row
        cursor = conn.cursor()

        # Fetch header
        cursor.execute("SELECT * FROM payslips WHERE payslip_id = ?", (payslip_id,))
        header = cursor.fetchone()

        if not header:
            conn.close()
            return

        # Fetch employee
        cursor.execute("SELECT emp_code, full_name FROM employees WHERE employee_id = ?", (header["employee_id"],))
        emp = cursor.fetchone()

        if emp:
            label = f"#{emp['emp_code']} - {emp['full_name']}"
            self.combo_employee.set(label)

        self.pay_period_var.set(header["pay_period"])
        self._period_start = self._parse_pay_period_start(header["pay_period"])

        self.entry_deductions.delete(0, tk.END)
        self.entry_deductions.insert(0, str(header["deductions"]))

        self.entry_remarks.delete(0, tk.END)
        self.entry_remarks.insert(0, header["remarks"] or "")

        # Fetch line items
        cursor.execute("SELECT * FROM payslip_items WHERE payslip_id = ?", (payslip_id,))
        items = cursor.fetchall()
        conn.close()

        for itm in self.tree_items.get_children():
            self.tree_items.delete(itm)

        for item in items:
            total = item["earnings"] * item["frequency"]
            self.tree_items.insert(
                "",
                "end",
                values=(
                    item["item_id"],
                    item["description"],
                    f"{item['earnings']:,.2f}",
                    item["frequency"],
                    f"{total:,.2f}"
                )
            )

    def clear_payslip_form(self):
        self.selected_payslip_id = None
        self.combo_employee.set("")
        self._set_period_start(date.today())
        self.entry_deductions.delete(0, tk.END)
        self.entry_deductions.insert(0, "0.0")
        self.entry_remarks.delete(0, tk.END)

        for item in self.tree_items.get_children():
            self.tree_items.delete(item)

    # --- Line Items Controllers ---
    def add_line_item(self):
        if not self.selected_payslip_id:
            messagebox.showwarning("Save Required", "Please save or select a payslip header first before adding line items.")
            return

        desc = self.entry_item_desc.get().strip()
        try:
            earnings = float(self.entry_item_earnings.get().strip())
            freq = float(self.entry_item_freq.get().strip())
        except ValueError:
            messagebox.showerror("Validation Error", "Earnings and Frequency must be valid numbers.")
            return

        if not desc:
            messagebox.showwarning("Validation Error", "Item description is required.")
            return

        conn = database.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO payslip_items (payslip_id, description, earnings, frequency) VALUES (?, ?, ?, ?)",
            (self.selected_payslip_id, desc, earnings, freq)
        )
        conn.commit()
        conn.close()

        # Clear item input
        self.entry_item_desc.delete(0, tk.END)
        self.entry_item_earnings.delete(0, tk.END)
        self.entry_item_earnings.insert(0, "500.0")
        self.entry_item_freq.delete(0, tk.END)
        self.entry_item_freq.insert(0, "1.0")

        self.load_payslip_details(self.selected_payslip_id)
        self.refresh_payslips_list()

    def remove_line_item(self):
        selected = self.tree_items.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select a line item to remove.")
            return

        item_id = self.tree_items.item(selected[0])["values"][0]

        conn = database.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM payslip_items WHERE item_id = ?", (item_id,))
        conn.commit()
        conn.close()

        self.load_payslip_details(self.selected_payslip_id)
        self.refresh_payslips_list()

    # --- PDF Generation Controller ---
    def generate_pdf(self):
        if not self.selected_payslip_id:
            messagebox.showwarning("Selection Error", "Please select or save a payslip to generate PDF.")
            return

        output_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "generated_payslips"
        )
        os.makedirs(output_dir, exist_ok=True)

        success = generate_payslip_pdf(self.selected_payslip_id)
        if success:
            messagebox.showinfo("Success", f"PDF payslip generated successfully in:\n{output_dir}")


if __name__ == "__main__":
    app = PayslipApp()
    app.mainloop()