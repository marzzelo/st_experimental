import pandas as pd
import streamlit as st

from config import page_config


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
    return end_date, end_dayofweek, end_time


class FTCCalc:
    def __init__(self):
        # use a frequency icon
        page_config(title="Calculadora de Frecuencia", icon=":infinity:")

    def run(self):
        self.show_form()

        self.calculate(st.session_state.var_to_calc)

        if 'result' in st.session_state:
            self.show_result()

    @staticmethod
    def show_form():

        with st.form(key='form1'):
            st.subheader("Calculadora de Frecuencia, Ciclos, Tiempo")
            st.markdown("<span style='color: yellow;'>Ingrese los datos disponibles y marque la opción a calcular: </span>", unsafe_allow_html=True)

            col1, col2 = st.columns(2)

            with col1:
                freq = st.number_input(label="Frecuencia [Hz]", min_value=0.0, value=1.0, key='input_freq')
                time = st.number_input(label="Tiempo [s]", min_value=0.0, value=1.0, key='input_time')

            with col2:
                cycles = st.number_input(label="Ciclos [#]", min_value=0, value=1, key='input_cycles')
                icycles = st.number_input(label="Ciclos Iniciales [#]", min_value=0, value=0, key='input_icycles')

            var_to_calc = st.radio("Seleccione la variable a calcular:", ["Frecuencia", "Tiempo", "Ciclos", "Ciclos Iniciales"],
                                   key='var_to_calc', index=1)

            st.form_submit_button("Calcular")

    @staticmethod
    def calculate(var_to_calc):
        """
        Calculate the selected variable
        cycles = freq * time + icycles
        """
        result = 0
        units = ""
        if var_to_calc == "Frecuencia":
            units = "Hz"
            result = (st.session_state.input_cycles - st.session_state.input_icycles) / st.session_state.input_time

        elif var_to_calc == "Tiempo":
            units = "s"
            result = (st.session_state.input_cycles - st.session_state.input_icycles) / st.session_state.input_freq

        elif var_to_calc == "Ciclos":
            units = "ciclos"
            result = st.session_state.input_freq * st.session_state.input_time + st.session_state.input_icycles

        elif var_to_calc == "Ciclos Iniciales":
            units = "ciclos"
            result = st.session_state.input_freq * st.session_state.input_time - st.session_state.input_cycles

        st.session_state.result = result
        st.session_state.units = units

    @staticmethod
    def show_result():
        st.markdown(f"<p>Resultado:</p><h2 style='color: magenta;'>{st.session_state.result} {st.session_state.units}</h4>", unsafe_allow_html=True)


if __name__ == "__main__":
    app = FTCCalc()
    app.run()
