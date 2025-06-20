import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="PNL Dashboard", layout="wide")
st.title("💰 Profit & Loss Dashboard")

uploaded_file = st.file_uploader("📁 Upload your PNL Excel file", type=["xlsx"])

if uploaded_file:
    try:
        # Load and clean data
        df = pd.read_excel(uploaded_file)
        df.columns = [col.strip() for col in df.columns]  # Remove whitespace

        if 'Txn Date' not in df or 'Credit' not in df or 'Debit' not in df:
            st.error("❗ Please make sure the file has 'Txn Date', 'Credit', and 'Debit' columns.")
        else:
            df['Txn Date'] = pd.to_datetime(df['Txn Date'])
            df['Net P&L'] = df['Credit'] - df['Debit']
            df['Month'] = df['Txn Date'].dt.to_period('M').astype(str)
            df['Year'] = df['Txn Date'].dt.year

            # Monthly P&L
            monthly_pnl = df.groupby('Month')['Net P&L'].sum().reset_index()
            monthly_pnl['color'] = monthly_pnl['Net P&L'].apply(lambda x: 'green' if x >= 0 else 'red')

            st.subheader("📅 Monthly Profit & Loss")
            fig, ax = plt.subplots(figsize=(10, 3))  # ⬅️ Reduced height
            ax.bar(monthly_pnl['Month'], monthly_pnl['Net P&L'], color=monthly_pnl['color'])
            ax.tick_params(axis='x', rotation=45, labelsize=7)
            ax.set_ylabel("Net P&L", fontsize=8)
            ax.grid(True, axis='y', linestyle='--', alpha=0.6)
            st.pyplot(fig)

            # Yearly P&L
            yearly_pnl = df.groupby('Year')['Net P&L'].sum().reset_index()
            yearly_pnl['color'] = yearly_pnl['Net P&L'].apply(lambda x: 'green' if x >= 0 else 'red')

            st.subheader("📆 Yearly Profit & Loss")
            fig2, ax2 = plt.subplots(figsize=(6, 2.5))  # ⬅️ Reduced size
            ax2.bar(yearly_pnl['Year'].astype(str), yearly_pnl['Net P&L'], color=yearly_pnl['color'])
            ax2.set_ylabel("Net P&L", fontsize=8)
            ax2.grid(True, axis='y', linestyle='--', alpha=0.6)
            st.pyplot(fig2)

            # Highest profit/loss
            max_profit = df.loc[df['Net P&L'].idxmax()]
            max_loss = df.loc[df['Net P&L'].idxmin()]

            st.subheader("📈 Highest Profit & 📉 Highest Loss")
            fig3, ax3 = plt.subplots(figsize=(4, 2.5))  # ⬅️ Smaller bar chart
            ax3.bar(['Highest Profit', 'Highest Loss'],
                    [max_profit['Net P&L'], max_loss['Net P&L']],
                    color=['green', 'red'])
            ax3.set_ylabel("Net P&L", fontsize=8)
            ax3.set_title("Best & Worst Trades", fontsize=10)
            st.pyplot(fig3)

            # Display metrics
            st.metric("💚 Highest Profit", f"₹{max_profit['Net P&L']:.2f}", delta=f"on {max_profit['Txn Date'].date()}")
            st.metric("💔 Highest Loss", f"₹{max_loss['Net P&L']:.2f}", delta=f"on {max_loss['Txn Date'].date()}")

    except Exception as e:
        st.error(f"⚠️ Error: {e}")

