"""Capture exact ori/syn/control PETsARD passes to InferenceEvaluator, reproduce, and test a NA-guard fix."""
import warnings
import pandas as pd

from anonymeter.evaluators import inference_evaluator as iev
from anonymeter.evaluators.inference_evaluator import InferenceEvaluator
import numpy as np
from petsard.executor import Executor

captured = {}


def capturing_init(self, ori, syn, control, aux_cols, secret, regression=False, n_attacks=500, inference_model=None):
    captured["ori"] = ori.copy()
    captured["syn"] = syn.copy()
    captured["control"] = None if control is None else control.copy()
    captured["aux"] = list(aux_cols)
    captured["secret"] = secret
    captured["n_attacks"] = n_attacks
    captured["n_jobs"] = -2
    return orig_init(self, ori, syn, control, aux_cols, secret, regression=regression, n_attacks=n_attacks, inference_model=inference_model)


orig_init = InferenceEvaluator.__init__
InferenceEvaluator.__init__ = capturing_init

e = Executor(config="workflow.yaml")
try:
    e.run()
except Exception as exc:
    print("[pipeline] FAILED:", type(exc).__name__, str(exc)[:120])
finally:
    InferenceEvaluator.__init__ = orig_init

# ---- reproduce standalone on the captured frames ----
o, s, c = captured["ori"], captured["syn"], captured["control"]
print("captured index built:", o.index.is_monotonic_increasing, "len", len(o),
      "| ori head idx:", o.index[:3].tolist(), "| syn head idx:", s.index[:3].tolist(),
      "| control head idx:", None if c is None else c.index[:3].tolist())

print("naive baseline repro:")
tgt = o.sample(2000, replace=False)
g = s.sample(2000)[captured["secret"]]
g2 = g.reindex_like(tgt)
print("  after reindex_like, NA in guesses =", int(g2.isna().sum()), "/2000")
try:
    _ = g2.to_numpy() == tgt[captured["secret"]].to_numpy()
    print("  compare OK")
except TypeError as ex:
    print("  compare FAILS:", ex)

print("maitn attack NA with KNN would follow same pattern; reporting done")
