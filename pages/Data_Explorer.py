import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from datetime import datetime, time, date, timedelta

from config import page_config
import seaborn as sns
import os

from utils import ss_get, ss_set


NOPLOT_COLS = ["t", "ts", "n", "time", "timespan", "tspan", "sample#", "sample"]


def format_seconds_hmsms(seconds: float) -> str:
    td = pd.to_timedelta(seconds, unit="s")
    total_seconds = td.total_seconds()
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    sec = total_seconds % 60
    return f"{hours:02d}:{minutes:02d}:{sec:06.3f}"

class DataExplorer:
    def __init__(self):
        page_config(title="Data Explorer", icon="📊", layout='wide')
        print("\n\n\nStarting...")
        self.layout()
        
    
    def layout(self):
        st.html('<h2>Explorador de Datos</h2>')
        # default_file_name = r'data\sample_data.csv'
                
        # load a csv file from disk and display a plot of its data
        uploaded_file = st.file_uploader(
            "Choose a CSV or Excel file",
            type=["csv", "txt", "xlsx", "xls"],
        )

        if uploaded_file is not None:
            data_file = uploaded_file
            self.data_file_name = data_file.name
            extension = os.path.splitext(self.data_file_name)[1].lower()
            if extension in [".xlsx", ".xls"]:
                raw_data = pd.read_excel(data_file)
            else:
                raw_data = pd.read_csv(data_file, sep=None, engine="python")
            self.data = raw_data.select_dtypes(include=[np.number])
            self.plot_data()
            self.show_data_stats()
          
               
    def show_data_stats(self):       
        st.subheader("Data Statistics", divider=True)
        st.html(f'<span style="color: green; padding-left: 8px;">{self.data.shape[0]} rows, {self.data.shape[1]} columns</span>')
        st.write(self.data.head(50))
        # Display the summary statistics
        st.subheader("Summary Statistics:", divider=True)
        st.write(self.data.describe())
        
        # Display the correlation matrix as a heatmap
        st.subheader("Correlation Matrix Heatmap", divider='rainbow')
        cols = st.columns([1,2,1])
        with cols[1]:
            # Eliminar columnas constantes
            data = self.data.loc[:, self.data.nunique() > 1]
            data = data.loc[:, ~data.columns.str.lower().isin(NOPLOT_COLS)]
            corr = data.corr()
            fig, ax = plt.subplots()
            sns.heatmap(corr, annot=True, cmap='coolwarm', ax=ax, fmt="0.3f", annot_kws={"size": 5})
            ax.set_title("Correlation Matrix Heatmap")
            st.pyplot(fig)
        
        
        # Display the histogram of each column
        st.subheader("Histograms", divider="violet")
        bins = st.number_input(
            "Cantidad de bins",
            min_value=1,
            value=st.session_state.get("hist_bins", 30),
            step=1,
            key="hist_bins_input",
        )
        st.session_state["hist_bins"] = bins
        cols = st.columns(3)
        for i, col_name in enumerate(self.data.columns):
            if col_name.lower() in NOPLOT_COLS:
                continue
            # Filtrar valores NaN y verificar si la columna tiene datos válidos
            column_data = self.data[col_name].dropna()
            if column_data.empty:
                st.warning(f"La columna '{col_name}' no tiene datos válidos para graficar.")
                continue
            with cols[i % 3]:
                fig, ax = plt.subplots()
                ax.hist(self.data[col_name], bins=int(bins), alpha=0.7)
                ax.set_title(f"Histogram of {col_name}")
                ax.set_xlabel(col_name)
                ax.set_ylabel("Frequency")
                st.pyplot(fig)
        
        
    def plot_data(self):

        # data, x_col, NOPLOT_COLS, etc. deben definirse antes de usarse fuera del formulario
        data = self.data
        x_col = data.columns[0]
        
        # --- SECCIÓN DE LÍMITES X/Y Y SELECCIÓN DE COLUMNAS A GRAFICAR (FUERA DEL FORMULARIO PRINCIPAL) ---
        st.subheader('Configuración de Visualización', divider=True)

        if "chk_reset" in st.session_state and st.session_state["chk_reset"]:
            for key in ['x_lower', 'x_upper', 'y_lower', 'y_upper']:
                st.session_state.pop(key, None)
            st.session_state["chk_reset"] = False
            # Forzar la recarga de la página para aplicar el reseteo inmediatamente
            # st.experimental_rerun() # Comentado para evitar bucles si no se maneja con cuidado

        st.write(f"Usando la columna '{x_col}' como eje X")
        x_col = st.selectbox(
            "Selecciona la columna para el eje X:",
            options=data.columns,
            index=0,
            key="x_col_select"
        )
        
        x_lower_val = ss_get('x_lower', float(data[x_col].min()))
        x_upper_val = ss_get('x_upper', float(data[x_col].max()))
        
        others_for_y_calc = [col for col in data.columns if col != x_col and col.lower() not in NOPLOT_COLS and np.issubdtype(data[col].dtype, np.number)]
        if others_for_y_calc:
            y_vals = pd.concat([data[col].dropna() for col in others_for_y_calc if not data[col].dropna().empty])
            if not y_vals.empty:
                y_lower_val = ss_get('y_lower', float(y_vals.min()))
                y_upper_val = ss_get('y_upper', float(y_vals.max()))
            else: # Fallback si todas las columnas 'others' están vacías después de dropna
                y_lower_val = ss_get('y_lower', 0.0)
                y_upper_val = ss_get('y_upper', 1.0)
        else: # Fallback si no hay columnas 'others'
            y_lower_val = ss_get('y_lower', 0.0)
            y_upper_val = ss_get('y_upper', 1.0)

        col1, col2, col3, col4 = st.columns(4)
        x_lower = col1.number_input(":green[Límite inferior eje X]", value=x_lower_val, key="x_lower_input")
        x_upper = col2.number_input(":green[Límite superior eje X]", value=x_upper_val, key="x_upper_input")
        y_lower = col3.number_input(":red[Límite inferior eje Y]", value=y_lower_val, key="y_lower_input")
        y_upper = col4.number_input(":red[Límite superior eje Y]", value=y_upper_val, key="y_upper_input")
        
        # Actualizar session_state cuando cambian los number_input
        ss_set('x_lower', x_lower)
        ss_set('x_upper', x_upper)
        ss_set('y_lower', y_lower)
        ss_set('y_upper', y_upper)

        st.markdown("### Selecciona las columnas a graficar:")
        if 'all_plot_selected_state' not in st.session_state:
            st.session_state.all_plot_selected_state = True 

        # rótulo para el botton "Check/Uncheck All"
        toggle_button_label = "Uncheck All" if st.session_state.all_plot_selected_state else "Check All"
        
        if st.button(toggle_button_label, key="toggle_all_plot_checkboxes_button"):
            st.session_state.all_plot_selected_state = not st.session_state.all_plot_selected_state
            current_master_checkbox_state = st.session_state.all_plot_selected_state
            for col_to_toggle in data.columns: 
                if col_to_toggle == x_col or col_to_toggle.lower() in NOPLOT_COLS:
                    continue
                st.session_state[f"plot_cb_{col_to_toggle}"] = current_master_checkbox_state
        
        # Checkboxes de columnas
        selected_cols = []
        checkbox_cols_layout = st.columns(6)
        i = 0
        for col_loop_var in data.columns:
            if col_loop_var == x_col or col_loop_var.lower() in NOPLOT_COLS:
                continue
            
            is_checked = checkbox_cols_layout[i % 6].checkbox(
                f"{col_loop_var}", 
                value=st.session_state.get(f"plot_cb_{col_loop_var}", True), 
                key=f"plot_cb_{col_loop_var}"
            )
            if is_checked:
                selected_cols.append(col_loop_var)
            i += 1

        with st.form("data_processing_form"): # Clave de formulario única
            st.subheader('Procesamiento y Filtrado de Datos', divider=True)
            
            # Sección para seleccionar columnas a filtrar
            st.markdown("### Selecciona las columnas a Filtrar (para Media Móvil):")
            selected_cols_for_filter = []
            cols_filter_selection = st.columns(6)
            i_filter = 0
            for col_name in data.columns:
                if col_name == x_col or col_name.lower() in NOPLOT_COLS or not np.issubdtype(data[col_name].dtype, np.number):
                    continue
                # Usar una clave única para estos checkboxes de filtro
                if cols_filter_selection[i_filter % 6].checkbox(f"Filtrar {col_name}", value=st.session_state.get(f"filter_cb_{col_name}", False), key=f"filter_cb_{col_name}"):
                    selected_cols_for_filter.append(col_name)
                i_filter += 1
                
            st.markdown("---")

            col_chk1, col_chk2, col_chk3 = st.columns(3)
            with col_chk1:
                st.checkbox("Resetear Límites al Graficar/Filtrar", key="chk_reset")
            with col_chk2:
                save_data = st.checkbox("Guardar dataset con columnas y límites seleccionados (al Graficar)", key="chk_save")
            with col_chk3:
                st.checkbox("Iniciar muestras en 0", key="chk_start_zero")

            col_convert, col_unit = st.columns(2)
            convert_x_time = col_convert.checkbox(
                "Convertir columna X a hh:mm:ss.mmm",
                key="chk_convert_x_time",
            )
            sample_period_us = col_unit.number_input(
                "Periodo de muestreo (μs)",
                min_value=1.0,
                value=st.session_state.get("sampling_period_us", 1_000.0),
                step=1.0,
                key="sampling_period_us_input",
            )
            st.session_state["sampling_period_us"] = sample_period_us

            col_date, col_time = st.columns(2)
            offset_date = col_date.date_input(
                "Fecha inicial eje X",
                value=st.session_state.get("offset_date", datetime.today().date()),
                key="offset_date",
            )
            offset_time = col_time.time_input(
                "Hora inicial eje X",
                value=st.session_state.get("offset_time", time(0, 0)),
                key="offset_time",
            )
            offset_seconds = (
                offset_time.hour * 3600
                + offset_time.minute * 60
                + offset_time.second
                + offset_time.microsecond / 1e6
            )
            # ESCALADO
            col_scale_time, col_scale_rest, col_dec = st.columns(3)
            scale_time = col_scale_time.number_input(
                "Factor de escala tiempo", value=1.0, step=0.01, key="scale_time"
            )
            scale_rest = col_scale_rest.number_input(
                "Factor de escala columnas", value=1.0, step=0.01, key="scale_rest"
            )
            decimals = col_dec.number_input(
                "Número de decimales", min_value=0, value=2, step=1, key="decimals"
            )

            col_buttons = st.columns([3,1,2,7], vertical_alignment="bottom")
            submitted_plot = col_buttons[0].form_submit_button("Graficar")
            submitted_filter = col_buttons[1].form_submit_button("Filtrar")
            window_size = col_buttons[2].number_input("Ventana Media Móvil", min_value=3, value=st.session_state.get('window_size', 21), step=1, key='window_size_input')
            st.session_state.window_size = window_size # Guardar en session state para persistencia

            if submitted_plot:
                start_zero = st.session_state.get('chk_start_zero', False)
                # Filtrar los datos basados en los límites del eje X ingresados por el usuario
                user_mask = (data[x_col] >= x_lower) & (data[x_col] <= x_upper)
                fig, ax = plt.subplots(figsize=(20, 10))

                all_plot_x_data = []
                all_plot_y_data = []
                any_data_plotted_for_limits = False

                for col in selected_cols:
                    y_series_masked = data.loc[user_mask, col]
                    x_series_masked = data.loc[user_mask, x_col]
                    if convert_x_time:
                        indices = data.loc[user_mask].index
                        period_s = sample_period_us / 1e6
                        x_series_masked = indices * period_s + offset_seconds
                    # aplicar escalado
                    x_series_masked = x_series_masked * scale_time
                    y_series_masked = y_series_masked * scale_rest

                    temp_df_plot = pd.DataFrame({
                        'x': x_series_masked,
                        'y': y_series_masked
                    }).dropna(subset=['y'])
                    if start_zero:
                        temp_df_plot['x'] = temp_df_plot['x'] - temp_df_plot['x'].min()

                    if not temp_df_plot.empty:
                        ax.plot(temp_df_plot['x'], temp_df_plot['y'], label=col)
                        all_plot_x_data.append(temp_df_plot['x'])
                        all_plot_y_data.append(temp_df_plot['y'])
                        any_data_plotted_for_limits = True
                    else:
                        st.warning(f"La columna '{col}' no tiene datos válidos para graficar después de aplicar la máscara y dropna.")
                
                # Usar los límites de entrada como predeterminados para el gráfico
                plot_x_min, plot_x_max = x_lower, x_upper
                plot_y_min, plot_y_max = y_lower, y_upper

                if any_data_plotted_for_limits:
                    combined_x_data = pd.concat(all_plot_x_data)
                    combined_y_data = pd.concat(all_plot_y_data)
                    if not combined_x_data.empty:
                        plot_x_min = combined_x_data.min()
                        plot_x_max = combined_x_data.max()
                    if not combined_y_data.empty:
                        plot_y_min = combined_y_data.min()
                        plot_y_max = combined_y_data.max()
                
                if convert_x_time:
                    ax.set_xlabel(f"{x_col} (hh:mm:ss.mmm)")
                    ax.xaxis.set_major_formatter(
                        FuncFormatter(lambda v, _: format_seconds_hmsms(v))
                    )
                else:
                    ax.set_xlabel(x_col)
                ax.set_ylabel('Value')
                ax.set_title("Data Plot")
                ax.set_xlim(plot_x_min, plot_x_max)
                ax.set_ylim(plot_y_min, plot_y_max)
                ax.grid()
                if selected_cols and any_data_plotted_for_limits:
                    ax.legend()
                st.pyplot(fig)

                # Preparar descarga
                if save_data:
                    columns_to_save = [x_col] + selected_cols
                    selected_data_to_save = data.loc[user_mask, columns_to_save].copy()
                    if st.session_state.get('chk_start_zero', False):
                        selected_data_to_save[x_col] = selected_data_to_save[x_col] - selected_data_to_save[x_col].min()
                    # aplicar escalado a CSV seleccionado
                    selected_data_to_save[x_col] = selected_data_to_save[x_col] * st.session_state.get('scale_time', 1.0)
                    for c in selected_cols:
                        selected_data_to_save[c] = selected_data_to_save[c] * st.session_state.get('scale_rest', 1.0)
                    # redondear según decimales
                    dec = st.session_state.get('decimals', 2)
                    selected_data_to_save = selected_data_to_save.round(dec)
                    csv = selected_data_to_save.to_csv(index=False).encode('utf-8')
                    original_name = os.path.basename(self.data_file_name)
                    output_file_name = f"selected_{original_name}"
                    st.session_state['selected_data_df'] = selected_data_to_save
                    st.session_state['selected_data_name'] = output_file_name
                    st.success(f"Dataset seleccionado listo para descargar.")

                if st.session_state.get("chk_reset", False):
                    ss_set('x_lower', plot_x_min)
                    ss_set('x_upper', plot_x_max)
                    ss_set('y_lower', plot_y_min)
                    ss_set('y_upper', plot_y_max)
                    st.session_state.chk_reset = False 
                    st.experimental_rerun()

            if submitted_filter:
                start_zero = st.session_state.get('chk_start_zero', False)
                st.write("Aplicando filtro de media móvil (ventana {})...".format(window_size))
                cols_to_filter = selected_cols_for_filter

                if not cols_to_filter:
                    st.warning("No hay columnas numéricas para aplicar el filtro.")
                else:
                    filtered_df = self.data.copy()
                    for col in cols_to_filter:
                        filtered_df[f"{col}_f"] = filtered_df[col].rolling(window=window_size, center=True).mean()

                    df_for_download = pd.DataFrame()
                    if x_col in data.columns:
                        df_for_download[x_col] = data[x_col].copy()
                    for col_to_plot_original_name in selected_cols:
                        if col_to_plot_original_name in cols_to_filter:
                            filtered_col_name_for_download = f"{col_to_plot_original_name}_f"
                            if filtered_col_name_for_download in filtered_df.columns:
                                df_for_download[filtered_col_name_for_download] = filtered_df[filtered_col_name_for_download].copy()
                        else:
                            if col_to_plot_original_name in data.columns:
                                df_for_download[col_to_plot_original_name] = data[col_to_plot_original_name].copy()
                    
                    st.session_state['filtered_data_df'] = df_for_download
                    st.session_state['filtered_data_name'] = f"plotted_data_{os.path.basename(self.data_file_name)}"
                    st.success("Filtro de media móvil aplicado.")
                    st.info("El botón de descarga aparecerá debajo del formulario.")

                    st.write("Graficando datos...")
                    fig, ax = plt.subplots(figsize=(20, 10))
                    any_data_plotted_for_limits = False
                    all_plot_x_data_filter = []
                    all_plot_y_data_filter = []

                    for col_to_plot_original_name in selected_cols:
                        if col_to_plot_original_name in cols_to_filter:
                            col_y_axis_name = f"{col_to_plot_original_name}_f"
                            source_df_for_plot = filtered_df
                            plot_series_label = f"{col_to_plot_original_name} (filtrado)"
                        else:
                            col_y_axis_name = col_to_plot_original_name
                            source_df_for_plot = data
                            plot_series_label = f"{col_to_plot_original_name}"

                        if x_col not in source_df_for_plot.columns:
                            st.warning(f"Columna X '{x_col}' no encontrada para '{plot_series_label}'.")
                            continue
                        if col_y_axis_name not in source_df_for_plot.columns:
                            st.warning(f"Columna Y '{col_y_axis_name}' no encontrada para '{plot_series_label}'.")
                            continue
                            
                        # Aplicar límites del eje X definidos por el usuario para la selección de datos
                        current_series_data_bounded = source_df_for_plot[
                            (source_df_for_plot[x_col] >= x_lower) & (source_df_for_plot[x_col] <= x_upper)
                        ][[x_col, col_y_axis_name]].copy()

                        current_series_data_bounded.dropna(subset=[col_y_axis_name], inplace=True)
                        if convert_x_time:
                            period_s = sample_period_us / 1e6
                            current_series_data_bounded[x_col] = (
                                current_series_data_bounded.index * period_s + offset_seconds
                            )

                        if current_series_data_bounded.empty:
                            st.warning(f"La serie '{plot_series_label}' no tiene datos válidos en el rango X después de NaNs.")
                            continue
                        
                        ax.plot(current_series_data_bounded[x_col], current_series_data_bounded[col_y_axis_name], label=plot_series_label)
                        all_plot_x_data_filter.append(current_series_data_bounded[x_col])
                        all_plot_y_data_filter.append(current_series_data_bounded[col_y_axis_name])
                        any_data_plotted_for_limits = True
                    
                    plot_x_min_f, plot_x_max_f = x_lower, x_upper
                    plot_y_min_f, plot_y_max_f = y_lower, y_upper

                    if any_data_plotted_for_limits:
                        combined_x_data_f = pd.concat(all_plot_x_data_filter)
                        combined_y_data_f = pd.concat(all_plot_y_data_filter)
                        if not combined_x_data_f.empty:
                            plot_x_min_f = combined_x_data_f.min()
                            plot_x_max_f = combined_x_data_f.max()
                        if not combined_y_data_f.empty:
                            plot_y_min_f = combined_y_data_f.min()
                            plot_y_max_f = combined_y_data_f.max()
                    
                    if convert_x_time:
                        ax.set_xlabel(f"{x_col} (hh:mm:ss.mmm)")
                        ax.xaxis.set_major_formatter(
                            FuncFormatter(lambda v, _: format_seconds_hmsms(v))
                        )
                    else:
                        ax.set_xlabel(x_col)
                    ax.set_ylabel('Value')
                    ax.set_title("Gráfico de Datos (con columnas filtradas y originales)")
                    ax.set_xlim(plot_x_min_f, plot_x_max_f)
                    ax.set_ylim(plot_y_min_f, plot_y_max_f)
                    ax.grid()
                    if any_data_plotted_for_limits:
                        ax.legend()
                    st.pyplot(fig)

                    if st.session_state.get("chk_reset", False):
                        ss_set('x_lower', plot_x_min_f)
                        ss_set('x_upper', plot_x_max_f)
                        ss_set('y_lower', plot_y_min_f)
                        ss_set('y_upper', plot_y_max_f)
                        st.session_state.chk_reset = False
                        st.experimental_rerun()

        # Check session state outside the form to display the download button
        if 'filtered_data_df' in st.session_state:
            filtered_df_to_download = st.session_state['filtered_data_df']
            # aplicar desplazamiento y escalado a datos filtrados
            df_fd = filtered_df_to_download.copy()
            if st.session_state.get('chk_start_zero', False):
                x0 = df_fd.columns[0]
                df_fd[x0] = df_fd[x0] - df_fd[x0].min()
            df_fd[df_fd.columns[0]] = df_fd[df_fd.columns[0]] * st.session_state.get('scale_time', 1.0)
            for c in df_fd.columns[1:]:
                df_fd[c] = df_fd[c] * st.session_state.get('scale_rest', 1.0)
            # redondear según decimales
            dec = st.session_state.get('decimals', 2)
            df_fd = df_fd.round(dec)
            csv = df_fd.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Descargar datos filtrados como CSV",
                data=csv,
                file_name=download_name,
                mime='text/csv'
            )
            # Remove 'filtered_data_df' from session state after download
            del st.session_state['filtered_data_df']
        
        if 'selected_data_df' in st.session_state:
            selected_df_to_download = st.session_state['selected_data_df']
            download_name = st.session_state['selected_data_name']
            # Aplicar desplazamiento a cero si corresponde
            df_to_download = selected_df_to_download.copy()
            if st.session_state.get('chk_start_zero', False):
                x_col_dl = df_to_download.columns[0]
                df_to_download[x_col_dl] = df_to_download[x_col_dl] - df_to_download[x_col_dl].min()
            # redondear según decimales
            dec = st.session_state.get('decimals', 2)
            df_to_download = df_to_download.round(dec)
            csv = df_to_download.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Descargar datos seleccionados como CSV",
                data=csv,
                file_name=download_name,
                mime='text/csv'
            )
                
                
                   
if __name__ == "__main__":
    app = DataExplorer()
