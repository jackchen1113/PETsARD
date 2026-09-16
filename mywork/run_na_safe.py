"""NA-proof inference-guess comparison for anonymeter inside PETsARD.

Drops the pytest's parsable-guess evaluation that anonymeter generates NA
for (see docs), replacing it with an NA-safe, dtype-agnostic elementwise
comparison that keeps anonymeter's *exact* semantics:

    - both guess & secret missing  -> match   (attacker "knew" it was missing)
    - one missing                  -> no match
    - regression  : |g-s|/|g| <= tolerance
    - categorical : g == s

This cannot raise "boolean value of NA is ambiguous" because we never let
pd.NA reach an ``==`` on a nullable array; we build explicit NA masks first.
"""
from types import ModuleType
from typing import Any

import numpy as np
import pandas as pd
import anonymeter.evaluators.inference_evaluator as _itiv

_orig_evaluate_inference_guesses = _itiv.evaluate_inference_guesses


def _na_safe_evaluate_inference_guesses(
    guesses: pd.Series,
    secrets: pd.Series,
    regression: bool,
    tolerance: float = 0.05,
) -> np.ndarray:
    g_obj = guesses.astype("object").to_numpy(dtype="object", na_value=None)
    s_obj = secrets.astype("object").to_numpy(dtype="object", na_value=None)

    g_nan = pd.isnull(g_obj)
    s_nan = pd.isnull(s_obj)

    # helper: returns a plain bool array, never pd.NA — safe for any dtype
    def _cmp(vals_l, vals_r):
        return vals_l == vals_r  # elementwise on object ndarray

    if regression:
        g_num = pd.to_numeric(pd.Series(g_obj, dtype="object"), errors="coerce").to_numpy()
        s_num = pd.to_numeric(pd.Series(s_obj, dtype="object"), errors="coerce").to_numpy()
        with np.errstate(divide="ignore", invalid="ignore"):
            rel = np.abs(g_num - s_num) / (np.abs(g_num) + 1e-12)
        value_match = rel <= tolerance
        value_match = value_match & ~np.isnan(rel)
        value_match = value_match & ~np.isnan(g_num) & ~np.isnan(s_num)
    else:
        value_match = _cmp(g_obj, s_obj)

    value_match = value_match & ~g_nan & ~s_nan
    nan_match = g_nan & s_nan

    return np.logical_or(nan_match, value_match)


_itiv.evaluate_inference_guesses = _na_safe_evaluate_inference_guesses

from petsard.executor import Executor  # noqa: E402

e = Executor(config="workflow.yaml")
try:
    e.run()
    print("RUN completed:", e.is_execution_completed(), flush=True)
except Exception as exc:  # noqa: B902
    import traceback

    traceback.print_exc(limit=8)
finally:
    _itiv.evaluate_inference_guesses = _orig_evaluate_inference_guesses
