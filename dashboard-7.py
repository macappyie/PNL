import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Page config
st.set_page_config(page_title="PNL Dashboard", layout="wide")
st.title("💰 Profit & Loss Dashboard")

# Load Excel file
FILE_PATH = "PNL.xlsx"
try:
    df = pd.read_excel(FILE_PATH)
    df.columns = [col.strip() for col in df.columns]
except Exception as e:
    st.error(f"❗ Failed to load Excel file: {e}")
    st.stop()

# Validate required columns
if 'Txn Date' not in df or 'Credit' not in df or 'Debit' not in df:
    st.error("❗ Excel file must have columns: 'Txn Date', 'Credit', and 'Debit'.")
    st.stop()

# Preprocess data
df['Txn Date'] = pd.to_datetime(df['Txn Date'])
df['Credit'] = pd.to_numeric(df['Credit'], errors='coerce').fillna(0)
df['Debit'] = pd.to_numeric(df['Debit'], errors='coerce').fillna(0)
df['Net P&L'] = df['Credit'] - df['Debit']
df['Month_dt'] = df['Txn Date'].dt.to_period('M').dt.to_timestamp()
df['Year'] = df['Txn Date'].dt.year

# Year filter
available_years = sorted(df['Year'].unique())
selected_year = st.selectbox("📅 Filter by Year (optional)", ["All"] + list(map(str, available_years)))

if selected_year != "All":
    df = df[df['Year'] == int(selected_year)]

# Monthly P&L
monthly_pnl = df.groupby('Month_dt')['Net P&L'].sum().reset_index()
monthly_pnl['Color'] = monthly_pnl['Net P&L'].apply(lambda x: 'green' if x >= 0 else 'red')

st.subheader("📅 Monthly Profit & Loss (Interactive)")
fig = go.Figure()
fig.add_trace(go.Bar(
    x=monthly_pnl['Month_dt'],
    y=monthly_pnl['Net P&L'],
    marker_color=monthly_pnl['Color'],
    hovertemplate='<b>%{x|%B %Y}</b><br>Net P&L: ₹%{y:,.2f}<extra></extra>',
))
fig.update_layout(
    xaxis=dict(title='Month', tickformat='%b %Y', tickangle=-45, rangeslider=dict(visible=True)),
    yaxis=dict(title='Net P&L'),
    plot_bgcolor='white',
    height=400,
    margin=dict(l=30, r=30, t=30, b=30)
)
st.plotly_chart(fig, use_container_width=True)

# Yearly P&L
yearly_pnl = df.groupby('Year')['Net P&L'].sum().reset_index()
st.subheader("📆 Yearly Profit & Loss")
st.bar_chart(yearly_pnl.set_index('Year'))

# Highest Profit & Loss
st.subheader("📈 Highest Profit & 📉 Highest Loss")
max_profit = df.loc[df['Net P&L'].idxmax()]
max_loss = df.loc[df['Net P&L'].idxmin()]
col1, col2 = st.columns(2)
with col1:
    st.metric("💚 Highest Profit", f"₹{max_profit['Net P&L']:.2f}", delta=f"on {max_profit['Txn Date'].date()}")
with col2:
    st.metric("💔 Highest Loss", f"₹{max_loss['Net P&L']:.2f}", delta=f"on {max_loss['Txn Date'].date()}")

# Net Profit vs Net Loss
st.subheader("📊 Net Profit vs Net Loss Summary")
total_profit = df[df['Net P&L'] > 0]['Net P&L'].sum()
total_loss = df[df['Net P&L'] < 0]['Net P&L'].sum()
net_total = total_profit + total_loss

fig4 = go.Figure()
fig4.add_trace(go.Bar(x=['Total Profit'], y=[total_profit], marker_color='green'))
fig4.add_trace(go.Bar(x=['Total Loss'], y=[abs(total_loss)], marker_color='red'))
fig4.update_layout(
    barmode='group',
    yaxis_title="Amount",
    plot_bgcolor='white',
    height=300,
    margin=dict(l=30, r=30, t=30, b=30),
    showlegend=False
)
st.plotly_chart(fig4, use_container_width=True)

# Net Summary
st.subheader("📌 Net Summary")
col1, col2, col3 = st.columns(3)
col1.metric("🟢 Total Profit", f"₹{total_profit:,.2f}")
col2.metric("🔴 Total Loss", f"₹{abs(total_loss):,.2f}")
col3.metric("🧾 Net Total", f"₹{net_total:,.2f}", delta="Profit" if net_total >= 0 else "Loss")

# Performance Insights
st.subheader("📈 Performance Insights")
total_trades = len(df)
winning_trades = len(df[df['Net P&L'] > 0])
losing_trades = len(df[df['Net P&L'] < 0])
win_ratio = (winning_trades / total_trades) * 100 if total_trades > 0 else 0
avg_monthly = monthly_pnl['Net P&L'].mean() if not monthly_pnl.empty else 0

col4, col5, col6, col7 = st.columns(4)
col4.metric("📊 Total Trades", f"{total_trades}")
col5.metric("✅ Wins", f"{winning_trades}")
col6.metric("❌ Losses", f"{losing_trades}")
col7.metric("🏆 Win Ratio", f"{win_ratio:.2f}%")
st.metric("📅 Avg Monthly P&L", f"₹{avg_monthly:,.2f}")

# ✅✅ Debugging Actual June 2025 Calculation
st.subheader("🐞 Debug: Actual June 2025 P&L from Data")
june_debug = df[df['Txn Date'].dt.to_period('M') == pd.Period('2025-06')]
st.write("🔢 Transaction Count:", len(june_debug))
st.metric("📉 June 2025 Net P&L", f"₹{june_debug['Net P&L'].sum():,.2f}")
st.dataframe(june_debug[['Txn Date', 'Credit', 'Debit', 'Net P&L']])

