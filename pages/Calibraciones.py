import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io
from datetime import date
import numpy as np


st.set_page_config(page_title="Calibraciones", page_icon="⚖️")

# Leer y escribir parámetros de la URL usando la nueva API
params = st.query_params

def_dut = params.get('dut', 'DUT')
def_patron = params.get('patron', 'PAT')

def set_url_params(denominacion_dut, denominacion_patron):
    st.query_params['dut'] = denominacion_dut
    st.query_params['patron'] = denominacion_patron


st.title("Calibraciones de Celdas de Carga")
st.markdown("""
Sube un archivo Excel (*.xlsx) con las siguientes columnas obligatorias:
- PAT1_0 (Patrón durante carga)
- DUT1_0 (DUT durante carga)
- PAT1_R (Patrón durante descarga)
- DUT1_R (DUT durante descarga)
""")

uploaded_file = st.file_uploader("Selecciona un archivo Excel de calibración", type=["xlsx"])

if uploaded_file is not None:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        denominacion_dut = st.text_input('Denominación DUT', value=def_dut, key='dut')
    with col2:
        denominacion_patron = st.text_input('Denominación patrón', value=def_patron, key='patron')
    with col3:
        fecha_calibracion = st.date_input('Fecha de Calibración', value=date.today())
        fecha_calibracion_str = fecha_calibracion.strftime('%d/%m/%Y')
    with col4:
        unidad_fuerza = st.selectbox('Unidades de Fuerza', options=['kgf', 'lbf', 'N', 'daN'], index=3)
    # Guardar en la URL cuando cambian
    set_url_params(denominacion_dut, denominacion_patron)
    df = pd.read_excel(uploaded_file)
    required_cols = ["PAT1_0", "DUT1_0", "PAT1_R", "DUT1_R"]
    if not all(col in df.columns for col in required_cols):
        st.error(f"El archivo debe contener las columnas: {', '.join(required_cols)}")
    else:
        st.success("Archivo cargado correctamente.")
        # Eliminar filas donde todos los elementos sean 0
        df = df.loc[~(df[required_cols] == 0).all(axis=1)]
        
        # Cálculo de errores
        abs_error_0 = df["DUT1_0"] - df["PAT1_0"]
        rel_error_0 = abs_error_0 / df["PAT1_0"].replace(0, pd.NA)
        abs_error_r = df["DUT1_R"] - df["PAT1_R"]
        rel_error_r = abs_error_r / df["PAT1_R"].replace(0, pd.NA)

        # Gráfico de error absoluto (barras verticales contiguas)
        fig1, ax1 = plt.subplots(figsize=(8, 4))
        x = np.arange(len(df))
        width = 0.4
        ax1.bar(x - width/2, abs_error_0, width=width, label="Carga", color='tab:blue', alpha=0.7)
        ax1.bar(x + width/2, abs_error_r, width=width, label="Descarga", color='tab:orange', alpha=0.7)
        ax1.set_xlabel(f"Patrón ({unidad_fuerza})")
        ax1.set_ylabel(f"Error absoluto ({unidad_fuerza})")
        ax1.set_title(f"Error Absoluto para la celda {denominacion_dut} - Patrón: {denominacion_patron}", pad=24)
        ax1.set_xticks(x)
        # ax1.set_xticklabels([f"{p0:.0f}/{pr:.0f}" for p0, pr in zip(df["PAT1_0"], df["PAT1_R"])] , rotation=45)
        ax1.legend()
        ax1.grid()
        ax1.axhline(0, color='black', linewidth=1)
        # Subtítulo con la fecha de calibración, más separado del título
        fig1.text(0.5, 0.91, f"Fecha de Calibración: {fecha_calibracion_str}", ha='center', fontsize=10, color='gray')
        st.pyplot(fig1)
        buf1 = io.BytesIO()
        fig1.savefig(buf1, format="png")
        st.download_button("Descargar gráfico de error absoluto (PNG)", data=buf1.getvalue(), file_name="error_absoluto.png", mime="image/png")

        # Gráfico de error relativo con scatter y ajuste polinómico de grado 3
        fig2, ax2 = plt.subplots(figsize=(8, 4))
        # Scatter plot de los puntos
        ax2.scatter(df["PAT1_0"], rel_error_0 * 100, label="Carga (muestras)", color='tab:blue', s=60, marker='o', zorder=3)
        ax2.scatter(df["PAT1_R"], rel_error_r * 100, label="Descarga (muestras)", color='tab:orange', s=60, marker='x', zorder=3)
        # Ajuste polinómico grado 3 para carga
        if len(df["PAT1_0"]) >= 4:
            coef_carga = np.polyfit(df["PAT1_0"], rel_error_0 * 100, 3)
            poly_carga = np.poly1d(coef_carga)
            x_carga = np.linspace(df["PAT1_0"].min(), df["PAT1_0"].max(), 200)
            ax2.plot(x_carga, poly_carga(x_carga), color='tab:blue', linestyle='--', label='Ajuste carga (grado 3)', zorder=2)
        # Ajuste polinómico grado 3 para descarga
        if len(df["PAT1_R"]) >= 4:
            coef_descarga = np.polyfit(df["PAT1_R"], rel_error_r * 100, 3)
            poly_descarga = np.poly1d(coef_descarga)
            x_descarga = np.linspace(df["PAT1_R"].min(), df["PAT1_R"].max(), 200)
            ax2.plot(x_descarga, poly_descarga(x_descarga), color='tab:orange', linestyle='--', label='Ajuste descarga (grado 3)', zorder=2)
        ax2.set_xlabel(f"Patrón ({unidad_fuerza})")
        ax2.set_ylabel("Error relativo (%)")
        ax2.set_title(f"Error Relativo para la celda {denominacion_dut} - Patrón: {denominacion_patron}", pad=24)
        # Subtítulo con la fecha de calibración, más separado del título
        fig2.text(0.5, 0.91, f"Fecha de Calibración: {fecha_calibracion_str}", ha='center', fontsize=10, color='gray')
        ax2.axhline(0, color='black', linewidth=1)
        ax2.legend()
        ax2.grid()
        ax2.grid(which='major', linestyle='-', linewidth=0.7)
        ax2.grid(which='minor', linestyle=':', linewidth=0.5, alpha=1.0)
        ax2.minorticks_on()
        st.pyplot(fig2)
        buf2 = io.BytesIO()
        fig2.savefig(buf2, format="png")
        st.download_button("Descargar gráfico de error relativo (PNG)", data=buf2.getvalue(), file_name="error_relativo.png", mime="image/png")
