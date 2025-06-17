import os, sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import pandas as pd

from pages.Arbitrary_Waveform_Script_Generator import validate_format


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
