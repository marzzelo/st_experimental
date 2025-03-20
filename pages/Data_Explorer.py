import pandas as pd
import numpy as np
from sqlalchemy import Null
import streamlit as st
import matplotlib.pyplot as plt

from config import page_config
from utils import ss_get, ss_set



class DataExplorer:
    def __init__(self):
        print('inside __init__')
        page_config(title="Data Explorer", icon="📊", layout='wide')
        
        # ss_init('counter', 0)
        
        self.layout()
        
    
    def layout(self):
        print('inside layout()')
        st.html('<h2>Explorador de Datos</h2>')
        default_file = r'data\kc-390-cromo.csv'
                
        # load a csv file from disk and display a plot of its data
        uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])
        
        
        @st.cache_data
        def read_data(fname):
            return pd.read_csv(fname, sep=r'\t', engine='python')               
               
               
        if uploaded_file is not None:             
            st.html(f'<div>Using file: <span style="color: green; padding-left: 8px;">{uploaded_file.name}</span></div>')
            data = read_data(uploaded_file)
            ss_set('ll', low_limit)
            ss_set('hl', high_limit)
        else:
            st.html(f'<div>Using default file: <span style="color: green; padding-left: 8px;">{default_file}</span></div>')
            data = read_data(default_file)
            
                
        numeric_data = data.select_dtypes(include=[np.number])
        low_limit = min(numeric_data['ts'])
        high_limit = max(numeric_data['ts'])
        
        cur_ll = ss_get('ll', low_limit)
        cur_hl = ss_get('hl', high_limit)
                
        if not numeric_data.empty:
            # Ensure there are at least two numeric columns to form a scatter plot
            num_cols = numeric_data.select_dtypes(include=[np.number]).columns
            if len(num_cols) < 2:
                st.error("Need at least two numeric columns for a scatter plot.")
            else:
                col1, col2, col3 = st.columns([1,8,1])
                with col2:
                    # Create a figure with a moderate size and adjust font sizes
                    fig, ax = plt.subplots(figsize=(8, 4))
                
                    mask = (numeric_data['ts'] >= cur_ll) & (numeric_data['ts'] <= cur_hl)
                    ax.plot(numeric_data.loc[mask, 'ts'], numeric_data.loc[mask, 'F1'], alpha=0.6)
                    ax.set_xlabel('ts [s]', fontsize=10)
                    ax.set_ylabel('F1 [daN]', fontsize=10)
                    ax.set_title("Scatter Plot of Numeric Data", fontsize=12)
                    ax.tick_params(axis='both', labelsize=8)
                    ax.grid()
                    st.pyplot(fig)
                    # st.line_chart(numeric_data, x="ts", y="F1")
                    
        else:
            st.error("No numeric columns available to plot.")
               
        cols = st.columns([1,1,1,1])
        ll = cols[0].number_input('Low Limit', min_value=ss_get('ll'), max_value=ss_get('hl'), value=ss_get('ll'))
        hl = cols[1].number_input('High Limit', min_value=ss_get('ll'), max_value=ss_get('hl'), value=ss_get('hl'))
        
        if cols[2].button('REDRAW', use_container_width=True):
            ss_set('ll', ll)
            ss_set('hl', hl)
            st.rerun()

        if cols[3].button('RESET', use_container_width=True):
            ss_set('ll', low_limit)
            ss_set('hl', high_limit)
            st.rerun()
            

if __name__ == "__main__":
    app = DataExplorer()
