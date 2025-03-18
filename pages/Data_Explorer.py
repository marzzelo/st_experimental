import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt

from config import page_config


def session_init(var: str, ini_val: any):
    if var not in st.session_state:
        st.session_state[var] = ini_val


class DataExplorer:
    def __init__(self):
        # use a frequency icon
        page_config(title="Data Explorer", icon="📊", layout='wide')
        
        session_init('counter', 0)
        
        self.layout()
        
    
    def layout(self):
        st.html('<h2>Explorador de Datos</h2>')
        default_file = r'data\kc-390-cromo.csv'
                
        # load a csv file from disk and display a plot of its data
        uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])
        
        @st.cache_data
        def load_file():             
            st.html(f'<div>Using default file: <span style="color: green; padding-left: 8px;">{default_file}</span></div>')
            data = pd.read_csv(default_file, sep=r'\t', engine='python')
            return data
                
        data = load_file()

        st.write("Dataset:", data.head()) 
        numeric_data = data.select_dtypes(include=[np.number])
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
                
                    ax.plot(numeric_data['ts'], numeric_data['F1'], alpha=0.6)
                    ax.set_xlabel('ts [s]', fontsize=10)
                    ax.set_ylabel('F1 [daN]', fontsize=10)
                    ax.set_title("Scatter Plot of Numeric Data", fontsize=12)
                    ax.tick_params(axis='both', labelsize=8)
                    ax.grid()
                    st.pyplot(fig)
                    # st.line_chart(numeric_data, x="ts", y="F1")
                    
        else:
            st.error("No numeric columns available to plot.")
    

        if st.button('Increment'):
            st.session_state['counter'] += 1
            
        st.write(f"COUNTER: {st.session_state['counter']}")
            

if __name__ == "__main__":
    app = DataExplorer()
