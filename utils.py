import streamlit as st


def ss_init(var: str, ini_val: any):
    if var not in st.session_state:
        st.session_state[var] = ini_val
        
def ss_set(var: str, ini_val: any):
    st.session_state[var] = ini_val