import streamlit as st
import pandas as pd
import numpy as np

from config import page_config


class PlayStoreApp:
    def __init__(self):
        self.answer = ""
        self.run_app()

    def run_app(self):
        page_config(title="Experimental LabStore", icon="🟡")
        self.main()

    @staticmethod
    def main():
        st.markdown('# Laboratorio de Experimental')

        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            with st.container(height=60, border=True):
                st.page_link('pages/Cálculo_Tracción_KC-390.py', label='Tracción KC-390', icon="🔧", help=None, disabled=False, use_container_width=True)
            with st.container(height=60, border=True):
                st.page_link('pages/Data_Explorer.py', label='Explorador de Datos', icon="📊", help=None, disabled=False, use_container_width=True)
        with col2:
            with st.container(height=60, border=True):
                st.page_link('pages/Calculadora_de_Tiempo.py', label='Tiempo Final', icon="⏰", help=None, disabled=False, use_container_width=True)
            with st.container(height=60, border=True):
                st.page_link('pages/Rotations.py', label='Rotations', icon="🔄", help=None, disabled=False, use_container_width=True)
        with col3:
            with st.container(height=60, border=True):
                st.page_link('pages/Calculadora_FTC.py', label='Frecuencia y Ciclos', icon="♾️", help=None, disabled=False, use_container_width=True)
            with st.container(height=60, border=True):
                st.page_link('pages/Calibraciones.py', label='Calibraciones', icon="⚖️", help=None, disabled=False, use_container_width=True)
            with st.container(height=60, border=True):
                st.page_link('pages/Arbitrary_Waveform_Script_Generator.py', label='AWF Script Generator', icon="📜", help=None, disabled=False, use_container_width=True)
           
        st.markdown("---")
        st.markdown('<h3>Contacto:</h3>', unsafe_allow_html=True)
        st.markdown('Correo: **[valdez@fadeasa.com.ar](mailto:valdez@fadeasa.com.ar)**', unsafe_allow_html=True)
        


if __name__ == "__main__":
    PlayStoreApp()

# run with: python -m streamlit run .\lab.py
