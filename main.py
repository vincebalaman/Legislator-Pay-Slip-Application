import database  # Uses your updated database.py module[cite: 2]
from pdf_generator import generate_payslip_pdf


def setup_application():
    """Initializes database schema and views."""
    print("Initializing application database...")
    database.init_db()  #[cite: 2]
    print("Database setup complete.")


def seed_sample_data():
    """Seeds sample data matching the provided image sample."""
    conn = database.get_connection()
    cursor = conn.cursor()

    # 1. Insert Employee (Vince Juliel Babman - #26)
    cursor.execute(
        """
        INSERT OR IGNORE INTO employees (emp_code, full_name, position)
        VALUES ('26', 'Vince Jalirl Balaman', 'Supervisor')
    """
    )

    # Get inserted/existing employee ID
    cursor.execute("SELECT employee_id FROM employees WHERE emp_code = '26'")
    employee_id = cursor.fetchone()[0]

    # 2. Create Payslip Record Header
    try:
        cursor.execute(
            """
            INSERT INTO payslips (employee_id, pay_period, deductions, remarks)
            VALUES (?, ?, ?, ?)
        """,
            (employee_id, "Aug. 15-21, 2024", 0.0, "Paid in full"),
        )
        payslip_id = cursor.lastrowid

        # 3. Insert Line Items matching handwritten details
        cursor.execute(
            """
            INSERT INTO payslip_items (payslip_id, description, earnings, frequency)
            VALUES (?, ?, ?, ?)
        """,
            (payslip_id, "7 days duty (with tasking)", 500.0, 7.0),
        )

        cursor.execute(
            """
            INSERT INTO payslip_items (payslip_id, description, earnings, frequency)
            VALUES (?, ?, ?, ?)
        """,
            (payslip_id, "allowance for next week", 500.0, 1.0),
        )

        conn.commit()
        print(f"Sample payslip created with ID: {payslip_id}")
        return payslip_id

    except database.sqlite3.IntegrityError:
        # If payslip already exists for this period
        cursor.execute(
            "SELECT payslip_id FROM payslips WHERE employee_id = ? AND pay_period = ?",
            (employee_id, "Aug. 15-21, 2024"),
        )
        existing_id = cursor.fetchone()[0]
        conn.close()
        return existing_id


def main():
    # Step 1: Initialize application database and views[cite: 2]
    setup_application()

    # Step 2: Populate sample database record matching the handwritten payslip
    payslip_id = seed_sample_data()

    # Step 3: Generate PDF using the generator script
    generate_payslip_pdf(payslip_id=payslip_id)


if __name__ == "__main__":
    main()