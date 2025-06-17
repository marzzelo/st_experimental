import os, sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import pandas as pd

from pages.Arbitrary_Waveform_Script_Generator import validate_format, encode_voltages


def test_validate_format_ok():
    df = pd.DataFrame([
        ["ms", "V"],
        [0, 0],
        [1, 1],
    ])
    assert validate_format(df) is None


def test_validate_format_invalid_unit():
    df = pd.DataFrame([
        ["min", "V"],
        [0, 0],
    ])
    assert "Unidad de tiempo" in validate_format(df)


def test_validate_format_non_numeric():
    df = pd.DataFrame([
        ["ms", "V"],
        ["a", 1],
    ])
    assert "num\u00e9ricos" in validate_format(df)


def test_encode_voltages_range():
    volts = pd.Series([-1, 0, 1])
    codes = encode_voltages(volts)
    assert codes.iloc[0] == -32767
    assert codes.iloc[1] == 0
    assert codes.iloc[2] == 32767


def test_encode_voltages_constant():
    volts = pd.Series([2.5, 2.5])
    codes = encode_voltages(volts)
    assert (codes == 0).all()
