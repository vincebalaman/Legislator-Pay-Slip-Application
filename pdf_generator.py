import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import database  # Uses your updated database.py

# Ensure output directory exists
output_dir = "generated_payslips"
os.makedirs(output_dir, exist_ok=True)

# Save PDF inside the folder
file_path = os.path.join(output_dir, output_filename)
doc = SimpleDocTemplate(file_path, ...)


def get_payslip_data(payslip_id: int):
    """Fetches payslip details, items, and totals from SQLite database."""
    conn = database.get_connection()
    conn.row_factory = database.sqlite3.Row
    cursor = conn.cursor()

    # 1. Fetch header data from v_payslip_totals view[cite: 2]
    cursor.execute(
        "SELECT * FROM v_payslip_totals WHERE payslip_id = ?", (payslip_id,)
    )
    header = cursor.fetchone()

    if not header:
        conn.close()
        return None, []

    # 2. Fetch line items[cite: 2]
    cursor.execute(
        "SELECT description, earnings, frequency FROM payslip_items WHERE payslip_id = ?",
        (payslip_id,),
    )
    items = cursor.fetchall()

    conn.close()
    return header, items


def generate_payslip_pdf(
    payslip_id: int,
    output_filename: str = None,
    logo_path: str = None,
    signature_path: str = None,
):
    """Generates a PDF payslip matching the handwritten Legislator payslip format."""
    header, items = get_payslip_data(payslip_id)

    if not header:
        print(f"Error: Payslip ID {payslip_id} not found in database.")
        return False

    if output_filename is None:
        output_filename = f"payslip_{header['emp_code']}_{header['pay_period']}.pdf"

    # Setup document geometry
    doc = SimpleDocTemplate(
        output_filename,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    story = []
    styles = getSampleStyleSheet()

    # Custom Paragraph Styles
    title_style = ParagraphStyle(
        'HeaderTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=16,
        alignment=1,  # Center align
    )

    label_style = ParagraphStyle(
        'LabelStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=13,
    )

    bold_label = ParagraphStyle(
        'BoldLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
    )

    cell_style = ParagraphStyle(
        'CellStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=12,
    )

    cell_right = ParagraphStyle(
        'CellRight',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=12,
        alignment=2,  # Right align
    )

    # -------------------------------------------------------------
    # HEADER SECTION: Logo, Title, and Pay Period Date
    # -------------------------------------------------------------
    logo_element = ""
    if logo_path and os.path.exists(logo_path):
        logo_element = Image(logo_path, width=1.2 * inch, height=0.6 * inch)

    header_table_data = [
        [
            logo_element,
            Paragraph("PAYSLIP", title_style),
            Paragraph(f"<b>{header['pay_period']}</b>", cell_right),
        ]
    ]

    header_table = Table(header_table_data, colWidths=[1.5 * inch, 3.5 * inch, 2.2 * inch])
    header_table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (1, 0), (1, 0), "CENTER"),
            ]
        )
    )
    story.append(header_table)
    story.append(Spacer(1, 15))

    # -------------------------------------------------------------
    # METADATA SECTION: Name, Position, Employee #
    # -------------------------------------------------------------
    meta_data = [
        [
            Paragraph(f"<b>Name:</b> {header['full_name']}", label_style),
            Paragraph(f"<b>Employee #:</b> {header['emp_code']}", cell_right),
        ],
        [
            Paragraph(f"<b>Position:</b> {header['position']}", label_style),
            "",
        ],
    ]

    meta_table = Table(meta_data, colWidths=[4.5 * inch, 2.7 * inch])
    meta_table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )
    story.append(meta_table)
    story.append(Spacer(1, 10))

    # -------------------------------------------------------------
    # MAIN ITEMS TABLE: Description | Earnings | Total Earnings
    # -------------------------------------------------------------
    items_table_data = [
        [
            Paragraph("<b>Description</b>", bold_label),
            Paragraph("<b>Earnings</b>", ParagraphStyle('C', parent=bold_label, alignment=1)),
            Paragraph("<b>Total Earnings</b>", ParagraphStyle('R', parent=bold_label, alignment=2)),
        ]
    ]

    # Populate items from database
    for item in items:
        earnings_val = item['earnings']
        freq_val = item['frequency']
        total_line = earnings_val * freq_val

        # Formatting earnings/frequency strings
        earn_str = f"{earnings_val:,.2f}" if earnings_val > 0 else "N/A"
        total_str = f"{total_line:,.2f}" if total_line > 0 else "N/A"

        items_table_data.append(
            [
                Paragraph(f"- {item['description']}", cell_style),
                Paragraph(earn_str, ParagraphStyle('C', parent=cell_style, alignment=1)),
                Paragraph(total_str, cell_right),
            ]
        )

    # Pad empty rows to maintain payslip height
    min_rows = 5
    while len(items_table_data) < min_rows:
        items_table_data.append(
            [
                Paragraph("- N/A", cell_style),
                Paragraph("N/A", ParagraphStyle('C', parent=cell_style, alignment=1)),
                Paragraph("N/A", cell_right),
            ]
        )

    items_table = Table(items_table_data, colWidths=[4.2 * inch, 1.4 * inch, 1.6 * inch])
    items_table.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.append(items_table)

    # -------------------------------------------------------------
    # TOTALS SUMMARY SECTION: Gross Total | Deductions | Net
    # -------------------------------------------------------------
    deductions_str = (
        f"{header['deductions']:,.2f}" if header['deductions'] > 0 else "N/A"
    )

    totals_data = [
        [
            Paragraph(f"<b>Gross Total:</b> {header['gross_total']:,.2f}", label_style),
            Paragraph(f"<b>Deductions:</b> {deductions_str}", label_style),
            Paragraph(f"<b>Net:</b> {header['net_pay']:,.2f}", label_style),
        ]
    ]

    totals_table = Table(totals_data, colWidths=[2.5 * inch, 2.2 * inch, 2.5 * inch])
    totals_table.setStyle(
        TableStyle(
            [
                ("BOX", (0, 0), (-1, -1), 1, colors.black),
                ("INNERGRID", (0, 0), (-1, -1), 1, colors.black),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.append(totals_table)
    story.append(Spacer(1, 15))

    # -------------------------------------------------------------
    # REMARKS & SIGNATURE SECTION
    # -------------------------------------------------------------
    remarks_text = header['remarks'] if header['remarks'] else ""
    
    sig_element = Paragraph("_______________________<br/>Authorized Signature", cell_right)
    if signature_path and os.path.exists(signature_path):
        sig_element = Image(signature_path, width=1.5 * inch, height=0.6 * inch)

    bottom_data = [
        [
            Paragraph(f"<b>REMARKS:</b> {remarks_text}", label_style),
            sig_element,
        ]
    ]

    bottom_table = Table(bottom_data, colWidths=[4.5 * inch, 2.7 * inch])
    bottom_table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
            ]
        )
    )
    story.append(bottom_table)

    # Build the PDF
    doc.build(story)
    print(f"Payslip PDF successfully generated: {output_filename}")
    return True