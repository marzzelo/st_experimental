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
def fecha_param():
    return params.get('fecha', date.today().strftime('%d/%m/%Y'))
def unidad_param():
    return params.get('unidad', 'daN')

def set_url_params(denominaciones, denominacion_patron, fecha_calibracion_str, unidad_fuerza):
    url_params = {
        'patron': denominacion_patron,
        'fecha': fecha_calibracion_str,
        'unidad': unidad_fuerza
    }
    for idx, nombre in denominaciones.items():
        url_params[f'dut{idx}'] = nombre
    st.query_params.clear()
    st.query_params.update(url_params)


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
    # col1, col2, col3, col4 = st.columns(4)
    # with col1:
    #     denominacion_dut = st.text_input('Denominación DUT', value=def_dut, key='dut')
    # Primera fila: patrón, fecha, unidades
    col_patron, col_fecha, col_unidad = st.columns(3)
    with col_patron:
        denominacion_patron = st.text_input('Denominación patrón', value=def_patron, key='patron')
    with col_fecha:
        fecha_default = fecha_param()
        try:
            fecha_default_dt = date.strptime(fecha_default, '%d/%m/%Y')
        except Exception:
            fecha_default_dt = date.today()
        fecha_calibracion = st.date_input('Fecha de Calibración', value=fecha_default_dt)
        fecha_calibracion_str = fecha_calibracion.strftime('%d/%m/%Y')
    with col_unidad:
        unidad_fuerza = st.selectbox('Unidades de Fuerza', options=['kgf', 'lbf', 'N', 'daN'], index=['kgf', 'lbf', 'N', 'daN'].index(unidad_param()))
    # Segunda y siguientes filas: denominaciones de celdas
    denominaciones = {}
    df = pd.read_excel(uploaded_file)
    required_cols = ["PAT1_0", "DUT1_0", "PAT1_R", "DUT1_R"]
    if not all(col in df.columns for col in required_cols):
        st.error(f"El archivo debe contener las columnas: {', '.join(required_cols)}")
    else:
        st.success("Archivo cargado correctamente.")
        # Eliminar filas donde todos los elementos sean 0
        df = df.loc[~(df[required_cols] == 0).all(axis=1)]
        
        # Detectar conjuntos de columnas para celdas adicionales
        import re
        # Buscar todos los grupos PATn_0, DUTn_0, PATn_R, DUTn_R
        col_pattern = re.compile(r'PAT(\d+)_0')
        celda_indices = sorted(set(int(col_pattern.match(col).group(1)) for col in df.columns if col_pattern.match(col))) # type: ignore
        # Permitir denominaciones para cada celda
        denominaciones = {}
        for idx in celda_indices:
            key = f'dut_{idx}'
            default = params.get(f'dut{idx}', f'Celda {idx}' if idx != 1 else def_dut)
            denominaciones[idx] = st.text_input(f'Denominación celda #{idx}', value=default, key=key)
        # Guardar todos los parámetros en la URL
        set_url_params(denominaciones, denominacion_patron, fecha_calibracion_str, unidad_fuerza)
        # Graficar para cada celda
        for idx in celda_indices:
            pat_0 = f'PAT{idx}_0'
            dut_0 = f'DUT{idx}_0'
            pat_r = f'PAT{idx}_R'
            dut_r = f'DUT{idx}_R'
            if not all(col in df.columns for col in [pat_0, dut_0, pat_r, dut_r]):
                continue
            abs_error_0 = df[dut_0] - df[pat_0]
            rel_error_0 = abs_error_0 / df[pat_0].replace(0, pd.NA)
            abs_error_r = df[dut_r] - df[pat_r]
            rel_error_r = abs_error_r / df[pat_r].replace(0, pd.NA)
            # Gráfico de error absoluto
            fig1, ax1 = plt.subplots(figsize=(8, 4))
            x = np.arange(len(df))
            width = 0.4
            ax1.bar(x - width/2, abs_error_0, width=width, label="Carga", color='tab:blue', alpha=0.7)
            ax1.bar(x + width/2, abs_error_r, width=width, label="Descarga", color='tab:orange', alpha=0.7)
            ax1.set_xlabel(f"Patrón ({unidad_fuerza})")
            ax1.set_ylabel(f"Error absoluto ({unidad_fuerza})")
            ax1.set_title(f"Error Absoluto para la celda {denominaciones[idx]} - Patrón: {denominacion_patron}", pad=24)
            ax1.set_xticks(x)
            ax1.legend()
            ax1.grid()
            ax1.axhline(0, color='black', linewidth=1)
            fig1.text(0.5, 0.91, f"Fecha de Calibración: {fecha_calibracion_str}", ha='center', fontsize=10, color='gray')
            st.pyplot(fig1)
            buf1 = io.BytesIO()
            fig1.savefig(buf1, format="png")
            st.download_button(f"Descargar gráfico de error absoluto celda {idx} (PNG)", data=buf1.getvalue(), file_name=f"error_absoluto_celda{idx}.png", mime="image/png")
            # Gráfico de error relativo
            fig2, ax2 = plt.subplots(figsize=(8, 4))
            ax2.scatter(df[pat_0], rel_error_0 * 100, label="Carga (muestras)", color='tab:blue', s=60, marker='o', zorder=3)
            ax2.scatter(df[pat_r], rel_error_r * 100, label="Descarga (muestras)", color='tab:orange', s=60, marker='x', zorder=3)
            if len(df[pat_0]) >= 4:
                coef_carga = np.polyfit(df[pat_0], rel_error_0 * 100, 3)
                poly_carga = np.poly1d(coef_carga)
                x_carga = np.linspace(df[pat_0].min(), df[pat_0].max(), 200)
                ax2.plot(x_carga, poly_carga(x_carga), color='tab:blue', linestyle='--', label='Ajuste carga (grado 3)', zorder=2)
            if len(df[pat_r]) >= 4:
                coef_descarga = np.polyfit(df[pat_r], rel_error_r * 100, 3)
                poly_descarga = np.poly1d(coef_descarga)
                x_descarga = np.linspace(df[pat_r].min(), df[pat_r].max(), 200)
                ax2.plot(x_descarga, poly_descarga(x_descarga), color='tab:orange', linestyle='--', label='Ajuste descarga (grado 3)', zorder=2)
            ax2.set_xlabel(f"Patrón ({unidad_fuerza})")
            ax2.set_ylabel("Error relativo (%)")
            ax2.set_title(f"Error Relativo para la celda {denominaciones[idx]} - Patrón: {denominacion_patron}", pad=24)
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
            st.download_button(f"Descargar gráfico de error relativo celda {idx} (PNG)", data=buf2.getvalue(), file_name=f"error_relativo_celda{idx}.png", mime="image/png")
