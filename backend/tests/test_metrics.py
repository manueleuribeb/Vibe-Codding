import math
import pandas as pd
import sys
import pathlib

# ensure project root is on sys.path so `backend` package can be imported when running pytest
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from backend.main import _mape, _rmse, evaluate_methods


def test_mape_basic():
    y_true = pd.Series([100.0, 200.0])
    y_pred = pd.Series([110.0, 190.0])
    # (10/100 + 10/200)/2 * 100 = (0.1 + 0.05)/2 *100 = 7.5
    assert math.isclose(_mape(y_true, y_pred), 7.5, rel_tol=1e-6)


def test_rmse_basic():
    y_true = pd.Series([1.0, 2.0, 3.0])
    y_pred = pd.Series([2.0, 2.0, 4.0])
    expected = math.sqrt(((1.0**2) + (0.0**2) + (1.0**2)) / 3.0)
    assert math.isclose(_rmse(y_true, y_pred), expected, rel_tol=1e-6)


def test_evaluate_methods_output():
    # create a simple increasing series
    idx = pd.date_range('2025-01-01', periods=30)
    s = pd.Series([100 + i for i in range(30)], index=idx)
    res = evaluate_methods(s, horizon=5)
    assert 'best_method' in res
    assert 'mape' in res and 'rmse' in res
    assert isinstance(res['series'], list)
    assert len(res['series']) == 5