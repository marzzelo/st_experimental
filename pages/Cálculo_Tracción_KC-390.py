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
        self.left_col, self.center_col, self.right_col = st.columns([8, 22, 8])


    def run(self):
        # Show RK-CR table                
        self.show_rk_cr_table()
        
        # Mostrar el formulario principal (diámetro y dureza)
        self.show_form()

        # Si ya se calculó la fuerza de tracción, mostrar los resultados. En caso contrario, mostrar las instrucciones.
        if 'results' in st.session_state:
            self.show_results()
        else:
            self.show_instructions()
        
        

    def show_rk_cr_table(self):
        with self.right_col:
            # titulo
            st.markdown('<div style="color: lightgreen; text-align: center;">Tabla Dureza-Resistencia</div>', unsafe_allow_html=True)
            dataframe = self.rk_cr_table
            target = st.session_state.get('rk', None)
            if target is not None:
                # Identificar la fila con RK menor o igual al target
                lower_df = dataframe[dataframe['RK'] <= target]
                # Identificar la fila con RK mayor o igual al target
                upper_df = dataframe[dataframe['RK'] >= target]
                target_idxs = set()
                if not lower_df.empty:
                    lower_idx = lower_df['RK'].idxmax()
                    target_idxs.add(lower_idx)
                if not upper_df.empty:
                    upper_idx = upper_df['RK'].idxmin()
                    target_idxs.add(upper_idx)

                def highlight_row(row):
                    if row.name in target_idxs:
                        return ['color: yellow; background-color: #333377'] * len(row)
                    else:
                        return [''] * len(row)

                styled_df = dataframe.style.apply(highlight_row, axis=1).format("{:.0f}")
                st.dataframe(styled_df, hide_index=True, use_container_width=True)
            else:
                st.dataframe(dataframe.style.format("{:.0f}"), hide_index=True, use_container_width=True)


    def show_instructions(self):
        with self.center_col:
            st.markdown('<h4 style="color:gray">Instrucciones</h4>', unsafe_allow_html=True)
            st.markdown('<p style="color:gray">Ingrese los datos solicitados de diámetro y dureza para calcular la fuerza de tracción '
                            'de ensayo.</p>',
                            unsafe_allow_html=True)


    def show_form(self):
        
        # Mostrar la imagen ilustrativa en la columna de la izquierda
        with self.left_col:
            img_path = 'resources/probeta.png'
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

                if st.form_submit_button("Calcular Carga de Prueba", type="primary"):
                   
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
                        'CARGA DE PRUEBA, :blue[$F$]': [f'{traction_force:.2f}', 'kgf'],
                        
                        '\nCARGA DE PRUEBA, :blue[$F$]': [f'{traction_force_dan:.2f}', 'daN'],
                        'LÍMITE INFERIOR (0.9)F, :blue[$F_l$]': [f'{traction_force_dan * 0.9:.2f}', 'daN'],
                        'LÍMITE SUPERIOR (1.1)F, :blue[$F_u$]': [f'{traction_force_dan * 1.1:.2f}', 'daN'],
                        'RESISTENCIA TRACCIÓN, :blue[$\\sigma_R$]': [f'{cr:.2f}', 'kgf/mm²'],
                        'DUREZA ROCKWELL, :blue[**HRC**]': [f'{rk:.2f}', ''],
                        'Diámetro en entalla, :blue[$\\phi_0$]': [f'{d:.2f}', 'mm'],
                        'Sección inicial de entalla, :blue[$S_0$]': [f'{s:.2f}', 'mm²']
                    }
                    st.rerun()


    def show_results(self):
        with self.center_col:
            st.markdown('<h4 style="color:red">Resultados</h4>', unsafe_allow_html=True)

            df = pd.DataFrame(st.session_state.results, index=['Magnitud', 'Unidad']).T
            stdf = df.style.apply(
                lambda x: ["font-weight: bold; font-size: 1.2em; color: yellow;"
                           if x.name in [df.index[1]] else "" for i in x],
                axis=1)
            st.table(stdf)
            with self.center_col:
                st.markdown('<br>', unsafe_allow_html=True)
                st.info('''
                :small[*Fórmula utilizada para el cálculo de la Fuerza:*]  
                :blue[$ F = \\sigma_R \\times S_0 \\times 0.75  $]''')



if __name__ == "__main__":
    app = TractionCalculator()
    app.run()
