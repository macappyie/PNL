import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime

st.set_page_config(page_title="💼 Investment Dashboard", layout="wide")

# --- Upload Excel ---
uploaded_file = st.sidebar.file_uploader("📁 Upload Investment Excel", type=["xlsx"])

@st.cache_data(ttl=60)
def load_excel(file):
    xls = pd.ExcelFile(file)
    data = {sheet: xls.parse(sheet) for sheet in xls.sheet_names}
    return data

if uploaded_file:
    data = load_excel(uploaded_file)
    sheet_names = list(data.keys())
    selected_sheet = st.sidebar.selectbox("📄 Select Sheet", sheet_names)
    df = data[selected_sheet]
else:
    st.warning("Please upload an Excel file.")
    st.stop()

# --- Clean Columns ---
df.columns = df.columns.str.strip()

# --- Detect & Parse Date Column ---
date_cols = df.select_dtypes(include='datetime').columns.tolist()
if not date_cols:
    for col in df.columns:
        try:
            df[col] = pd.to_datetime(df[col])
            date_cols.append(col)
            break
        except Exception:
            continue

date_col = date_cols[0] if date_cols else None
if date_col:
    df = df.sort_values(by=date_col)

# --- Sidebar Filters ---
text_cols = df.select_dtypes(include='object').columns.tolist()
st.sidebar.header("🔍 Filters")
if text_cols:
    filter_col = st.sidebar.selectbox("Filter by", text_cols)
    selected_vals = st.sidebar.multiselect("Choose values", options=df[filter_col].dropna().unique())
    if selected_vals:
        df = df[df[filter_col].isin(selected_vals)]

# --- Main Title ---
st.title("📈 Advanced Investment Dashboard")

# --- Metrics ---
col1, col2, col3 = st.columns(3)
col1.metric("Total Records", len(df))
if 'Amount' in df.columns:
    col2.metric("Total Investment", f"₹{df['Amount'].sum():,.2f}")
if 'Returns' in df.columns:
    col3.metric("Total Returns", f"₹{df['Returns'].sum():,.2f}")

# --- Line Chart: NAV / Amount over time ---
st.subheader("⏳ NAV / Amount Over Time")

num_cols = df.select_dtypes(include=np.number).columns.tolist()
time_series_y = st.selectbox("Select Numeric Column for Line Chart", options=num_cols)
if date_col and time_series_y:
    fig = px.line(df, x=date_col, y=time_series_y, title=f"{time_series_y} over Time")
    st.plotly_chart(fig, use_container_width=True)

# --- CAGR & IRR Calculator ---
st.subheader("🧮 CAGR & IRR Calculator")

if 'Amount' in df.columns and date_col:
    amount_grouped = df.groupby(date_col)['Amount'].sum().reset_index()
    if len(amount_grouped) >= 2:
        start_val = amount_grouped['Amount'].iloc[0]
        end_val = amount_grouped['Amount'].iloc[-1]
        start_date = amount_grouped[date_col].iloc[0]
        end_date = amount_grouped[date_col].iloc[-1]
        years = (end_date - start_date).days / 365.25
        if years > 0:
            cagr = ((end_val / start_val) ** (1 / years)) - 1
            st.write(f"📈 **CAGR** from {start_date.date()} to {end_date.date()}: **{cagr*100:.2f}%**")
        else:
            st.warning("Not enough date range for CAGR.")

# IRR requires cashflows (optional user input)
st.subheader("📥 IRR Calculator (Optional)")

with st.expander("Enter cash flows (Date & Amount)"):
    irr_input = st.text_area("Enter cashflows like:\n2020-01-01,-100000\n2023-01-01,140000")
    if irr_input:
        try:
            lines = irr_input.strip().split("\n")
            cashflows = [tuple(line.split(",")) for line in lines]
            cashflows = [(datetime.strptime(d.strip(), "%Y-%m-%d"), float(a)) for d, a in cashflows]
            cashflows.sort(key=lambda x: x[0])
            base_date = cashflows[0][0]
            irr_series = [cf[1] for cf in cashflows]
            days = [(cf[0] - base_date).days / 365.0 for cf in cashflows]

            def xnpv(rate, cashflows):
                return sum(cf / ((1 + rate) ** t) for cf, t in zip(irr_series, days))

            def xirr(cashflows):
                from scipy.optimize import newton
                return newton(lambda r: xnpv(r, cashflows), 0.1)

            irr = xirr(cashflows)
            st.success(f"📊 Estimated IRR: **{irr*100:.2f}%**")
        except Exception as e:
            st.error(f"Error in IRR input: {e}")

# --- Data Table ---
st.subheader("📋 Filtered Data Table")
st.dataframe(df, use_container_width=True)

# --- Download ---
csv = df.to_csv(index=False).encode('utf-8')
st.download_button("📥 Download Filtered Data", csv, "filtered_investment.csv", "text/csv")

