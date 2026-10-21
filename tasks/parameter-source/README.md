# parameter-source (larger)

**Bug:** [pallets/click#3458](https://github.com/pallets/click/issues/3458) (fixed by PR 3484). `ctx.get_parameter_source()` returns `None` while a parameter is being converted or its callback runs; the source was only recorded afterwards. It must be set earlier, yet a flag option that loses arbitration for a shared destination must not overwrite the winner's source. The fix is in `src/click/core.py` (`Parameter.handle_parse_result`).

**Judged by:** the original suite must still pass, and `test_regression.py` must pass. It checks that the type's `convert`, the callback and the command body all see the right source (default, environment, command line, default map), eager or not, and that with two flags sharing a destination, in either declaration order, the final source is the winner's `COMMANDLINE`.

## Files

- `prompt.md`: the task text given to the model (bug description, reproducer, constraints).
- `reference.patch`: the upstream fix, used only by `eval.py validate` to prove the task is solvable. Never shown to the model.
- `test_regression.py`: withheld grading tests, copied into the workspace only after the model finishes.
