import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# ------------------------------
# 🌈 Custom CSS Styling
# ------------------------------
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #f3f4f6, #dbeafe);
        font-family: 'Segoe UI', sans-serif;
    }
    .stTitle {
        font-size: 3em;
        font-weight: 800;
        color: #1f2937;
        text-shadow: 1px 1px 1px #d1d5db;
    }
    .stMarkdown {
        background: rgba(255, 255, 255, 0.9);
        padding: 1.2em;
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    }
    .summary-box {
        background-color: #ffffff;
        padding: 1em 2em;
        border-radius: 10px;
        margin-bottom: 1em;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

# ------------------------------
# 📈 App Title
# ------------------------------
st.title("📈 Interest Payment Tracker (Single Investor)")

# --- Investment Parameters ---
investment_date = "10-Dec-24"
amount_invested = 200000
annual_roi = 36  # percent
monthly_profit = 6000
months_paid = 5
months = list(range(1, 13))
total_paid = months_paid * monthly_profit

# --- Calculate Dates ---
investment_datetime = datetime.strptime(investment_date, "%d-%b-%y")
final_refund_date = investment_datetime.replace(year=investment_datetime.year + 1)
refund_str = final_refund_date.strftime("%d-%b-%Y")

# --- Monthly Payouts DataFrame ---
df_months = pd.DataFrame({
    "Month": months,
    "Pay Date": pd.date_range(start="10-Jan-2025", periods=12, freq='MS') + pd.DateOffset(days=9),
    "Amount Paid": [monthly_profit if m <= months_paid else 0 for m in months]
})

df_months["Status"] = df_months["Amount Paid"].apply(lambda x: "✅ Paid" if x > 0 else "⏳ Upcoming")
df_months["Emoji"] = df_months["Status"].map({"✅ Paid": "📤", "⏳ Upcoming": "⏳"})
df_months["Label"] = df_months.apply(lambda row: f"{row['Emoji']} ₹{row['Amount Paid']:,.0f}" if row['Amount Paid'] > 0 else row['Emoji'], axis=1)

# --- Append Final Refund ---
df_stacked = df_months.copy()
df_stacked.loc[len(df_stacked)] = {
    "Month": 13,
    "Pay Date": final_refund_date,
    "Amount Paid": amount_invested,
    "Status": "🧾 Refund Principal",
    "Emoji": "💸",
    "Label": f"💸 ₹{amount_invested:,.0f}"
}

# ------------------------------
# 📊 Bar Chart with Emojis
# ------------------------------
fig = px.bar(
    df_stacked,
    x="Month",
    y="Amount Paid",
    color="Status",
    text="Label",
    color_discrete_map={
        "✅ Paid": "#22c55e",
        "⏳ Upcoming": "#9ca3af",
        "🧾 Refund Principal": "#3b82f6"
    },
    title="💸 Monthly Interest + Final Refund"
)

fig.update_traces(textposition="outside")
fig.update_layout(
    xaxis_title="Month",
    yaxis_title="₹ Amount",
    yaxis_tickprefix="₹",
    yaxis_tickformat=",",
    xaxis=dict(tickmode='linear'),
    plot_bgcolor="#ffffff",
    paper_bgcolor="#ffffff",
    showlegend=True,
    transition=dict(duration=500)
)
fig.update_xaxes(
    tickvals=list(range(1, 14)),
    ticktext=[str(m) if m < 13 else "Refund" for m in range(1, 14)]
)

st.plotly_chart(fig, use_container_width=True)

# ------------------------------
# 🧾 Summary Section
# ------------------------------
total_interest = monthly_profit * 12

st.subheader("💰 Summary")
st.markdown(f"""
<div class="summary-box">
- 📅 **Investment Date:** {investment_date}  
- 💼 **Amount Invested:** ₹{amount_invested:,}  
- 📈 **Annual ROI:** {annual_roi}%  
- 💸 **Monthly Payout:** ₹{monthly_profit:,}  
- ✅ **Paid Till Date:** ₹{total_paid:,}  
- 🔁 **Total Interest (1 Year):** ₹{total_interest:,}  
- 🧾 **Final Refund After Lock-In:** ₹{amount_invested:,} on **{refund_str}**  
</div>
""", unsafe_allow_html=True)

