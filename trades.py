
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



# ===== Fetch trades =====
try:
    st.info("🔄 Fetching trade data...")
    trades = kite.trades()
    instruments = kite.instruments()

    df = pd.DataFrame(trades)
    if df.empty:
        st.warning("⚠️ No trades found.")
        st.stop()

    # Clean data
    df = df[['order_id', 'instrument_token', 'quantity', 'price', 'transaction_type', 'trade_id', 'exchange_timestamp']]
    df.columns = df.columns.str.lower()
    df['exchange_timestamp'] = pd.to_datetime(df['exchange_timestamp'])
    df.sort_values('exchange_timestamp', inplace=True)

    # Add symbol name
    inst_df = pd.DataFrame(instruments)[['instrument_token', 'tradingsymbol']]
    df = df.merge(inst_df, on='instrument_token', how='left')

    # ===== FIFO BUY-SELL matching =====
    matched_trades = []
    for symbol in df['tradingsymbol'].unique():
        symbol_df = df[df['tradingsymbol'] == symbol]
        buy_queue = []

        for _, row in symbol_df.iterrows():
            qty = row['quantity']
            price = row['price']
            txn = row['transaction_type']
            time = row['exchange_timestamp']

            if txn == 'BUY':
                buy_queue.append({'qty': qty, 'price': price, 'time': time})
            elif txn == 'SELL':
                sell_qty = qty
                sell_price = price
                while sell_qty > 0 and buy_queue:
                    buy = buy_queue[0]
                    match_qty = min(sell_qty, buy['qty'])

                    pnl = (sell_price - buy['price']) * match_qty
                    matched_trades.append({
                        'symbol': symbol,
                        'buy_price': buy['price'],
                        'sell_price': sell_price,
                        'qty': match_qty,
                        'pnl': pnl,
                        'buy_time': buy['time'],
                        'sell_time': time
                    })

                    # Update qty
                    buy['qty'] -= match_qty
                    if buy['qty'] == 0:
                        buy_queue.pop(0)
                    sell_qty -= match_qty

    pnl_df = pd.DataFrame(matched_trades)

    if pnl_df.empty:
        st.warning("⚠️ No matched BUY/SELL trades found.")
        st.stop()

    # ===== Summary =====
    total_trades = len(pnl_df)
    wins = pnl_df[pnl_df['pnl'] > 0]
    losses = pnl_df[pnl_df['pnl'] < 0]
    win_count = len(wins)
    loss_count = len(losses)
    total_profit = wins['pnl'].sum()
    total_loss = losses['pnl'].sum()
    net_total = total_profit + total_loss
    win_rate = (win_count / total_trades) * 100 if total_trades else 0

    # ===== Metrics =====
    st.subheader("📊 Trade Summary")
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Trades", total_trades)
    c2.metric("✅ Profitable", win_count)
    c3.metric("❌ Loss-Making", loss_count)
    c4.metric("🏆 Win Rate", f"{win_rate:.2f}%")
    c5.metric("📈 Net P&L", f"₹{net_total:,.2f}", delta="Profit" if net_total >= 0 else "Loss")

    # ===== Bar Chart =====
    st.subheader("📉 Trade-wise Realized P&L")
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=pnl_df['sell_time'],
        y=pnl_df['pnl'],
        marker_color=['green' if x > 0 else 'red' for x in pnl_df['pnl']],
        hovertemplate='Symbol: %{text}<br>P&L: ₹%{y:,.2f}<extra></extra>',
        text=pnl_df['symbol']
    ))
    fig.update_layout(
        xaxis_title="Sell Time",
        yaxis_title="Realized P&L",
        height=400,
        plot_bgcolor='white'
    )
    st.plotly_chart(fig, use_container_width=True)

    # ===== Trade Table =====
    st.subheader("📋 Matched Trade Log")
    pnl_df['pnl'] = pnl_df['pnl'].round(2)
    pnl_df['qty'] = pnl_df['qty'].astype(int)
    st.dataframe(pnl_df[['symbol', 'buy_time', 'buy_price', 'sell_time', 'sell_price', 'qty', 'pnl']])

except Exception as e:
    st.error(f"❌ Error fetching or processing trades: {e}")
