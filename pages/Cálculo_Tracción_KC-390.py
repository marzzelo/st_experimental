import numpy as np
import pandas as pd
import streamlit as st

from config import page_config


# to install PIL use: pip install Pillow
class TractionCalculator:
    """
    This class creates a Streamlit app that calculates the traction force of a test given the diameter of the test
    specimen and the Rockwell hardness of the material.
    """

    def __init__(self):
        page_config(
            title="Fuerza de Tracción",
            icon="🚀",
            layout="wide"

        )
        self.rk_cr_table = pd.read_csv('resources/RK_CR.csv', dtype={'RK': float, 'CR': float})
        self.left_col, self.center_col, self.right_col = st.columns([1, 2, 1])

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
            st.markdown('<p>Ingrese los datos solicitados para calcular la fuerza de tracción de ensayo.</p>',
                        unsafe_allow_html=True)
            with st.form(key='form_kc390'):
                col1, col2 = st.columns(2)

                d = col1.number_input(label="Diámetro de la probeta en la entalla", min_value=0.0,
                                      value=5.97, help="ver registro de instructivo de trabajo")
                rk = col2.number_input(label="Valor de dureza", min_value=30.0, value=51.0, max_value=60.0,
                                       help="ver registro de instructivo de trabajo")

                st.session_state.d = d
                st.session_state.rk = rk

                if st.form_submit_button("Calcular"):
                    s = np.pi * d ** 2 / 4
                    # find the index of the closest value to cr in the table
                    # idx = (np.abs(self.rk_cr_table['RK'] - rk)).idxmin()

                    # interpolate the value of CR from the table
                    # truncate the value of RK
                    rk_low = np.trunc(rk)
                    rk_high = np.ceil(rk)

                    if rk_low == rk_high:
                        idx = (np.abs(self.rk_cr_table['RK'] - rk_low)).idxmin()
                        cr = self.rk_cr_table.loc[idx, 'CR']
                    else:
                        idx_low = self.rk_cr_table['RK'].sub(rk_low).gt(0).idxmin()
                        idx_high = self.rk_cr_table['RK'].sub(rk_high).gt(0).idxmin()

                        cr_low = self.rk_cr_table.loc[idx_low, 'CR']
                        cr_high = self.rk_cr_table.loc[idx_high, 'CR']
                        print(f'rk_low: {rk_low}, rk_high: {rk_high}')
                        print(f'cr_low: {cr_low}, cr_high: {cr_high}')

                        cr = cr_low + (cr_high - cr_low) / (rk_high - rk_low) * (rk - rk_low)
                        print(f'cr: {cr}')

                    # cr = self.rk_cr_table.loc[idx, 'CR']
                    traction_force = s * cr * 0.75  # kgf
                    traction_force_dan = traction_force * 9.81 / 10  # daN
                    st.session_state.results = {
                        'CARGA DE PRUEBA [kgf]': [f'{traction_force:.2f}', 'kgf'],
                        'CARGA DE PRUEBA [daN]': [f'{traction_force_dan:.2f}', 'daN'],
                        'RESISTENCIA TRACCIÓN': [f'{cr:.2f}', 'kgf/mm²'],
                        'DUREZA ROCKWELL': [f'{rk:.2f}', 'HRC'],
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
