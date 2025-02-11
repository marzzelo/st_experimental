import pandas as pd
import numpy as np
import streamlit as st
import time

from config import page_config


class DataExplorer:
    def __init__(self):
        # use a frequency icon
        page_config(title="Data Explorer", icon="📊", layout='wide')
        
        self.layout()
        
    
    def layout(self):
        st.markdown('### Explorador de Datos')
        
        conn = st.connection("experimental")
        df = conn.query("select name, email, ncontrol from users")
        st.dataframe(df)
        pass
        
            


if __name__ == "__main__":
    app = DataExplorer()
