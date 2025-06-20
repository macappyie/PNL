
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





# Fetch order history
st.info("🔄 Fetching trades from Kite...")
try:
    orders = kite.orders()
    trades = kite.trades()

    df = pd.DataFrame(trades)
    if df.empty:
        st.warning("No trades found in your account.")
        st.stop()

    df = df[['order_id', 'instrument_token', 'product', 'quantity', 'price', 'transaction_type', 'trade_id', 'exchange_timestamp']]
    df.columns = df.columns.str.lower()
    df['exchange_timestamp'] = pd.to_datetime(df['exchange_timestamp'])
    df.sort_values('exchange_timestamp', inplace=True)

    # Instrument lookup
    instrument_df = pd.read_csv("https://api.kite.trade/instruments")  # Cached or downloaded once
    instrument_df = instrument_df[['instrument_token', 'tradingsymbol']]
    df = df.merge(instrument_df, on='instrument_token', how='left')

    trades_list = []
    for symbol in df['tradingsymbol'].unique():
        buy_queue = []
        symbol_df = df[df['tradingsymbol'] == symbol]

        for _, row in symbol_df.iterrows():
            qty = row['quantity']
            price = row['price']
            time = row['exchange_timestamp']

            if row['transaction_type'] == 'BUY':
                buy_queue.append({'quantity': qty, 'price': price, 'timestamp': time})
            elif row['transaction_type'] == 'SELL':
                sell_qty = qty
                sell_price = price
                while sell_qty > 0 and buy_queue:
                    buy_trade = buy_queue[0]
                    match_qty = min(sell_qty, buy_trade['quantity'])

                    pnl = (sell_price - buy_trade['price']) * match_qty
                    trades_list.append({
                        'symbol': symbol,
                        'buy_price': buy_trade['price'],
                        'sell_price': sell_price,
                        'quantity': match_qty,
                        'pnl': pnl,
                        'buy_time': buy_trade['timestamp'],
                        'sell_time': time
                    })

                    # Update queue
                    buy_trade['quantity'] -= match_qty
                    if buy_trade['quantity'] == 0:
                        buy_queue.pop(0)
                    sell_qty -= match_qty

    pnl_df = pd.DataFrame(trades_list)

    if pnl_df.empty:
        st.warning("No matched trades found.")
        st.stop()

    # Summary
    total_trades = len(pnl_df)
    winning = len(pnl_df[pnl_df['pnl'] > 0])
    losing = len(pnl_df[pnl_df['pnl'] < 0])
    total_profit = pnl_df[pnl_df['pnl'] > 0]['pnl'].sum()
    total_loss = pnl_df[pnl_df['pnl'] < 0]['pnl'].sum()
    win_rate = (winning / total_trades) * 100 if total_trades else 0

    st.subheader("📊 Realized P&L Summary")
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("🔁 Total Trades", total_trades)
    c2.metric("✅ Winning", winning)
    c3.metric("❌ Losing", losing)
    c4.metric("🏆 Win Rate", f"{win_rate:.2f}%")
    c5.metric("💰 Net P&L", f"₹{total_profit + total_loss:,.2f}")

    # Bar Chart
    st.subheader("📉 Trade-wise P&L")
    fig = go.Figure(go.Bar(
        x=pnl_df['sell_time'],
        y=pnl_df['pnl'],
        marker_color=['green' if x > 0 else 'red' for x in pnl_df['pnl']]
    ))
    fig.update_layout(xaxis_title="Sell Time", yaxis_title="Realized P&L", height=400)
    st.plotly_chart(fig, use_container_width=True)

    # Trade table
    st.subheader("📋 Matched Trade Details")
    st.dataframe(pnl_df)

except Exception as e:
    st.error(f"⚠️ Failed to fetch or process trades: {e}")

