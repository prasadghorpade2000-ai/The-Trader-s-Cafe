import streamlit as st
import pandas as pd
import qrcode
from io import BytesIO
from datetime import datetime
import urllib.parse
import os

# --- CONFIGURATION ---
CAFE_NAME = "The Trader's Cafe"
INSTAGRAM_HANDLE = "the_traders_cafe"
CURRENCY = "₹"

st.set_page_config(page_title=CAFE_NAME, layout="wide", initial_sidebar_state="expanded")

# --- STYLING ---
st.markdown("""
    <style>
    .main { background-color: #f5f5f5; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; }
    .cat-header { color: #2e7d32; font-weight: bold; border-bottom: 2px solid #2e7d32; }
    </style>
    """, unsafe_allow_html=True)

# --- DATABASE SETUP ---
if not os.path.isfile('cafe_sales.csv'):
    df = pd.DataFrame(columns=['Date', 'Item', 'Price', 'Qty', 'Total', 'Phone'])
    df.to_csv('cafe_sales.csv', index=False)

# --- MENU DATA ---
menu = {
    "☕ Coffee & Tea": {"Cappuccino": 180, "Iced Latte": 200, "Masala Chai": 50, "Espresso": 120},
    "🍔 Snacks": {"Paneer Wrap": 150, "Club Sandwich": 120, "Peri Peri Fries": 110},
    "🍰 Desserts": {"Choco Lava Cake": 110, "Brownie": 95}
}

# --- SESSION STATE ---
if 'cart' not in st.session_state:
    st.session_state.cart = {}

# --- HELPER FUNCTIONS ---
def generate_qr(data):
    qr = qrcode.QRCode(version=1, box_size=10, border=2)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

# --- SIDEBAR (BILLING & SOCIAL) ---
st.sidebar.title(f"🛒 {CAFE_NAME}")
customer_phone = st.sidebar.text_input("Customer Phone (91...)", placeholder="91XXXXXXXXXX")

total_bill = 0
if st.session_state.cart:
    st.sidebar.subheader("Current Order")
    for item, qty in st.session_state.cart.items():
        # Get price
        price = next(p for cat in menu.values() for i, p in cat.items() if i == item)
        subtotal = price * qty
        total_bill += subtotal
        st.sidebar.write(f"{item} x {qty} = {CURRENCY}{subtotal}")
    
    st.sidebar.markdown("---")
    st.sidebar.header(f"Total: {CURRENCY}{total_bill}")

    if st.sidebar.button("✅ Confirm & Send Bill"):
        # Save to CSV
        records = [[datetime.now().strftime("%Y-%m-%d %H:%M"), i, 0, q, 0, customer_phone] for i, q in st.session_state.cart.items()]
        pd.DataFrame(records).to_csv('cafe_sales.csv', mode='a', header=False, index=False)
        
        # WhatsApp Link
        msg = f"Thanks for visiting *{CAFE_NAME}*! \nYour total bill is *{CURRENCY}{total_bill}*. \nFollow us: instagram.com/{INSTAGRAM_HANDLE}"
        wa_url = f"https://wa.me/{customer_phone}?text={urllib.parse.quote(msg)}"
        st.sidebar.success("Bill Saved!")
        st.sidebar.markdown(f"[📲 Click to send WhatsApp Bill]({wa_url})")
        st.session_state.cart = {}

    if st.sidebar.button("🗑️ Clear Cart"):
        st.session_state.cart = {}
        st.rerun()
else:
    st.sidebar.info("Cart is empty")

st.sidebar.markdown("---")
if st.sidebar.button("📸 Show Instagram QR"):
    st.sidebar.image(generate_qr(f"https://instagram.com/{INSTAGRAM_HANDLE}"), caption="Scan to Follow")

# --- MAIN INTERFACE ---
st.title("Bake Your Taste 🥧")
tabs = st.tabs(list(menu.keys()))

for i, category in enumerate(menu.keys()):
    with tabs[i]:
        items = menu[category]
        cols = st.columns(3)
        for idx, (item, price) in enumerate(items.items()):
            with cols[idx % 3]:
                st.write(f"### {item}")
                st.write(f"Price: {CURRENCY}{price}")
                if st.button(f"Add {item}", key=f"add_{item}"):
                    st.session_state.cart[item] = st.session_state.cart.get(item, 0) + 1
                    st.rerun()

# --- ADMIN SECTION ---
with st.expander("📊 View Sales Report"):
    if os.path.exists('cafe_sales.csv'):
        report_df = pd.read_csv('cafe_sales.csv')
        st.dataframe(report_df.tail(20), use_container_width=True)
