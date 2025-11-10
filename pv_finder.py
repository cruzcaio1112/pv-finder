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

# --- Botão de Reset ---
if st.button("🔄 Reset All Filters"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.experimental_rerun()

# --- Global Search ---
global_search = st.text_input("🔍 Global search (fragment across ALL columns)", placeholder="e.g., Doritos, C2, X-Dock, P000...")
filtered_df = df.copy()
if global_search:
    filtered_df = filtered_df[filtered_df.apply(lambda row: row.astype(str).str.contains(global_search, case=False).any(), axis=1)]

# --- FILTROS BÁSICOS ---
st.subheader("Basic column filters")
col_filters = st.columns(8)

def filtro_texto(label, key):
    valor = st.text_input(label, value=st.session_state.get(key, ""), key=key)
    st.session_state[key] = valor
    return valor

def filtro_multiselect(label, key, opcoes):
    valor = st.multiselect(label, options=opcoes, default=st.session_state.get(key, []), key=key)
    st.session_state[key] = valor
    return valor

with col_filters[0]:
    pv_text = filtro_texto("PVNumber contains", "pv_text")
    pv_select = filtro_multiselect("PVNumber options", "pv_select", sorted(df["PVNumber"].dropna().astype(str).unique()))
with col_filters[1]:
    status_text = filtro_texto("PVStatus contains", "status_text")
    status_select = filtro_multiselect("PVStatus options", "status_select", sorted(df["PVStatus"].dropna().astype(str).unique()))
with col_filters[2]:
    doc_text = filtro_texto("DocumentType contains", "doc_text")
    doc_select = filtro_multiselect("DocumentType options", "doc_select", sorted(df["DocumentType"].dropna().astype(str).unique()))
with col_filters[3]:
    sales_text = filtro_texto("SalesClass contains", "sales_text")
    sales_select = filtro_multiselect("SalesClass options", "sales_select", sorted(df["SalesClass"].dropna().astype(str).unique()))
with col_filters[4]:
    shape_text = filtro_texto("Shape contains", "shape_text")
    shape_select = filtro_multiselect("Shape options", "shape_select", sorted(df["Shape"].dropna().astype(str).unique()))
with col_filters[5]:
    size_text = filtro_texto("Size contains", "size_text")
    size_select = filtro_multiselect("Size options", "size_select", sorted(df["Size"].dropna().astype(str).unique()))
with col_filters[6]:
    count_text = filtro_texto("Count contains", "count_text")
    count_select = filtro_multiselect("Count options", "count_select", sorted(df["Count"].dropna().astype(str).unique()))
with col_filters[7]:
    weight_text = filtro_texto("Weight contains", "weight_text")
    weight_select = filtro_multiselect("Weight options", "weight_select", sorted(df["Weight"].dropna().astype(str).unique()))

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
