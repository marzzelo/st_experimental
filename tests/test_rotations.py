import os, sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import pandas as pd
import io

from pages.Rotations import to_excel


def test_to_excel_roundtrip():
    """Verifica que to_excel escriba y lea sin modificar el DataFrame."""
    df = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
    excel_bytes = to_excel(df)
    read_df = pd.read_excel(io.BytesIO(excel_bytes))
    pd.testing.assert_frame_equal(read_df, df)
