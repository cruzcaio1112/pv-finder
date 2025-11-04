import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="PV Finder", layout="wide", page_icon="📦")

DEFAULT_FILE = "pv_specs.xlsx"

# --- Carrega base padrão ---
df = None
if os.path.exists(DEFAULT_FILE):
    try:
        df = pd.read_excel(DEFAULT_FILE, engine="openpyxl")
        last_update = datetime.fromtimestamp(os.path.getmtime(DEFAULT_FILE)).strftime("%d-%m-%Y %H:%M")
    except Exception as e:
        st.error(f"Error loading default file: {e}")
        df = None
else:
    last_update = "No data loaded yet"

# --- Sidebar Admin ---
st.sidebar.header("Admin – Weekly Upload")
pin_input = st.sidebar.text_input("Enter PIN", type="password")

if pin_input == "130125":
    uploaded_file = st.sidebar.file_uploader("Upload official PV Spec Excel file", type=["xlsx"])
    if uploaded_file:
        df = pd.read_excel(uploaded_file, engine="openpyxl")
        with open(DEFAULT_FILE, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.sidebar.success("✅ Base updated successfully!")
        last_update = datetime.now().strftime("%d-%m-%Y %H:%M")

st.write(f"**Last updated:** {last_update}")

if df is None:
    st.warning("⚠️ No data loaded. Please upload the official file using PIN.")
    st.stop()

# --- Global Search ---
global_search = st.text_input("🔍 Global search (fragment across ALL columns)", placeholder="e.g., Doritos, C2, X-Dock, P000...")
filtered_df = df.copy()
if global_search:
    filtered_df = filtered_df[filtered_df.apply(lambda row: row.astype(str).str.contains(global_search, case=False).any(), axis=1)]

# --- FILTROS BÁSICOS ---
st.subheader("Basic column filters")
col_filters = st.columns(8)

with col_filters[0]:
    pv_text = st.text_input("PVNumber contains")
    pv_select = st.multiselect("PVNumber options", options=sorted(df["PVNumber"].dropna().astype(str).unique()))
with col_filters[1]:
    status_text = st.text_input("PVStatus contains")
    status_select = st.multiselect("PVStatus options", options=sorted(df["PVStatus"].dropna().astype(str).unique()))
with col_filters[2]:
    doc_text = st.text_input("DocumentType contains")
    doc_select = st.multiselect("DocumentType options", options=sorted(df["DocumentType"].dropna().astype(str).unique()))
with col_filters[3]:
    sales_text = st.text_input("SalesClass contains")
    sales_select = st.multiselect("SalesClass options", options=sorted(df["SalesClass"].dropna().astype(str).unique()))
with col_filters[4]:
    shape_text = st.text_input("Shape contains")
    shape_select = st.multiselect("Shape options", options=sorted(df["Shape"].dropna().astype(str).unique()))
with col_filters[5]:
    size_text = st.text_input("Size contains")
    size_select = st.multiselect("Size options", options=sorted(df["Size"].dropna().astype(str).unique()))
with col_filters[6]:
    count_text = st.text_input("Count contains")
    count_select = st.multiselect("Count options", options=sorted(df["Count"].dropna().astype(str).unique()))
with col_filters[7]:
    weight_text = st.text_input("Weight contains")
    weight_select = st.multiselect("Weight options", options=sorted(df["Weight"].dropna().astype(str).unique()))

# --- APLICA FILTROS ---
def apply_filter(column, text_value, select_values):
    global filtered_df
    if column in filtered_df.columns:
        if text_value:
            filtered_df = filtered_df[filtered_df[column].astype(str).str.contains(text_value, case=False, na=False)]
        if select_values:
            filtered_df = filtered_df[filtered_df[column].astype(str).isin(select_values)]

apply_filter("PVNumber", pv_text, pv_select)
apply_filter("PVStatus", status_text, status_select)
apply_filter("DocumentType", doc_text, doc_select)
apply_filter("SalesClass", sales_text, sales_select)
apply_filter("Shape", shape_text, shape_select)
apply_filter("Size", size_text, size_select)
apply_filter("Count", count_text, count_select)
apply_filter("Weight", weight_text, weight_select)

# --- RESULTADOS ---
st.subheader("📋 Filtered Results")
st.dataframe(filtered_df)

# --- DOWNLOAD ---
st.download_button("Download Filtered Results", data=filtered_df.to_csv(index=False), file_name="filtered_pv_specs.csv", mime="text/csv")
