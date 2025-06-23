from re import X
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

from config import page_config
import os



def encode_voltages(voltages: pd.Series) -> pd.Series:
    """Return a Series with voltages linearly mapped to [-32767, 32767]."""
    v_max = voltages.max()
    v_min = voltages.min()
    if v_max == v_min:
        return pd.Series(0, index=voltages.index, dtype=int)
    scale = 65534 / (v_max - v_min)
    codes = ((voltages - v_min) * scale - 32767).round().astype(int)
    return codes

def validate_format(df: pd.DataFrame) -> str | None:
    if df.shape[1] < 2 or df.empty:
        return "El archivo debe tener al menos dos columnas y una fila de datos."

    time_unit = str(df.iloc[0, 0]).strip()
    volt_unit = str(df.iloc[0, 1]).strip()

    if time_unit not in ("us", "ms", "s"):
        return "Unidad de tiempo inválida en la fila 1, columna A."
    if volt_unit not in ("uV", "mV", "V"):
        return "Unidad de voltaje inválida en la fila 1, columna B."

    data = df.iloc[1:, :2]
    try:
        data.apply(pd.to_numeric)
    except Exception:
        return "Los valores a partir de la fila 2 deben ser numéricos."
    return None


class AWScriptGenerator:
    def __init__(self):
        page_config(title="Arbitrary Waveform Script Generator", icon="📜")
        st.markdown("# Arbitrary Waveform Script Generator")
        self.layout()

    def layout(self):
        with st.expander("ℹ️ Ayuda", expanded=False):
            st.markdown(
                """
                Esta aplicación permite crear un script para la generación de ondas arbitrarias en el generador de funciones Agilent 33522A, a partir de un archivo Excel que contiene la información correspondiente a la forma de onda.
                """
            )

        with st.expander("ℹ️ Formato de datos en el archivo Excel", expanded=False):
            st.markdown(
                """
                **Fila 1**
                - Columna A: unidad de tiempo `[us, ms, s]`
                - Columna B: unidad de voltaje `[uV, mV, V]`

                **Fila 2 en adelante**
                - Columna A: tiempo de la muestra
                - Columna B: voltaje de la muestra
                """
            )

        uploaded_file = st.file_uploader(
            "Cargar archivo XLSX", type=["xlsx"], accept_multiple_files=False
        )

        if uploaded_file is not None:
            try:
                df = pd.read_excel(uploaded_file, header=None)
            except Exception as e:
                st.error(f"Error al leer el archivo: {e}")
                return

            error = validate_format(df)
            if error:
                st.error(error)
                return

            time_unit = str(df.iloc[0, 0]).strip()
            volt_unit = str(df.iloc[0, 1]).strip()

            data = df.iloc[1:, :2].astype(float)
            sample_count = len(data)

            time_factors = {"us": 1e-6, "ms": 1e-3, "s": 1.0}
            volt_factors = {"uV": 1e-6, "mV": 1e-3, "V": 1.0}

            if sample_count >= 2:
                dt = data.iloc[1, 0] - data.iloc[0, 0]
                try:
                    sample_freq = 1.0 / (dt * time_factors[time_unit])
                except ZeroDivisionError:
                    sample_freq = float("inf")
            else:
                sample_freq = None

            voltages = data.iloc[:, 1] * volt_factors[volt_unit]
            volt_df = pd.DataFrame({"Voltage (V)": voltages})
            v_max = voltages.max()
            v_min = voltages.min()

            codes = encode_voltages(voltages)
            data.iloc[:, 1] = codes
            code_df = pd.DataFrame({"Code": codes})

            st.success(
                f"Formato correcto. {sample_count} muestras detectadas."
            )
            st.markdown(f"- Unidad de tiempo: **{time_unit}**")
            st.markdown(f"- Unidad de voltaje: **{volt_unit}**")

            if sample_freq is not None:
                st.markdown(f"- Frecuencia de muestreo: **{sample_freq:.6f} Sa/s**")
            else:
                st.markdown("- Frecuencia de muestreo: N/A")
            st.markdown(f"- Voltaje máximo: **{v_max:.6f} V**")
            st.markdown(f"- Voltaje mínimo: **{v_min:.6f} V**")
            st.dataframe(volt_df.head(), use_container_width=True)
            # Gráfico de tensión vs tiempo
            st.subheader("Gráfico de tensión vs tiempo")
            fig, ax = plt.subplots()
            ax.plot(data.iloc[:, 0], voltages)
            ax.set_xlabel(f"Tiempo ({time_unit})")
            ax.set_ylabel(f"Voltaje ({volt_unit})")
            ax.grid(True)
            st.pyplot(fig)
            # Histograma de voltajes
            st.subheader("Histograma de voltajes")
            fig2, ax2 = plt.subplots()
            ax2.hist(voltages, bins=50)
            ax2.set_xlabel("Voltaje (V)")
            ax2.set_ylabel("Frecuencia")
            ax2.grid(axis='y')
            st.pyplot(fig2)
            # Controles de suavizado en dos columnas
            col1, col2, col3 = st.columns([2, 2, 5], vertical_alignment='bottom', gap='small')
            with col2:
                window = st.number_input("Tamaño de ventana", min_value=1, max_value=sample_count, value=3, step=1)
            with col1:
                suavizar = st.button("Suavizar", use_container_width=True)
            if suavizar:
                base_name = os.path.splitext(uploaded_file.name)[0]
                smoothed = voltages.rolling(window=window, center=True, min_periods=1).mean()
                codes_smoothed = encode_voltages(smoothed)
                v_max_s = smoothed.max()
                v_min_s = smoothed.min()
                script_lines_s = [
                    f'Copyright:Agilent Technologies, 2010',
                    'File Format:1.10',
                    'Channel Count:1',
                    f'Sample Rate:{sample_freq:.6f}' if sample_freq else 'Sample Rate:1',
                    f'High Level:{v_max_s:.6f}',
                    f'Low Level:{v_min_s:.6f}',
                    'Data Type:"short"',
                    f'Data Points:{sample_count}',
                    'Data:'
                ]
                script_lines_s.extend(codes_smoothed.astype(str).tolist())
                script_content_s = "\n".join(script_lines_s)
                arb_file_name_s = f"{base_name}_smooth{window}.arb"
                st.success("Script suavizado generado correctamente.")
                st.download_button(
                    label="Descargar script suavizado .arb",
                    data=script_content_s,
                    file_name=arb_file_name_s,
                    mime="text/plain"
                )
                # Gráfico comparativo entre señal original y suavizada
                st.subheader("Comparación original vs señal suavizada")
                fig3, ax3 = plt.subplots()
                ax3.plot(data.iloc[:, 0], voltages, label="Original")
                ax3.plot(data.iloc[:, 0], smoothed, label=f"Suavizada (w={window})")
                ax3.set_xlabel(f"Tiempo ({time_unit})")
                ax3.set_ylabel(f"Voltaje ({volt_unit})")
                ax3.legend()
                ax3.grid(True)
                st.pyplot(fig3)

            st.dataframe(code_df.head(), use_container_width=True)

            # Generate script .arb file
            
            # ejemplo:
            # """
            # Copyright:Agilent Technologies, 2010  
            # File Format:1.10
            # Channel Count:1
            # Sample Rate:<sample_rate>
            # High Level:<v_max>
            # Low Level:<v_min>
            # Data Type:"short"
            # Data Points:<sample_count>
            # Data:
            # <encoded sample #1>
            # <encoded sample #2>
            # <encoded sample #3>
            # ...
            # <encoded sample #(sample_count)>
            # """
            
            script_lines = [
                f'Copyright:Agilent Technologies, 2010',
                'File Format:1.10',
                'Channel Count:1',
                f'Sample Rate:{sample_freq:.6f}' if sample_freq else 'Sample Rate:1',
                f'High Level:{v_max:.6f}',
                f'Low Level:{v_min:.6f}',
                'Data Type:"short"',
                f'Data Points:{sample_count}',
                'Data:'
            ]
            script_lines.extend(codes.astype(str).tolist())
            script_content = "\n".join(script_lines)
            base_name = os.path.splitext(uploaded_file.name)[0]
            arb_file_name = f"{base_name}.arb"
            st.success("Script generado correctamente. Puedes descargarlo usando el botón de abajo.")
            st.download_button(
                label="Descargar script .arb",
                data=script_content,
                file_name=arb_file_name,
                mime="text/plain"
            )
            
            

if __name__ == "__main__":
    AWScriptGenerator()
