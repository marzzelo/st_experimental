import os, sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import pandas as pd

from pages.Calibraciones import CalibrationApp


def test_generar_plantilla_excel():
    """Comprueba que la plantilla Excel tiene las columnas correctas y una fila de ceros."""
    app = CalibrationApp()
    output = app._generar_plantilla_excel()
    output.seek(0)
    df = pd.read_excel(output)
    expected_cols = [
        'PAT1_0', 'DUT1_0', 'PAT1_R', 'DUT1_R',
        'PAT2_0', 'DUT2_0', 'PAT2_R', 'DUT2_R',
        'PAT3_0', 'DUT3_0', 'PAT3_R', 'DUT3_R'
    ]
    assert df.columns.tolist() == expected_cols
    assert (df.iloc[0] == 0).all()
