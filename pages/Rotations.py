import streamlit as st
import pandas as pd # Importar pandas
import random # Importar random
import io # Añadido para la descarga de Excel
import numpy as np # AÑADIDO para generación de arrays aleatorios
from config import page_config

# Configuración de la página
page_config(title="Cell Rotations", icon="🔄")

# Función auxiliar para convertir DataFrame a Excel en memoria
def to_excel(df_to_convert):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_to_convert.to_excel(writer, index=False, sheet_name='Sheet1')
    processed_data = output.getvalue()
    return processed_data

# Título de la página
st.markdown("# Cell Rotations")

# Expander con instrucciones
with st.expander("ℹ️ Instrucciones", expanded=False):
    st.markdown("""
    Esta aplicación genera nuevas columnas en un archivo Excel basadas en rotaciones de mediciones existentes.

    **Pasos:**
    1.  **Configura los Parámetros:**
        *   **Decimales PAT:** Número de decimales para las columnas PAT (Patrón) generadas.
        *   **Decimales DUT:** Número de decimales para las columnas DUT (Dispositivo Bajo Prueba) generadas.
        *   **Semilla Aleatoria:** Un número entero para inicializar el generador de números aleatorios. Usar la misma semilla con el mismo archivo de entrada y los mismos parámetros producirá siempre el mismo resultado.
        *   **Dispersión (%):** El porcentaje máximo (en valor absoluto) que cada nueva medición puede desviarse aleatoriamente de su valor de referencia original. Por ejemplo, un 10% significa que los valores pueden variar entre -10% y +10% del valor original.

    2.  **Carga tu Archivo Excel:**
        *   El archivo debe tener columnas nombradas siguiendo el patrón `PATn_0` y `DUTn_0` (donde `n` es un identificador, por ejemplo, `PAT1_0`, `DUT1_0`, `PAT2_0`, `DUT2_0`, etc.).
        *   Por cada par `PATn_0` y `DUTn_0`, la aplicación generará cuatro nuevas columnas:
            *   `PATn_120`, `DUTn_120`: Simulan una rotación de 120 grados.
            *   `PATn_240`, `DUTn_240`: Simulan una rotación de 240 grados.
        *   Cada valor en estas nuevas columnas se calculará tomando el valor de la columna `_0` correspondiente y multiplicándolo por `(1 + delta)`, donde `delta` es un valor porcentual aleatorio. Este `delta` se genera individualmente para cada celda, con un módulo máximo definido por el parámetro "Dispersión (%)".

    3.  **Procesamiento:**
        *   La aplicación leerá el archivo, mostrará el contenido original y luego generará las nuevas columnas.
        *   Las nuevas columnas se insertarán directamente después de su par `DUTn_0` correspondiente.

    4.  **Descarga:**
        *   Podrás descargar un nuevo archivo Excel con las columnas originales y las generadas. El nombre del archivo incluirá el nombre original, la palabra `_rot_` y la semilla utilizada.
    """)

# Entradas para la cantidad de decimales y semilla en columnas
col1, col2, col3, col4 = st.columns(4)

with col1:
    pat_decimals = st.number_input("Decimales PAT:", min_value=0, value=2, step=1, key="pat_decimals")
with col2:
    dut_decimals = st.number_input("Decimales DUT:", min_value=0, value=0, step=1, key="dut_decimals")
with col3:
    # Usar un valor aleatorio como semilla inicial si no hay uno ya en el estado de la sesión
    if 'seed_value' not in st.session_state:
        st.session_state.seed_value = random.randint(0, 1000000)
    seed_value = st.number_input("Semilla Aleatoria:", min_value=0, value=st.session_state.seed_value, step=1, key="seed_value_input")
with col4: # Nueva columna para el campo de dispersión
    dispersion_percentage = st.number_input("Dispersión (%):", min_value=0.0, value=10.0, step=0.1, key="dispersion_percentage")

# File uploader para archivos Excel
uploaded_file = st.file_uploader("Selecciona un archivo Excel para generar rotaciones", type=["xlsx", "xls"])

if uploaded_file is not None:
    # Leer el archivo Excel
    try:
        df = pd.read_excel(uploaded_file)
        st.write("Contenido del archivo Excel Original:")
        st.dataframe(df)

        # Procesar columnas para generar rotaciones
        pat_cols_0 = [col for col in df.columns if col.startswith('PAT') and col.endswith('_0')]

        np.random.seed(seed_value) # AÑADIDO: Sembrar el RNG de NumPy una vez
        num_rows = len(df) # AÑADIDO: Obtener el número de filas para los arrays de deltas

        for pat_col_0 in pat_cols_0:
            try:
                # Extraer el identificador 'n' de PATn_0 (ej: '1' de 'PAT1_0', 'XYZ' de 'PATXYZ_0')
                identifier = pat_col_0[len('PAT'):-len('_0')]
                if not identifier: # Si el identificador es vacío (ej. PAT_0)
                    st.warning(f"No se pudo extraer un identificador válido de la columna {pat_col_0}.")
                    continue
            except IndexError:
                st.warning(f"No se pudo procesar la columna {pat_col_0}. No sigue el formato PATn_0 esperado.")
                continue

            dut_col_0 = f'DUT{identifier}_0'

            if dut_col_0 not in df.columns:
                st.warning(f"No se encontró la columna {dut_col_0} correspondiente a {pat_col_0}.")
                continue

            # Generar deltas aleatorios. Un delta diferente para PAT y DUT, y para 120 y 240.
            # Usar el valor de dispersión ingresado por el usuario
            max_delta = dispersion_percentage / 10000.0
            
            # MODIFICADO: Generar Series de deltas aleatorios, uno para cada fila
            deltas_pat_120 = pd.Series(np.random.uniform(-max_delta, max_delta, num_rows), index=df.index)
            deltas_dut_120 = pd.Series(np.random.uniform(-max_delta, max_delta, num_rows), index=df.index)
            deltas_pat_240 = pd.Series(np.random.uniform(-max_delta, max_delta, num_rows), index=df.index)
            deltas_dut_240 = pd.Series(np.random.uniform(-max_delta, max_delta, num_rows), index=df.index)

            # Calcular y agregar nuevas columnas para 120 grados
            pat_col_120_name = f'PAT{identifier}_120'
            dut_col_120_name = f'DUT{identifier}_120'
            
            # MODIFICADO: Aplicar Series de deltas (operación elemento a elemento)
            val_pat_120 = df[pat_col_0] * (1 + deltas_pat_120)
            val_dut_120 = df[dut_col_0] * (1 + deltas_dut_120)

            if pat_decimals == 0:
                df[pat_col_120_name] = val_pat_120.round(0).astype(int)
            else:
                df[pat_col_120_name] = val_pat_120.round(pat_decimals)
            
            if dut_decimals == 0:
                df[dut_col_120_name] = val_dut_120.round(0).astype(int)
            else:
                df[dut_col_120_name] = val_dut_120.round(dut_decimals)

            # Calcular y agregar nuevas columnas para 240 grados
            pat_col_240_name = f'PAT{identifier}_240'
            dut_col_240_name = f'DUT{identifier}_240'

            # MODIFICADO: Aplicar Series de deltas (operación elemento a elemento)
            val_pat_240 = df[pat_col_0] * (1 + deltas_pat_240)
            val_dut_240 = df[dut_col_0] * (1 + deltas_dut_240)

            if pat_decimals == 0:
                df[pat_col_240_name] = val_pat_240.round(0).astype(int)
            else:
                df[pat_col_240_name] = val_pat_240.round(pat_decimals)

            if dut_decimals == 0:
                df[dut_col_240_name] = val_dut_240.round(0).astype(int)
            else:
                df[dut_col_240_name] = val_dut_240.round(dut_decimals)

            # Reordenar columnas para insertar las nuevas después de DUTn_0
            cols = list(df.columns)
            # Encuentra el índice de DUTn_0
            dut_col_0_index = cols.index(dut_col_0)

            # Elimina las nuevas columnas de su posición actual (al final)
            new_cols_to_insert = [pat_col_120_name, dut_col_120_name, pat_col_240_name, dut_col_240_name]
            cols_set = set(cols) # Usar un set para la comprobación de pertenencia eficiente
            new_cols_to_insert_existing = [col for col in new_cols_to_insert if col in cols_set]
            
            # Eliminar solo las columnas que realmente existen en el DataFrame
            for col_to_remove in new_cols_to_insert_existing:
                cols.remove(col_to_remove)

            # Inserta las nuevas columnas después de DUTn_0
            for i, new_col in enumerate(new_cols_to_insert):
                # Asegurarse de que la columna no se inserte si ya existe en la posición correcta (poco probable aquí)
                # o simplemente reconstruir la lista de columnas en el orden deseado
                # Esta inserción asume que las columnas no están ya en `cols` en otras posiciones
                cols.insert(dut_col_0_index + 1 + i, new_col)
            
            df = df[cols]

        st.write("Contenido del archivo Excel con Rotaciones:")
        st.dataframe(df)

        # Lógica para el botón de descarga
        excel_data = to_excel(df)
        original_name_without_ext = uploaded_file.name.rsplit('.', 1)[0]
        download_file_name = f"{original_name_without_ext}_rot_{seed_value}.xlsx"

        st.download_button(
            label="Descargar Excel con rotaciones",
            data=excel_data,
            file_name=download_file_name,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        st.error(f"Error al leer o procesar el archivo Excel: {e}")

# Aquí puedes agregar más contenido o funcionalidades para esta página en el futuro.
# st.write("Página en construcción.")

