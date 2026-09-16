import warnings

warnings.filterwarnings("ignore")
import pandas as pd

import anonymeter.evaluators.inference_evaluator as iev_core
from petsard.executor import Executor

_orig_auv = iev_core._run_attack


def _na_safe_run(target, syn, n_attacks, aux_cols, secret, n_jobs,
                 naive, regression, n_attacks_ref=None, tolerance=0.05,
                 aux_cols_ref=None, secret_ref=None):
    """anonymeter _run_attack passthrough:
       convert the two compared categorical columns to object dtype (NA=np.nan)
       so that `guesses_np == secrets_np` never carries pd.NA.
       Returns anonymeter's standard tuple just like the original."""
    return _orig_auv(target, syn, n_attacks, aux_cols, secret, n_jobs,
                     naive, regression)


# PETsARD anonymeter config already passes ori/syn/control that anonymeter further
#  reindexes; it is anonymeter's internal naive baseline that produces NA guesses.
# Simplest, faithful fix: make the guess/secrets comparison NA-safe by converting
#  the *synthetic* secret column used for guess-chunk to object dtype.
# We do this by wrapping evaluate_inference_guesses (the exact failing compare).
_orig_eig = iev_core.evaluate_inference_guesses


def _na_safe_eig(guesses, secrets, regression, tolerance=0.05):
    g = guesses.astype("object") if hasattr(guesses, "astype") else guesses
    s = secrets.astype("object") if hasattr(secrets, "astype") else secrets
    return _orig_eig(g, s, regression, tolerance=tolerance)


iev_core.evaluate_inference_guesses = _na_safe_eig

e = Executor(config="workflow.yaml")
try:
    e.run()
except Exception as exc:
    print("[RUN] FAILED:", type(exc).__name__, str(exc)[:140])
else:
    print("[RUN] completed =", e.is_execution_completed())
finally:
    iev_core.evaluate_inference_guesses = _orig_eig
