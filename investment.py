import streamlit as st
import pandas as pd
import os
import plotly.express as px

st.set_page_config(page_title="Investor Summary", layout="wide")

st.title("📊 Investment by Person (Bar Chart View)")

# --- Auto load file ---
FILE_NAME = "INVESTMENT.xlsx"

if not os.path.exists(FILE_NAME):
    st.error(f"❌ File `{FILE_NAME}` not found in the current directory.")
    st.stop()

# --- Load Excel ---
@st.cache_data
def load_data(file_path):
    xls = pd.ExcelFile(file_path)
    sheet = xls.sheet_names[0]
    df = pd.read_excel(xls, sheet_name=sheet)
    return df

df = load_data(FILE_NAME)

# --- Clean column names ---
df.columns = df.columns.str.strip()

# --- Ask user to select name and amount columns ---
text_cols = df.select_dtypes(include='object').columns.tolist()
num_cols = df.select_dtypes(include='number').columns.tolist()

if not text_cols or not num_cols:
    st.error("File must have at least one name (text) column and one amount (number) column.")
    st.stop()

name_col = st.selectbox("👤 Select column for Investor Name", text_cols)
amount_col = st.selectbox("💰 Select column for Investment Amount", num_cols)

# --- Remove suspicious (blank/duplicate names) ---
df_clean = df[[name_col, amount_col]].dropna()
df_clean = df_clean[df_clean[name_col] != ""]
df_clean = df_clean.groupby(name_col, as_index=False)[amount_col].sum()

# --- Sort and plot ---
df_sorted = df_clean.sort_values(by=amount_col, ascending=False)

st.subheader("📈 Total Investment per Person")
fig = px.bar(df_sorted, x=name_col, y=amount_col, title="Inv_

