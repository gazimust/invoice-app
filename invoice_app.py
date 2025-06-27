import streamlit as st
from jinja2 import Environment, FileSystemLoader
from datetime import date

# Set paths
TEMPLATE_DIR = "templates"

st.set_page_config(page_title="Invoice Generator", layout="wide")
st.title("🧾 Invoice Generator for MET Logistics Ltd")

# Sidebar
st.sidebar.header("Invoice From")
invoice_from = st.sidebar.text_area("Name & Address", "Name\nAddress Line 1\nAddress Line 2\nPostcode")

st.sidebar.header("Payment Info")
sort_code = st.sidebar.text_input("Sort Code", "04-00-72")
account_no = st.sidebar.text_input("Account Number", "24348341")

with st.form("invoice_form"):
    st.subheader("Invoice Details")

    col1, col2, col3 = st.columns(3)
    with col1:
        invoice_number = st.text_input("Invoice Number", f"25-01-01")
    with col2:
        invoice_date = st.date_input("Invoice Date", date.today())
    with col3:
        tax_point = st.date_input("Tax Point", date.today())

    payment_due = st.date_input("Payment Due Date", date.today())

    depot = st.text_input("Depot", "DBR1")
    week_no = st.text_input("Week No.", "21")
    week_commencing = st.date_input("Week Commencing", date.today())

    st.subheader("Line Items")
    item_count = st.number_input("Number of Items", min_value=1, max_value=20, value=1)

    items = []
    for i in range(int(item_count)):
        st.markdown(f"### Item {i + 1}")
        description = st.text_input(f"Description {i + 1}", key=f"desc{i}")
        unit_cost = st.number_input(f"Unit Cost (£) {i + 1}", min_value=0.0, step=0.01, key=f"unit{i}")
        quantity = st.number_input(f"Quantity {i + 1}", min_value=0.0, step=1.0, key=f"qty{i}")
        net = unit_cost * quantity
        items.append({
            "description": description,
            "unit_cost": f"{unit_cost:.2f}",
            "quantity": f"{quantity:.0f}",
            "net": f"{net:.2f}"
        })

    admin_fee = st.checkbox("Add Admin Fee (£12.50)", value=False)
    wise_line = st.checkbox("Include Wise Line", value=True)

    total = sum(float(item["net"]) for item in items)
    if admin_fee:
        total += 12.50

    submitted = st.form_submit_button("Preview Invoice")

# Render Invoice
if submitted:
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template("invoice_template.html")
    html_out = template.render(
        invoice_from=invoice_from.replace("\n", "<br>"),
        invoice_number=invoice_number,
        invoice_date=invoice_date.strftime("%d/%m/%Y"),
        tax_point=tax_point.strftime("%d/%m/%Y"),
        payment_due_date=payment_due.strftime("%d/%m/%Y"),
        depot=depot,
        week_no=week_no,
        week_commencing=week_commencing.strftime("%d/%m/%Y"),
        items=items,
        admin_fee=admin_fee,
        total=f"{total:.2f}",
        sort_code=sort_code,
        account_no=account_no,
        wise_line=wise_line
    )

    st.subheader("Preview Invoice")
    st.components.v1.html(html_out, height=900, scrolling=True)

    if st.button("Generate Invoice HTML File"):
        html_bytes = html_out.encode('utf-8')
        st.download_button(
            label="📥 Download Invoice as HTML",
            data=html_bytes,
            file_name=f"Invoice_{invoice_number}.html",
            mime="text/html",
        )
        st.success("✅ Invoice generated. Click the button above to download.")
