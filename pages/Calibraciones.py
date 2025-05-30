import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io
from datetime import date
import numpy as np
from config import page_config
import re
import zipfile  # Importar zipfile
from report_generator import ReportGenerator
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT


class CalibrationApp:
    """
    Aplicación Streamlit para la calibración de celdas de carga.

    Permite a los usuarios cargar datos de calibración desde archivos Excel,
    configurar parámetros, visualizar gráficos de errores y generar informes en PDF.
    """
    def __init__(self):
        """
        Inicializa la aplicación configurando la página y los atributos necesarios.
        """
        page_config(
            title="Calibraciones",
            icon="⚖️",
            layout="centered")
        self.st = st
        self.pd = pd
        self.plt = plt
        self.io = io
        self.date = date
        self.np = np
        self.report_generator = ReportGenerator()

    def generar_informe_pdf(self, st_obj, fecha_calibracion_str, denominacion_patron, unidad_fuerza, limite_tolerancia_rel, celda_indices, denominaciones, df_calibracion, all_plot_buffers_with_names, n_requerimiento=None, documentacion_aplicada=None, ficha_dut_file=None, ficha_patron_file=None, foto_montaje_file=None):
        """
        Delega la generación del informe PDF al ReportGenerator.

        Args:
            st_obj: Objeto Streamlit para mostrar errores.
            fecha_calibracion_str (str): Fecha de calibración.
            denominacion_patron (str): Denominación del patrón.
            unidad_fuerza (str): Unidad de fuerza.
            limite_tolerancia_rel (float): Límite de tolerancia relativo.
            celda_indices (list): Lista de índices de celdas.
            denominaciones (dict): Diccionario con denominaciones de celdas.
            df_calibracion (pd.DataFrame): DataFrame con los datos de calibración.
            all_plot_buffers_with_names (list): Lista de tuplas (nombre_grafico, buffer_grafico).
            n_requerimiento (str, optional): Número de requerimiento.
            documentacion_aplicada (str, optional): Documentación aplicada.
            ficha_dut_file (BytesIO, optional): Archivo de imagen de la ficha DUT.
            ficha_patron_file (BytesIO, optional): Archivo de imagen de la ficha Patrón.
            foto_montaje_file (BytesIO, optional): Archivo de imagen de la foto del montaje.

        Returns:
            BytesIO: Buffer con el PDF generado o None en caso de error.
        """
        return self.report_generator.generar_informe_pdf(
            st_obj, fecha_calibracion_str, denominacion_patron, unidad_fuerza, limite_tolerancia_rel,
            celda_indices, denominaciones, df_calibracion, all_plot_buffers_with_names,
            n_requerimiento, documentacion_aplicada, ficha_dut_file, ficha_patron_file, foto_montaje_file
        )

    def run(self):
        """
        Ejecuta la lógica principal de la aplicación Streamlit.

        Maneja la interfaz de usuario, la carga de archivos, el procesamiento de datos,
        la visualización de gráficos y la generación de informes.
        """
        st = self.st
        pd = self.pd
        plt = self.plt
        io = self.io
        date = self.date
        np = self.np
        params = st.query_params
        def_dut = params.get('dut', 'DUT')
        def_patron = params.get('patron', 'PAT')

        # Funciones auxiliares para obtener parámetros de URL o valores por defecto
        def fecha_param():
            """Obtiene el parámetro 'fecha' de la URL o devuelve la fecha actual."""
            return params.get('fecha', date.today().strftime('%d/%m/%Y'))

        def unidad_param():
            """Obtiene el parámetro 'unidad' de la URL o devuelve 'daN'."""
            return params.get('unidad', 'daN')

        def limite_tolerancia_param():
            """Obtiene el parámetro 'lim_tol_rel' de la URL o devuelve '1.0'."""
            return params.get('lim_tol_rel', '1.0')

        # Función para actualizar los parámetros de la URL
        def set_url_params(denominaciones, denominacion_patron, fecha_calibracion_str, unidad_fuerza, limite_tolerancia_rel_str):
            """Actualiza los parámetros de la URL con los valores proporcionados."""
            url_params = {
                'patron': denominacion_patron,
                'fecha': fecha_calibracion_str,
                'unidad': unidad_fuerza,
                'lim_tol_rel': limite_tolerancia_rel_str
            }
            for idx, nombre in denominaciones.items():
                url_params[f'dut{idx}'] = nombre
            st.query_params.clear()
            st.query_params.update(url_params)

        st.title("Calibraciones de Celdas de Carga")

        # Sección de instrucciones expandible
        with st.expander("I N S T R U C C I O N E S", expanded=False):
            st.markdown("""
            ### Formato del archivo xls de entrada
            **Columnas obligatorias para una celda:**
            - `PAT1_0` (Patrón durante carga)
            - `DUT1_0` (DUT durante carga)
            - `PAT1_R` (Patrón durante descarga)
            - `DUT1_R` (DUT durante descarga)
            
            **Columnas opcionales (por celda) para ensayos de excentricidad:**
            - `PATn_120` (Patrón durante carga a 120°)
            - `DUTn_120` (DUT durante carga a 120°)
            - `PATn_240` (Patrón durante carga a 240°)
            - `DUTn_240` (DUT durante carga a 240°)

            ### Formato para calibraciones de múltiples celdas:
            - Para cada celda adicional, agregue columnas siguiendo el patrón:
                - `PATn_0`, `DUTn_0`, `PATn_R`, `DUTn_R` (donde n = 2, 3, ...)
            - Ejemplo para tres celdas:
                - `PAT1_0`, `DUT1_0`, `PAT1_R`, `DUT1_R`
                - `PAT2_0`, `DUT2_0`, `PAT2_R`, `DUT2_R`
                - `PAT3_0`, `DUT3_0`, `PAT3_R`, `DUT3_R`
            """)

        # Carga del archivo Excel
        uploaded_file = st.file_uploader("Selecciona un archivo Excel de calibración", type=["xlsx"])

        if uploaded_file is not None:
            # Contenedor para parámetros de configuración
            parm_container = st.container(border=True)
            with parm_container:
                st.subheader("Parámetros de Configuración")
                col_patron, col_fecha, col_unidad = st.columns(3)
                # Entradas para denominación del patrón y límite de tolerancia
                with col_patron:
                    denominacion_patron = st.text_input('Denominación patrón', value=def_patron, key='patron')
                    limite_tolerancia_rel = st.number_input('Límite de tolerancia (%)', min_value=0.1, value=float(limite_tolerancia_param()), step=0.1, key='lim_tol_rel')
                # Entrada para fecha de calibración
                with col_fecha:
                    fecha_default = fecha_param()
                    try:
                        fecha_default_dt = date.strptime(fecha_default, '%d/%m/%Y')
                    except Exception:
                        fecha_default_dt = date.today()
                    fecha_calibracion = st.date_input('Fecha de Calibración', value=fecha_default_dt)
                    fecha_calibracion_str = fecha_calibracion.strftime('%d/%m/%Y')
                # Selección de unidades de fuerza
                with col_unidad:
                    unidad_fuerza = st.selectbox('Unidades de Fuerza', options=['kgf', 'lbf', 'N', 'daN'], index=['kgf', 'lbf', 'N', 'daN'].index(unidad_param()))

            denominaciones = {}
            # Lectura del archivo Excel
            df = pd.read_excel(uploaded_file)

            # Verificación de columnas obligatorias
            required_cols = ["PAT1_0", "DUT1_0", "PAT1_R", "DUT1_R"]
            if not all(col in df.columns for col in required_cols):
                st.error(f"El archivo debe contener las columnas: {', '.join(required_cols)}")
            else:
                st.success("Archivo cargado correctamente.")
                # Limpieza de filas con todos los valores en cero para las columnas requeridas
                df = df.loc[~(df[required_cols] == 0).all(axis=1)]

                # Identificación de los índices de las celdas calibradas
                col_pattern = re.compile(r'PAT(\d+)_0')
                celda_indices = sorted(set(int(col_pattern.match(col).group(1)) for col in df.columns if col_pattern.match(col)))

                denominaciones = {}
                # Entradas para las denominaciones de cada celda
                for idx in celda_indices:
                    key = f'dut_{idx}'
                    default = params.get(f'dut{idx}', f'Celda {idx}' if idx != 1 else def_dut)
                    denominaciones[idx] = parm_container.text_input(f'Denominación celda #{idx}', value=default, key=key)

                # Actualización de los parámetros de la URL con los valores actuales
                set_url_params(denominaciones, denominacion_patron, fecha_calibracion_str, unidad_fuerza, str(limite_tolerancia_rel))
                st.divider()

                all_plot_buffers = []  # Lista para almacenar todos los buffers de gráficos generados

                # Bucle principal: procesamiento para cada celda de carga identificada
                for idx in celda_indices:
                    st.title(f'Calibración para {denominaciones[idx]}')

                    # Definición de nombres de columnas para la celda actual
                    pat_0 = f'PAT{idx}_0'
                    dut_0 = f'DUT{idx}_0'
                    pat_r = f'PAT{idx}_R'
                    dut_r = f'DUT{idx}_R'

                    pat_120 = f'PAT{idx}_120'
                    dut_120 = f'DUT{idx}_120'
                    pat_240 = f'PAT{idx}_240'
                    dut_240 = f'DUT{idx}_240'

                    # Verificación de la existencia de datos para diferentes condiciones de carga
                    has_0 = all(col in df.columns for col in [pat_0, dut_0])
                    has_r = all(col in df.columns for col in [pat_r, dut_r])
                    has_120 = all(col in df.columns for col in [pat_120, dut_120])
                    has_240 = all(col in df.columns for col in [pat_240, dut_240])

                    # Se requieren datos base de carga y descarga para continuar
                    if not (has_0 and has_r):
                        st.warning(f"Datos base (carga/descarga) incompletos para celda {idx}. Saltando.")
                        continue

                    # Cálculo de errores absolutos y relativos para carga 0°
                    abs_error_0, rel_error_0 = None, None
                    if has_0:
                        abs_error_0 = df[dut_0] - df[pat_0]
                        rel_error_0 = abs_error_0 / df[pat_0].replace(0, pd.NA)

                    # Cálculo de errores absolutos y relativos para descarga 0°
                    abs_error_r, rel_error_r = None, None
                    if has_r:
                        abs_error_r = df[dut_r] - df[pat_r]
                        rel_error_r = abs_error_r / df[pat_r].replace(0, pd.NA)

                    # Cálculo de errores absolutos y relativos para carga 120° (excentricidad)
                    abs_error_120, rel_error_120 = None, None
                    if has_120:
                        abs_error_120 = df[dut_120] - df[pat_120]
                        rel_error_120 = abs_error_120 / df[pat_120].replace(0, pd.NA)

                    # Cálculo de errores absolutos y relativos para carga 240° (excentricidad)
                    abs_error_240, rel_error_240 = None, None
                    if has_240:
                        abs_error_240 = df[dut_240] - df[pat_240]
                        rel_error_240 = abs_error_240 / df[pat_240].replace(0, pd.NA)

                    # Cálculo y visualización de coeficientes de correlación de Pearson
                    if has_0:
                        corr_carga = df[pat_0].corr(df[dut_0])
                        st.info(f"**Coeficiente de Correlación de Pearson (Carga 0°):** {corr_carga:.8f}")
                    if has_r:
                        corr_descarga = df[pat_r].corr(df[dut_r])
                        st.info(f"**Coeficiente de Correlación de Pearson (Descarga 0°):** {corr_descarga:.8f}")
                    if has_120:
                        corr_carga_120 = df[pat_120].corr(df[dut_120])
                        st.info(f"**Coeficiente de Correlación de Pearson (Carga 120°):** {corr_carga_120:.8f}")
                    if has_240:
                        corr_carga_240 = df[pat_240].corr(df[dut_240])
                        st.info(f"**Coeficiente de Correlación de Pearson (Carga 240°):** {corr_carga_240:.8f}")

                    # Gráfico de Puntos de Medición Originales
                    fig_orig, ax_orig = plt.subplots(figsize=(10, 5))

                    if has_0:
                        ax_orig.scatter(df[pat_0], df[dut_0], label="Carga 0°", color='tab:blue', marker='o', s=60, zorder=3)
                    if has_r:
                        ax_orig.scatter(df[pat_r], df[dut_r], label="Descarga 0°", color='tab:orange', marker='x', s=60, zorder=3)
                    if has_120:
                        ax_orig.scatter(df[pat_120], df[dut_120], label="Carga 120°", color='tab:green', marker='s', s=60, zorder=3)
                    if has_240:
                        ax_orig.scatter(df[pat_240], df[dut_240], label="Carga 240°", color='tab:red', marker='^', s=60, zorder=3)

                    ax_orig.set_xlabel(f"Patrón ({unidad_fuerza})")
                    ax_orig.set_ylabel(f"DUT ({unidad_fuerza})")
                    ax_orig.set_title(f"Puntos de Medición Originales para {denominaciones[idx]} - Patrón: {denominacion_patron}", pad=24)
                    ax_orig.legend()
                    ax_orig.grid(True)
                    fig_orig.text(0.5, 0.91, f"Fecha de Calibración: {fecha_calibracion_str}", ha='center', fontsize=10, color='gray')
                    st.pyplot(fig_orig)

                    buf_orig = io.BytesIO()
                    fig_orig.savefig(buf_orig, format="png", dpi=200)
                    st.download_button(f"Descargar gráfico de puntos originales para celda #{idx} (PNG)", data=buf_orig.getvalue(), file_name=f"puntos_originales_celda{idx}_{denominaciones[idx]}.png", mime="image/png")
                    all_plot_buffers.append((f"puntos_originales_celda{idx}_{denominaciones[idx]}.png", buf_orig))
                    st.divider()

                    # Gráfico de Error Absoluto
                    fig1, ax1 = plt.subplots(figsize=(10, 5))  # Ajustado figsize
                    x = np.arange(len(df))

                    # Cálculo del número de series para el gráfico de barras de error absoluto
                    num_series_abs = 0
                    if abs_error_0 is not None:
                        num_series_abs += 1
                    if abs_error_r is not None:
                        num_series_abs += 1
                    if abs_error_120 is not None:
                        num_series_abs += 1
                    if abs_error_240 is not None:
                        num_series_abs += 1

                    # Configuración de ancho de barras y desplazamiento para el gráfico
                    bar_width = 0.8 / num_series_abs if num_series_abs > 0 else 0.2
                    current_offset = -(num_series_abs - 1) * bar_width / 2

                    # Generación de barras para cada serie de error absoluto
                    if abs_error_0 is not None:
                        ax1.bar(x + current_offset, abs_error_0, width=bar_width, label="Carga 0°", color='tab:blue', alpha=0.7)
                        current_offset += bar_width
                    if abs_error_r is not None:
                        ax1.bar(x + current_offset, abs_error_r, width=bar_width, label="Descarga 0°", color='tab:orange', alpha=0.7)
                        current_offset += bar_width
                    if abs_error_120 is not None:
                        ax1.bar(x + current_offset, abs_error_120, width=bar_width, label="Carga 120°", color='tab:green', alpha=0.7)
                        current_offset += bar_width
                    if abs_error_240 is not None:
                        ax1.bar(x + current_offset, abs_error_240, width=bar_width, label="Carga 240°", color='tab:red', alpha=0.7)

                    # Configuración y visualización del gráfico de error absoluto
                    ax1.set_xlabel(f"Patrón ({unidad_fuerza})")
                    ax1.set_ylabel(f"Error absoluto ({unidad_fuerza})")
                    ax1.set_title(f"Error Absoluto para {denominaciones[idx]} - Patrón: {denominacion_patron}", pad=24)
                    ax1.set_xticks(x)
                    ax1.legend()
                    ax1.grid()
                    ax1.axhline(0, color='black', linewidth=1)
                    fig1.text(0.5, 0.91, f"Fecha de Calibración: {fecha_calibracion_str}", ha='center', fontsize=10, color='gray')
                    st.pyplot(fig1)
                    buf1 = io.BytesIO()
                    fig1.savefig(buf1, format="png", dpi=200)
                    st.download_button(f"Descargar gráfico de error absoluto para celda #{idx} (PNG)", data=buf1.getvalue(), file_name=f"error_absoluto_celda{idx}.png", mime="image/png")
                    all_plot_buffers.append((f"error_absoluto_celda{idx}_{denominaciones[idx]}.png", buf1))  # Agregar buffer a la lista

                    # Preparación de datos para la tabla de error absoluto
                    tabla_abs_data = {}
                    if has_0:
                        tabla_abs_data[f'PAT(L0°) [{unidad_fuerza}]'] = df[pat_0]
                        tabla_abs_data[f'DUT(L0°) [{unidad_fuerza}]'] = df[dut_0]
                        tabla_abs_data[f'Err(L0°) [{unidad_fuerza}]'] = abs_error_0
                    if has_r:
                        tabla_abs_data[f'PAT(U0°) [{unidad_fuerza}]'] = df[pat_r]
                        tabla_abs_data[f'DUT(U0°) [{unidad_fuerza}]'] = df[dut_r]
                        tabla_abs_data[f'Err(U0°) [{unidad_fuerza}]'] = abs_error_r
                    if has_120 and abs_error_120 is not None:
                        tabla_abs_data[f'PAT(L120°) [{unidad_fuerza}]'] = df[pat_120]
                        tabla_abs_data[f'DUT(L120°) [{unidad_fuerza}]'] = df[dut_120]
                        tabla_abs_data[f'Err(L120°) [{unidad_fuerza}]'] = abs_error_120
                    if has_240 and abs_error_240 is not None:
                        tabla_abs_data[f'PAT(L240°) [{unidad_fuerza}]'] = df[pat_240]
                        tabla_abs_data[f'DUT(L240°) [{unidad_fuerza}]'] = df[dut_240]
                        tabla_abs_data[f'Err(L240°) [{unidad_fuerza}]'] = abs_error_240

                    # Visualización de la tabla de error absoluto
                    tabla_abs = pd.DataFrame(tabla_abs_data)
                    st.markdown(f'**Tabla de Error Absoluto para {denominaciones[idx]}**')
                    st.dataframe(tabla_abs.style.format(precision=4).set_properties(**{'text-align': 'center'}), use_container_width=True)
                    st.info('Refs.: PAT=patrón, DUT=dispositivo, L=carga, U=descarga, Err=Error Absoluto o Relativo')
                    st.divider()

                    # Gráfico de Error Relativo
                    fig2, ax2 = plt.subplots(figsize=(10, 5))  # Ajustado figsize
                    # Puntos de error relativo
                    if rel_error_0 is not None:
                        ax2.scatter(df[pat_0], rel_error_0 * 100, label="Carga 0°", color='tab:blue', s=60, marker='o', zorder=3)
                    if rel_error_r is not None:
                        ax2.scatter(df[pat_r], rel_error_r * 100, label="Descarga 0°", color='tab:orange', s=60, marker='x', zorder=3)
                    if rel_error_120 is not None:
                        ax2.scatter(df[pat_120], rel_error_120 * 100, label="Carga 120°", color='tab:green', s=60, marker='s', zorder=3)  # square marker
                    if rel_error_240 is not None:
                        ax2.scatter(df[pat_240], rel_error_240 * 100, label="Carga 240°", color='tab:red', s=60, marker='^', zorder=3)  # triangle_up marker

                    # Ajustes polinómicos para las curvas de error relativo
                    if has_0 and rel_error_0 is not None and len(df[pat_0]) >= 4:
                        coef_carga = np.polyfit(df[pat_0].dropna(), rel_error_0.dropna() * 100, 3)
                        poly_carga = np.poly1d(coef_carga)
                        x_carga_plot = np.linspace(df[pat_0].min(), df[pat_0].max(), 200)
                        ax2.plot(x_carga_plot, poly_carga(x_carga_plot), color='tab:blue', linestyle='--', label='Ajuste carga 0°', zorder=2)

                    if has_r and rel_error_r is not None and len(df[pat_r]) >= 4:
                        coef_descarga = np.polyfit(df[pat_r].dropna(), rel_error_r.dropna() * 100, 3)
                        poly_descarga = np.poly1d(coef_descarga)
                        x_descarga_plot = np.linspace(df[pat_r].min(), df[pat_r].max(), 200)
                        ax2.plot(x_descarga_plot, poly_descarga(x_descarga_plot), color='tab:orange', linestyle='--', label='Ajuste descarga 0°', zorder=2)

                    if has_120 and rel_error_120 is not None and len(df[pat_120]) >= 4:
                        coef_carga_120 = np.polyfit(df[pat_120].dropna(), rel_error_120.dropna() * 100, 3)
                        poly_carga_120 = np.poly1d(coef_carga_120)
                        x_carga_120_plot = np.linspace(df[pat_120].min(), df[pat_120].max(), 200)
                        ax2.plot(x_carga_120_plot, poly_carga_120(x_carga_120_plot), color='tab:green', linestyle='--', label='Ajuste carga 120°', zorder=2)

                    if has_240 and rel_error_240 is not None and len(df[pat_240]) >= 4:
                        coef_carga_240 = np.polyfit(df[pat_240].dropna(), rel_error_240.dropna() * 100, 3)
                        poly_carga_240 = np.poly1d(coef_carga_240)
                        x_carga_240_plot = np.linspace(df[pat_240].min(), df[pat_240].max(), 200)
                        ax2.plot(x_carga_240_plot, poly_carga_240(x_carga_240_plot), color='tab:red', linestyle='--', label='Ajuste carga 240°', zorder=2)

                    # Configuración del gráfico de error relativo
                    ax2.set_xlabel(f"Patrón ({unidad_fuerza})")
                    ax2.set_ylabel("Error relativo (%)")
                    ax2.set_title(f"Error Relativo para {denominaciones[idx]} - Patrón: {denominacion_patron}", pad=24)
                    fig2.text(0.5, 0.91, f"Fecha de Calibración: {fecha_calibracion_str}", ha='center', fontsize=10, color='gray')
                    ax2.axhline(0, color='black', linewidth=1)
                    # Líneas de tolerancia y área sombreada
                    ax2.axhline(-limite_tolerancia_rel, color='gray', linestyle='--', linewidth=1)
                    ax2.axhline(limite_tolerancia_rel, color='gray', linestyle='--', linewidth=1)

                    # Determinación del rango para el área sombreada de tolerancia
                    all_pat_data = []
                    if has_0:
                        all_pat_data.append(df[pat_0].dropna())
                    if has_r:
                        all_pat_data.append(df[pat_r].dropna())
                    if has_120:
                        all_pat_data.append(df[pat_120].dropna())
                    if has_240:
                        all_pat_data.append(df[pat_240].dropna())

                    if all_pat_data:
                        combined_pat_data = pd.concat(all_pat_data)
                        x_fill_min = combined_pat_data.min()
                        x_fill_max = combined_pat_data.max()
                        ax2.fill_between(
                            np.linspace(x_fill_min, x_fill_max, 200),
                            -limite_tolerancia_rel,
                            limite_tolerancia_rel,
                            color='green',
                            alpha=0.2,
                            label=f'Zona de tolerancia (+/-{limite_tolerancia_rel:.1f}%)'
                        )
                    else:  # Fallback si no hay datos de patrón
                        ax2.fill_between(
                            np.linspace(0, 1, 200),  # dummy range
                            -limite_tolerancia_rel,
                            limite_tolerancia_rel,
                            color='green',
                            alpha=0.2,
                            label=f'Zona de tolerancia (+/-{limite_tolerancia_rel:.1f}%)'
                        )

                    # Visualización y descarga del gráfico de error relativo
                    ax2.legend()
                    ax2.grid()
                    ax2.grid(which='major', linestyle='-', linewidth=0.7)
                    ax2.grid(which='minor', linestyle=':', linewidth=0.5, alpha=1.0)
                    ax2.minorticks_on()
                    st.pyplot(fig2)
                    buf2 = io.BytesIO()
                    fig2.savefig(buf2, format="png", dpi=200)
                    st.download_button(f"Descargar gráfico de error relativo para celda #{idx} (PNG)", data=buf2.getvalue(), file_name=f"error_relativo_celda{idx}.png", mime="image/png")
                    all_plot_buffers.append((f"error_relativo_celda{idx}_{denominaciones[idx]}.png", buf2))  # Agregar buffer a la lista

                    # Preparación de datos para la tabla de error relativo
                    tabla_rel_data = {}
                    if has_0 and rel_error_0 is not None:
                        tabla_rel_data[f'PAT(L0°) [{unidad_fuerza}]'] = df[pat_0]
                        tabla_rel_data[f'DUT(L0°) [{unidad_fuerza}]'] = df[dut_0]
                        tabla_rel_data['Err(L0°) [%]'] = rel_error_0 * 100
                    if has_r and rel_error_r is not None:
                        tabla_rel_data[f'PAT(U0°) [{unidad_fuerza}]'] = df[pat_r]
                        tabla_rel_data[f'DUT(U0°) [{unidad_fuerza}]'] = df[dut_r]
                        tabla_rel_data['Err(U0°) [%]'] = rel_error_r * 100
                    if has_120 and rel_error_120 is not None:
                        tabla_rel_data[f'PAT(L120°) [{unidad_fuerza}]'] = df[pat_120]
                        tabla_rel_data[f'DUT(L120°) [{unidad_fuerza}]'] = df[dut_120]
                        tabla_rel_data['Err(L120°) [%]'] = rel_error_120 * 100
                    if has_240 and rel_error_240 is not None:
                        tabla_rel_data[f'PAT(L240°) [{unidad_fuerza}]'] = df[pat_240]
                        tabla_rel_data[f'DUT(L240°) [{unidad_fuerza}]'] = df[dut_240]
                        tabla_rel_data['Err(L240°) [%]'] = rel_error_240 * 100

                    # Visualización de la tabla de error relativo
                    tabla_rel = pd.DataFrame(tabla_rel_data)
                    st.markdown(f'**Tabla de Error Relativo para {denominaciones[idx]}**')
                    st.dataframe(tabla_rel.style.format(precision=4).set_properties(**{'text-align': 'center'}), use_container_width=True)
                    st.info('Refs.: PAT=patrón, DUT=dispositivo, L=carga, U=descarga, Err=Error Absoluto o Relativo')
                    st.divider()

                # Sección para cargar documentación adicional
                st.subheader("Documentación Adicional")
                ficha_patron_file = st.file_uploader("Ficha de la celda patrón (PNG o JPG)", type=["png", "jpg"], key="ficha_patron")
                ficha_dut_file = st.file_uploader("Ficha de la celda bajo prueba (PNG o JPG)", type=["png", "jpg"], key="ficha_dut")
                foto_montaje_file = st.file_uploader("Fotografía del montaje del sistema (PNG o JPG)", type=["png", "jpg"], key="foto_montaje")
                documentacion_aplicada = st.text_input("Documentación aplicada", value="N/C", key="doc_aplicada")
                n_requerimiento = st.text_input("N° de requerimiento", key="n_requerimiento")
                st.divider()

                # Sección para descargar todos los gráficos en un ZIP y generar el informe PDF
                if all_plot_buffers:
                    # Creación del archivo ZIP en memoria
                    zip_buffer = io.BytesIO()
                    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
                        for file_name, buf_data in all_plot_buffers:
                            buf_data.seek(0)
                            zip_file.writestr(file_name, buf_data.read())

                    zip_buffer.seek(0)

                    col_zip, col_pdf = st.columns(2)

                    # Botón para descargar el archivo ZIP
                    with col_zip:
                        st.download_button(
                            label="Descargar todos los gráficos (ZIP)",
                            data=zip_buffer,
                            file_name=f"graficos_calibracion_{fecha_calibracion.strftime('%Y%m%d')}.zip",
                            mime="application/zip"
                        )

                    # Botón para generar y descargar el informe PDF
                    with col_pdf:
                        if st.button("Generar informe PDF"):
                            pdf_data = self.generar_informe_pdf(
                                self.st,
                                fecha_calibracion_str,
                                denominacion_patron,
                                unidad_fuerza,
                                limite_tolerancia_rel,
                                celda_indices,
                                denominaciones,
                                df,
                                all_plot_buffers,
                                n_requerimiento,
                                documentacion_aplicada,
                                ficha_dut_file,
                                ficha_patron_file,
                                foto_montaje_file
                            )
                            if pdf_data:
                                st.download_button(
                                    label="Descargar PDF generado",
                                    data=pdf_data.getvalue(),
                                    file_name=f"informe_calibracion_{fecha_calibracion.strftime('%Y%m%d')}.pdf",
                                    mime="application/pdf"
                                )


if __name__ == "__main__":
    app = CalibrationApp()
    app.run()
