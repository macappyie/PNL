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

# --- Static Styled Bar Chart ---
st.subheader("💸 Monthly Payout Overview (₹ Style Bars)")

fig = px.bar(
    df_months,
    x="Month",
    y="Amount Paid",
    color="Status",
    text="Amount Paid",
    color_discrete_map={"✅ Paid": "#00cc96", "⏳ Upcoming": "#d3d3d3"},
    title="💸 ₹ Interest Payout Summary"
)

fig.update_layout(
    yaxis_tickprefix="₹",
    yaxis_tickformat=",",
    xaxis=dict(tickmode='linear'),
    plot_bgcolor="#f9f9f9",
    paper_bgcolor="#f0f2f6",
    font=dict(family="Arial", size=14),
    bargap=0.3,
    height=420,
    showlegend=True
)

fig.update_traces(
    texttemplate="₹%{text:.0f}",
    textposition="outside",
    marker=dict(
        line=dict(width=1.5, color='black')
    )
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

# --- Calculate Final Refund Date ---
investment_datetime = datetime.strptime(investment_date, "%d-%b-%y")
final_refund_date = investment_datetime.replace(year=investment_datetime.year + 1)
refund_str = final_refund_date.strftime("%d-%b-%Y")

# --- Show Refund Date Notice ---
st.markdown("---")
st.subheader("🔚 Final Refund Details")
st.info(f"""
💰 **₹{final_refund:,}** will be refunded  
📅 On **{refund_str}** (End of Lock-In Period)
""")

