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
