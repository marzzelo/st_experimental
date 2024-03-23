import pandas as pd
import streamlit as st
import streamlit.components.v1 as com

def compute_end_time(i_datetime, time_to_add):
    """
    Compute the end time of an event given the start time and the duration of the event.
    :param i_datetime:
    :param time_to_add:
    :return: a tuple with the date, day of the week and time of the end of the event.
    """
    end_datetime = i_datetime + pd.Timedelta(hours=time_to_add)
    end_date = end_datetime.date()
    end_time = end_datetime.time()
    end_dayofweek_number = int(end_datetime.dayofweek)
    days_of_week = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    end_dayofweek = days_of_week[end_dayofweek_number]
    answer = (end_date, end_dayofweek, end_time)
    return answer


class TimeCalculatorApp:
    """
    This class creates a Streamlit app that calculates the end time of an event given the start time and the duration
    of the event. It also generates a table with the end times of a number of periods of 1 hour starting from the start
    time.
    """
    def __init__(self):
        st.set_page_config(
            layout="centered",
            page_title="Calculadora de Tiempo",
            page_icon="⏰"
        )

    def run(self):
        self.calculate_end_time()

        if 'answer' in st.session_state:
            self.show_btn_table()

        if 'btn_table' in st.session_state:
            self.create_table()

        if 'table' in st.session_state:
            self.show_table()

    def calculate_end_time(self):
        # https://lottie.host/embed/1342ec1b-cde3-4fd6-bc6b-edc51ec6c36e/ptMYNjPv5j.json
        com.iframe("https://lottie.host/embed/1342ec1b-cde3-4fd6-bc6b-edc51ec6c36e/ptMYNjPv5j.json", width=200,
                   height=200)
        st.markdown('<h4 style="color:red">Calculadora de Tiempo Final</h4>', unsafe_allow_html=True)
        st.markdown('<p>Ingrese la fecha y hora de inicio del ensayo y la duración del mismo para calcular la fecha y '
                    'hora de finalización.</p>', unsafe_allow_html=True)
        with st.form(key='my_form'):
            col1, col2 = st.columns(2)

            i_date = col1.date_input(label="Fecha de inicio del ensayo", format="DD/MM/YYYY")
            i_time = col2.time_input(label="Hora de inicio del ensayo")
            time_to_add = col1.number_input(label="Duración del ensayo en horas", min_value=0, value=200, step=1)

            st.session_state.i_date = i_date
            st.session_state.i_time = i_time
            st.session_state.time_to_add = time_to_add

            i_datetime = pd.to_datetime(str(i_date) + ' ' + str(i_time))

            if st.form_submit_button("Calcular"):
                end_time = compute_end_time(i_datetime, time_to_add)
                answer = f'El ensayo finaliza el día {end_time[0]} a las {end_time[2]} ({end_time[1]}).'

                st.session_state.answer = (
                    f'<div style="border: 2px solid; padding:10px; border-radius:5px; margin-bottom:10px;">'
                    f'{answer}</div>')

                if 'btn_table' in st.session_state:
                    del st.session_state['btn_table']
                if 'table' in st.session_state:
                    del st.session_state['table']

    def show_btn_table(self):
        st.markdown(st.session_state.answer, unsafe_allow_html=True)
        if 'btn_table' not in st.session_state:
            btn_table = st.button("Generar tabla de tiempos",
                                  on_click=lambda: setattr(st.session_state, 'btn_table', True))

    def create_table(self):
        st.markdown('<h4 style="color:red">Tabla de Tiempos</h4>', unsafe_allow_html=True)
        st.markdown('<p>Ingrese cantidad de periodos de 1 hora a calcular a partir de la hora inicial.</p>',
                    unsafe_allow_html=True)
        with st.form(key='form_table'):
            col1, col2 = st.columns(2)

            # start time = now
            i_date = col1.date_input(label="Fecha inicial", value=st.session_state.i_date,
                                     format="DD/MM/YYYY")
            i_time = col2.time_input(label="Hora inicial", value=st.session_state.i_time)
            time_to_add = col1.number_input(label="Duración del ensayo en horas", min_value=0,
                                            value=st.session_state.time_to_add, step=1)

            i_datetime = pd.to_datetime(str(i_date) + ' ' + str(i_time))
            periods = col2.number_input(label="Cantidad de periodos", min_value=1, value=10, step=1)

            if st.form_submit_button("Calcular"):
                times = pd.date_range(start=i_datetime, periods=periods, freq='H')
                df = pd.DataFrame({'Fecha': pd.to_datetime(times).date, 'Hora': pd.to_datetime(times).time})
                end_times = [compute_end_time(i, st.session_state.time_to_add) for i in times]
                df['Fecha de finalización'] = [i[0] for i in end_times]
                df['Hora de finalización'] = [i[2] for i in end_times]
                df['Día de la semana'] = [i[1] for i in end_times]

                st.session_state.table = df

    def show_table(self):
        st.dataframe(st.session_state.table, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    app = TimeCalculatorApp()
    app.run()
