import streamlit as st
import pandas as pd
from fpdf import FPDF
import base64
import datetime
import smtplib
from email.message import EmailMessage
import os

# Load customer and product data
customers = pd.read_csv("customers.csv")
products = pd.read_csv("products.csv")

# Function to send email
def send_email(receiver_email, subject, body, attachment_path):
    sender_email = st.secrets["email"]["address"]
    sender_password = st.secrets["email"]["password"]  # Use secrets or env variables for security

    msg = EmailMessage()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject  # Email subject: "Your invoice is ready"
    msg.set_content(body)

    # Attach PDF
    with open(attachment_path, "rb") as f:
        file_data = f.read()
        file_name = os.path.basename(attachment_path)
        msg.add_attachment(file_data, maintype="application", subtype="pdf", filename=file_name)

    # Send Email
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
        st.success(f"Invoice sent to {receiver_email}")
    except Exception as e:
        st.error(f"Failed to send email: {e}")

# Function to generate invoice PDF
def generate_invoice(customer_id, product_ids, quantities):
    customer = customers[customers['customer_id'] == customer_id].iloc[0]
    selected_products = products[products['product_id'].isin(product_ids)]

    if len(selected_products) != len(quantities):
        st.error("Mismatch between selected products and quantities")
        return None

    invoice_date = datetime.datetime.now().strftime("%d/%m/%Y")
    invoice_number = f"ITCAM{datetime.datetime.now().strftime('%m%d%H%M%S')}"

    pdf = FPDF()
    pdf.add_page()
    pdf.add_font('DejaVu', '', 'DejaVuSans.ttf', uni=True)
    pdf.add_font('DejaVu', 'B', 'DejaVuSans-Bold.ttf', uni=True)

    pdf.set_font("DejaVu", 'B', size=18)
    pdf.cell(200, 15, txt="INVOICE ~ IT CAM Security", ln=True, align='C')
    pdf.set_font("DejaVu", 'B', 10)
    pdf.cell(200, 5, "IT CAM Security Pvt. Ltd.", ln=True, align='C')
    pdf.set_font("DejaVu", '', 10)
    pdf.cell(200, 5, "Mandleshwer Road, Gawali Palasiya, 453441", ln=True, align='C')
    pdf.cell(200, 5, "Phone: 0987654321 | Email: support@itcam.in", ln=True, align='C')
    pdf.image("Mlogo.png", x=165, y=35, w=30)
    pdf.cell(200, 10, txt="", ln=True)

    pdf.set_font("DejaVu", size=12)
    pdf.cell(200, 10, txt=f"Invoice Number: {invoice_number}", ln=True)
    pdf.cell(200, 10, txt=f"Invoice Date: {invoice_date}", ln=True)
    pdf.cell(200, 5, txt="", ln=True)

    # Customer Info
    pdf.set_font("DejaVu", 'B', size=12)
    pdf.cell(200, 10, txt="Customer Details:", ln=True)

    pdf.set_font("DejaVu", size=12)
    pdf.cell(200, 10, txt=f"Customer Name: {customer['customer_name']}", ln=True)
    pdf.cell(200, 10, txt=f"Address: {customer['address']} | Mob: {customer['mobile']}", ln=True)
    pdf.cell(200, 10, txt=f"Email: {customer['email']}", ln=True)
    pdf.cell(200, 10, txt="", ln=True)

    # Table
    pdf.set_font("DejaVu", 'B', size=12)
    pdf.cell(40, 10, txt="Product Id", border=1)
    pdf.cell(70, 10, txt="Product Name", border=1)
    pdf.cell(15, 10, txt="Qty", border=1)
    pdf.cell(30, 10, txt="Unit Price", border=1)
    pdf.cell(30, 10, txt="Total", border=1)
    pdf.ln()

    total = 0
    pdf.set_font("DejaVu", size=12)
    for i, product in selected_products.iterrows():
        quantity = quantities[product_ids.index(product['product_id'])]
        line_total = product['price'] * quantity
        total += line_total
        pdf.cell(40, 10, txt=str(product['product_name']), border=1)
        pdf.cell(70, 10, txt=product['product'], border=1)
        pdf.cell(15, 10, txt=str(quantity), border=1)
        pdf.cell(30, 10, txt=f"₹ {product['price']}", border=1)
        pdf.cell(30, 10, txt=f"₹ {line_total}", border=1)
        pdf.ln()

    pdf.cell(200, 10, txt=" ", ln=True)

    # Total
    pdf.set_font("DejaVu", 'B', size=12)
    pdf.cell(155, 10, txt="Final Total", border=1)
    pdf.cell(30, 10, txt=f"₹ {total}", border=1)

    # Signature
    pdf.ln(35)
    pdf.set_font("DejaVu", 'B', size=12)
    pdf.image("stampseal.png", x=160, y=161, w=40)
    pdf.image("sign.png", x=140, y=169, w=80)
    pdf.cell(0, 9, "Authorized Signatory", ln=True, align='R')
    pdf.cell(0, 9, "Devendra Patidar", ln=True, align='R')
    pdf.set_font("DejaVu", '', size=11)
    pdf.cell(0, 5, "ITCAM Security Pvt. Ltd.", ln=True, align='R')

    filename = f"invoice_{invoice_number}.pdf"
    pdf.output(filename)
    return filename

# Streamlit UI
st.title("Invoice Automation System")
st.markdown("##### by Devendra Patidar")
st.sidebar.image("Mlogo.png", width=100)
st.sidebar.header("Select Customer and Products")

customer_names = customers["customer_name"].tolist()
selected_customer = st.sidebar.selectbox("Customer", customer_names)
customer_id = customers[customers['customer_name'] == selected_customer]['customer_id'].values[0]

product_names = products['product_name'].tolist()
selected_products = st.sidebar.multiselect("Products", product_names)
product_ids = products[products['product_name'].isin(selected_products)]['product_id'].tolist()

quantities = []
for product in selected_products:
    quantity = st.sidebar.number_input(f"Quantity of {product}", min_value=1, max_value=100, value=1)
    quantities.append(quantity)

# Email customization section
email_subject = st.text_input("Email Subject", "IT CAM Security sends invoice!")
email_body = st.text_area("Email Body", "Dear Customer,\n\nPlease find the attached invoice for your recent purchase.\n\nBest regards,\nIT CAM Security Pvt. Ltd.")

if st.sidebar.button("Generate Invoice"):
    if len(product_ids) != len(quantities):
        st.error("Mismatch between selected products and quantities")
    else:
        filename = generate_invoice(customer_id, product_ids, quantities)
        if filename:
            st.success("Invoice Generated Successfully!")
            customer_email = customers[customers['customer_id'] == customer_id]['email'].values[0]
            send_email(customer_email, email_subject, email_body, filename)

            with open(filename, 'rb') as f:
                st.download_button("Download Invoice", data=f, file_name=filename, mime="application/pdf")

            with open(filename, "rb") as f:
                base64_pdf = base64.b64encode(f.read()).decode('utf-8')
            st.markdown(f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>', unsafe_allow_html=True)

# Summary
st.write(f"*Selected Customer:*  {selected_customer}")
st.write("*Selected Products:* ")
for i, product in enumerate(selected_products):
    st.write(f"{product} - {quantities[i]} units")
