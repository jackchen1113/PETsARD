"""Dump the exact ori/syn/control that PETsARD passes to the Inference evaluator."""
from petsard.executor import Executor

import petsard.evaluator.anonymeter as PEA

_orig_ud = PEA.Anonymeter.update_data


def patched(self, data):
    tag = PEA.AnonymeterMap(self.eval_method_code).name if self.eval_method_code is not None else "?"
    if "INFERENCE" in tag:
        for name in ("ori", "syn", "control"):
            df = data[name]
            df.to_csv(f"exact_{name}.csv", index=False, encoding="utf-8")
            print(f"[DUMP] {name} shape={df.shape} idx=[{df.index.min()},{df.index.max()}] n={len(df.index)}")
    return _orig_ud(self, data)


PEA.Anonymeter.update_data = patched

e = Executor(config="workflow.yaml")
try:
    e.run()
except Exception as exc:
    print("[FAIL]", type(exc).__name__)
finally:
    PEA.Anonymeter.update_data = _orig_ud