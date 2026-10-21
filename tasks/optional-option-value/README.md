# optional-option-value (medium)

**Bug:** [pallets/click#3084](https://github.com/pallets/click/issues/3084) (fixed by PR 3152). An option with `is_flag=False`, a `flag_value` and a `default` should accept zero or one value, but bare `--name` errors with "requires an argument". The fix is in `src/click/core.py` (`Option` init).

**Judged by:** the original suite must still pass, and `test_regression.py` must pass. It checks omitted, bare, `--opt value` and `--opt=value` for a string and an int option, that an invalid int still exits 2 with "Invalid value", and that a normal required-value option still errors without an argument.

## Files

- `prompt.md`: the task text given to the model (bug description, reproducer, constraints).
- `reference.patch`: the upstream fix, used only by `eval.py validate` to prove the task is solvable. Never shown to the model.
- `test_regression.py`: withheld grading tests, copied into the workspace only after the model finishes.
