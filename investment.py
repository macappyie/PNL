import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Investor Summary", layout="centered")

st.title("👥 Unique Investors Summary")

# Automatically load local file
FILE_NAME = "INVESTMENT.xlsx"

if not os.path.exists(FILE_NAME):
    st.error(f"❌ File `{FILE_NAME}` not found in the current directory.")
    st.stop()

# Load Excel
@st.cache_data
def load_data(file_path):
    xls = pd.ExcelFile(file_path)
    sheet = xls.sheet_names[0]  # Load first sheet by default
    df = pd.read_excel(xls, sheet_name=sheet)
    return df

df = load_data(FILE_NAME)

# Clean column names
df.columns = df.columns.str.strip()

# Preview
st.write("### 📄 Sample Data")
st.dataframe(df.head())

# Select column to identify people
text_cols = df.select_dtypes(include='object').columns.tolist()
if not text_cols:
    st.error("No text columns found (like Name, Email, PAN, etc).")
    st.stop()

col = st.selectbox("Select identifier column (Name, Email, PAN, etc):", text_cols)

# Filter out blanks & duplicates
df_clean = df[df[col].notnull()]
df_clean = df_clean.drop_duplicates(subset=[col])

# Show results
total = len(df_clean)
st.success(f"✅ Total unique people who invested: **{total}**")

# Optional: Show list
if st.checkbox("📋 Show unique investor list"):
    st.dataframe(df_clean[[col]].reset_index(drop=True))

