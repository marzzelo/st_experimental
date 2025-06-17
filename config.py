from typing import Literal

import streamlit as st


def page_config(title, icon, layout: Literal["centered", "wide"] = "centered"):
    st.set_page_config(
        layout=layout,
        page_title=title,
        page_icon=icon,
        menu_items={
            'Get Help': None,
            'Report a bug': None,
            'About': "# Lab Store\n### Laboratorio de Experimental\n## FAdeA "
                     "S.A.\n[Marcelo Valdez](mailto:valdez@fadeasa.com.ar)"
        }
    )
    st.markdown("""
        <style>
            .st-emotion-cache-cnbvxy.e1nzilvr5 > :nth-child(5) {
                display: none;
            }
            .st-emotion-cache-10trblm e1nzilvr1 {
                color: red !important;
            }
        </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown(f"## {title}")
        st.markdown("---")
        st.page_link("lab.py", label="Lab Store", icon="🟡")
        st.markdown("---")
        st.page_link("pages/Calculadora_de_Tiempo.py", label="Tiempo Final", icon="⏰")
        st.page_link("pages/Calculadora_FTC.py", label="Frecuencia y Ciclos", icon="♾️")
        st.page_link("pages/Cálculo_Tracción_KC-390.py", label="Tracción KC-390", icon="🔧")
        st.page_link("pages/Data_Explorer.py", label="Explorador de Datos", icon="📊")
        st.page_link("pages/Rotations.py", label="Rotations", icon="🔄")
        st.page_link("pages/Calibraciones.py", label="Calibraciones", icon="⚖️")
        st.page_link("pages/Arbitrary_Waveform_Script_Generator.py", label="AWF Script Generator", icon="📜")
        
