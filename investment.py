
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import requests

# === Configuration ===
TELEGRAM_BOT_TOKEN = "8060596624:AAEy0fb4tMTGtBJBywF-fHXmwjIYhVDQzjs"
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

required_cols = {"NAME", "AMOUNT", "ROI", "MONTHS_PAID", "START_DATE", "CHAT_ID"}
if not required_cols.issubset(df_data.columns):
    st.error(f"❌ Missing columns: {required_cols - set(df_data.columns)}")
    st.stop()

# === Select Investor ===
investor = st.selectbox("👤 Select Investor", df_data["NAME"].unique())
row = df_data[df_data["NAME"] == investor].iloc[0]

# === Extract Fields ===
amount = row["AMOUNT"]
roi = row["ROI"]
months_paid = int(row["MONTHS_PAID"])
monthly_profit = round((amount * roi / 100) / 12)
total_interest = monthly_profit * 12
total_paid = months_paid * monthly_profit
chat_id = str(row["CHAT_ID"]).strip()

# === Dates ===
investment_date = pd.to_datetime(row["START_DATE"], dayfirst=True, errors='coerce')
refund_date = investment_date + pd.DateOffset(months=12) if pd.notnull(investment_date) else pd.NaT
refund_str = refund_date.strftime('%d-%b-%Y') if pd.notnull(refund_date) else "N/A"

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
📅 On **{refund_str}** (after 1-year lock-in from investment date)
""")

# === Telegram Alerts ===
def send_telegram_msg(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": 8108934088, "text": text, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        st.warning(f"⚠️ Telegram failed: {e}")

# Refund Reminder
if pd.notnull(refund_date):
    days_left = (refund_date - datetime.today()).days
    if 0 <= days_left <= REMINDER_DAYS:
        send_telegram_msg(
            chat_id,
            f"👋 Hey {investor}!\n\n🎯 Your ₹{amount:,.0f} refund is scheduled on *{refund_str}*\n"
            f"⏰ That's just *{days_left} day{'s' if days_left > 1 else ''}* away!\n"
            f"🪃 Sit tight — your money’s coming back!\n\n🤖 ~ Your Investment Bot"
        )

# Monthly Payout Alerts
for i in range(months_paid):
    pay_month = i + 1
    pay_date = investment_date + pd.DateOffset(months=pay_month)
    send_telegram_msg(
        chat_id,
        f"💸 *Month {pay_month} Payout Sent!*\n\n👤 *{investor}*\n💰 ₹{monthly_profit:,.0f}\n📆 {pay_date.strftime('%d-%b-%Y')}\n\n☕ Enjoy the chai & profits!\n\n🤖 ~ Your Bot"
    )

# Loss Alert
days_since_investment = (datetime.today() - investment_date).days
expected_months = min(days_since_investment // 30, 12)
expected_paid = expected_months * monthly_profit
actual_paid = months_paid * monthly_profit

if actual_paid < expected_paid:
    send_telegram_msg(
        chat_id,
        f"😅 Dear {investor},\n\nWe know it's a little red 📉 right now...\n\n"
        f"💸 Received: ₹{actual_paid:,.0f}\n🧮 Expected: ₹{expected_paid:,.0f}\n\n"
        f"🕰️ Hang tight — recovery is on its way! 🔁\n☀️ Good days ahead!\n\n🤖 ~ Friendly Profit Bot"
    )

