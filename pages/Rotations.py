import streamlit as st
import pandas as pd # Importar pandas
from config import page_config

# Configuración de la página
page_config(title="Cell Rotations", icon="🔄")

# Título de la página
st.markdown("# Cell Rotations")

# File uploader para archivos Excel
uploaded_file = st.file_uploader("Selecciona un archivo Excel para generar rotaciones", type=["xlsx", "xls"])

if uploaded_file is not None:
    # Leer el archivo Excel
    try:
        df = pd.read_excel(uploaded_file)
        st.write("Contenido del archivo Excel Original:")
        st.dataframe(df)
    except Exception as e:
        st.error(f"Error al leer el archivo Excel: {e}")

# Aquí puedes agregar más contenido o funcionalidades para esta página en el futuro.
# st.write("Página en construcción.")

