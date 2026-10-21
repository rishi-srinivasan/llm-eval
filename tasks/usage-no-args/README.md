# usage-no-args (small)

**Bug:** [pallets/click#3360](https://github.com/pallets/click/issues/3360) (fixed by PR 3434). `HelpFormatter.write_usage("program")` with no arguments emits a blank line instead of `Usage: program`. The fix is in `src/click/formatting.py`.

**Judged by:** the original suite must still pass, and `test_regression.py` must pass. It checks that no-args output equals the with-args output minus the arguments (no trailing space), across default and custom prefixes and indents 0, 2 and 8, plus the exact default strings.

## Files

- `prompt.md`: the task text given to the model (bug description, reproducer, constraints).
- `reference.patch`: the upstream fix, used only by `eval.py validate` to prove the task is solvable. Never shown to the model.
- `test_regression.py`: withheld grading tests, copied into the workspace only after the model finishes.
