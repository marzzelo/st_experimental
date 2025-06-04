import os, sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import pandas as pd
import pytest

from pages.Calculadora_de_Tiempo import compute_end_time


@pytest.mark.parametrize(
    "start, hours, exp_date, exp_dow, exp_time",
    [
        (
            pd.Timestamp("2024-01-01 12:00:00"),
            24,
            pd.Timestamp("2024-01-02").date(),
            "Martes",
            pd.Timestamp("12:00:00").time(),
        ),
        (
            pd.Timestamp("2024-01-01 12:00:00"),
            25,
            pd.Timestamp("2024-01-02").date(),
            "Martes",
            pd.Timestamp("13:00:00").time(),
        ),
        (
            pd.Timestamp("2023-12-31 23:00:00"),
            2,
            pd.Timestamp("2024-01-01").date(),
            "Lunes",
            pd.Timestamp("01:00:00").time(),
        ),
    ],
)
def test_compute_end_time(start, hours, exp_date, exp_dow, exp_time):
    date, dow, time = compute_end_time(start, hours)
    assert date == exp_date
    assert dow == exp_dow
    assert time == exp_time
