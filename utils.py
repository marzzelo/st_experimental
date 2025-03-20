import streamlit as st


def ss_get(var: str, ini_val: any = None):
    if var not in st.session_state:
        st.session_state[var] = ini_val
        
    return st.session_state[var]
        
def ss_set(var: str, ini_val: any):
    st.session_state[var] = ini_val
    
    