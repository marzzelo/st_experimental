import pandas as pd
import streamlit as st


class InstrumentsApp:
    def __init__(self):
        self.answer = ""
        self.run_app()

    def run_app(self):
        st.set_page_config(
            layout="centered",
            page_title="Instrumentos",
            page_icon="🔧"
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
        st.markdown('<h4 style="color:red">Administración de Instrumentos</h4>', unsafe_allow_html=True)
        st.markdown('<p>En esta sección se administran los instrumentos de la empresa.</p>', unsafe_allow_html=True)
        st.markdown('<h4 style="color:blue">Instrumentos</h4>', unsafe_allow_html=True)
        # Initialize connection.
        conn = st.connection('mysql', type='sql')

        with st.form(key='my_form'):
            # Add a text input to the form.
            brand = st.text_input(label='Marca', value='', placeholder='Ingrese la marca del instrumento').upper()

            # Add a submit button to the form.
            submit_button = st.form_submit_button(label='Buscar')

        if submit_button:
            # Perform query.
            df = conn.query(f'SELECT * from instruments WHERE brand like "%{brand}%"', ttl=600)

            # Print results.
            st.dataframe(df[['name', 'brand', 'model', 'serial', 'cal_date', 'exp_date']])


if __name__ == "__main__":
    InstrumentsApp()
