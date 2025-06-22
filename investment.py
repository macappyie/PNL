import streamlit as st
import pandas as pd

# Set page title
st.set_page_config(page_title="Investment Dashboard", layout="wide")

# Title
st.title("📊 Investment Portfolio Dashboard")

# Load Excel
@st.cache_data
def load_data():
    file_path = "INVESTMENT.xlsx"
    df = pd.read_excel(file_path, sheet_name=None)  # Load all sheets
    return df

data = load_data()

# Sidebar to choose sheet
sheet_names = list(data.keys())
selected_sheet = st.sidebar.selectbox("Select Sheet", sheet_names)

# Show selected data
df = data[selected_sheet]
st.write(f"### 📄 Data from sheet: `{selected_sheet}`")
st.dataframe(df, use_container_width=True)

# Basic stats
if st.checkbox("Show Summary Statistics"):
    st.write(df.describe())

# Column filter
if st.checkbox("Enable Column Filter"):
    col = st.selectbox("Select a column to filter", df.columns)
    unique_vals = df[col].dropna().unique()
    selected_val = st.selectbox(f"Filter `{col}` by:", unique_vals)
    st.dataframe(df[df[col] == selected_val])

# Download button
csv = df.to_csv(index=False).encode('utf-8')
st.download_button("📥 Download this table as CSV", csv, "filtered_data.csv", "text/csv")

