import numpy as np
import pandas as pd
import streamlit as st
import streamlit.components.v1 as com
from PIL import Image

from config import page_config


# to install PIL use: pip install Pillow
class TractionCalculator:
    """
    This class creates a Streamlit app that calculates the traction force of a test given the diameter of the test
    specimen and the Rockwell hardness of the material.
    """

    def __init__(self):
        page_config(
            title="Cálculo Fuerza de Tracción KC-390",
            icon="🚀",
            layout="wide"

        )
        self.rk_cr_table = pd.read_csv('resources/RK_CR.csv')
        self.left_col, self.center_col, self.right_col = st.columns([1, 2, 2])

    def run(self):
        self.show_form()

        if 'results' in st.session_state:
            self.show_results()
        else:
            with self.center_col:
                st.markdown('<h4 style="color:gray">Resultados</h4>', unsafe_allow_html=True)
                st.markdown('<p style="color:gray">Ingrese los datos solicitados para calcular la fuerza de tracción '
                            'de ensayo.</p>',
                            unsafe_allow_html=True)

    def show_form(self):
        img_path = 'resources/probeta.png'

        with self.left_col:
            st.image(img_path, width=200)

        with self.center_col:
            st.markdown('<h4 style="color:red">Calculadora de Fuerza de Tracción de Ensayo</h4>',
                        unsafe_allow_html=True)
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
                    traction_force_dan = traction_force * 9.81 / 10  # daN
                    st.session_state.results = {
                        'FUERZA DE ENSAYO [kgf]': [f'{traction_force:.2f}', 'kgf'],
                        'FUERZA DE ENSAYO [daN]': [f'{traction_force_dan:.2f}', 'daN'],
                        'RESISTENCIA TRACCIÓN': [f'{cr:.2f}', 'kgf/mm²'],
                        'DUREZA ROCKWELL': [f'{rk:.2f}', 'HRB'],
                        'Diámetro en entalla': [f'{d:.2f}', 'mm'],
                        'Sección en entalla': [f'{s:.2f}', 'mm²']
                    }

    def show_results(self):
        with self.center_col:
            st.markdown('<h4 style="color:red">Resultados</h4>', unsafe_allow_html=True)

            df = pd.DataFrame(st.session_state.results, index=['Magnitud', 'Unidad']).T
            stdf = df.style.apply(
                lambda x: ["background: gray; color: black; font-weight: bold; font-size: 1.5em"
                           if x.name in [df.index[0], df.index[1]] else "" for i in x],
                axis=1)
            st.table(stdf)



if __name__ == "__main__":
    app = TractionCalculator()
    app.run()
