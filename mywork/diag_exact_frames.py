"""Dump the exact dataframes anonymeter's InferenceEvaluator receives in the pipeline, then
re-run the SAME anonymeter evaluate() standalone on those exact frames to see if it reproduces."""
from anonymeter.evaluators.inference_evaluator import InferenceEvaluator
from petsard.executor import Executor

captured = {}


def saving_init(self, ori, syn, aux_cols, secret, regression=False, n_attacks=500, control=None, n_jobs=-2, inference_model=None):
    captured["ori"] = ori.copy()
    captured["syn"] = syn.copy()
    captured["control"] = None if control is None else control.copy()
    captured["aux"] = list(aux_cols)
    captured["secret"] = secret
    return orig_init(self, ori, syn, aux_cols, secret, regression=regression, n_attacks=n_attacks, control=control, n_jobs=n_jobs, inference_model=inference_model)


orig_init = InferenceEvaluator.__init__
InferenceEvaluator.__init__ = saving_init

e = Executor(config="workflow.yaml")
try:
    e.run()
except Exception:
    pass

InferenceEvaluator.__init__ = orig_init

# Now standalone reproduce against the EXACT captured frames
print("captured index:", type(captured["ori"].index))
print("ori idx head:", captured["ori"].index[:5].tolist())
print("syn idx head:", captured["syn"].index[:5].tolist())
print("control idx head:", None if captured["control"] is None else captured["control"].index[:5].tolist())
print("marital NA ori/syn/control:",
      int(captured["ori"]["marital_status"].isna().sum()),
      int(captured["syn"]["marital_status"].isna().sum()),
      int(captured["control"]["marital_status"].isna().sum()))

try:
    ev = InferenceEvaluator(
        ori=captured["ori"], syn=captured["syn"], aux_cols=captured["aux"],
        secret=captured["secret"], n_attacks=500, control=captured["control"],
        n_jobs=1)
    ev.evaluate(n_jobs=1)
    print("STANDALONE-REPRO OK", ev.risk().value)
except Exception as exc:
    print("STANDALONE-REPRO FAILED:", type(exc).__name__, str(exc)[:120])
