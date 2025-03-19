import pandas as pd
import streamlit as st

from config import page_config


def compute_end_time(i_datetime: pd.Timestamp, time_to_add: float) -> tuple[pd.Timestamp, str, pd.Timestamp]:
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
        # if 'result' not in st.session_state:
        #     st.session_state.result_freq = 1.0
        #     st.session_state.result_time = 1.0
        #     st.session_state.result_cycles = 1
        #     st.session_state.result_icycles = 0
        result = None
        units = None

        with st.form(key='form1'):
            st.subheader("Calculadora de Frecuencia, Ciclos, Tiempo")
            st.markdown("<span style='color: yellow;'>Ingrese los datos disponibles y marque la opción a calcular: </span>", unsafe_allow_html=True)

            col1, col2 = st.columns(2)

            with col1:
                freq = st.number_input(label="Frecuencia [Hz]", min_value=0.0, value=1.0, key='input_freq')
                time = st.number_input(label="Tiempo [s]", min_value=0.0, value=1.0, key='input_time')
                idate = st.date_input(label="Fecha de inicio", key='input_idate')

            with col2:
                cycles = st.number_input(label="Ciclos [#]", min_value=0, value=1, key='input_cycles')
                icycles = st.number_input(label="Ciclos Iniciales [#]", min_value=0, value=0, key='input_icycles')
                itime = st.time_input(label="Hora de inicio", key='input_itime')

            var_to_calc = st.radio("Seleccione la variable a calcular:", ["Frecuencia", "Tiempo", "Ciclos", "Ciclos Iniciales"],
                                   key='var_to_calc', index=1)

            if st.form_submit_button("Calcular"):

                if var_to_calc == "Frecuencia":
                    units = "Hz"
                    result = (cycles - icycles) / time

                elif var_to_calc == "Tiempo":
                    units = ""
                    result0 = (cycles - icycles) / freq
                    fdate, dow, ftime = compute_end_time(pd.to_datetime(str(idate) + ' ' + str(itime)), result0 / 3600)
                    # format fdate as 'dd/mm/yyyy'
                    fdatef = fdate.strftime('%d-%m-%Y')
                    result = f"{result0} s<br>{dow} {fdatef}, {ftime}"

                elif var_to_calc == "Ciclos":
                    units = "ciclos"
                    result = freq * time + icycles

                elif var_to_calc == "Ciclos Iniciales":
                    units = "ciclos"
                    result = freq * time - cycles

        if result:
            st.markdown("Resultado:<br><span style='color: magenta; font-size: 24px;'>"
                        f"{var_to_calc} = {result} {units}</span>", unsafe_allow_html=True)


if __name__ == "__main__":
    app = FTCCalc()
