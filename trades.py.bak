
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




try:
    # 🧾 Fetch trades
    trades = kite.trades()
    df = pd.DataFrame(trades)

    if df.empty:
        st.warning("No trades found.")
    else:
        # 📦 Preprocess
        df['date'] = pd.to_datetime(df['exchange_timestamp']).dt.date
        df['pnl'] = df['average_price'] * df['quantity']
        df['pnl'] = df['pnl'].where(df['transaction_type'] == 'SELL', -df['pnl'])

        # 📅 Daily Summary
        daily_summary = df.groupby('date').agg(
            Trades=('order_id', 'nunique'),
            Net_PnL=('pnl', 'sum')
        ).reset_index()

        st.subheader("📋 Daily Trade Summary")
        st.dataframe(daily_summary.sort_values(by='date', ascending=False), use_container_width=True)

        # 📊 Daily P&L Chart
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

        # 📊 Trade Performance Summary
        profitable_trades = df[df['pnl'] > 0]
        loss_making_trades = df[df['pnl'] < 0]
        total_trades = len(df)
        profitable_count = len(profitable_trades)
        loss_count = len(loss_making_trades)
        win_rate = (profitable_count / total_trades) * 100 if total_trades else 0

        st.subheader("📊 Trade Performance Summary")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Trades", f"{total_trades}")
        col2.metric("✅ Profitable", f"{profitable_count}")
        col3.metric("❌ Loss-Making", f"{loss_count}")
        col4.metric("🏆 Win Rate", f"{win_rate:.2f}%")

        # 📉 Bar Chart: Profitable vs Loss-Making
        st.subheader("📉 Profitable vs Loss-Making Trades")
        fig_bar = go.Figure(data=[
            go.Bar(name='Profitable', x=['Profitable'], y=[profitable_count], marker_color='green'),
            go.Bar(name='Loss-Making', x=['Loss-Making'], y=[loss_count], marker_color='red')
        ])
        fig_bar.update_layout(
            yaxis_title='Number of Trades',
            height=350,
            showlegend=False,
            plot_bgcolor='white',
            title='Trade Outcome Distribution'
        )
        st.plotly_chart(fig_bar, use_container_width=True)

except Exception as e:
    st.error(f"⚠️ Error loading trades: {e}")

