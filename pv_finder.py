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
    df = pd.read_excel(DEFAULT_FILE, engine="openpyxl")
    last_update = datetime.fromtimestamp(os.path.getmtime(DEFAULT_FILE)).strftime("%d-%m-%Y %H:%M")
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

# --- Info ---
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
with col_filters[0]:
    pv_text = st.text_input("PVNumber contains")
    pv_select = st.multiselect("PVNumber options", options=sorted(df["PVNumber"].dropna().unique()))
with col_filters[1]:
    status_text = st.text_input("PVStatus contains")
    status_select = st.multiselect("PVStatus options", options=sorted(df["PVStatus"].dropna().unique()))
with col_filters[2]:
    doc_text = st.text_input("DocumentType contains")
    doc_select = st.multiselect("DocumentType options", options=sorted(df["DocumentType"].dropna().unique()))
with col_filters[3]:
    sales_text = st.text_input("SalesClass contains")
    sales_select = st.multiselect("SalesClass options", options=sorted(df["SalesClass"].dropna().unique()))
with col_filters[4]:
    shape_text = st.text_input("Shape contains")
    shape_select = st.multiselect("Shape options", options=sorted(df["Shape"].dropna().unique()))
with col_filters[5]:
    size_text = st.text_input("Size contains")
    size_select = st.multiselect("Size options", options=sorted(df["Size"].dropna().unique()))
with col_filters[6]:
    count_text = st.text_input("Count contains")
    count_select = st.multiselect("Count options", options=sorted(df["Count"].dropna().unique()))
with col_filters[7]:
    weight_text = st.text_input("Weight contains")
    weight_select = st.multiselect("Weight options", options=sorted(df["Weight"].dropna().unique()))

# --- Aplica filtros ---
if pv_text:
    filtered_df = filtered_df[filtered_df["PVNumber"].astype(str).str.contains(pv_text, case=False, na=False)]
if pv_select:
    filtered_df = filtered_df[filtered_df["PVNumber"].isin(pv_select)]
if status_text:
    filtered_df = filtered_df[filtered_df["PVStatus"].astype(str).str.contains(status_text, case=False, na=False)]
if status_select:
    filtered_df = filtered_df[filtered_df["PVStatus"].isin(status_select)]
if doc_text:
    filtered_df = filtered_df[filtered_df["DocumentType"].astype(str).str.contains(doc_text, case=False, na=False)]
if doc_select:
    filtered_df = filtered_df[filtered_df["DocumentType"].isin(doc_select)]
if sales_text:
    filtered_df = filtered_df[filtered_df["SalesClass"].astype(str).str.contains(sales_text, case=False, na=False)]
if sales_select:
    filtered_df = filtered_df[filtered_df["SalesClass"].isin(sales_select)]
if shape_text:
    filtered_df = filtered_df[filtered_df["Shape"].astype(str).str.contains(shape_text, case=False, na=False)]
if shape_select:
    filtered_df = filtered_df[filtered_df["Shape"].isin(shape_select)]
if size_text:
    filtered_df = filtered_df[filtered_df["Size"].astype(str).str.contains(size_text, case=False, na=False)]
if size_select:
    filtered_df = filtered_df[filtered_df["Size"].isin(size_select)]
if count_text:
    filtered_df = filtered_df[filtered_df["Count"].astype(str).str.contains(count_text, case=False, na=False)]
if count_select:
    filtered_df = filtered_df[filtered_df["Count"].isin(count_select)]
if weight_text:
    filtered_df = filtered_df[filtered_df["Weight"].astype(str).str.contains(weight_text, case=False, na=False)]
if weight_select:
    filtered_df = filtered_df[filtered_df["Weight"].isin(weight_select)]

# --- Resultados ---
st.subheader("📋 Filtered Results")
st.dataframe(filtered_df)

# --- Download ---
st.download_button("Download Filtered Results", data=filtered_df.to_csv(index=False), file_name="filtered_pv_specs.csv", mime="text/csv")
