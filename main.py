import os
import tkinter as tk
from tkinter import ttk, messagebox
import database
from pdf_generator import generate_payslip_pdf


class PayslipApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Legislator Payslip Management System")
        self.geometry("1100x720")
        self.minsize(950, 650)

        # Initialize database schema
        database.init_db()

        # State Variables
        self.selected_payslip_id = None
        self.selected_employee_db_id = None

        self._build_ui()
        self.refresh_employees()
        self.refresh_payslips_list()

    def _build_ui(self):
        # Create Notebook / Tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Tab 1: Payslip Management & Generation
        self.payslip_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.payslip_tab, text=" Payslips & Entry ")

        # Tab 2: Employee Directory (CRUD)
        self.employee_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.employee_tab, text=" Employee Directory ")

        self._build_payslip_tab()
        self._build_employee_tab()

    # =========================================================================
    # TAB 1: PAYSLIP & LINE ITEMS CRUD
    # =========================================================================
    def _build_payslip_tab(self):
        # Split left and right
        left_frame = ttk.Frame(self.payslip_tab)
        left_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        right_frame = ttk.Frame(self.payslip_tab)
        right_frame.pack(side="right", fill="both", expand=True, padx=5, pady=5)

        # --- LEFT PANEL: Payslip Form ---
        header_group = ttk.LabelFrame(left_frame, text=" 1. Header Information ")
        header_group.pack(fill="x", padx=5, pady=5)

        # Employee Selector
        ttk.Label(header_group, text="Select Employee:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.combo_employee = ttk.Combobox(header_group, state="readonly", width=30)
        self.combo_employee.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        # Pay Period
        ttk.Label(header_group, text="Pay Period:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.entry_pay_period = ttk.Entry(header_group, width=32)
        self.entry_pay_period.insert(0, "Aug. 15-21, 2024")
        self.entry_pay_period.grid(row=1, column=1, sticky="w", padx=5, pady=5)

        # Deductions
        ttk.Label(header_group, text="Deductions:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.entry_deductions = ttk.Entry(header_group, width=32)
        self.entry_deductions.insert(0, "0.0")
        self.entry_deductions.grid(row=2, column=1, sticky="w", padx=5, pady=5)

        # Remarks
        ttk.Label(header_group, text="Remarks:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.entry_remarks = ttk.Entry(header_group, width=32)
        self.entry_remarks.grid(row=3, column=1, sticky="w", padx=5, pady=5)

        # Payslip Header Actions
        btn_frame_header = ttk.Frame(header_group)
        btn_frame_header.grid(row=4, column=0, columnspan=2, pady=8)

        ttk.Button(btn_frame_header, text="New / Clear", command=self.clear_payslip_form).pack(side="left", padx=3)
        ttk.Button(btn_frame_header, text="Save Header", command=self.save_payslip_header).pack(side="left", padx=3)
        ttk.Button(btn_frame_header, text="Delete Payslip", command=self.delete_payslip).pack(side="left", padx=3)

        # Line Items Table Group
        items_group = ttk.LabelFrame(left_frame, text=" 2. Line Items (Earnings) ")
        items_group.pack(fill="both", expand=True, padx=5, pady=5)

        # Item Inputs
        item_input_frame = ttk.Frame(items_group)
        item_input_frame.pack(fill="x", padx=5, pady=5)

        ttk.Label(item_input_frame, text="Description:").grid(row=0, column=0, padx=2)
        self.entry_item_desc = ttk.Entry(item_input_frame, width=20)
        self.entry_item_desc.grid(row=0, column=1, padx=2)

        ttk.Label(item_input_frame, text="Earnings:").grid(row=0, column=2, padx=2)
        self.entry_item_earnings = ttk.Entry(item_input_frame, width=8)
        self.entry_item_earnings.insert(0, "500.0")
        self.entry_item_earnings.grid(row=0, column=3, padx=2)

        ttk.Label(item_input_frame, text="Freq/Qty:").grid(row=0, column=4, padx=2)
        self.entry_item_freq = ttk.Entry(item_input_frame, width=6)
        self.entry_item_freq.insert(0, "1.0")
        self.entry_item_freq.grid(row=0, column=5, padx=2)

        ttk.Button(item_input_frame, text="+ Add Item", command=self.add_line_item).grid(row=0, column=6, padx=5)

        # Items Treeview
        self.tree_items = ttk.Treeview(
            items_group,
            columns=("ID", "Description", "Earnings", "Frequency", "Total"),
            show="headings",
            height=6
        )
        self.tree_items.heading("ID", text="ID")
        self.tree_items.heading("Description", text="Description")
        self.tree_items.heading("Earnings", text="Earnings")
        self.tree_items.heading("Frequency", text="Qty")
        self.tree_items.heading("Total", text="Total")

        self.tree_items.column("ID", width=30, anchor="center")
        self.tree_items.column("Description", width=180)
        self.tree_items.column("Earnings", width=70, anchor="e")
        self.tree_items.column("Frequency", width=40, anchor="center")
        self.tree_items.column("Total", width=80, anchor="e")

        self.tree_items.pack(fill="both", expand=True, padx=5, pady=5)

        btn_item_del = ttk.Button(items_group, text="Remove Selected Item", command=self.remove_line_item)
        btn_item_del.pack(anchor="e", padx=5, pady=2)

        # PDF Action
        btn_pdf = ttk.Button(left_frame, text=" Generate PDF Payslip", command=self.generate_pdf)
        btn_pdf.pack(fill="x", padx=5, pady=10)

        # --- RIGHT PANEL: Payslips Directory List ---
        list_group = ttk.LabelFrame(right_frame, text=" Saved Payslips Records ")
        list_group.pack(fill="both", expand=True, padx=5, pady=5)

        self.tree_payslips = ttk.Treeview(
            list_group,
            columns=("ID", "Emp #", "Name", "Period", "Gross", "Net"),
            show="headings"
        )
        self.tree_payslips.heading("ID", text="ID")
        self.tree_payslips.heading("Emp #", text="Emp #")
        self.tree_payslips.heading("Name", text="Name")
        self.tree_payslips.heading("Period", text="Period")
        self.tree_payslips.heading("Gross", text="Gross")
        self.tree_payslips.heading("Net", text="Net")

        self.tree_payslips.column("ID", width=30, anchor="center")
        self.tree_payslips.column("Emp #", width=50, anchor="center")
        self.tree_payslips.column("Name", width=110)
        self.tree_payslips.column("Period", width=100)
        self.tree_payslips.column("Gross", width=65, anchor="e")
        self.tree_payslips.column("Net", width=65, anchor="e")

        self.tree_payslips.pack(fill="both", expand=True, padx=5, pady=5)
        self.tree_payslips.bind("<<TreeviewSelect>>", self.on_payslip_select)

    # =========================================================================
    # TAB 2: EMPLOYEE DIRECTORY CRUD
    # =========================================================================
    def _build_employee_tab(self):
        top_frame = ttk.LabelFrame(self.employee_tab, text=" Employee Form ")
        top_frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(top_frame, text="Employee Code (#):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entry_emp_code = ttk.Entry(top_frame, width=20)
        self.entry_emp_code.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(top_frame, text="Full Name:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.entry_emp_name = ttk.Entry(top_frame, width=30)
        self.entry_emp_name.grid(row=0, column=3, padx=5, pady=5, sticky="w")

        ttk.Label(top_frame, text="Position:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.entry_emp_pos = ttk.Entry(top_frame, width=20)
        self.entry_emp_pos.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        emp_btn_frame = ttk.Frame(top_frame)
        emp_btn_frame.grid(row=1, column=2, columnspan=2, sticky="e", padx=5, pady=5)

        ttk.Button(emp_btn_frame, text="Save Employee", command=self.save_employee).pack(side="left", padx=5)
        ttk.Button(emp_btn_frame, text="Clear Form", command=self.clear_employee_form).pack(side="left", padx=5)
        ttk.Button(emp_btn_frame, text="Delete Employee", command=self.delete_employee).pack(side="left", padx=5)

        bottom_frame = ttk.LabelFrame(self.employee_tab, text=" Registered Employees ")
        bottom_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.tree_employees = ttk.Treeview(
            bottom_frame,
            columns=("ID", "Emp Code", "Full Name", "Position"),
            show="headings"
        )
        self.tree_employees.heading("ID", text="DB ID")
        self.tree_employees.heading("Emp Code", text="Employee #")
        self.tree_employees.heading("Full Name", text="Full Name")
        self.tree_employees.heading("Position", text="Position")

        self.tree_employees.column("ID", width=60, anchor="center")
        self.tree_employees.column("Emp Code", width=120, anchor="center")
        self.tree_employees.column("Full Name", width=300)
        self.tree_employees.column("Position", width=250)

        self.tree_employees.pack(fill="both", expand=True, padx=5, pady=5)
        self.tree_employees.bind("<<TreeviewSelect>>", self.on_employee_select)

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

        self.entry_pay_period.delete(0, tk.END)
        self.entry_pay_period.insert(0, header["pay_period"])

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
        self.entry_pay_period.delete(0, tk.END)
        self.entry_pay_period.insert(0, "Aug. 15-21, 2024")
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

        output_dir = os.path.join(os.getcwd(), "generated_payslips")
        os.makedirs(output_dir, exist_ok=True)

        success = generate_payslip_pdf(self.selected_payslip_id)
        if success:
            messagebox.showinfo("Success", f"PDF payslip generated successfully in:\n{output_dir}")


if __name__ == "__main__":
    app = PayslipApp()
    app.mainloop()