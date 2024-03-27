import numpy as np
import pandas as pd
import streamlit as st
import streamlit.components.v1 as com

from config import page_config


class TractionCalculator:
    """

    """

    def __init__(self):
        page_config(title="Cálculo Fuerza de Tracción KC-390", icon="🚀")
        self.rk_cr_table = pd.read_csv('resources/RK_CR.csv')

    def run(self):
        self.show_form()

        if 'results' in st.session_state:
            self.show_results()
        else:
            st.markdown('<h4 style="color:red">Resultados</h4>', unsafe_allow_html=True)
            st.markdown('<p>Ingrese los datos solicitados para calcular la fuerza de tracción de ensayo.</p>',
                        unsafe_allow_html=True)

    def show_form(self):
        # https://lottie.host/embed/1342ec1b-cde3-4fd6-bc6b-edc51ec6c36e/ptMYNjPv5j.json
        com.iframe("https://lottie.host/embed/1342ec1b-cde3-4fd6-bc6b-edc51ec6c36e/ptMYNjPv5j.json", width=200,
                   height=200)
        st.markdown('<h4 style="color:red">Calculadora de Fuerza de Tracción de Ensayo</h4>', unsafe_allow_html=True)
        st.markdown('<p>Ingrese los datos soicitados para calcular la fuerza de tracción de ensayo.</p>',
                    unsafe_allow_html=True)
        with st.form(key='form_kc390'):
            col1, col2 = st.columns(2)

            d = col1.number_input(label="Diámetro de la probeta en la entalla", min_value=0.0,
                                  value=5.97, help="ver registro de instructivo de trabajo")
            rk = col2.number_input(label="Valor de dureza", min_value=30, value=51, max_value=60, step=1,
                                   help="ver registro de instructivo de trabajo")

            st.session_state.d = d
            st.session_state.rk = rk

            if st.form_submit_button("Calcular"):
                s = np.pi * d ** 2 / 4
                # find the index of the closest value to cr in the table
                idx = (np.abs(self.rk_cr_table['RK'] - rk)).idxmin()
                cr = self.rk_cr_table.loc[idx, 'CR']
                traction_force = s * cr * 0.75  # kgf
                traction_force_dan = traction_force * 9.81 / 10 # daN
                st.session_state.results = {
                    'FUERZA DE ENSAYO [kgf]': [f'{traction_force:.2f}', 'kgf'],
                    'FUERZA DE ENSAYO [daN]': [f'{traction_force_dan:.2f}', 'daN'],
                    'RESISTENCIA TRACCIÓN': [f'{cr:.2f}', 'kgf/mm²'],
                    'DUREZA ROCKWELL': [f'{rk:.2f}', 'HRB'],
                    'Diámetro en entalla': [f'{d:.2f}', 'mm'],
                    'Sección en entalla': [f'{s:.2f}', 'mm²']
                }

    @staticmethod
    def show_results():
        st.markdown('<h4 style="color:red">Resultados</h4>', unsafe_allow_html=True)
        st.dataframe(pd.DataFrame(st.session_state.results, index=['Magnitud', 'Unidad']).T, use_container_width=True)


if __name__ == "__main__":
    app = TractionCalculator()
    app.run()
