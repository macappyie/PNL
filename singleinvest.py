import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(layout="wide")
st.title("📈 Interest Payment Tracker (Single Investor)")

# --- Static sample data ---
investment_date = "10-Dec-24"
amount_invested = 200000
annual_roi = 36  # percent
monthly_profit = 6000
months_paid = 5  # already paid
total_paid = months_paid * monthly_profit
months = list(range(1, 13))

# --- Create DataFrame ---
df_months = pd.DataFrame({
    "Month": months,
    "Pay Date": pd.date_range(start="10-Jan-2025", periods=12, freq='MS') + pd.DateOffset(days=9),
    "Amount Paid": [monthly_profit if m <= months_paid else 0 for m in months]
})

df_months["Status"] = df_months["Amount Paid"].apply(lambda x: "✅ Paid" if x > 0 else "⏳ Upcoming")

# --- Total values ---
total_interest = monthly_profit * 12
final_refund = amount_invested

# --- Plot Bar Chart ---
fig = px.bar(
    df_months,
    x="Month",
    y="Amount Paid",
    color="Status",
    text="Amount Paid",
    color_discrete_map={"✅ Paid": "green", "⏳ Upcoming": "lightgray"},
    title="Monthly Interest Payouts"
)

fig.update_layout(
    xaxis_title="Month",
    yaxis_title="₹ Amount",
    yaxis_tickprefix="₹",
    xaxis=dict(tickmode='linear'),
    showlegend=True
)

st.plotly_chart(fig, use_container_width=True)

# --- Summary ---
st.subheader("💰 Summary")
st.markdown(f"""
- 📅 **Investment Date:** {investment_date}  
- 💼 **Amount Invested:** ₹{amount_invested:,}  
- 📈 **Annual ROI:** {annual_roi}%  
- 💸 **Monthly Payout:** ₹{monthly_profit:,}  
- ✅ **Paid Till Date:** ₹{total_paid:,}  
- 🔁 **Total Interest (1 Year):** ₹{total_interest:,}  
- 🧾 **Final Refund After Lock-In:** ₹{final_refund:,}
""")

