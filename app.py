from flask import Flask, render_template_string, request, send_file
import pandas as pd
from fpdf import FPDF
import os

app = Flask(__name__)

# Updated Fund recommendations based on risk profile
fund_recommendations = {
    "Conservative": [
        "HDFC Corporate Bond Fund",
        "ICICI Prudential Short Term Fund",
        "SBI Magnum Low Duration Fund",
        "Axis Banking & PSU Debt Fund",
        "ICICI Prudential Regular Savings Fund",
        "Kotak Debt Hybrid Fund",
        "HDFC Hybrid Debt Fund",
        "Canara Robeco Conservative Hybrid Fund",
        "Nippon India Liquid Fund",
        "ICICI Prudential Liquid Fund",
        "Aditya Birla Sun Life Money Manager Fund",
        "Axis Money Market Fund",
        "HDFC Banking & PSU Debt Fund",
        "SBI Banking & PSU Fund",
        "ICICI Prudential Banking & PSU Debt Fund"
    ],
    "Moderate": [
        "ICICI Prudential Equity & Debt Fund",
        "HDFC Hybrid Equity Fund",
        "SBI Equity Hybrid Fund",
        "Mirae Asset Hybrid Equity Fund",
        "ICICI Prudential Balanced Advantage Fund",
        "Edelweiss Balanced Advantage Fund",
        "HDFC Balanced Advantage Fund",
        "Nippon India Balanced Advantage Fund",
        "ICICI Prudential Multi-Asset Fund",
        "SBI Multi Asset Allocation Fund",
        "Kotak Multi Asset Allocation Fund",
        "HDFC Equity Savings Fund",
        "ICICI Prudential Equity Savings Fund",
        "Nippon India Equity Savings Fund"
    ],
    "Aggressive": [
        "Nippon India Small Cap Fund",
        "SBI Small Cap Fund",
        "Quant Small Cap Fund",
        "Kotak Emerging Equity Fund",
        "PGIM India Midcap Opportunities Fund",
        "Motilal Oswal Midcap Fund",
        "Parag Parikh Flexi Cap Fund",
        "Mirae Asset Flexi Cap Fund",
        "HDFC Flexi Cap Fund",
        "ICICI Prudential Technology Fund",
        "Nippon India Pharma Fund",
        "Aditya Birla Sun Life Digital India Fund",
        "Motilal Oswal Nasdaq 100 Fund of Fund",
        "Franklin India Feeder – U.S. Opportunities Fund",
        "ICICI Prudential Liquid Fund"
    ]
}

# HTML template
html_form = """
<!DOCTYPE html>
<html>
<head>
    <title>Client Fund Recommendation</title>
</head>
<body>
    <h2>Enter Client Risk Profile</h2>
    <form method="post">
        <label>Client Name:</label>
        <input type="text" name="client_name" required><br><br>

        <label>Select Risk Profile:</label>
        <select name="risk_profile" required>
            <option value="">--Select--</option>
            <option value="Conservative">Conservative</option>
            <option value="Moderate">Moderate</option>
            <option value="Aggressive">Aggressive</option>
        </select><br><br>

        <input type="submit" name="action" value="Get Recommendations">
        <input type="submit" name="action" value="Download PDF">
    </form>

    {% if profile %}
        <h3>Client: {{ name }}</h3>
        <h4>Risk Profile: {{ profile }}</h4>
        <h4>Suggested Funds:</h4>
        <ul>
            {% for fund in funds %}
                <li>{{ fund }}</li>
            {% endfor %}
        </ul>
    {% endif %}
</body>
</html>
"""

# Excel storage file
EXCEL_FILE = "client_data.xlsx"
LOGO_PATH = "logo.png"  # optional: place logo image in same folder

@app.route('/', methods=['GET', 'POST'])
def index():
    profile = None
    funds = []
    name = None

    if request.method == 'POST':
        name = request.form.get('client_name')
        profile = request.form.get('risk_profile')
        action = request.form.get('action')

        if profile in fund_recommendations:
            funds = fund_recommendations[profile]

            # Save to Excel
            new_entry = pd.DataFrame([[name, profile, ", ".join(funds)]], columns=["Client Name", "Risk Profile", "Recommended Funds"])
            if os.path.exists(EXCEL_FILE):
                existing = pd.read_excel(EXCEL_FILE)
                updated = pd.concat([existing, new_entry], ignore_index=True)
            else:
                updated = new_entry
            updated.to_excel(EXCEL_FILE, index=False)

            # PDF generation if requested
            if action == "Download PDF":
                pdf = FPDF()
                pdf.add_page()

                # Add logo if available
                if os.path.exists(LOGO_PATH):
                    pdf.image(LOGO_PATH, x=10, y=8, w=33)
                    pdf.ln(35)
                else:
                    pdf.ln(10)

                pdf.set_font("Arial", 'B', 14)
                pdf.cell(200, 10, txt="Client Fund Recommendation Report", ln=True, align='C')

                pdf.set_font("Arial", size=12)
                pdf.ln(10)
                pdf.cell(200, 10, txt=f"Client Name: {name}", ln=True)
                pdf.cell(200, 10, txt=f"Risk Profile: {profile}", ln=True)
                pdf.cell(200, 10, txt="Recommended Funds:", ln=True)
                for fund in funds:
                    pdf.cell(200, 10, txt=f"- {fund}", ln=True)

                pdf_output = "client_report.pdf"
                pdf.output(pdf_output)
                return send_file(pdf_output, as_attachment=True)

    return render_template_string(html_form, profile=profile, funds=funds, name=name)

if __name__ == '__main__':
    app.run(debug=True)