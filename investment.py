import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- Setup page ---
st.set_page_config(page_title="Investor Summary", layout="wide")
st.title("📊 Investment Summary by Person")

# --- Load file automatically ---
FILE_NAME = "INVESTMENT.xlsx"

if not os.path.exists(FILE_NAME):
    st.error("❌ File 'INVESTMENT.xlsx' not found in the current folder.")
    st.stop()

@st.cache_data
def load_data(file_path):
    xls = pd.ExcelFile(file_path)
    df = pd.read_excel(xls, sheet_name=xls.sheet_names[0])
    return df

df = load_data(FILE_NAME)
df.columns = df.columns.str.strip()  # Clean column names

# --- Auto-select name and amount columns ---
text_cols = df.select_dtypes(include='object').columns.tolist()
num_cols = df.select_dtypes(include='number').columns.tolist()

if not text_cols or not num_cols:
    st.error("The file must contain at least one text column (like Name) and one number column (like Amount).")
    st.stop()

name_col = "NAME" if "NAME" in df.columns else text_cols[0]
amount_col = "DEPOSIT" if "DEPOSIT" in df.columns else num_cols[0]

# --- Prepare data ---
df_clean = df[[name_col, amount_col]].dropna()
df_clean = df_clean[df_clean[name_col].str.strip() != ""]  # Remove empty names
df_grouped = df_clean.groupby(name_col, as_index=False)[amount_col].sum()

# Convert to lakhs
df_grouped["Amount (in Lakhs)"] = df_grouped[amount_col] / 1_00_000

# --- Add Net Total row ---
total_lakhs = df_grouped["Amount (in Lakhs)"].sum()
df_total = pd.DataFrame({
    name_col: ["🧮 Net Total"],
    "Amount (in Lakhs)": [total_lakhs]
})

# Combine data for chart
df_chart = pd.concat([df_grouped[[name_col, "Amount (in Lakhs)"]], df_total], ignore_index=True)

# --- Plot bar chart ---
fig_bar = px.bar(
    df_chart,
    x=name_col,
    y="Amount (in Lakhs)",
    title="Total Investment per Person (in ₹ Lakhs)",
    labels={name_col: "Investor", "Amount (in Lakhs)": "Investment (₹ Lakhs)"},
    text_auto='.2f'
)
fig_bar.update_layout(xaxis_tickangle=-45)
fig_bar.update_yaxes(tickprefix="₹", ticksuffix=" L")

# Display chart
st.plotly_chart(fig_bar, use_container_width=True)

# --- Optional: Show table ---
if st.checkbox("📋 Show Table"):
    st.dataframe(df_grouped[[name_col, amount_col, "Amount (in Lakhs)"]].sort_values("Amount (in Lakhs)", ascending=False))

# --- Optional: Download summary CSV ---
csv = df_grouped[[name_col, "Amount (in Lakhs)"]].to_csv(index=False).encode("utf-8")
st.download_button("📥 Download CSV", data=csv, file_name="investment_summary.csv", mime="text/csv")

