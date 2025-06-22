import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import requests

# === Configuration ===
TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN"
REMINDER_DAYS = 7

# === Page Setup ===
st.set_page_config(page_title="Investor Tracker", layout="wide")
st.title("📈 Monthly Interest & Refund Tracker")

# === Load Data ===
@st.cache_data
def load_data(path="INVESTMENT.xlsx"):
    df = pd.read_excel(path)
    df.columns = df.columns.str.strip().str.upper()
    return df

try:
    df_data = load_data()
except:
    st.error("❌ Could not load 'INVESTMENT.xlsx'. Make sure it's present and well-formatted.")
    st.stop()

required_cols = {"NAME", "AMOUNT", "ROI", "MONTHS_PAID"}
if not required_cols.issubset(df_data.columns):
    st.error(f"❌ Missing columns: {required_cols - set(df_data.columns)}")
    st.stop()

# === Select Investor ===
investor = st.selectbox("👤 Select Investor", df_data["NAME"].unique())
row = df_data[df_data["NAME"] == investor].iloc[0]

# === Manual Chat ID Mapping ===
chat_id_map = {
    "Atul": "123456789",
    "Shruti": "234567890",
    "Raj": "345678901",
    # Add more investors here
}

chat_id = chat_id_map.get(investor, "")
if not chat_id:
    st.warning(f"⚠️ No chat ID found for {investor}. Please update chat_id_map.")

# === Extract Fields ===
amount = row["AMOUNT"]
roi = row["ROI"]
months_paid = int(row["MONTHS_PAID"])
monthly_profit = round((amount * roi / 100) / 12)
total_interest = monthly_profit * 12
total_paid = months_paid * monthly_profit

# === Dates ===
investment_date = None  # Not using actual dates
refund_str = "End of Month 12"

# === Monthly Payout Table ===
df_months = pd.DataFrame({
    "Month": list(range(1, 13)),
    "Amount Paid": [monthly_profit if m <= months_paid else 0 for m in range(1, 13)]
})
df_months["Status"] = df_months["Amount Paid"].apply(lambda x: "✅ Paid" if x > 0 else "⏳ Upcoming")
df_months.loc[12] = [13, amount, "🔚 Refund"]

# === Chart ===
fig = px.bar(
    df_months,
    x="Month",
    y="Amount Paid",
    color="Status",
    text="Amount Paid",
    color_discrete_map={"✅ Paid": "green", "⏳ Upcoming": "lightgray", "🔚 Refund": "orange"},
    title=f"📊 Monthly Interest & Refund for {investor}"
)
fig.update_layout(xaxis_title="Month", yaxis_title="₹ Amount", yaxis_tickprefix="₹", xaxis=dict(tickmode='linear'))
fig.update_xaxes(tickvals=list(range(1, 14)), ticktext=[str(m) if m <= 12 else "Refund" for m in range(1, 14)])
st.plotly_chart(fig, use_container_width=True)

# === Summary ===
st.subheader("🧾 Summary")
st.markdown(f"""
- 💼 **Investor:** `{investor}`  
- 💰 **Amount Invested:** ₹{amount:,.0f}  
- 📈 **Annual ROI:** {roi}%  
- 💸 **Monthly Payout:** ₹{monthly_profit:,.0f}  
- ✅ **Months Paid:** `{months_paid}` / 12  
- 💵 **Total Paid So Far:** ₹{total_paid:,.0f}  
- 🔁 **Interest Expected (1 Yr):** ₹{total_interest:,.0f}
""")

# === Refund Highlight ===
st.markdown("---")
st.subheader("🔚 Final Refund Details")
st.info(f"""
💰 **₹{amount:,.0f}** will be refunded to **{investor}**  
📅 On **{refund_str}** (at the end of the 12-month lock-in)
""")

# === Telegram Alerts ===
def send_telegram_msg(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        st.warning(f"⚠️ Telegram failed: {e}")

# Refund Reminder (simulate if months_paid == 11)
if months_paid == 11:
    send_telegram_msg(
        chat_id,
        f"👋 Hey {investor}!\n\n🎯 Your ₹{amount:,.0f} refund is coming soon (Month 12)!\n"
        f"⏰ Just 1 month left!\n🪃 Sit tight — your money’s coming back!\n\n🤖 ~ Your Investment Bot"
    )

# Monthly Payout Alerts
for i in range(months_paid):
    pay_month = i + 1
    send_telegram_msg(
        chat_id,
        f"💸 *Month {pay_month} Payout Sent!*\n\n👤 *{investor}*\n💰 ₹{monthly_profit:,.0f}\n📆 Month {pay_month}\n\n☕ Enjoy the chai & profits!\n\n🤖 ~ Your Bot"
    )

# Loss Alert
expected_paid = months_paid * monthly_profit
if expected_paid < (roi * amount / 100):
    send_telegram_msg(
        chat_id,
        f"😅 Dear {investor},\n\nWe know it's a little red 📉 right now...\n\n"
        f"💸 Received: ₹{expected_paid:,.0f}\n🧮 Full ROI Expected: ₹{total_interest:,.0f}\n\n"
        f"🕰️ Hang tight — recovery is on its way! 🔁\n☀️ Good days ahead!\n\n🤖 ~ Friendly Profit Bot"
    )
