from fpdf import FPDF

# Function to calculate total pay
def calculate_total_pay(pay_rate, hours_worked):
    return pay_rate * hours_worked

# Function to create paycheck PDF
def create_paycheck_pdf(employee_name, pay_rate, hours_worked):
    # Calculate total pay
    total_pay = calculate_total_pay(pay_rate, hours_worked)

    # Create instance of FPDF class
    pdf = FPDF(format='letter', unit='in')
    pdf.add_page()

    # Set font
    pdf.set_font("Arial", size=12)

    # Add a title
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 1, "Paycheck", 0, 1, 'C')

    # Add employee details
    pdf.set_font("Arial", size=12)
    pdf.ln(0.5)  # Add a line break
    pdf.cell(0, 0.25, f"Employee Name: {employee_name}", 0, 1)
    pdf.cell(0, 0.25, f"Pay Rate: ${pay_rate}/hour", 0, 1)
    pdf.cell(0, 0.25, f"Hours Worked: {hours_worked}", 0, 1)
    pdf.cell(0, 0.25, f"Total Pay: ${total_pay}", 0, 1)

    # Save the pdf with name .pdf
    pdf_file = f"{employee_name.replace(' ', '_')}_paycheck.pdf"
    pdf.output(pdf_file)

    return pdf_file

# Example usage
if __name__ == "__main__":
    employee_name = "John Doe"
    pay_rate = 25  # $ per hour
    hours_worked = 40
    paycheck_pdf = create_paycheck_pdf(employee_name, pay_rate, hours_worked)
    print(f"Paycheck PDF created: {paycheck_pdf}")
