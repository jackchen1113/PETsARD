"""Run workflow while forcing nullable string columns back to object dtype (so anonymeter's
reindex_like NA -> np.nan, not pd.NA), then print a privacy summary.
"""
import traceback
import warnings

import pandas as pd

from petsard.executor import Executor


def coerce_object(df):
    df = df.copy()
    for col in df.columns:
        if pd.api.types.is_string_dtype(df[col]):
            df[col] = df[col].astype(object)
        elif pd.api.types.is_bool_dtype(df[col]):
            df[col] = df[col].astype(object)
    return df


e = Executor(config="workflow.yaml")
try:
    e.run()
    print("[RUN] completed =", e.is_execution_completed())
except Exception as exc:
    print("[RUN] FAILED:", type(exc).__name__, str(exc)[:120])
    traceback.print_exc(limit=6)
