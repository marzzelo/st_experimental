import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io
from datetime import date
import numpy as np
from config import page_config
import re
import zipfile # Importar zipfile
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT


class CalibrationApp:
    def __init__(self):
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

    def generar_informe_pdf(self, st_obj, fecha_calibracion_str, denominacion_patron, unidad_fuerza, limite_tolerancia_rel, celda_indices, denominaciones, df_calibracion, all_plot_buffers_with_names, n_requerimiento=None, documentacion_aplicada=None, ficha_dut_file=None, ficha_patron_file=None, foto_montaje_file=None):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter,
                                rightMargin=inch, leftMargin=inch,
                                topMargin=inch, bottomMargin=inch)
        styles = getSampleStyleSheet()
        story = []

        # Estilos personalizados
        style_titulo_principal = ParagraphStyle(name='TituloPrincipal', parent=styles['h1'], alignment=TA_CENTER, fontSize=16, spaceAfter=20)
        style_subtitulo = ParagraphStyle(name='Subtitulo', parent=styles['h2'], alignment=TA_CENTER, fontSize=14, spaceAfter=10)
        style_normal_centro = ParagraphStyle(name='NormalCentro', parent=styles['Normal'], alignment=TA_CENTER)
        style_normal_justificado = ParagraphStyle(name='NormalJustificado', parent=styles['Normal'], alignment=TA_JUSTIFY, spaceBefore=6, spaceAfter=6)
        style_info_header = ParagraphStyle(name='InfoHeader', parent=styles['Normal'], fontSize=10, alignment=TA_LEFT, spaceBefore=6, spaceAfter=6)
        style_celda_header = ParagraphStyle(name='CeldaHeader', parent=styles['h3'], fontSize=12, spaceBefore=12, spaceAfter=8, alignment=TA_CENTER) # Centered for image titles
        style_table_title = ParagraphStyle(name='TableTitle', parent=styles['h3'], fontSize=10, spaceBefore=10, spaceAfter=4, alignment=TA_LEFT)

        # Título General
        story.append(Paragraph("LABORATORIO DE INGENIERÍA DE MATERIALES Y ENSAYOS ESTRUCTURALES", style_titulo_principal))
        story.append(Paragraph("INFORME DE ENSAYO DE CALIBRACIÓN", style_subtitulo))
        if n_requerimiento and n_requerimiento.strip():
            story.append(Paragraph(f"Requerimiento N°: {n_requerimiento}", style_info_header))
        if documentacion_aplicada and documentacion_aplicada.strip():
            story.append(Paragraph(f"Documentación Aplicada: {documentacion_aplicada}", style_info_header))
        story.append(Spacer(1, 0.5*inch))

        # Información General de Calibración
        story.append(Paragraph(f"<b>Fecha de calibración:</b> {fecha_calibracion_str}", style_info_header))
        story.append(Paragraph(f"<b>Instrumento Patrón:</b> {denominacion_patron}", style_info_header))
        story.append(Paragraph(f"<b>Unidad de Fuerza:</b> {unidad_fuerza}", style_info_header))
        story.append(Paragraph(f"<b>Límite de Tolerancia Relativa:</b> ± {limite_tolerancia_rel}%", style_info_header))
        story.append(Spacer(1, 0.3*inch))

        for idx in celda_indices:
            story.append(PageBreak())
            story.append(Paragraph(f"Resultados para: {denominaciones[idx]}", style_celda_header))
            
            # Ficha DUT
            story.append(Paragraph("Equipo bajo prueba", style_celda_header))
            if ficha_dut_file:
                try:
                    ficha_dut_file.seek(0)
                    img_dut = Image(ficha_dut_file, width=5*inch, height=3.5*inch, kind='bound') # Width set, height auto
                    img_dut.hAlign = 'CENTER'
                    story.append(img_dut)
                    story.append(Spacer(1, 0.2*inch))
                except Exception as e:
                    story.append(Paragraph(f"(Error al cargar imagen DUT: {e})", styles['Normal']))
            else:
                story.append(Paragraph("(No se proporcionó imagen)", style_normal_centro))
            story.append(Spacer(1, 0.2*inch))

            # Ficha Patrón
            story.append(Paragraph("Equipamiento Patrón Utilizado", style_celda_header))
            if ficha_patron_file:
                try:
                    ficha_patron_file.seek(0)
                    img_patron = Image(ficha_patron_file, width=5*inch, height=3.5*inch, kind='bound') # Width set, height auto
                    img_patron.hAlign = 'CENTER'
                    story.append(img_patron)
                    story.append(Spacer(1, 0.2*inch))
                except Exception as e:
                    story.append(Paragraph(f"(Error al cargar imagen Patrón: {e})", styles['Normal']))
            else:
                story.append(Paragraph("(No se proporcionó imagen)", style_normal_centro))
            story.append(Spacer(1, 0.3*inch)) # Extra spacer before coefficients

            # Coeficientes de Correlación (Ejemplo, necesitaría datos reales)
            story.append(Paragraph("<b>Coeficientes de Correlación de Pearson:</b>", styles['Normal']))
            
            pat_0_col = f'PAT{idx}_0'
            dut_0_col = f'DUT{idx}_0'
            pat_r_col = f'PAT{idx}_R'
            dut_r_col = f'DUT{idx}_R'
            pat_120_col = f'PAT{idx}_120'
            dut_120_col = f'DUT{idx}_120'
            pat_240_col = f'PAT{idx}_240'
            dut_240_col = f'DUT{idx}_240'

            if pat_0_col in df_calibracion.columns and dut_0_col in df_calibracion.columns and not df_calibracion[[pat_0_col, dut_0_col]].isnull().all().all():
                try:
                    corr_carga_0 = df_calibracion[pat_0_col].corr(df_calibracion[dut_0_col])
                    story.append(Paragraph(f"- Carga 0°: {corr_carga_0:.8f}", styles['Bullet']))
                except Exception as e:
                    story.append(Paragraph(f"- Carga 0°: (Error al calcular: {e})", styles['Bullet']))
            else:
                story.append(Paragraph("- Carga 0°: (Datos no disponibles o insuficientes)", styles['Bullet']))

            if pat_r_col in df_calibracion.columns and dut_r_col in df_calibracion.columns and not df_calibracion[[pat_r_col, dut_r_col]].isnull().all().all():
                try:
                    corr_descarga_0 = df_calibracion[pat_r_col].corr(df_calibracion[dut_r_col])
                    story.append(Paragraph(f"- Descarga 0°: {corr_descarga_0:.8f}", styles['Bullet']))
                except Exception as e:
                    story.append(Paragraph(f"- Descarga 0°: (Error al calcular: {e})", styles['Bullet']))
            else:
                story.append(Paragraph("- Descarga 0°: (Datos no disponibles o insuficientes)", styles['Bullet']))

            if pat_120_col in df_calibracion.columns and dut_120_col in df_calibracion.columns and not df_calibracion[[pat_120_col, dut_120_col]].isnull().all().all():
                try:
                    corr_carga_120 = df_calibracion[pat_120_col].corr(df_calibracion[dut_120_col])
                    story.append(Paragraph(f"- Carga 120°: {corr_carga_120:.8f}", styles['Bullet']))
                except Exception as e:
                    story.append(Paragraph(f"- Carga 120°: (Error al calcular: {e})", styles['Bullet']))
            
            if pat_240_col in df_calibracion.columns and dut_240_col in df_calibracion.columns and not df_calibracion[[pat_240_col, dut_240_col]].isnull().all().all():
                try:
                    corr_carga_240 = df_calibracion[pat_240_col].corr(df_calibracion[dut_240_col])
                    story.append(Paragraph(f"- Carga 240°: {corr_carga_240:.8f}", styles['Bullet']))
                except Exception as e:
                    story.append(Paragraph(f"- Carga 240°: (Error al calcular: {e})", styles['Bullet']))

            story.append(Spacer(1, 0.2*inch))
            story.append(Paragraph("<b>Gráficos:</b>", styles['Normal']))

            for plot_name, plot_buffer in all_plot_buffers_with_names:
                if f"celda{idx}" in plot_name:
                    plot_buffer.seek(0)
                    img = Image(plot_buffer, width=6*inch, height=3*inch) # Ajustar tamaño según sea necesario
                    img.hAlign = 'CENTER'
                    story.append(img)
                    # Extraer título del gráfico del nombre del archivo para el pie de foto
                    clean_plot_name = plot_name.replace(f'_celda{idx}_{denominaciones[idx]}', '').replace(f'_celda{idx}','').replace('_',' ').capitalize()
                    if clean_plot_name.endswith('.png'):
                        clean_plot_name = clean_plot_name[:-4]
                    story.append(Paragraph(f"<i>Gráfico: {clean_plot_name}</i>", style_normal_centro))
                    story.append(Spacer(1, 0.2*inch))
            
            story.append(Paragraph("<b>Tablas de Datos:</b>", styles['Normal']))
            story.append(Spacer(1, 0.1*inch))

            # Helper function for formatting numbers
            def format_val(value, precision=4):
                if self.pd.isna(value):
                    return "N/A"
                if isinstance(value, (float, self.np.float_)):
                    return f"{value:.{precision}f}"
                return str(value)

            # Column names for this idx (already defined above, ensure they are used consistently)
            # pat_0_col, dut_0_col, pat_r_col, dut_r_col, pat_120_col, dut_120_col, pat_240_col, dut_240_col

            # Check column existence
            has_0 = pat_0_col in df_calibracion.columns and dut_0_col in df_calibracion.columns
            has_r = pat_r_col in df_calibracion.columns and dut_r_col in df_calibracion.columns
            has_120 = pat_120_col in df_calibracion.columns and dut_120_col in df_calibracion.columns
            has_240 = pat_240_col in df_calibracion.columns and dut_240_col in df_calibracion.columns

            common_table_style_list = [
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#4F81BD")), # Header background
                ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,0), 7), 
                ('FONTSIZE', (0,1), (-1,-1), 6), 
                ('BOTTOMPADDING', (0,0), (-1,0), 5),
                ('TOPPADDING', (0,0), (-1,0), 5),
                ('BOTTOMPADDING', (0,1), (-1,-1), 3),
                ('TOPPADDING', (0,1), (-1,-1), 3),
                ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
                ('LEFTPADDING', (0,0), (-1,-1), 1.5), 
                ('RIGHTPADDING', (0,0), (-1,-1), 1.5),
            ]
            
            # 1. Original Measurements Table
            story.append(Paragraph(f"Tabla de Mediciones Originales: {denominaciones[idx]}", style_table_title))
            table_data_orig = []
            headers_orig = []
            cols_orig_series = []

            if has_0:
                headers_orig.extend([f'PAT(L0°)\n({unidad_fuerza})', f'DUT(L0°)\n({unidad_fuerza})'])
                cols_orig_series.extend([df_calibracion[pat_0_col], df_calibracion[dut_0_col]])
            if has_r:
                headers_orig.extend([f'PAT(U0°)\n({unidad_fuerza})', f'DUT(U0°)\n({unidad_fuerza})'])
                cols_orig_series.extend([df_calibracion[pat_r_col], df_calibracion[dut_r_col]])
            if has_120:
                headers_orig.extend([f'PAT(L120°)\n({unidad_fuerza})', f'DUT(L120°)\n({unidad_fuerza})'])
                cols_orig_series.extend([df_calibracion[pat_120_col], df_calibracion[dut_120_col]])
            if has_240:
                headers_orig.extend([f'PAT(L240°)\n({unidad_fuerza})', f'DUT(L240°)\n({unidad_fuerza})'])
                cols_orig_series.extend([df_calibracion[pat_240_col], df_calibracion[dut_240_col]])

            if headers_orig:
                table_data_orig.append(headers_orig)
                for i in range(len(df_calibracion)):
                    row = [format_val(s.iloc[i] if i < len(s) and not self.pd.isna(s.iloc[i]) else self.pd.NA) for s in cols_orig_series]
                    table_data_orig.append(row)
                
                num_cols_orig = len(headers_orig)
                col_width_orig = (7.5 * inch) / num_cols_orig if num_cols_orig > 0 else 1 * inch
                
                pdf_table_orig = Table(table_data_orig, colWidths=[col_width_orig]*num_cols_orig if num_cols_orig > 0 else None)
                pdf_table_orig.setStyle(TableStyle(common_table_style_list))
                story.append(pdf_table_orig)
                story.append(Spacer(1, 0.1*inch))

            # 2. Absolute Error Table
            story.append(Paragraph(f"Tabla de Error Absoluto: {denominaciones[idx]}", style_table_title))
            table_data_abs = []
            headers_abs = []
            cols_abs_series = []

            if has_0:
                abs_err_0 = df_calibracion[dut_0_col] - df_calibracion[pat_0_col]
                headers_abs.extend([f'PAT(L0°)\n({unidad_fuerza})', f'DUT(L0°)\n({unidad_fuerza})', f'Err.Abs(L0°)\n({unidad_fuerza})'])
                cols_abs_series.extend([df_calibracion[pat_0_col], df_calibracion[dut_0_col], abs_err_0])
            if has_r:
                abs_err_r = df_calibracion[dut_r_col] - df_calibracion[pat_r_col]
                headers_abs.extend([f'PAT(U0°)\n({unidad_fuerza})', f'DUT(U0°)\n({unidad_fuerza})', f'Err.Abs(U0°)\n({unidad_fuerza})'])
                cols_abs_series.extend([df_calibracion[pat_r_col], df_calibracion[dut_r_col], abs_err_r])
            if has_120:
                abs_err_120 = df_calibracion[dut_120_col] - df_calibracion[pat_120_col]
                headers_abs.extend([f'PAT(L120°)\n({unidad_fuerza})', f'DUT(L120°)\n({unidad_fuerza})', f'Err.Abs(L120°)\n({unidad_fuerza})'])
                cols_abs_series.extend([df_calibracion[pat_120_col], df_calibracion[dut_120_col], abs_err_120])
            if has_240:
                abs_err_240 = df_calibracion[dut_240_col] - df_calibracion[pat_240_col]
                headers_abs.extend([f'PAT(L240°)\n({unidad_fuerza})', f'DUT(L240°)\n({unidad_fuerza})', f'Err.Abs(L240°)\n({unidad_fuerza})'])
                cols_abs_series.extend([df_calibracion[pat_240_col], df_calibracion[dut_240_col], abs_err_240])

            if headers_abs:
                table_data_abs.append(headers_abs)
                for i in range(len(df_calibracion)):
                    row = [format_val(s.iloc[i] if i < len(s) and not self.pd.isna(s.iloc[i]) else self.pd.NA) for s in cols_abs_series]
                    table_data_abs.append(row)

                num_cols_abs = len(headers_abs)
                col_width_abs = (7.5 * inch) / num_cols_abs if num_cols_abs > 0 else 1 * inch
                
                pdf_table_abs = Table(table_data_abs, colWidths=[col_width_abs]*num_cols_abs if num_cols_abs > 0 else None)
                pdf_table_abs.setStyle(TableStyle(common_table_style_list))
                story.append(pdf_table_abs)
                story.append(Spacer(1, 0.1*inch))

            # 3. Relative Error Table
            story.append(Paragraph(f"Tabla de Error Relativo: {denominaciones[idx]}", style_table_title))
            table_data_rel = []
            headers_rel = []
            cols_rel_series = []

            if has_0:
                pat_0_series_for_rel = df_calibracion[pat_0_col].replace(0, self.np.nan)
                rel_err_0 = ((df_calibracion[dut_0_col] - df_calibracion[pat_0_col]) / pat_0_series_for_rel) * 100
                headers_rel.extend([f'PAT(L0°)\n({unidad_fuerza})', f'DUT(L0°)\n({unidad_fuerza})', f'Err.Rel(L0°)\n(%)'])
                cols_rel_series.extend([df_calibracion[pat_0_col], df_calibracion[dut_0_col], rel_err_0])
            if has_r:
                pat_r_series_for_rel = df_calibracion[pat_r_col].replace(0, self.np.nan)
                rel_err_r = ((df_calibracion[dut_r_col] - df_calibracion[pat_r_col]) / pat_r_series_for_rel) * 100
                headers_rel.extend([f'PAT(U0°)\n({unidad_fuerza})', f'DUT(U0°)\n({unidad_fuerza})', f'Err.Rel(U0°)\n(%)'])
                cols_rel_series.extend([df_calibracion[pat_r_col], df_calibracion[dut_r_col], rel_err_r])
            if has_120:
                pat_120_series_for_rel = df_calibracion[pat_120_col].replace(0, self.np.nan)
                rel_err_120 = ((df_calibracion[dut_120_col] - df_calibracion[pat_120_col]) / pat_120_series_for_rel) * 100
                headers_rel.extend([f'PAT(L120°)\n({unidad_fuerza})', f'DUT(L120°)\n({unidad_fuerza})', f'Err.Rel(L120°)\n(%)'])
                cols_rel_series.extend([df_calibracion[pat_120_col], df_calibracion[dut_120_col], rel_err_120])
            if has_240:
                pat_240_series_for_rel = df_calibracion[pat_240_col].replace(0, self.np.nan)
                rel_err_240 = ((df_calibracion[dut_240_col] - df_calibracion[pat_240_col]) / pat_240_series_for_rel) * 100
                headers_rel.extend([f'PAT(L240°)\n({unidad_fuerza})', f'DUT(L240°)\n({unidad_fuerza})', f'Err.Rel(L240°)\n(%)'])
                cols_rel_series.extend([df_calibracion[pat_240_col], df_calibracion[dut_240_col], rel_err_240])

            if headers_rel:
                table_data_rel.append(headers_rel)
                for i in range(len(df_calibracion)):
                    row_values = []
                    for k, series_obj in enumerate(cols_rel_series):
                        val = series_obj.iloc[i] if i < len(series_obj) and not self.pd.isna(series_obj.iloc[i]) else self.pd.NA
                        is_err_col = (k + 1) % 3 == 0 
                        precision = 2 if is_err_col else 4
                        row_values.append(format_val(val, precision=precision))
                    table_data_rel.append(row_values)

                num_cols_rel = len(headers_rel)
                col_width_rel = (7.5 * inch) / num_cols_rel if num_cols_rel > 0 else 1 * inch
                
                pdf_table_rel = Table(table_data_rel, colWidths=[col_width_rel]*num_cols_rel if num_cols_rel > 0 else None)
                pdf_table_rel.setStyle(TableStyle(common_table_style_list))
                story.append(pdf_table_rel)
            
            story.append(Spacer(1, 0.2*inch)) # Spacer after all tables for this celda

        # Foto Montaje al final del informe
        if foto_montaje_file:
            story.append(PageBreak())
            story.append(Paragraph("Montaje del Sistema de Ensayos", style_celda_header))
            try:
                foto_montaje_file.seek(0)
                img_montaje = Image(foto_montaje_file, width=6*inch, height=8*inch, kind='bound') # Width set, height auto
                img_montaje.hAlign = 'CENTER'
                story.append(img_montaje)
                story.append(Spacer(1, 0.2*inch))
            except Exception as e:
                story.append(Paragraph(f"(Error al cargar imagen de montaje: {e})", styles['Normal']))
        
        try:
            doc.build(story)
        except Exception as e:
            st_obj.error(f"Error al generar el PDF: {e}")
            error_buffer = io.BytesIO()
            error_doc = SimpleDocTemplate(error_buffer, pagesize=letter)
            error_story = [Paragraph(f"Error al generar el PDF: {e}", styles['Normal'])]
            try:
                error_doc.build(error_story)
                error_buffer.seek(0)
                return error_buffer
            except:
                return None

        buffer.seek(0)
        return buffer

    def run(self):
        st = self.st
        pd = self.pd
        plt = self.plt
        io = self.io
        date = self.date
        np = self.np
        params = st.query_params
        def_dut = params.get('dut', 'DUT')
        def_patron = params.get('patron', 'PAT')
        def fecha_param():
            return params.get('fecha', date.today().strftime('%d/%m/%Y'))
        def unidad_param():
            return params.get('unidad', 'daN')
        def limite_tolerancia_param():
            return params.get('lim_tol_rel', '1.0')
        def set_url_params(denominaciones, denominacion_patron, fecha_calibracion_str, unidad_fuerza, limite_tolerancia_rel_str):
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
        uploaded_file = st.file_uploader("Selecciona un archivo Excel de calibración", type=["xlsx"])
        if uploaded_file is not None:
            parm_container = st.container(border=True)
            with parm_container:
                st.subheader("Parámetros de Configuración")
                col_patron, col_fecha, col_unidad = st.columns(3)
                with col_patron:
                    denominacion_patron = st.text_input('Denominación patrón', value=def_patron, key='patron')
                    limite_tolerancia_rel = st.number_input('Límite de tolerancia (%)', min_value=0.1, value=float(limite_tolerancia_param()), step=0.1, key='lim_tol_rel')
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
            denominaciones = {}
            df = pd.read_excel(uploaded_file)
            required_cols = ["PAT1_0", "DUT1_0", "PAT1_R", "DUT1_R"]
            if not all(col in df.columns for col in required_cols):
                st.error(f"El archivo debe contener las columnas: {', '.join(required_cols)}")
            else:
                st.success("Archivo cargado correctamente.")
                df = df.loc[~(df[required_cols] == 0).all(axis=1)]
                col_pattern = re.compile(r'PAT(\d+)_0')
                celda_indices = sorted(set(int(col_pattern.match(col).group(1)) for col in df.columns if col_pattern.match(col)))
                denominaciones = {}
                for idx in celda_indices:
                    key = f'dut_{idx}'
                    default = params.get(f'dut{idx}', f'Celda {idx}' if idx != 1 else def_dut)
                    denominaciones[idx] = parm_container.text_input(f'Denominación celda #{idx}', value=default, key=key)
                set_url_params(denominaciones, denominacion_patron, fecha_calibracion_str, unidad_fuerza, str(limite_tolerancia_rel))
                st.divider()

                all_plot_buffers = [] # Lista para almacenar todos los buffers de gráficos

                for idx in celda_indices:
                    st.title(f'Calibración para {denominaciones[idx]}')
                    pat_0 = f'PAT{idx}_0'
                    dut_0 = f'DUT{idx}_0'
                    pat_r = f'PAT{idx}_R'
                    dut_r = f'DUT{idx}_R'

                    pat_120 = f'PAT{idx}_120'
                    dut_120 = f'DUT{idx}_120'
                    pat_240 = f'PAT{idx}_240'
                    dut_240 = f'DUT{idx}_240'

                    has_0 = all(col in df.columns for col in [pat_0, dut_0])
                    has_r = all(col in df.columns for col in [pat_r, dut_r])
                    has_120 = all(col in df.columns for col in [pat_120, dut_120])
                    has_240 = all(col in df.columns for col in [pat_240, dut_240])

                    if not (has_0 and has_r): # Need at least the basic load and unload
                        st.warning(f"Datos base (carga/descarga) incompletos para celda {idx}. Saltando.")
                        continue
                    
                    abs_error_0, rel_error_0 = None, None
                    if has_0:
                        abs_error_0 = df[dut_0] - df[pat_0]
                        rel_error_0 = abs_error_0 / df[pat_0].replace(0, pd.NA)

                    abs_error_r, rel_error_r = None, None
                    if has_r:
                        abs_error_r = df[dut_r] - df[pat_r]
                        rel_error_r = abs_error_r / df[pat_r].replace(0, pd.NA)

                    abs_error_120, rel_error_120 = None, None
                    if has_120:
                        abs_error_120 = df[dut_120] - df[pat_120]
                        rel_error_120 = abs_error_120 / df[pat_120].replace(0, pd.NA)

                    abs_error_240, rel_error_240 = None, None
                    if has_240:
                        abs_error_240 = df[dut_240] - df[pat_240]
                        rel_error_240 = abs_error_240 / df[pat_240].replace(0, pd.NA)

                    # Calcular y mostrar coeficientes de correlación de Pearson
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
                    
                    # Gráfico de Puntos de Medición Originales ------------------------------------------
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

                    # Gráfico de Error Absoluto ------------------------------------------
                    fig1, ax1 = plt.subplots(figsize=(10, 5)) # Ajustado figsize
                    x = np.arange(len(df))
                    
                    num_series_abs = 0
                    if abs_error_0 is not None: num_series_abs +=1
                    if abs_error_r is not None: num_series_abs +=1
                    if abs_error_120 is not None: num_series_abs +=1
                    if abs_error_240 is not None: num_series_abs +=1

                    bar_width = 0.8 / num_series_abs if num_series_abs > 0 else 0.2
                    current_offset = - (num_series_abs -1) * bar_width / 2
                    
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
                    all_plot_buffers.append((f"error_absoluto_celda{idx}_{denominaciones[idx]}.png", buf1)) # Agregar buffer a la lista
                    
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
                    
                    tabla_abs = pd.DataFrame(tabla_abs_data)
                    st.markdown(f'**Tabla de Error Absoluto para {denominaciones[idx]}**')
                    st.dataframe(tabla_abs.style.format(precision=4).set_properties(**{'text-align': 'center'}), use_container_width=True)
                    st.info('Refs.: PAT=patrón, DUT=dispositivo, L=carga, U=descarga, Err=Error Absoluto o Relativo')
                    st.divider()
                    
                    # Gráfico de Error Relativo ------------------------------------------
                    fig2, ax2 = plt.subplots(figsize=(10, 5)) # Ajustado figsize
                    if rel_error_0 is not None:
                        ax2.scatter(df[pat_0], rel_error_0 * 100, label="Carga 0°", color='tab:blue', s=60, marker='o', zorder=3)
                    if rel_error_r is not None:
                        ax2.scatter(df[pat_r], rel_error_r * 100, label="Descarga 0°", color='tab:orange', s=60, marker='x', zorder=3)
                    if rel_error_120 is not None:
                        ax2.scatter(df[pat_120], rel_error_120 * 100, label="Carga 120°", color='tab:green', s=60, marker='s', zorder=3) # square marker
                    if rel_error_240 is not None:
                        ax2.scatter(df[pat_240], rel_error_240 * 100, label="Carga 240°", color='tab:red', s=60, marker='^', zorder=3) # triangle_up marker

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
                    
                    ax2.set_xlabel(f"Patrón ({unidad_fuerza})")
                    ax2.set_ylabel("Error relativo (%)")
                    ax2.set_title(f"Error Relativo para {denominaciones[idx]} - Patrón: {denominacion_patron}", pad=24)
                    fig2.text(0.5, 0.91, f"Fecha de Calibración: {fecha_calibracion_str}", ha='center', fontsize=10, color='gray')
                    ax2.axhline(0, color='black', linewidth=1)
                    # Agregar cotas horizontales y área sombreada
                    ax2.axhline(-limite_tolerancia_rel, color='gray', linestyle='--', linewidth=1)
                    ax2.axhline(limite_tolerancia_rel, color='gray', linestyle='--', linewidth=1)
                    
                    # Determine overall min/max for fill_between x-range
                    all_pat_data = []
                    if has_0: all_pat_data.append(df[pat_0].dropna())
                    if has_r: all_pat_data.append(df[pat_r].dropna())
                    if has_120: all_pat_data.append(df[pat_120].dropna())
                    if has_240: all_pat_data.append(df[pat_240].dropna())
                    
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
                    else: # Fallback if no pat data at all (should not happen with current checks)
                         ax2.fill_between(
                            np.linspace(0,1,200), # dummy range
                            -limite_tolerancia_rel,
                            limite_tolerancia_rel,
                            color='green',
                            alpha=0.2,
                            label=f'Zona de tolerancia (+/-{limite_tolerancia_rel:.1f}%)'
                        )

                    ax2.legend()
                    ax2.grid()
                    ax2.grid(which='major', linestyle='-', linewidth=0.7)
                    ax2.grid(which='minor', linestyle=':', linewidth=0.5, alpha=1.0)
                    ax2.minorticks_on()
                    st.pyplot(fig2)
                    buf2 = io.BytesIO()
                    fig2.savefig(buf2, format="png", dpi=200)
                    st.download_button(f"Descargar gráfico de error relativo para celda #{idx} (PNG)", data=buf2.getvalue(), file_name=f"error_relativo_celda{idx}.png", mime="image/png")
                    all_plot_buffers.append((f"error_relativo_celda{idx}_{denominaciones[idx]}.png", buf2)) # Agregar buffer a la lista
                    
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
                        
                    tabla_rel = pd.DataFrame(tabla_rel_data)
                    st.markdown(f'**Tabla de Error Relativo para {denominaciones[idx]}**')
                    st.dataframe(tabla_rel.style.format(precision=4).set_properties(**{'text-align': 'center'}), use_container_width=True)
                    st.info('Refs.: PAT=patrón, DUT=dispositivo, L=carga, U=descarga, Err=Error Absoluto o Relativo')
                    st.divider()

                st.subheader("Documentación Adicional")
                ficha_patron_file = st.file_uploader("Ficha de la celda patrón (PNG o JPG)", type=["png", "jpg"], key="ficha_patron")
                ficha_dut_file = st.file_uploader("Ficha de la celda bajo prueba (PNG o JPG)", type=["png", "jpg"], key="ficha_dut")
                foto_montaje_file = st.file_uploader("Fotografía del montaje del sistema (PNG o JPG)", type=["png", "jpg"], key="foto_montaje")
                documentacion_aplicada = st.text_input("Documentación aplicada", value="N/C", key="doc_aplicada")
                n_requerimiento = st.text_input("N° de requerimiento", key="n_requerimiento")
                st.divider()

                if all_plot_buffers:
                    zip_buffer = io.BytesIO()
                    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
                        for file_name, buf_data in all_plot_buffers:
                            buf_data.seek(0)
                            zip_file.writestr(file_name, buf_data.read())
                    
                    zip_buffer.seek(0)
                    
                    col_zip, col_pdf = st.columns(2)

                    with col_zip:
                        st.download_button(
                            label="Descargar todos los gráficos (ZIP)",
                            data=zip_buffer,
                            file_name=f"graficos_calibracion_{fecha_calibracion.strftime('%Y%m%d')}.zip",
                            mime="application/zip"
                        )
                    
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
