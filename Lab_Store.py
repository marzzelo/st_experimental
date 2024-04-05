import streamlit as st
from config import page_config


class PlayStoreApp:
    def __init__(self):
        self.answer = ""
        self.run_app()

    def run_app(self):
        page_config(title="Experimental LabStore", icon="🟡")
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
        st.markdown('# Laboratorio de Experimental')
        st.markdown("---")
        st.markdown('<h3>Contacto:</h3>', unsafe_allow_html=True)
        st.markdown('Correo: **[valdez@fadeasa.com.ar](mailto:valdez@fadeasa.com.ar)**', unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            st.page_link('pages/Cálculo_Tracción_KC-390.py', label='Tracción KC-390', icon="🔧", help=None, disabled=False, use_container_width=True)
        with col2:
            st.page_link('pages/Calculadora_de_Tiempo.py', label='Tiempo Final', icon="⏰", help=None, disabled=False, use_container_width=True)
        with col3:
            st.page_link('Lab_Store.py', label='Frecuencia y Ciclos', icon="🔄", help=None, disabled=False, use_container_width=True)


if __name__ == "__main__":
    PlayStoreApp()
