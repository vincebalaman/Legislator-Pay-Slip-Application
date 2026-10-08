import sqlite3

DB_NAME = "legislator_payslip_data.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Employees Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            employee_id INTEGER PRIMARY KEY AUTOINCREMENT,
            emp_code TEXT UNIQUE NOT NULL,
            full_name TEXT NOT NULL,
            position TEXT NOT NULL
        )
    """)
    
    # 2. Payslips Master Table (Header)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS payslips (
            payslip_id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            pay_period TEXT NOT NULL, -- Format: 'YYYY-MM-DD' or 'YYYY-MM'
            deductions REAL NOT NULL DEFAULT 0.0,
            remarks TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (employee_id) REFERENCES employees (employee_id) ON DELETE CASCADE,
            UNIQUE(employee_id, pay_period)
        )
    """)
    
    # 3. Payslip Line Items Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS payslip_items (
            item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            payslip_id INTEGER NOT NULL,
            description TEXT NOT NULL,
            earnings REAL NOT NULL DEFAULT 0.0,
            frequency REAL NOT NULL DEFAULT 1.0,
            FOREIGN KEY (payslip_id) REFERENCES payslips (payslip_id) ON DELETE CASCADE
        )
    """)

    # 4. BASE VIEW: Calculated Totals Per Payslip (Uses LEFT JOIN & COALESCE)
    cursor.execute("""
        CREATE VIEW IF NOT EXISTS v_payslip_totals AS
        SELECT 
            p.payslip_id,
            p.employee_id,
            e.emp_code,
            e.full_name,
            e.position,
            p.pay_period,
            p.created_at,
            p.pay_period AS pay_month, -- Use explicit period instead of created_at
            COALESCE(SUM(i.earnings * i.frequency), 0.0) AS gross_total,
            p.deductions,
            (COALESCE(SUM(i.earnings * i.frequency), 0.0) - p.deductions) AS net_pay,
            p.remarks
        FROM payslips p
        JOIN employees e ON p.employee_id = e.employee_id
        LEFT JOIN payslip_items i ON p.payslip_id = i.payslip_id
        GROUP BY 
            p.payslip_id, p.employee_id, e.emp_code, e.full_name, 
            e.position, p.pay_period, p.created_at, p.deductions, p.remarks;
    """)

    # 5. VIEW: Monthly Employee Summary
    cursor.execute("""
        CREATE VIEW IF NOT EXISTS v_monthly_employee_summary AS
        SELECT 
            employee_id,
            emp_code,
            full_name,
            position,
            pay_month,
            COUNT(payslip_id) AS total_payslips_issued,
            SUM(gross_total) AS monthly_gross,
            SUM(deductions) AS monthly_deductions,
            SUM(net_pay) AS monthly_net
        FROM v_payslip_totals
        GROUP BY employee_id, pay_month;
    """)

    # 6. VIEW: Monthly Company Payroll Summary
    cursor.execute("""
        CREATE VIEW IF NOT EXISTS v_monthly_company_summary AS
        SELECT 
            pay_month,
            COUNT(DISTINCT employee_id) AS total_employees_paid,
            COUNT(payslip_id) AS total_payslips_issued,
            SUM(gross_total) AS company_gross_total,
            SUM(deductions) AS company_total_deductions,
            SUM(net_pay) AS company_net_total
        FROM v_payslip_totals
        GROUP BY pay_month;
    """)
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database and all views initialized successfully.")