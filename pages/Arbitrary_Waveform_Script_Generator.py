import pandas as pd
import streamlit as st

from config import page_config


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
        with st.expander("ℹ️ Formato de archivo", expanded=False):
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

            st.success(
                f"Formato correcto. {sample_count} muestras detectadas."
            )
            st.markdown(f"- Unidad de tiempo: **{time_unit}**")
            st.markdown(f"- Unidad de voltaje: **{volt_unit}**")
            if sample_freq is not None:
                st.markdown(f"- Frecuencia de muestreo: **{sample_freq:.3f} Sa/s**")
            else:
                st.markdown("- Frecuencia de muestreo: N/A")
            st.markdown(f"- Voltaje máximo: **{v_max:.3f} V**")
            st.markdown(f"- Voltaje mínimo: **{v_min:.3f} V**")
            st.dataframe(volt_df.head(), use_container_width=True)


if __name__ == "__main__":
    AWScriptGenerator()
