import pandas as pd
import streamlit as st

from config import page_config



def compute_end_time(i_datetime, time_to_add):
    """
    Se define la función compute_end_time, que recibe una fecha/hora de inicio y una 
    cantidad de horas para sumar. Dentro de esta función se calcula la fecha/hora final, 
    se extrae la fecha, la hora y se determina el día de la semana en formato de texto, 
    retornando estos valores en una tupla.
    """
    end_datetime = i_datetime + pd.Timedelta(hours=time_to_add)
    end_date = end_datetime.date()
    end_time = end_datetime.time()
    end_dayofweek_number = int(end_datetime.dayofweek)
    days_of_week = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    end_dayofweek = days_of_week[end_dayofweek_number]
    return end_date, end_dayofweek, end_time


class TimeCalculatorApp:
    """
    This class creates a Streamlit app that calculates the end time of an event given the start time and the duration
    of the event. It also generates a table with the end times of a number of periods of 1 hour starting from the start
    time.
    """

    def __init__(self):
        page_config(title="Calculadora de Tiempo", icon="⏰")

    def run(self):
        """
        El método run orquesta la ejecución de la aplicación. Llama a calculate_end_time para mostrar 
        el formulario de entrada. Luego, según los valores almacenados en st.session_state:
        - Si ya se calculó un tiempo final, se muestra un botón para generar una tabla.
        - Si se ha presionado dicho botón, se invoca create_table para generar la tabla con períodos de 1 hora.
        - Si la tabla ya se creó, se muestra en pantalla.
        """            
        self.show_main_form()

        if 'end_time' in st.session_state:
            self.show_btn_table()

        if 'btn_table_pressed' in st.session_state:
            self.create_table()

        if 'table' in st.session_state:
            self.show_table()

    @staticmethod
    def show_main_form():
        """
        El método show_main_form() presenta un formulario en el que el usuario ingresa la fecha y hora 
        de inicio, junto con la duración del ensayo. Al enviarse el formulario, se utiliza 
        compute_end_time para calcular y almacenar el tiempo final en st.session_state.
        """
        st.markdown('<h4 style="color:red">Calculadora de Tiempo Final</h4>', unsafe_allow_html=True)
        st.markdown('<p>Ingrese la fecha y hora de inicio del ensayo y la duración del mismo para calcular la fecha y '
                    'hora de finalización.</p>', unsafe_allow_html=True)
        with st.form(key='my_form'):
            col1, col2 = st.columns(2)

            i_date = col1.date_input(label="Fecha de inicio del ensayo", format="DD/MM/YYYY", key='i_date')
            i_time = col2.time_input(label="Hora de inicio del ensayo", key='i_time')
            time_to_add = col1.number_input(label="Duración del ensayo en horas", min_value=0, value=200, step=1, key='time_to_add')

            i_datetime = pd.to_datetime(str(i_date) + ' ' + str(i_time))

            if st.form_submit_button("Calcular"):
                st.session_state.end_time = compute_end_time(i_datetime, time_to_add)  # habilita show_btn_table() en self.run()

                # Inhabilita el botón de calcular y el formulario con valores antiguos en self.run() 
                if 'btn_table_pressed' in st.session_state:
                    del st.session_state['btn_table_pressed']
                if 'table' in st.session_state:
                    del st.session_state['table']

    @staticmethod
    def show_btn_table():
        """
        El método show_btn_table muestra un mensaje con el tiempo final calculado y coloca un botón que, 
        al presionarlo, indica que se debe generar la tabla de tiempos.
        """
        end_time = st.session_state.end_time
        st.markdown(f'<div style="border: 2px solid; padding:10px; border-radius:5px; margin-bottom:10px;">'
                    f'El ensayo finaliza el día {end_time[0]} a las {end_time[2]} ({end_time[1]}).</div>', unsafe_allow_html=True)

        if 'btn_table_pressed' not in st.session_state:
            btn_table = st.button("Generar tabla de tiempos",
                                  on_click=lambda: setattr(st.session_state, 'btn_table_pressed', True))  # habilita 

    @staticmethod
    def create_table():
        """
        El método create_table permite al usuario ingresar nuevos parámetros (como la cantidad de períodos) 
        y, mediante un formulario, crea una tabla en la que se calcula, para cada periodo, la fecha 
        y hora de término usando compute_end_time. Esta tabla se guarda en st.session_state.
        """
        st.markdown('<h4 style="color:red">Tabla de Tiempos</h4>', unsafe_allow_html=True)
        st.markdown('<p>Ingrese cantidad de periodos de 1 hora a calcular a partir de la hora inicial.</p>',
                    unsafe_allow_html=True)
        with st.form(key='form_table'):
            col1, col2 = st.columns(2)

            # start time = now
            i_date = col1.date_input(label="Fecha inicial", value=st.session_state.i_date,
                                     format="DD/MM/YYYY")
            i_time = col2.time_input(label="Hora inicial", value=st.session_state.i_time)
            
            if "new_time_to_add" not in st.session_state:
                st.session_state.new_time_to_add = 200
            
            time_to_add = col1.number_input(label="Duración del ensayo en horas", min_value=0,
                                            value=st.session_state.new_time_to_add, step=1)

            i_datetime = pd.to_datetime(str(i_date) + ' ' + str(i_time))
            periods = col2.number_input(label="Cantidad de periodos", min_value=1, value=10, step=1)

            if st.form_submit_button("Calcular"):
                st.session_state.new_time_to_add = time_to_add
                times = pd.date_range(start=i_datetime, periods=periods, freq='h')
                df = pd.DataFrame({'Fecha': pd.to_datetime(times).date, 'Hora': pd.to_datetime(times).time})
                end_times = [compute_end_time(i, st.session_state.new_time_to_add) for i in times]
                df['Fecha de finalización'] = [i[0] for i in end_times]
                df['Hora de finalización'] = [i[2] for i in end_times]
                df['Día de la semana'] = [i[1] for i in end_times]

                st.session_state.table = df

    @staticmethod
    def show_table():
        st.dataframe(st.session_state.table, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    app = TimeCalculatorApp()
    app.run()
