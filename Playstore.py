import pandas as pd
import streamlit as st


class PlayStoreApp:
    def __init__(self):
        self.answer = ""
        self.run_app()

    def run_app(self):
        st.set_page_config(
            layout="centered",
            page_title="Experimental PlayStore",
            page_icon="📱"
        )
        # self.setup()
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
        st.markdown('# Experimental LabStore')
        st.markdown("---")
        st.markdown('<p>En esta sección se presentan aplicaciones desarrolladas por el <b>Laboratorio de '
                    'Experimental</b>. </p>', unsafe_allow_html=True)
        st.markdown('<p>Seleccione la aplicación deseada desde el menú lateral.</p>', unsafe_allow_html=True)
        st.markdown("<p>Si desea acceder a la página web de <b>Experimental</b>, haga click en el siguiente "
                    "enlace:</p>", unsafe_allow_html=True)
        st.markdown('Sitio de **[Experimental Web](http://experimental01)**', unsafe_allow_html=True)
        st.markdown("---")
        st.markdown('<h3>Contacto:</h3>', unsafe_allow_html=True)
        st.markdown('Correo: **[valdez@fadeasa.com.ar](mailto:valdez@fadeasa.com.ar)**', unsafe_allow_html=True)


if __name__ == "__main__":
    PlayStoreApp()
