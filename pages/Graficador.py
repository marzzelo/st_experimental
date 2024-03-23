import pandas as pd
import streamlit as st


class Graficador:
    def __init__(self):
        self.run_app()

    def run_app(self):
        st.set_page_config(
            layout="centered",
            page_title="Graficador de Datos - Experimental PlayStore",
            page_icon="📈"
        )
        self.setup()
        self.main()

    @staticmethod
    def setup():
        st.markdown("""
        <style>
        .st-emotion-cache-zq5wmm.ezrtsby0 {
            display: none;
            }
        </style>
        """, unsafe_allow_html=True)

    @staticmethod
    def main():
        st.markdown('<h4 style="color:red">Graficador de Datos</h4>', unsafe_allow_html=True)
        file_names = []
        files = st.file_uploader("Subir Archivos de Excel", type=["xlsx", "xls", "csv"], accept_multiple_files=True)
        if files:
            for file in files:
                file_names.append(file.name)

            selected_files = st.multiselect("Seleccionar archivos para visualizar", options=file_names)
            if selected_files:
                for file in files:
                    if file.name in selected_files:
                        if file.name.endswith(".csv"):
                            df = pd.read_csv(file, sep="\t")
                        else:
                            df = pd.read_excel(file)
                        st.markdown(f"### {file.name}")
                        st.write(df)
                        st.markdown(f"### Estadísticas Descriptivas para {file.name}")
                        st.write(df.describe())

                        headers = df.columns
                        option = st.radio("Seleccione variable a graficar vs #muestra", headers.insert(0, "None"))
                        if option != "None":
                            st.line_chart(df[option])


if __name__ == "__main__":
    Graficador()
