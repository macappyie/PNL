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

# --- Calculate Final Refund Date ---
investment_datetime = datetime.strptime(investment_date, "%d-%b-%y")
final_refund_date = investment_datetime.replace(year=investment_datetime.year + 1)
refund_str = final_refund_date.strftime("%d-%b-%Y")

# --- Create Monthly Payout DataFrame ---
df_months = pd.DataFrame({
    "Month": months,
    "Pay Date": pd.date_range(start="10-Jan-2025", periods=12, freq='MS') + pd.DateOffset(days=9),
    "Amount Paid": [monthly_profit if m <= months_paid else 0 for m in months]
})
df_months["Status"] = df_months["Amount Paid"].apply(lambda x: "✅ Paid" if x > 0 else "⏳ Upcoming")

# --- Add Emoji Markers ---
df_months["Emoji"] = df_months["Status"].map({
    "✅ Paid": "📤",
    "⏳ Upcoming": "⏳"
})
df_months["Label"] = df_months.apply(
    lambda row: f"{row['Emoji']} ₹{row['Amount Paid']:,.0f}" if row['Amount Paid'] > 0 else row['Emoji'],
    axis=1
)

# --- Add Refund Row (Principal) ---
df_stacked = df_months.copy()
df_stacked.loc[len(df_stacked)] = {
    "Month": 13,
    "Pay Date": final_refund_date,
    "Amount Paid": amount_invested,
    "Status": "🧾 Refund Principal",
    "Emoji": "💸",
    "Label": f"💸 ₹{amount_invested:,.0f}"
}

# --- Plotly Bar Chart with Emojis & Animation ---
fig = px.bar(
    df_stacked,
    x="Month",
    y="Amount Paid",
    color="Status",
    text="Label",
    hover_data={"Pay Date": True, "Amount Paid": True, "Label": False},
    color_discrete_map={
        "✅ Paid": "#2ecc71",               # Green
        "⏳ Upcoming": "#bdc3c7",           # Grey
        "🧾 Refund Principal": "#3498db"    # Blue
    },
    title="💸 Monthly Interest + Final Refund"
)

fig.update_traces(textposition='outside')
fig.update_layout(
    xaxis_title="Month",
    yaxis_title="₹ Amount",
    yaxis_tickprefix="₹",
    yaxis_tickformat=",",
    plot_bgcolor="#f9f9f9",
    paper_bgcolor="#f9f9f9",
    font=dict(size=14),
    xaxis=dict(tickmode='linear'),
    showlegend=True,
    transition=dict(duration=500)  # 👈 Animation
)
fig.update_xaxes(
    tickvals=list(range(1, 14)),
    ticktext=[str(m) if m < 13 else "Refund" for m in range(1, 14)]
)

st.plotly_chart(fig, use_container_width=True)

# --- Summary Section ---
st.subheader("💰 Summary")
total_interest = monthly_profit * 12
st.markdown(f"""
- 📅 **Investment Date:** {investment_date}  
- 💼 **Amount Invested:** ₹{amount_invested:,}  
- 📈 **Annual ROI:** {annual_roi}%  
- 💸 **Monthly Payout:** ₹{monthly_profit:,}  
- ✅ **Paid Till Date:** ₹{total_paid:,}  
- 🔁 **Total Interest (1 Year):** ₹{total_interest:,}  
- 🧾 **Final Refund After Lock-In:** ₹{amount_invested:,}
""")

# --- Final Refund Notice ---
st.markdown("---")
st.subheader("🔚 Final Refund Details")
st.info(f"""
💰 **₹{amount_invested:,}** will be refunded  
📅 On **{refund_str}** (End of Lock-In Period)
""")

