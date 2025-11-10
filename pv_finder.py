import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="PV Finder", layout="wide", page_icon="📦")

# --- Título do App ---
st.title("📦 PV Finder – PepsiCo Packaging Specs")
st.markdown("Use the filters below to quickly find PV specifications for packaging.")

DEFAULT_FILE = "pv_specs.xlsx"

# --- Cache para carregar base ---
@st.cache_data
def load_excel(file_path):
    return pd.read_excel(file_path, engine="openpyxl")

# --- Função para salvar arquivo ---
def save_uploaded_file(uploaded_file):
    with open(DEFAULT_FILE, "wb") as f:
        f.write(uploaded_file.getbuffer())

# --- Carrega base padrão ---
df = None
if os.path.exists(DEFAULT_FILE):
    try:
        df = load_excel(DEFAULT_FILE)
        last_update = datetime.fromtimestamp(os.path.getmtime(DEFAULT_FILE)).strftime("%d-%m-%Y %H:%M")
    except Exception as e:
        st.error(f"⚠️ Error loading default file: {e}. Please upload a valid .xlsx file.")
        df = None
else:
    last_update = "No data loaded yet"

# --- Sidebar Admin ---
st.sidebar.header("Admin – Weekly Upload")
pin_input = st.sidebar.text_input("Enter PIN", type="password")

if pin_input == "130125":
    uploaded_file = st.sidebar.file_uploader("Upload official PV Spec Excel file", type=["xlsx"])
    if uploaded_file:
        if uploaded_file.name.endswith(".xlsx"):
            try:
                df = pd.read_excel(uploaded_file, engine="openpyxl")
                save_uploaded_file(uploaded_file)
                st.sidebar.success("✅ Base updated successfully!")
                last_update = datetime.now().strftime("%d-%m-%Y %H:%M")
            except Exception as e:
                st.sidebar.error(f"Upload failed: {e}")
        else:
            st.sidebar.error("Invalid file format. Please upload a .xlsx file.")

st.write(f"**Last updated:** {last_update}")

if df is None:
    st.warning("⚠️ No data loaded. Please upload the official file using PIN.")
    st.stop()

# --- Botão de Reset ---
if st.button("🔄 Reset All Filters"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# --- Global Search ---
global_search = st.text_input("🔍 Global search (fragment across ALL columns)", placeholder="e.g., Doritos, C2, X-Dock, P000...")
filtered_df = df.copy()
if global_search:
    mask = filtered_df.astype(str).apply(lambda col: col.str.contains(global_search, case=False, na=False))
    filtered_df = filtered_df[mask.any(axis=1)]

# --- FILTROS BÁSICOS ---
st.subheader("Basic column filters")

# Funções para filtros
def filtro_texto(label, key):
    return st.text_input(label, value=st.session_state.get(key, ""), key=key)

def filtro_multiselect(label, key, opcoes):
    return st.multiselect(label, options=opcoes, default=st.session_state.get(key, []), key=key)

# Lista final (sem PVNumber, CasesPerLayer(TI), HI(Layers/Pallet), CodeDate)
columns_list = [
    "PVStatus", "Count", "Weight", "Description", "DocumentType",
    "NoteForMarketing", "CaseTypeDescriptor", "AirFillDescriptor",
    "SalesClass", "Size", "Shape", "TotalNumberOfCasesPerPallet", "BagsOrTraysPerLayer"
]

# Criar filtros dinamicamente
filters_text = {}
filters_select = {}

# Organizar em duas linhas
cols_row1 = st.columns(8)
cols_row2 = st.columns(6)

for i, col in enumerate(columns_list):
    if col in filtered_df.columns:  # ✅ Agora usamos filtered_df
        target_col = cols_row1[i] if i < 8 else cols_row2[i - 8]
        with target_col:
            with st.container():  # ✅ Agrupa os dois filtros para alinhamento
                text_key = f"{col}_text"
                select_key = f"{col}_select"
                filters_text[col] = filtro_texto(f"{col} contains", text_key)
                filters_select[col] = filtro_multiselect(f"{col} options", select_key, sorted(filtered_df[col].dropna().astype(str).unique()))
    else:
        filters_text[col], filters_select[col] = "", []

# --- APLICA FILTROS ---
def apply_filter(column, text_value, select_values):
    global filtered_df
    if column in filtered_df.columns:
        if text_value:
            filtered_df = filtered_df[filtered_df[column].astype(str).str.contains(text_value, case=False, na=False)]
        if select_values:
            filtered_df = filtered_df[filtered_df[column].astype(str).isin(select_values)]

for col in columns_list:
    apply_filter(col, filters_text[col], filters_select[col])

# --- RESULTADOS ---
st.subheader("📋 Filtered Results")
st.dataframe(filtered_df)

# --- DOWNLOAD ---
st.download_button("Download Filtered Results", data=filtered_df.to_csv(index=False), file_name="filtered_pv_specs.csv", mime="text/csv")
