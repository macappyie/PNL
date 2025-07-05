
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
    st.info("🔄 Fetching orders...")
    orders = kite.orders()
    df = pd.DataFrame(orders)

    if df.empty:
        st.warning("No completed orders found.")
        st.stop()

    # ====== Filter only completed BUY/SELL orders ======
    df = df[df['status'] == 'COMPLETE']
    df = df[df['transaction_type'].isin(['BUY', 'SELL'])]

    df = df[['order_id', 'tradingsymbol', 'transaction_type', 'quantity', 'price', 'order_timestamp']]
    df.columns = ['order_id', 'symbol', 'type', 'qty', 'price', 'time']
    df['time'] = pd.to_datetime(df['time'])
    df = df.sort_values('time')

    # ====== FIFO BUY–SELL Matching ======
    matched = []
    for symbol in df['symbol'].unique():
        symbol_df = df[df['symbol'] == symbol]
        buy_queue = []

        for _, row in symbol_df.iterrows():
            qty = row['qty']
            price = row['price']
            typ = row['type']
            time = row['time']

            if typ == 'BUY':
                buy_queue.append({'qty': qty, 'price': price, 'time': time})
            elif typ == 'SELL':
                sell_qty = qty
                sell_price = price

                while sell_qty > 0 and buy_queue:
                    buy = buy_queue[0]
                    match_qty = min(sell_qty, buy['qty'])
                    pnl = (sell_price - buy['price']) * match_qty

                    matched.append({
                        'symbol': symbol,
                        'buy_price': buy['price'],
                        'sell_price': sell_price,
                        'qty': match_qty,
                        'pnl': pnl,
                        'buy_time': buy['time'],
                        'sell_time': time
                    })

                    buy['qty'] -= match_qty
                    if buy['qty'] == 0:
                        buy_queue.pop(0)
                    sell_qty -= match_qty

    pnl_df = pd.DataFrame(matched)

    if pnl_df.empty:
        st.warning("⚠️ No matched BUY–SELL pairs found.")
        st.stop()

    # ====== Summary Stats ======
    total_trades = len(pnl_df)
    wins = pnl_df[pnl_df['pnl'] > 0]
    losses = pnl_df[pnl_df['pnl'] < 0]
    total_profit = wins['pnl'].sum()
    total_loss = losses['pnl'].sum()
    net_total = total_profit + total_loss
    win_rate = (len(wins) / total_trades) * 100 if total_trades else 0

    # ====== Metrics ======
    st.subheader("📊 Summary")
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Trades", total_trades)
    c2.metric("✅ Profitable", len(wins))
    c3.metric("❌ Loss-Making", len(losses))
    c4.metric("🏆 Win Rate", f"{win_rate:.2f}%")
    c5.metric("📈 Net P&L", f"₹{net_total:,.2f}", delta="Profit" if net_total >= 0 else "Loss")

    # ====== Bar Chart ======
    st.subheader("📉 Trade-wise Realized P&L")
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=pnl_df['sell_time'],
        y=pnl_df['pnl'],
        marker_color=['green' if x > 0 else 'red' for x in pnl_df['pnl']],
        text=pnl_df['symbol'],
        hovertemplate="Symbol: %{text}<br>P&L: ₹%{y:,.2f}<extra></extra>"
    ))
    fig.update_layout(
        xaxis_title="Sell Time",
        yaxis_title="P&L",
        height=400,
        plot_bgcolor='white'
    )
    st.plotly_chart(fig, use_container_width=True)

    # ====== Trade Log Table ======
    st.subheader("📋 Matched Trades")
    pnl_df['qty'] = pnl_df['qty'].astype(int)
    pnl_df['pnl'] = pnl_df['pnl'].round(2)
    st.dataframe(pnl_df[['symbol', 'buy_time', 'buy_price', 'sell_time', 'sell_price', 'qty', 'pnl']])

except Exception as e:
    st.error(f"❌ Error fetching or processing trades: {e}")

