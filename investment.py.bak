import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Investor Chart", layout="wide")
st.title("📊 Investment Summary by Person")

# === Auto-load file ===
FILE_NAME = "INVESTMENT.xlsx"

if not os.path.exists(FILE_NAME):
    st.error("❌ File 'INVESTMENT.xlsx' not found in the current folder.")
    st.stop()

# === Load Data ===
@st.cache_data
def load_data(file_path):
    xls = pd.ExcelFile(file_path)
    df = pd.read_excel(xls, sheet_name=xls.sheet_names[0])
    return df

df = load_data(FILE_NAME)
df.columns = df.columns.str.strip()

# === Try auto-selecting name and amount columns ===
text_cols = df.select_dtypes(include='object').columns.tolist()
num_cols = df.select_dtypes(include='number').columns.tolist()

if not text_cols or not num_cols:
    st.error("File must contain at least one text (name) and one numeric (amount) column.")
    st.stop()

# Try best guess or fallback to first available
name_col = "Name" if "Name" in df.columns else text_cols[0]
amount_col = "Amount" if "Amount" in df.columns else num_cols[0]

#st.info(f"Auto-selected: **Investor = `{name_col}`**, **Amount = `{amount_col}`**")



# === Clean & Aggregate ===
df_clean = df[[name_col, amount_col]].dropna()
df_clean = df_clean[df_clean[name_col].str.strip() != ""]  # Remove blank names
df_summary = df_clean.groupby(name_col, as_index=False)[amount_col].sum()
df_summary = df_summary.sort_values(by=amount_col, ascending=False)

# === Bar Chart ===
st.subheader("📈 Total Investment by Investor")
#fig = px.bar(
#    df_summary,
#    x=name_col,
#    y=amount_col,
#    title="Total Investment per Person",
#    labels={name_col: "Investor", amount_col: "Total Invested"},
#    text_auto=True
#)


# Convert amount to lakhs
df_summary["Amount (in Lakhs)"] = df_summary[amount_col] / 1_00_000


# ➕ Add a "Total" row to the DataFrame
total_invested_lakh = df_summary["Amount (in Lakhs)"].sum()
df_total = pd.DataFrame({
    name_col: ["Total 🧮"],
    "Amount (in Lakhs)": [total_invested_lakh]
})

fig = px.bar(
    df_summary,
    x=name_col,
    y="Amount (in Lakhs)",
    title="Total Investment per Person (in ₹ Lakhs)",
    labels={name_col: "Investor", "Amount (in Lakhs)": "Investment (₹ Lakhs)"},
    text_auto='.2f'
)
fig.update_layout(xaxis_tickangle=-45)


# Combine with original
df_chart = pd.concat([df_summary[[name_col, "Amount (in Lakhs)"]], df_total], ignore_index=True)
fig.update_yaxes(tickprefix="₹", ticksuffix=" L")





fig.update_layout(xaxis_tickangle=-45)
st.plotly_chart(fig, use_container_width=True)



# Show the chart
st.plotly_chart(fig, use_container_width=True)

# === Show Table (optional) ===
if st.checkbox("📋 Show Table"):
    st.dataframe(df_summary.reset_index(drop=True))

# === CSV Download ===
csv = df_summary.to_csv(index=False).encode('utf-8')
st.download_button("📥 Download CSV", csv, "investor_summary.csv", "text/csv")

