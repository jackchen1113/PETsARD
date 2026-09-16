"""Workflow.yaml end-to-end run with an NA-proof anonymeter inference patch.

Why this wrapper is needed
--------------------------
Anonymeter's *naive* inference baseline attack samples synthetic rows
(``syn.sample(n_attacks)[secret]``) and then aligns them onto the targets
sampled from ``ori`` via ``guesses.reindex_like(targets)``. PETsARD feeds it
three frames whose index label-spaces do not fully overlap (``ori`` = train
subset of the original data with *scattered* original indices, ``syn`` =
synthetic RangeIndex 0..n, ``control`` = held-out subset), so the ``reindex``
fills many guess values with missing entries. anonymeter then compares
``guesses_np == secrets_np`` elementwise; when the columns use pandas
nullable ``string`` dtype the missing entry is ``pd.NA`` and that elementwise
comparison raises ``TypeError: boolean value of NA is ambiguous``.

The wrapper below does **exactly** what anonymeter's original
``evaluate_inference_guesses`` intends (see its ``nan_match`` note: a guess
that cannot be evaluated counts as a failed attack unless the secret is also
missing, in which case both-missing counts as a match), but materialises the
missing values as ``np.nan`` *before* the array comparison so no ``pd.NA``
can ever reach an elementwise ``==``. Numeric (regression) columns keep the
relative-difference semantics of anonymeter, with the tolerance check applied
only to non-missing pairs.
"""
import warnings

warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd

import anonymeter.evaluators.inference_evaluator as _infeval_module

_ORIG_EVALUATE_INFERENCE_GUESSES = _infeval_module.evaluate_inference_guesses


def _na_safe_evaluate_inference_guesses(
    guesses: pd.Series,
    secrets: pd.Series,
    regression: bool,
    tolerance: float = 0.05,
) -> np.ndarray:
    """NA-proof, dtype-agnostic version of anonymeter's per-guess compare.

    Parameters
    ----------
    guesses : pd.Series
        Attacker guesses for each target (may contain missing values from
        anonymeter's reindex alignment).
    secrets : pd.Series
        True secret values.
    regression : bool
        Whether the secret is numeric (True) or categorical (False).
    tolerance : float, default 0.05
        Relative-difference tolerance for regression secrets.

    Returns
    -------
    np.ndarray
        Elementwise boolean “attack succeeded” flags.

    Notes
    -----
    Missing handling mirrors anonymeter's ``nan_match``:
      * guess missing AND secret missing  -> match
        (the attacker's uncertainty coincides with an actually-missing value)
      * guess missing, secret present     -> no match
      * guess present,  secret missing    -> no match
    """
    g = guesses.to_numpy(dtype="object", na_value=np.nan)
    s = secrets.to_numpy(dtype="object", na_value=np.nan)

    g_nan = pd.isnull(g)
    s_nan = pd.isnull(s)

    if regression:
        g_num = pd.to_numeric(guesses, errors="coerce").astype("float64").to_numpy()
        s_num = pd.to_numeric(secrets, errors="coerce").astype("float64").to_numpy()
        with np.errstate(divide="ignore", invalid="ignore"):
            rel = np.abs(g_num - s_num) / (np.abs(g_num) + 1e-12)
        # tolerance test is meaningful only where both are real numbers
        value_match = (rel <= tolerance) & ~np.isnan(rel) & ~g_nan & ~s_nan
    else:
        value_match = (g == s) & ~g_nan & ~s_nan

    nan_match = g_nan & s_nan
    return np.logical_or(nan_match, value_match)


_infeval_module.evaluate_inference_guesses = _na_safe_evaluate_inference_guesses

from petsard.executor import Executor  # noqa: E402

e = Executor(config="workflow.yaml")
try:
    e.run()
    print("RUN completed =", e.is_execution_completed(), flush=True)
finally:
    _infeval_module.evaluate_inference_guesses = _ORIG_EVALUATE_INFERENCE_GUESSES
