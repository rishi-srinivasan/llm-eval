# enum-choice-completion (medium)

**Bug:** [pallets/click#3015](https://github.com/pallets/click/issues/3015) (fixed by PR 3471). `Choice` built from an `Enum` suggests `Mode.fast` in shell completion (via `str()`), but the parser only accepts `fast`. The fix is in `src/click/types.py`.

**Judged by:** the original suite must still pass (except one test deselected in `tasks.json`), and `test_regression.py` must pass. It checks that every suggestion round-trips through `convert()`, for enum and string choices, case-sensitive and not, with prefix filtering, and that a `Choice` subclass overriding `normalize_choice` is respected.

## Files

- `prompt.md`: the task text given to the model (bug description, reproducer, constraints).
- `reference.patch`: the upstream fix, used only by `eval.py validate` to prove the task is solvable. Never shown to the model.
- `test_regression.py`: withheld grading tests, copied into the workspace only after the model finishes.
