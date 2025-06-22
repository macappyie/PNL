
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

# Load all sheets
data = load_excel()
sheet_names = list(data.keys())
selected_sheet = st.sidebar.selectbox("📄 Select Sheet", sheet_names)
df = data[selected_sheet]

# --- Clean Column Names ---
df.columns = df.columns.str.strip()

# --- Try parsing first datetime column ---
date_cols = df.select_dtypes(include='datetime').columns.tolist()
if not date_cols:
    for col in df.columns:
        try:
            df[col] = pd.to_datetime(df[col])
            date_cols.append(col)
            break
        except Exception:
            continue
if date_cols:
    df = df.sort_values(by=date_cols[0])

# --- Sidebar Filters ---
st.sidebar.header("🔍 Filters")

# Text-based filter
text_cols = df.select_dtypes(include='object').columns.tolist()
if text_cols:
    filter_col = st.sidebar.selectbox("Filter by Column", text_cols)
    selected_vals = st.sidebar.multiselect(f"Select values in `{filter_col}`", options=df[filter_col].dropna().unique())
    if selected_vals:
        df = df[df[filter_col].isin(selected_vals)]

# --- Main Section ---
st.title("📈 Investment Dashboard")

# --- Metrics ---
col1, col2, col3 = st.columns(3)
col1.metric("Total Records", len(df))
if 'Amount' in df.columns:
    col2.metric("Total Investment", f"₹{df['Amount'].sum():,.2f}")
if 'Returns' in df.columns:
    col3.metric("Total Returns", f"₹{df['Returns'].sum():,.2f}")

# --- Charts ---
st.subheader("📊 Visualizations")

if text_cols:
    chart_col = st.selectbox("Select Column for Chart", text_cols)
    
    # Bar Chart: Amount by Category
    if 'Amount' in df.columns:
        bar_data = df.groupby(chart_col)['Amount'].sum().reset_index()
        fig1 = px.bar(bar_data, x=chart_col, y='Amount', title=f'Total Investment by {chart_col}')
        st.plotly_chart(fig1, use_container_width=True)
    
    # Pie Chart: Returns Distribution
    if 'Returns' in df.columns:
        pie_data = df.groupby(chart_col)['Returns'].sum().reset_index()
        fig2 = px.pie(pie_data, values='Returns', names=chart_col, title=f'Returns Distribution by {chart_col}')
        st.plotly_chart(fig2, use_container_width=True)
else:
    st.info("No suitable text columns available for charting.")

# --- Data Table ---
st.subheader("📋 Filtered Data Table")
st.dataframe(df, use_container_width=True)

# --- Export CSV ---
csv = df.to_csv(index=False).encode('utf-8')
st.download_button("📥 Download Filtered Data as CSV", csv, "filtered_investment.csv", "text/csv")

