import streamlit as st


def ss_get(var: str, ini_val=None):
    """Retrieve a value from st.session_state, creating it if missing."""
    if var not in st.session_state:
        st.session_state[var] = ini_val
    return st.session_state[var]


def ss_set(var: str, val):
    """Set a value in st.session_state."""
    st.session_state[var] = val
