import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
import pandas as pd
import numpy as np
from reportlab.platypus import HRFlowable
from datetime import datetime
import getpass # Importar getpass

class ReportGenerator:
    @staticmethod
    def generar_informe_pdf(st_obj, fecha_calibracion_str, denominacion_patron, unidad_fuerza, limite_tolerancia_rel, celda_indices, denominaciones, df_calibracion, all_plot_buffers_with_names, n_requerimiento=None, documentacion_aplicada=None, ficha_dut_file=None, ficha_patron_file=None, foto_montaje_file=None):
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
        
        story.append(HRFlowable(width="100%", thickness=1, color=colors.grey, spaceBefore=10, spaceAfter=10))
        
        if n_requerimiento and n_requerimiento.strip():
            story.append(Spacer(1, 1.5*inch))
            story.append(Paragraph(f"<b>Requerimiento N°:</b> {n_requerimiento}", style_info_header))
        if documentacion_aplicada and documentacion_aplicada.strip():
            story.append(Paragraph(f"<b>Documentación Aplicada:</b> {documentacion_aplicada}", style_info_header))
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
            
            story.append(PageBreak())
            # Coeficientes de Correlación de Pearson en una tabla
            story.append(Paragraph("<b>Coeficientes de Correlación de Pearson</b>", style_table_title))
            
            correlation_data = [["Caso", "Pearson C.C"]] # Encabezados de la tabla

            pat_0_col = f'PAT{idx}_0'
            dut_0_col = f'DUT{idx}_0'
            pat_r_col = f'PAT{idx}_R'
            dut_r_col = f'DUT{idx}_R'
            pat_120_col = f'PAT{idx}_120'
            dut_120_col = f'DUT{idx}_120'
            pat_240_col = f'PAT{idx}_240'
            dut_240_col = f'DUT{idx}_240'

            # Carga 0°
            if pat_0_col in df_calibracion.columns and dut_0_col in df_calibracion.columns and not df_calibracion[[pat_0_col, dut_0_col]].isnull().all().all():
                try:
                    corr_carga_0 = df_calibracion[pat_0_col].corr(df_calibracion[dut_0_col])
                    correlation_data.append(["Carga 0°", f"{corr_carga_0:.8f}"])
                except Exception as e:
                    correlation_data.append(["Carga 0°", f"(Error: {e})"])
            else:
                correlation_data.append(["Carga 0°", "(Datos no disponibles)"])

            # Descarga 0°
            if pat_r_col in df_calibracion.columns and dut_r_col in df_calibracion.columns and not df_calibracion[[pat_r_col, dut_r_col]].isnull().all().all():
                try:
                    corr_descarga_0 = df_calibracion[pat_r_col].corr(df_calibracion[dut_r_col])
                    correlation_data.append(["Descarga 0°", f"{corr_descarga_0:.8f}"])
                except Exception as e:
                    correlation_data.append(["Descarga 0°", f"(Error: {e})"])
            else:
                correlation_data.append(["Descarga 0°", "(Datos no disponibles)"])

            # Carga 120°
            if pat_120_col in df_calibracion.columns and dut_120_col in df_calibracion.columns and not df_calibracion[[pat_120_col, dut_120_col]].isnull().all().all():
                try:
                    corr_carga_120 = df_calibracion[pat_120_col].corr(df_calibracion[dut_120_col])
                    correlation_data.append(["Carga 120°", f"{corr_carga_120:.8f}"])
                except Exception as e:
                    correlation_data.append(["Carga 120°", f"(Error: {e})"])
            # No agregar fila si no hay datos, para mantener la tabla limpia
            
            # Carga 240°
            if pat_240_col in df_calibracion.columns and dut_240_col in df_calibracion.columns and not df_calibracion[[pat_240_col, dut_240_col]].isnull().all().all():
                try:
                    corr_carga_240 = df_calibracion[pat_240_col].corr(df_calibracion[dut_240_col])
                    correlation_data.append(["Carga 240°", f"{corr_carga_240:.8f}"])
                except Exception as e:
                    correlation_data.append(["Carga 240°", f"(Error: {e})"])
            # No agregar fila si no hay datos, para mantener la tabla limpia

            if len(correlation_data) > 1: # Si hay datos además de los encabezados
                col_widths = [2.5*inch, 2.5*inch] # Ancho de las columnas
                correlation_table = Table(correlation_data, colWidths=col_widths)
                correlation_table.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#4F81BD")),
                    ('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),
                    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0,0), (-1,-1), 8),
                    ('BOTTOMPADDING', (0,0), (-1,0), 8),
                    ('TOPPADDING', (0,0), (-1,0), 8),
                    ('BOTTOMPADDING', (0,1), (-1,-1), 4),
                    ('TOPPADDING', (0,1), (-1,-1), 4),
                    ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
                    ('LEFTPADDING', (0,0), (-1,-1), 2), 
                    ('RIGHTPADDING', (0,0), (-1,-1), 2),
                ]))
                story.append(correlation_table)

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
            
            story.append(PageBreak())
            story.append(Paragraph("<b>Tablas de Datos</b>", style_subtitulo))
            story.append(Spacer(1, 0.1*inch))

            # Helper function for formatting numbers
            def format_val(value, precision=4):
                if pd.isna(value):
                    return "N/A"
                if isinstance(value, (float, np.float64)):
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
                headers_orig.extend([f'PAT(L0°)', f'DUT(L0°)'])
                cols_orig_series.extend([df_calibracion[pat_0_col], df_calibracion[dut_0_col]])
            if has_r:
                headers_orig.extend([f'PAT(U0°)', f'DUT(U0°)'])
                cols_orig_series.extend([df_calibracion[pat_r_col], df_calibracion[dut_r_col]])
            if has_120:
                headers_orig.extend([f'PAT(L120°)', f'DUT(L120°)'])
                cols_orig_series.extend([df_calibracion[pat_120_col], df_calibracion[dut_120_col]])
            if has_240:
                headers_orig.extend([f'PAT(L240°)', f'DUT(L240°)'])
                cols_orig_series.extend([df_calibracion[pat_240_col], df_calibracion[dut_240_col]])

            if headers_orig:
                table_data_orig.append(headers_orig)
                for i in range(len(df_calibracion)):
                    row = [format_val(s.iloc[i] if i < len(s) and not pd.isna(s.iloc[i]) else pd.NA) for s in cols_orig_series]
                    table_data_orig.append(row)
                
                num_cols_orig = len(headers_orig)
                col_width_orig = (6.5 * inch) / num_cols_orig if num_cols_orig > 0 else 1 * inch
                
                pdf_table_orig = Table(table_data_orig, colWidths=[col_width_orig]*num_cols_orig if num_cols_orig > 0 else None)
                pdf_table_orig.setStyle(TableStyle(common_table_style_list))
                story.append(pdf_table_orig)
                story.append(Spacer(1, 0.1*inch))
                
            story.append(Paragraph(f"Todas las unidades en [{unidad_fuerza}]", style_info_header))

            # 2. Absolute Error Table
            story.append(Spacer(1, 0.2*inch))
            story.append(Paragraph(f"Tabla de Error Absoluto: {denominaciones[idx]}", style_table_title))
            table_data_abs = []
            headers_abs = []
            cols_abs_series = []

            if has_0:
                abs_err_0 = df_calibracion[dut_0_col] - df_calibracion[pat_0_col]
                headers_abs.extend([f'PAT(L0°)', f'DUT(L0°)', f'Err(L0°)'])
                cols_abs_series.extend([df_calibracion[pat_0_col], df_calibracion[dut_0_col], abs_err_0])
            if has_r:
                abs_err_r = df_calibracion[dut_r_col] - df_calibracion[pat_r_col]
                headers_abs.extend([f'PAT(U0°)', f'DUT(U0°)', f'Err(U0°)'])
                cols_abs_series.extend([df_calibracion[pat_r_col], df_calibracion[dut_r_col], abs_err_r])
            if has_120:
                abs_err_120 = df_calibracion[dut_120_col] - df_calibracion[pat_120_col]
                headers_abs.extend([f'PAT(L120°)', f'DUT(L120°)', f'Err(L120°)'])
                cols_abs_series.extend([df_calibracion[pat_120_col], df_calibracion[dut_120_col], abs_err_120])
            if has_240:
                abs_err_240 = df_calibracion[dut_240_col] - df_calibracion[pat_240_col]
                headers_abs.extend([f'PAT(L240°)', f'DUT(L240°)', f'Err(L240°)'])
                cols_abs_series.extend([df_calibracion[pat_240_col], df_calibracion[dut_240_col], abs_err_240])

            if headers_abs:
                table_data_abs.append(headers_abs)
                for i in range(len(df_calibracion)):
                    row = [format_val(s.iloc[i] if i < len(s) and not pd.isna(s.iloc[i]) else pd.NA) for s in cols_abs_series]
                    table_data_abs.append(row)

                num_cols_abs = len(headers_abs)
                col_width_abs = (6.5 * inch) / num_cols_abs if num_cols_abs > 0 else 1 * inch
                
                pdf_table_abs = Table(table_data_abs, colWidths=[col_width_abs]*num_cols_abs if num_cols_abs > 0 else None)
                pdf_table_abs.setStyle(TableStyle(common_table_style_list))
                story.append(pdf_table_abs)
                story.append(Spacer(1, 0.1*inch))
                
            story.append(Paragraph(f"Todas las unidades en [{unidad_fuerza}]", style_info_header))

            # 3. Relative Error Table
            story.append(PageBreak())
            story.append(Paragraph(f"Tabla de Error Relativo: {denominaciones[idx]}", style_table_title))
            table_data_rel = []
            headers_rel = []
            cols_rel_series = []

            if has_0:
                pat_0_series_for_rel = df_calibracion[pat_0_col].replace(0, np.nan)
                rel_err_0 = ((df_calibracion[dut_0_col] - df_calibracion[pat_0_col]) / pat_0_series_for_rel) * 100
                headers_rel.extend([f'PAT(L0°)', f'DUT(L0°)', f'Err(L0°)'])
                cols_rel_series.extend([df_calibracion[pat_0_col], df_calibracion[dut_0_col], rel_err_0])
            if has_r:
                pat_r_series_for_rel = df_calibracion[pat_r_col].replace(0, np.nan)
                rel_err_r = ((df_calibracion[dut_r_col] - df_calibracion[pat_r_col]) / pat_r_series_for_rel) * 100
                headers_rel.extend([f'PAT(U0°)', f'DUT(U0°)', f'Err(U0°)'])
                cols_rel_series.extend([df_calibracion[pat_r_col], df_calibracion[dut_r_col], rel_err_r])
            if has_120:
                pat_120_series_for_rel = df_calibracion[pat_120_col].replace(0, np.nan)
                rel_err_120 = ((df_calibracion[dut_120_col] - df_calibracion[pat_120_col]) / pat_120_series_for_rel) * 100
                headers_rel.extend([f'PAT(L120°)', f'DUT(L120°)', f'Err(L120°)'])
                cols_rel_series.extend([df_calibracion[pat_120_col], df_calibracion[dut_120_col], rel_err_120])
            if has_240:
                pat_240_series_for_rel = df_calibracion[pat_240_col].replace(0, np.nan)
                rel_err_240 = ((df_calibracion[dut_240_col] - df_calibracion[pat_240_col]) / pat_240_series_for_rel) * 100
                headers_rel.extend([f'PAT(L240°)', f'DUT(L240°)', f'Err(L240°)'])
                cols_rel_series.extend([df_calibracion[pat_240_col], df_calibracion[dut_240_col], rel_err_240])

            if headers_rel:
                table_data_rel.append(headers_rel)
                for i in range(len(df_calibracion)):
                    row_values = []
                    for k, series_obj in enumerate(cols_rel_series):
                        val = series_obj.iloc[i] if i < len(series_obj) and not pd.isna(series_obj.iloc[i]) else pd.NA
                        is_err_col = (k + 1) % 3 == 0 
                        precision = 2 if is_err_col else 4
                        row_values.append(format_val(val, precision=precision))
                    table_data_rel.append(row_values)

                num_cols_rel = len(headers_rel)
                col_width_rel = (6.5 * inch) / num_cols_rel if num_cols_rel > 0 else 1 * inch
                
                pdf_table_rel = Table(table_data_rel, colWidths=[col_width_rel]*num_cols_rel if num_cols_rel > 0 else None)
                pdf_table_rel.setStyle(TableStyle(common_table_style_list))
                story.append(pdf_table_rel)
            
            story.append(Paragraph(f"Todas las unidades en [{unidad_fuerza}], Errores en [%]", style_info_header))
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
        
        def page_template(canvas, doc):
            canvas.saveState()
            # Encabezado
            header_text = "Laboratorio de Adquisición de datos - FAdeA"
            canvas.setFont('Helvetica', 9)
            canvas.drawString(doc.leftMargin, doc.height + doc.topMargin + 0.5*inch, header_text)

            # Pie de página original
            original_footer_text = f"- Pág. {doc.page} -"
            canvas.setFont('Helvetica', 9)
            canvas.drawCentredString(doc.width/2 + doc.leftMargin, 0.75*inch, original_footer_text) # Subido un poco para dar espacio

            # Línea horizontal para separar el nuevo pie de página
            canvas.line(doc.leftMargin, 0.6*inch, doc.width + doc.leftMargin, 0.6*inch)

            # Nuevo pie de página
            current_date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            try:
                logged_user = getpass.getuser()
            except Exception:
                logged_user = "<Usuario Desconocido>" # Fallback si getuser falla
            preliminary_report_text = f"Informe Preliminar - Generado por {logged_user} - {current_date} - Laboratorio de Adquisición de Datos - FAdeA"
            canvas.setFont('Helvetica', 7) # Fuente más pequeña para el texto largo
            canvas.drawCentredString(doc.width/2 + doc.leftMargin, 0.35*inch, preliminary_report_text)
            
            canvas.restoreState()

        try:
            doc.build(story, onFirstPage=page_template, onLaterPages=page_template)
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
