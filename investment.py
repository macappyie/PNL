import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="💼 Investment Dashboard", layout="wide")

# --- Load Excel ---
@st.cache_data
def load_excel():
    xls = pd.ExcelFile("INVESTMENT.xlsx")
    data = {sheet: xls.parse(sheet) for sheet in xls.sheet_names}
    return data

data = load_excel()
sheet_names = list(data.keys())
selected_sheet = st.sidebar.selectbox("📄 Select Sheet", sheet_names)
df = data[selected_sheet]

# --- Data Cleanup ---
df.columns = df.columns.str.strip()
date_cols = df.select_dtypes(include='datetime').columns.tolist()
if date_cols:
    df[date_cols[0]] = pd.to_datetime(df[date_cols[0]])
    df = df.sort_values(by=date_cols[0])

# --- Sidebar Filters ---
st.sidebar.header("🔍 Filters")

# Category filter (e.g., fund name, type)
category_cols = df.select_dtypes(include='object').columns.tolist()
filter_col = st.sidebar.selectbox("Filter by Column", category_cols)
selected_val = st.sidebar.multiselect(f"Select {filter_col}", options=df[filter_col].unique())

if selected_val:
    df = df[df[filter_col].isin(selected_val)]

# --- Main Display ---
st.title("📈 Advanced Investment Dashboard")

# Summary metrics
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Rows", len(df))
with col2:
    if 'Amount' in df.columns:
        st.metric("Total Investment", f"₹{df['Amount'].sum():,.2f}")
with col3:
    if 'Returns' in df.columns:
        st.metric("Total Returns", f"₹{df['Returns'].sum():,.2f}")

# --- Charts ---
st.subheader("📊 Visualizations")

chart_col = st.selectbox("Select Column_

