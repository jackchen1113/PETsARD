"""Trace _run_attack in anonymeter to find where syn[secret] gains NA."""
from petsard.executor import Executor

import anonymeter.evaluators.inference_evaluator as iev

_orig_ra = iev._run_attack


def patched_ra(target, syn, n_attacks, aux_cols, secret, n_jobs, naive, regression, inference_model=None):
    s = syn[secret] if secret in syn.columns else None
    print(
        f"[RA] naive={naive} aux={aux_cols} secret={secret} "
        f"target_idx({target.index.min()},{target.index.max()}) n={len(target)} "
        f"syn_secret_NA={int(s.isna().sum()) if s is not None else '?'} "
        f"syn_secret_dtype={s.dtype if s is not None else '?'} syn_idx({syn.index.min()},{syn.index.max()})",
        flush=True,
    )
    import inspect
    if naive:
        # baseline path: sample and reindex imitation (what anonymeter will do)
        tgts = target.sample(n_attacks, replace=False)
        g = syn.sample(n_attacks)[secret]
        g2 = g.reindex_like(tgts)
        print(f"[RA] baseline-sample NA={int(g.isna().sum())} reindex_like NA={int(g2.isna().sum())}", flush=True)
    return _orig_ra(
        target=target, syn=syn, n_attacks=n_attacks, aux_cols=aux_cols, secret=secret,
        n_jobs=n_jobs, naive=naive, regression=regression, inference_model=inference_model,
    )


iev._run_attack = patched_ra

e = Executor(config="workflow.yaml")
try:
    e.run()
finally:
    iev._run_attack = _orig_ra
