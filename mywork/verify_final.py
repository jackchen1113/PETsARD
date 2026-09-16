"""Final clean verification run with the NA-safe anonymeter patch.

Applies the NA-safe wrapper (anonymeter's evaluate_inference_guesses), runs
the full workflow, then prints a concise summary of every saved artifact
and the anonymeter privacy-risk numbers from the reporter report.
"""
import warnings

warnings.filterwarnings("ignore")

import anonymeter.evaluators.inference_evaluator as _iev  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from anonymeter.evaluators.inference_evaluator import (  # noqa: E402
    evaluate_inference_guesses as _iev_orig,
)

_VERBOSE = False


def _na_safe_evaluate_inference_guesses(guesses, secrets, regression, tolerance=0.05):
    """NA-safe version of anonymeter's evaluate_inference_guesses.

    anonymeter injects missing values into guesses via reindex when the
    attack-target and synthetic frames do not share index labels; the
    nullable `string` dtype then makes `guesses_np == secrets_np` raise
    "boolean value of NA is ambiguous". We compare after converting both to
    plain object arrays where a missing value cannot be a successful guess
    (a missing secret also never matches a value), which mirrors anonymeter's
    intended nan_match semantics (both-NaN -> match) without the crash.
    """
    g = guesses.astype("object").to_numpy()
    s = secrets.astype("object").to_numpy()
    g_nan = pd.isna(g)
    s_nan = pd.isna(s)

    if regression:
        g_num = pd.to_numeric(guesses, errors="coerce").astype("float64").to_numpy()
        s_num = pd.to_numeric(secrets, errors="coerce").astype("float64").to_numpy()
        with np.errstate(divide="ignore", invalid="ignore"):
            rel = np.abs(g_num - s_num) / (np.abs(g_num) + 1e-12)
            value_match = rel <= tolerance
    else:
        gobj = pd.Series(g, dtype="object")
        sobj = pd.Series(s, dtype="object")
        value_match = (gobj.to_numpy() == sobj.to_numpy())

    nan_match = g_nan & s_nan
    value_match = value_match & ~g_nan & ~s_nan

    return pd.Series(np.logical_or(nan_match, value_match), index=...[:len(value_match)]) if False else np.logical_or(nan_match, value_match)


_iev.evaluate_inference_guesses = _na_safe_evaluate_inference_guesses

from petsard.executor import Executor  # noqa: E402
from petsard.loader import Loader  # noqa: E402
from petsard.reporter import Reporter  # noqa: E402

e = Executor(config="workflow.yaml")
e.run()
print("execution_completed =", e.is_execution_completed())

# Summarize anonymeter part of the saved PETsARD report
import glob  # noqa: E402

rep = [p for p in glob.glob("petsard_Reporter[global].csv")]
if rep:
    df = pd.read_csv(rep[0], encoding="utf-8")
    print(df.to_string(index=False))

_iev.evaluate_inference_guesses = _iev_orig
