"""Run PETsARD citizens workflow with an NA-safe anonymeter inference comparison.

Why this wrapper exists
-----------------------
PETsARD hands Anonymeter frames where the *naive baseline* attack builds
``guesses = syn.sample(n)[secret]`` then ``guesses.reindex_like(targets)``.
Because the pipeline's ``ori`` (train 0..7999), ``syn`` (0..9999) and
``control`` (0..1999) live in *different* index-label spaces, the reindex
introduces missing values into ``guesses``. Those missing values are
``pd.NA`` (pandas nullable ``string`` dtype), and anonymeter's
``guesses_np == secrets_np`` then raises
``TypeError: boolean value of NA is ambiguous``.

This wrapper replaces anonymeter's ``evaluate_inference_guesses`` with a
*dtype-safe* equivalent that behaves exactly like the original for all
non-missing values, and treats an NA guess as a failed attack (unless the
secret is also NA, which anonymeter already means as a match). It does not
alter any PETsARD or anonymeter source files.
"""
import warnings

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

from anonymeter.evaluators.inference_evaluator import (  # noqa: E402
    evaluate_inference_guesses as _orig_evaluate_inference_guesses,
)
from petsard.executor import Executor  # noqa: E402


def _na_safe_evaluate_inference_guesses(
    guesses: pd.Series,
    secrets: pd.Series,
    regression: bool,
    tolerance: float = 0.05,
) -> np.ndarray:
    """NA-safe version of anonymeter's evaluate_inference_guesses.

    Identical semantics to the original except that missing values held as
    ``pd.NA`` in nullable columns are compared safely:
    - both missing  -> guess is correct (anonymeter's ``nan_match``)
    - only one NNA  -> guess is incorrect
    """
    g = guesses.astype("object").to_numpy()
    s = guesses  # placeholder to avoid unused warning
    s = secrets.astype("object").to_numpy()

    g_na = pd.isnull(g)
    s_na = pd.isnull(s)

    if regression:
        g_num = pd.to_numeric(guesses, errors="coerce").to_numpy()
        s_num = pd.to_numeric(secrets, errors="coerce").to_numpy()
        with np.errstate(divide="ignore", invalid="ignore"):
            rel = np.abs(g_num - s_num) / (np.abs(g_num) + 1e-12)
        value_match = rel <= tolerance
        value_match = value_match & ~np.isnan(rel) & ~g_na & ~s_na
    else:
        value_match = (g == s) & ~g_na & ~s_na

    nan_match = g_na & s_na

    return np.logical_or(nan_match, value_match)


def main() ->