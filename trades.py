
import streamlit as st
from kiteconnect import KiteConnect
import pandas as pd
import plotly.graph_objects as go

# Kite Connect setup
API_KEY = "awh2j04pcd83zfvq"
ACCESS_TOKEN = "ZRhKTJpPt9SFCFmELIA0qJnL1pos2tFr"

kite = KiteConnect(api_key=API_KEY)
kite.set_access_token(ACCESS_TOKEN)

st.set_page_config(page_title="Kite Daily P&L", layout="wide")
st.title("📅 Kite Daily Trade Tracker")



# 🧾 Fetch trades
try:
    trades = kite.trades()
    df = pd.DataFrame(trades)

    if df.empty:
        st.warning("No trades found.")
    else:
        df['date'] = pd.to_datetime(df['exchange_timestamp']).dt.date
        df['pnl'] = df['average_price'] * df['quantity']
        df['pnl'] = df['pnl'].where(df['transaction_type'] == 'SELL', -df['pnl'])

        # Group by date
        daily_summary = df.groupby('date').agg(
            Trades=('order_id', 'nunique'),
            Net_PnL=('pnl', 'sum')
        ).reset_index()

        # 📋 Daily table
        st.subheader("📋 Daily Summary")
        st.dataframe(daily_summary.sort_values(by='date', ascending=False), use_container_width=True)

        # 📈 Daily bar chart
        st.subheader("📈 Daily Net P&L Chart")
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=daily_summary['date'],
            y=daily_summary['Net_PnL'],
            marker_color=['green' if x >= 0 else 'red' for x in daily_summary['Net_PnL']],
            hovertemplate='Date: %{x}<br>Net P&L: ₹%{y:.2f}<extra></extra>'
        ))
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Net P&L",
            height=400,
            plot_bgcolor='white',
            xaxis_tickangle=-45
        )
        st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"⚠️ Error loading trades: {e}")

