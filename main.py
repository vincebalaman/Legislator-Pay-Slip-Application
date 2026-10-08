import sqlite3
import database


def setup_application():
    print("Initializing application database...")
    database.init_db()
    print("Database setup complete.")


def fetch_all_payslip_totals():
    """Example helper to query calculated totals from the base view."""
    conn = database.get_connection()
    conn.row_factory = sqlite3.Row  # Enables column access by name (dict-like)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM v_payslip_totals")
    records = cursor.fetchall()

    conn.close()
    return records


def fetch_monthly_company_summary():
    """Example helper to fetch the company-level monthly payroll summary view."""
    conn = database.get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM v_monthly_company_summary")
    summary = cursor.fetchall()

    conn.close()
    return summary


def main():
    # 1. Run database initialization on startup
    setup_application()

    # 2. Example usage / query verification
    print("\n--- Testing Database Views ---")
    
    payslips = fetch_all_payslip_totals()
    print(f"Total payslip records found: {len(payslips)}")

    company_summary = fetch_monthly_company_summary()
    print(f"Total monthly summaries found: {len(company_summary)}")

    # Add your GUI / CLI main application execution logic here


if __name__ == "__main__":
    main()