import warnings
import pandas as pd

from anonymeter.evaluators.inference_evaluator import InferenceEvaluator
from petsard.executor import Executor

captured: dict = {}
_orig_init = InferenceEvaluator.__init__


def capturing_init(self, ori, syn, aux_cols, secret, regression=False, n_attacks=500, control=None, n_jobs=-2, inference_model=None):
    captured["ori"] = ori.copy()
    captured["syn"] = syn.copy()
    captured["control"] = None if control is None else control.copy()
    captured["aux"] = list(aux_cols)
    captured["secret"] = secret
    return _orig_init(self, ori, syn, aux_cols, secret, regression=regression, n_attacks=n_attacks, control=control, n_jobs=n_jobs, inference_model=inference_model)


InferenceEvaluator.__init__ = capturing_init
e = Executor(config="workflow.yaml")
try:
    e.run()
except Exception as exc:
    print("[PIPELINE] FAILED:", type(exc).__name__, str(exc)[:90], flush=True)
finally:
    InferenceEvaluator.__init__ = _orig_init


def convert_str_to_obj(df):
    df = df.copy()
    for col in df.columns:
        if pd.api.types.is_string_dtype(df[col]) and not pd.api.types.is_object_dtype(df[col]):
            df[col] = df[col].astype(object)
    return df


def run(tag, ori, syn, control, aux, secret):
    try:
        ev = InferenceEvaluator(ori=ori, syn=syn, aux_cols=aux, secret=secret, control=control, n_attacks=500)
        ev.evaluate(n_jobs=1)
        r = ev.risk()
        print(f"[{tag}] OK attack={round(ev._n_success / max(ev._n_attacks_ori, 1), 4)} "
              f"control_rate~{round(ev._n_control / max(ev._n_attacks_control, 1), 4) if ev._n_attacks_control > 0 else 'NA'} "
              f"| risk={round(r.value, 4)} [{round(r.ci[0], 4)},{round(r.ci[1], 4)}]", flush=True)
    except Exception as exc:
        print(f"[{tag}] FAILED:", type(exc).__name__, str(exc)[:110], flush=True)


if captured:
    o, s, c = captured["ori"], captured["syn"], captured["control"]
    aux, sec = captured["aux"], captured["secret"]
    print("[frame] ori/syn/control:", o.shape, s.shape, c.shape,
          "dtypes marital:", o["marital_status"].dtype, "| aux dtypes:", [str(o[x].dtype) for x in aux], flush=True)
    run("AS-IS", o, s, c, aux, sec)
    run("OBJ-DTYPE", convert_str_to_obj(o), convert_str_to_obj(s), None if c is None else convert_str_to_obj(c), aux, sec)
else:
    print("nothing captured?!", flush=True)
