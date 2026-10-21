# resource-exception (larger)

**Bug:** [pallets/click#2447](https://github.com/pallets/click/issues/2447) (fixed by PR 3058). `Context.__exit__` closes the exit stack without exception info, so resources from `ctx.with_resource()` get `(None, None, None)` even when the block raised, and can't see or suppress the error. The fix is in `src/click/core.py` (`Context.__exit__` / `close`).

**Judged by:** the original suite must still pass, and `test_regression.py` must pass. It checks that the real exception type, instance and traceback are forwarded; that a suppressing resource swallows the error and later-unwound resources then see no exception; that cleanup runs in reverse order; and that nested contexts, explicit `close()` and reuse of a closed context behave as before.

## Files

- `prompt.md`: the task text given to the model (bug description, reproducer, constraints).
- `reference.patch`: the upstream fix, used only by `eval.py validate` to prove the task is solvable. Never shown to the model.
- `test_regression.py`: withheld grading tests, copied into the workspace only after the model finishes.
