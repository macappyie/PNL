import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Page setup
st.set_page_config(page_title="PNL Dashboard", layout="wide")
st.title("💰 Profit & Loss Dashboard")

# Upload file
uploaded_file = st.file_uploader("📁 Upload your PNL Excel file", type=["xlsx"])

if uploaded_file:
    try:
        # Load data
        df = pd.read_excel(uploaded_file)
        df.columns = [col.strip() for col in df.columns]  # Clean column names

        # Validate required columns
        if 'Txn Date' not in df or 'Credit' not in df or 'Debit' not in df:
            st.error("❗ Please make sure the file has 'Txn Date', 'Credit', and 'Debit' columns.")
        else:
            # Process
            df['Txn Date'] = pd.to_datetime(df['Txn Date'])
            df['Net P&L'] = df['Credit'] - df['Debit']
            df['Month_dt'] = df['Txn Date'].dt.to_period('M').dt.to_timestamp()
            df['Year'] = df['Txn Date'].dt.year

            # ▶️ Monthly Interactive Chart
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
                xaxis=dict(
                    title='Month',
                    tickformat='%b %Y',
                    tickangle=-45,
                    rangeslider=dict(visible=True),
                    showgrid=False
                ),
                yaxis=dict(title='Net P&L'),
                plot_bgcolor='white',
                height=400,
                margin=dict(l=30, r=30, t=30, b=30)
            )
            st.plotly_chart(fig, use_container_width=True)

            # ▶️ Yearly P&L Summary
            st.subheader("📆 Yearly Profit & Loss")
            yearly_pnl = df.groupby('Year')['Net P&L'].sum().reset_index()
            st.bar_chart(yearly_pnl.set_index('Year'))

            # ▶️ Highest Profit / Loss
            st.subheader("📈 Highest Profit & 📉 Highest Loss")
            max_profit = df.loc[df['Net P&L'].idxmax()]
            max_loss = df.loc[df['Net P&L'].idxmin()]

            col1, col2 = st.columns(2)
            with col1:
                st.metric("💚 Highest Profit", f"₹{max_profit['Net P&L']:.2f}", delta=f"on {max_profit['Txn Date'].date()}")
            with col2:
                st.metric("💔 Highest Loss", f"₹{max_loss['Net P&L']:.2f}", delta=f"on {max_loss['Txn Date'].date()}")

            # ▶️ Net Profit vs Net Loss Chart
            st.subheader("📊 Net Profit vs Net Loss Summary")
            total_profit = df[df['Net P&L'] > 0]['Net P&L'].sum()
            total_loss = df[df['Net P&L'] < 0]['Net P&L'].sum()

            fig4 = go.Figure()
            fig4.add_trace(go.Bar(
                x=['Total Profit'],
                y=[total_profit],
                marker_color='green',
                hovertemplate='Profit: ₹%{y:,.2f}<extra></extra>',
            ))
            fig4.add_trace(go.Bar(
                x=['Total Loss'],
                y=[abs(total_loss)],
                marker_color='red',
                hovertemplate='Loss: ₹%{y:,.2f}<extra></extra>',
            ))
            fig4.update_layout(
                barmode='group',
                yaxis_title="Amount",
                plot_bgcolor='white',
                height=300,
                margin=dict(l=30, r=30, t=30, b=30),
                showlegend=False
            )
            st.plotly_chart(fig4, use_container_width=True)

            # ▶️ Numeric Summary
            st.subheader("📌 Net Summary")
            net_total = total_profit + total_loss  # total_loss is negative
            col1, col2, col3 = st.columns(3)
            col1.metric("🟢 Total Profit", f"₹{total_profit:,.2f}")
            col2.metric("🔴 Total Loss", f"₹{abs(total_loss):,.2f}")
            col3.metric("🧾 Net Total", f"₹{net_total:,.2f}", delta=f"{'Profit' if net_total >= 0 else 'Loss'}")

    except Exception as e:
        st.error(f"⚠️ Error: {e}")
else:
    st.info("📂 Please upload a valid Excel file with 'Txn Date', 'Credit', and 'Debit' columns.")

