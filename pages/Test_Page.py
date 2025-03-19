import pandas as pd
import streamlit as st

from config import page_config
from utils import ss_init, ss_set





class TestPage:
    def __init__(self):
        # use a frequency icon
        page_config(title="Test Page", icon="📊", layout='wide')
        ss_init('cnt1', 0)
        ss_init('cnt2', 0)
        ss_init('text', "Hello World (CHANGE this!)")
        self.layout()
        
        
        
    def layout(self):
        
        @st.fragment()
        def toggle_and_text():
            cols = st.columns(2)
            cols[0].toggle("Toggle")
            if st.button('INC', key='btn1'):
                st.session_state['cnt1'] += 1
                
            st.title(st.session_state['cnt1'])
            cols[1].text_area("Enter text", value=st.session_state['text'], key='text_area')


        @st.fragment()
        def filter_and_file():
            cols = st.columns(2)
            cols[0].checkbox("Filter")
            cols[1].file_uploader("Upload image")
            if st.button('INC'):
                st.session_state['cnt2'] += 1   
                
            st.title(st.session_state['cnt2'])


        st.title("My Awesome App")

        st.markdown("---")
        st.markdown("<h3 style='color:green;'>Toggle and Text Area (Fragment)</h3>", unsafe_allow_html=True)
        toggle_and_text()
        st.markdown("---")
        
        st.markdown("<h3 style='color:green;'>Select and Button (MAIN)</h3>", unsafe_allow_html=True)
        cols = st.columns(2)
        cols[0].selectbox("Select", [1,2,3], None)
        if cols[1].button("Update"):
            ss_set('cnt1', 0)
            ss_set('cnt2', 0)
            st.rerun()
        st.markdown("---")
        
        st.markdown("<h3 style='color:green;'>Filter and File Uploader (Fragment)</h3>", unsafe_allow_html=True)
        filter_and_file()
        st.markdown("---")
        
        
        
if __name__ == "__main__":
    app = TestPage()
