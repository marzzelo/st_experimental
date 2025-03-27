import pandas as pd
import numpy as np
from sqlalchemy import Null
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
        else:
            st.html(f'<div>Using default file: <span style="color: green; padding-left: 8px;">{default_file_name}</span></div>')
            data_file = default_file_name
            self.data_file_name = data_file
            
        raw_data = pd.read_csv(data_file, sep=None, engine='python')  
        self.data = raw_data.select_dtypes(include=[np.number])
        
        self.plot_data()
                        
        self.show_data_stats()
        
        return
          
               
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

            # Agregar checkbox para guardar el dataset filtrado
            save_data = st.checkbox("Save dataset")
            if save_data:
                saved_message = st.empty()    
                
            reset_limits = st.checkbox("Reset Limits", key="chk_reset")                                               

            submitted = st.form_submit_button("Graficar")
            if submitted:
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

                if save_data:
                    # Crear un DataFrame con las columnas seleccionadas y los datos filtrados
                    columns_to_save = [x_col] + selected_cols
                    filtered_data = data.loc[mask, columns_to_save]
                    # st.write("Dataset filtrado:", filtered_data)

                    original_name = os.path.basename(self.data_file_name )
                    output_file_name = f"data/filtered_{original_name}"
                    # save to csv
                    filtered_data.to_csv(output_file_name, index=False)
                    st.success(f"Dataset saved as '{output_file_name}'")
                    saved_message.markdown(f":violet[Data set saved as] :blue['{output_file_name}']")
                
                
                
            
   
if __name__ == "__main__":
    app = DataExplorer()
