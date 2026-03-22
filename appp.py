import streamlit as st
import pandas as pd
import qrcode
from io import BytesIO
from datetime import datetime
import urllib.parse
import os

# --- CONFIGURATION ---
CAFE_NAME = "The Trader's Cafe"
TAGLINE = "Bake Your Taste 🥧"
INSTAGRAM_HANDLE = "the_traders_cafe"

st.set_page_config(page_title=CAFE_NAME, layout="wide")

# --- CUSTOM MENU DATA (As per your sample) ---
menu = {
    "🍕 Pizza": {
        "Golden Corn": 59,
        "Testy Tomato": 49,
        "Shiney Onion": 49,
        "Choppy Capcicum": 49,
        "Spicy Shezwan": 79,
        "Mighty Paneer Pizza": 79,
        "Mixed Veges Spicy": 69
    },
    "🍔 Burger": {
        "Classic Burger": 39,
        "Cheese Burger": 55,
        "Spicy Salsa": 59,
        "Royal Paneer Grill Burger": 69
    },
    "🥪 Sandwich": {
        "Grill Sandwich": 39,
        "Vegs Cheese Sandwich": 49,
        "Schezwan Sandwich": 49,
        "Choklet Sandwich": 59
    }
}

# --- DATABASE SETUP ---
if not os.path.isfile('cafe_sales.csv'):
    df = pd.DataFrame(columns=['Date', 'Item', 'Qty', 'Total', 'Phone'])
    df.to_csv('cafe_sales.csv', index=False)

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

# --- UI LAYOUT ---
st.title(CAFE_NAME)
st.subheader(TAGLINE)

col1, col2 = st.columns()

with col1:
    tabs = st.tabs(list(menu.keys()))
    for i, category in enumerate(menu.keys()):
        with tabs[i]:
            items = menu[category]
            cols = st.columns(2) # Mobile par 2 columns ache lagte hain
            for idx, (item, price) in enumerate(items.items()):
                with cols[idx % 2]:
                    st.info(f"**{item}**\n\n₹{price}")
                    if st.button(f"Add {item}", key=f"add_{item}"):
                        st.session_state.cart[item] = st.session_state.cart.get(item, 0) + 1
                        st.rerun()

with col2:
    st.header("🛒 Bill Detail")
    total_bill = 0
    cust_phone = st.text_input("Customer Phone", placeholder="91XXXXXXXXXX")
    
    if st.session_state.cart:
        for item, qty in st.session_state.cart.items():
            # Find price
            price = 0
            for cat in menu:
                if item in menu[cat]:
                    price = menu[cat][item]
            subtotal = price * qty
            total_bill += subtotal
            st.write(f"**{item}** x {qty} = ₹{subtotal}")

        st.markdown("---")
        st.subheader(f"Total: ₹{total_bill}")

        if st.button("Confirm & WhatsApp Bill", use_container_width=True):
            # Save to CSV
            new_records = [[datetime.now().strftime("%Y-%m-%d %H:%M"), i, q, 0, cust_phone] for i, q in st.session_state.cart.items()]
            pd.DataFrame(new_records).to_csv('cafe_sales.csv', mode='a', header=False, index=False)
            
            # WhatsApp Link
            msg = f"Thanks for visiting *{CAFE_NAME}*! \nYour bill is *₹{total_bill}*. \nFollow us on Instagram: instagram.com/{INSTAGRAM_HANDLE}"
            wa_url = f"https://wa.me/{cust_phone}?text={urllib.parse.quote(msg)}"
            st.success("Order Saved!")
            st.markdown(f"[📲 Send Bill to WhatsApp]({wa_url})")
            st.session_state.cart = {}

        if st.button("Clear Cart", type="secondary"):
            st.session_state.cart = {}
            st.rerun()

    st.markdown("---")
    if st.button("📸 Instagram QR"):
        st.image(generate_qr(f"https://instagram.com/{INSTAGRAM_HANDLE}"), width=150)
