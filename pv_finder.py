import streamlit as st
import pandas as pd
from datetime import datetime
import os

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

# --- Filtros básicos ---
st.subheader("Basic column filters")
col_filters = st.columns(8)

def safe_multiselect(label, column):
    if column in df.columns:
        return st.multiselect(label, options=sorted(df[column].dropna().unique()))
    return []

def safe_text_input(label, column):
    if column in df.columns:
        return st.text_input(label)
    return ""

with col_filters[0]:
    pv_text = safe_text_input("PVNumber contains", "PVNumber")
    pv_select = safe_multiselect("PVNumber options", "PVNumber")
with col_filters[1]:
    status_text = safe_text_input("PVStatus contains", "PVStatus")
    status_select = safe_multiselect("PVStatus options", "PVStatus")
with col_filters[2]:
    doc_text = safe_text_input("DocumentType contains", "DocumentType")
    doc_select = safe_multiselect("DocumentType options", "DocumentType")
with col_filters[3]:
    sales_text = safe_text_input("SalesClass contains", "SalesClass")
    sales_select = safe_multiselect("SalesClass options", "SalesClass")
with col_filters[4]:
    shape_text = safe_text_input("Shape contains", "Shape")
    shape_select = safe_multiselect("Shape options", "Shape")
with col_filters[5]:
    size_text = safe_text_input("Size contains", "Size")
    size_select = safe_multiselect("Size options", "Size")
with col_filters[6]:
    count_text = safe_text_input("Count contains", "Count")
    count_select = safe_multiselect("Count options", "Count")
with col_filters[7]:
    weight_text = safe_text_input("Weight contains", "Weight")
    weight_select = safe_multiselect("Weight options", "Weight")

# --- Aplica filtros ---
def apply_filter(column, text_value, select_values):
    global filtered_df
    if column in filtered_df.columns:
        if text_value:
            filtered_df = filtered_df[filtered_df[column].astype(str).str.contains(text_value, case=False, na=False)]
        if select_values:
            filtered_df = filtered_df[filtered_df[column].isin(select_values)]

apply_filter("PVNumber", pv_text, pv_select)
apply_filter("PVStatus", status_text, status_select)
apply_filter("DocumentType", doc_text, doc_select)
apply_filter("SalesClass", sales_text, sales_select)
apply_filter("Shape", shape_text, shape_select)
apply_filter("Size", size_text, size_select)
apply_filter("Count", count_text, count_select)
apply_filter("Weight", weight_text, weight_select)

# --- Resultados ---
st.subheader("📋 Filtered Results")
st.dataframe(filtered_df)

st.download_button("Download Filtered Results", data=filtered_df.to_csv(index=False), file_name="filtered_pv_specs.csv", mime="text/csv")
