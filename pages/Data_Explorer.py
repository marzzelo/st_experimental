import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt

from config import page_config
import seaborn as sns
import os

from utils import ss_get, ss_set


NOPLOT_COLS = ["t", "ts", "n", "time", "timespan", "tspan", "sample#", "sample"]

class DataExplorer:
    def __init__(self):
        page_config(title="Data Explorer", icon="📊", layout='wide')
        print("\n\n\n=================================================================================================")
        self.layout()
        
    
    def layout(self):
        st.html('<h2>Explorador de Datos</h2>')
        default_file_name = r'data\sample_data.csv'
                
        # load a csv file from disk and display a plot of its data
        uploaded_file = st.file_uploader("Choose a CSV file", type=["csv", "txt"])
        
        if uploaded_file is not None:               
            data_file = uploaded_file
            self.data_file_name = data_file.name
            raw_data = pd.read_csv(data_file, sep=None, engine='python')  
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
            sns.heatmap(corr, annot=True, cmap='coolwarm', ax=ax, fmt="0.3f")
            ax.set_title("Correlation Matrix Heatmap")
            st.pyplot(fig)
        
        
        # Display the histogram of each column
        st.subheader("Histograms", divider="violet")
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
                ax.hist(self.data[col_name], bins=20, alpha=0.7)
                ax.set_title(f"Histogram of {col_name}")
                ax.set_xlabel(col_name)
                ax.set_ylabel("Frequency")
                st.pyplot(fig)
        
        
    def plot_data(self):

        with st.form("data_plot_form"):
            st.subheader('Data Plotting', divider=True)
            
            if "chk_reset" in st.session_state:
                if st.session_state["chk_reset"]:
                    for key in ['x_lower', 'x_upper', 'y_lower', 'y_upper']:
                        st.session_state.pop(key, None)
                    st.session_state["chk_reset"] = False
                    
            print(f"session state: {st.session_state}")
            
            data = self.data
            x_col = data.columns[0]
            st.write(f"Usando la columna '{x_col}' como eje X")
            
            x_lower_val = ss_get('x_lower', float(data[x_col].min()))
            x_upper_val = ss_get('x_upper', float(data[x_col].max()))
            
            others = [col for col in data.columns if col != x_col and col.lower() not in NOPLOT_COLS]
            y_vals = pd.concat([data[col].dropna() for col in others])
            y_lower_val = ss_get('y_lower', float(y_vals.min()))
            y_upper_val = ss_get('y_upper', float(y_vals.max()))  
            
            print(f"session state after get: {st.session_state}")
            print('x_lower_val:', x_lower_val)
            
            
            # Permitir al usuario seleccionar los límites para el eje X
            col1, col2, col3, col4 = st.columns(4)
            x_lower = col1.number_input(":green[Límite inferior eje X]", value=x_lower_val)
            x_upper = col2.number_input(":green[Límite superior eje X]", value=x_upper_val)

            # Calcular valores por defecto para el eje Y a partir de las columnas numéricas a graficar
            others = [col for col in data.columns if col != x_col and col.lower() not in NOPLOT_COLS]
            if others:
                y_vals = pd.concat([data[col].dropna() for col in others])
                y_lower_default = y_lower_val
                y_upper_default = y_upper_val
            else:
                y_lower_default = 0.0
                y_upper_default = 1.0

            # Permitir al usuario seleccionar los límites para el eje Y
            y_lower = col3.number_input(":red[Límite inferior eje Y]", value=y_lower_default)
            y_upper = col4.number_input(":red[Límite superior eje Y]", value=y_upper_default)

            # Agregar checkboxes para que el usuario seleccione las columnas a graficar
            selected_cols = []
            st.markdown("### Selecciona las columnas a graficar:")
            cols = st.columns(6)
            i = 0
            for col in data.columns:
                if col == x_col or col.lower() in NOPLOT_COLS:
                    continue
                if cols[i % 6].checkbox(f"{col}", value=True):
                    selected_cols.append(col)
                i += 1

            # Sección para seleccionar columnas a filtrar
            st.markdown("### Selecciona las columnas a Filtrar:")
            selected_cols_for_filter = []
            cols_filter_selection = st.columns(6)
            i_filter = 0
            for col_name in data.columns:
                if col_name == x_col or col_name.lower() in NOPLOT_COLS or not np.issubdtype(data[col_name].dtype, np.number):
                    continue
                if cols_filter_selection[i_filter % 6].checkbox(f"Filtrar {col_name}", value=False, key=f"filter_{col_name}"):
                    selected_cols_for_filter.append(col_name)
                i_filter += 1
                
            # horizontal line to separate sections
            st.markdown("---")

            # Agregar checkbox para resetear los límites
            st.checkbox("Reset Limits", key="chk_reset")
            # Agregar checkbox para guardar el dataset filtrado 
            save_data = st.checkbox("Save with selected cols and limits")

            # Use columns for buttons
            col_buttons = st.columns([3,1,2,7], vertical_alignment="bottom")
            submitted_plot = col_buttons[0].form_submit_button("Graficar")
            submitted_filter = col_buttons[1].form_submit_button("Filtrar")
            # Add input for rolling mean window size
            window_size = col_buttons[2].number_input("Media Movil Window", min_value=3, value=21, step=1)

            if submitted_plot:
                # Filtrar los datos basados en los límites del eje X ingresados
                mask = (data[x_col] >= x_lower) & (data[x_col] <= x_upper)
                fig, ax = plt.subplots(figsize=(20, 10))
                for col in selected_cols:
                    column_data = data[col].dropna()
                    if column_data.empty:
                        st.warning(f"La columna '{col}' no tiene datos válidos para graficar.")
                        continue
                    ax.plot(data.loc[mask, x_col], data.loc[mask, col], label=col)
                ax.set_xlabel(x_col)
                ax.set_ylabel('Value')
                ax.set_title("Data Plot")
                ax.set_xlim(x_lower, x_upper)
                ax.set_ylim(y_lower, y_upper)
                ax.grid()
                if selected_cols:
                    ax.legend()
                st.pyplot(fig)

                # Check the state of the checkbox outside the form
                if save_data:
                    # Crear un DataFrame con las columnas seleccionadas y los datos filtrados
                    columns_to_save = [x_col] + selected_cols
                    selected_data = data.loc[mask, columns_to_save]
                    # Convertir el DataFrame a CSV en memoria
                    csv = selected_data.to_csv(index=False).encode('utf-8')
                    original_name = os.path.basename(self.data_file_name)
                    output_file_name = f"selected_{original_name}"
                    # Store selected data in session state
                    st.session_state['selected_data_df'] = selected_data
                    st.session_state['selected_data_name'] = output_file_name
                    st.success(f"Dataset seleccionado listo para descargar.")

            if submitted_filter:
                st.write("Aplicando filtro de media móvil (ventana {})...".format(window_size))
                # Identify columns to filter based on user selection
                cols_to_filter = selected_cols_for_filter

                if not cols_to_filter:
                    st.warning("No hay columnas numéricas para aplicar el filtro.")
                else:
                    # Apply rolling mean
                    filtered_df = self.data.copy()
                    for col in cols_to_filter:
                        filtered_df[f"{col}_f"] = filtered_df[col].rolling(window=window_size, center=True).mean()

                    # Prepare the data for download to match the plot
                    df_for_download = pd.DataFrame()
                    if x_col in data.columns: # 'data' is self.data in this scope
                        df_for_download[x_col] = data[x_col].copy()

                    for col_to_plot_original_name in selected_cols: # Iterate through columns selected for plotting
                        if col_to_plot_original_name in cols_to_filter:
                            # This column was filtered, use its filtered version for download
                            filtered_col_name_for_download = f"{col_to_plot_original_name}_f"
                            if filtered_col_name_for_download in filtered_df.columns:
                                df_for_download[filtered_col_name_for_download] = filtered_df[filtered_col_name_for_download].copy()
                        else:
                            # This column was plotted but not filtered, use its original version for download
                            if col_to_plot_original_name in data.columns:
                                df_for_download[col_to_plot_original_name] = data[col_to_plot_original_name].copy()
                    
                    # Store this comprehensive DataFrame in session state for download
                    st.session_state['filtered_data_df'] = df_for_download
                    # Update the name to reflect that it contains plotted data (original and/or filtered)
                    st.session_state['filtered_data_name'] = f"plotted_data_{os.path.basename(self.data_file_name)}"

                    # st.write("Datos filtrados con media móvil (ventana {}):".format(window_size))
                    # st.write(df_for_download.head(50)) # If you want to display the head of the download-ready data

                    st.success("Filtro de media móvil aplicado.")
                    st.info("El botón de descarga aparecerá debajo del formulario.")

                    # Graficar los datos (combinando originales y filtrados según selección)
                    st.write("Graficando datos...")
                    fig, ax = plt.subplots(figsize=(20, 10))
                    any_data_plotted = False

                    # Iterar sobre las columnas seleccionadas para graficar en general (selected_cols)
                    for col_to_plot_original_name in selected_cols:
                        
                        # Determinar si esta columna fue también seleccionada para filtrar
                        if col_to_plot_original_name in cols_to_filter:
                            # Sí fue filtrada: usar la versión filtrada (_f) desde filtered_df
                            col_y_axis_name = f"{col_to_plot_original_name}_f"
                            source_df_for_plot = filtered_df
                            plot_series_label = f"{col_to_plot_original_name} (filtrado)"
                        else:
                            # No fue filtrada: usar la versión original desde 'data' (self.data)
                            col_y_axis_name = col_to_plot_original_name
                            source_df_for_plot = data # 'data' es self.data en este scope
                            plot_series_label = f"{col_to_plot_original_name}"

                        # Asegurarse que las columnas x_col y col_y_axis_name existen en el source_df_for_plot
                        if x_col not in source_df_for_plot.columns:
                            st.warning(f"Columna X '{x_col}' no encontrada en el DataFrame de origen para '{plot_series_label}'.")
                            continue
                        if col_y_axis_name not in source_df_for_plot.columns:
                            st.warning(f"Columna Y '{col_y_axis_name}' no encontrada en el DataFrame de origen para '{plot_series_label}'.")
                            continue
                            
                        # Aplicar límites del eje X al DataFrame de origen correspondiente
                        # y seleccionar solo las columnas x_col y col_y_axis_name
                        current_series_data_bounded = source_df_for_plot[
                            (source_df_for_plot[x_col] >= x_lower) & (source_df_for_plot[x_col] <= x_upper)
                        ][[x_col, col_y_axis_name]].copy()
                        
                        # Eliminar NaNs de la columna Y para esta serie, ajustando X correspondientemente
                        current_series_data_bounded.dropna(subset=[col_y_axis_name], inplace=True)
                        
                        if current_series_data_bounded.empty:
                            st.warning(f"La serie '{plot_series_label}' no tiene datos válidos en el rango X seleccionado después de eliminar NaNs.")
                            continue
                        
                        ax.plot(current_series_data_bounded[x_col], current_series_data_bounded[col_y_axis_name], label=plot_series_label)
                        any_data_plotted = True
                    
                    ax.set_xlabel(x_col)
                    ax.set_ylabel('Value') # Y-label es genérico
                    ax.set_title("Gráfico de Datos (con columnas filtradas y originales)") # Título actualizado
                    ax.set_xlim(x_lower, x_upper)
                    ax.set_ylim(y_lower, y_upper)
                    ax.grid()
                    if any_data_plotted:
                        ax.legend()
                    st.pyplot(fig)

        # Check session state outside the form to display the download button
        if 'filtered_data_df' in st.session_state:
            filtered_df_to_download = st.session_state['filtered_data_df']
            download_name = st.session_state['filtered_data_name']
            csv = filtered_df_to_download.to_csv(index=False).encode('utf-8')
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
            csv = selected_df_to_download.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Descargar dataset seleccionado como CSV",
                data=csv,
                file_name=download_name,
                mime='text/csv'
            )
            # Remove 'selected_data_df' from session state after download
            del st.session_state['selected_data_df']
                
            
   
if __name__ == "__main__":
    app = DataExplorer()
