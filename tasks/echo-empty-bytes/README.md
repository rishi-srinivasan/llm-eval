# echo-empty-bytes (small)

**Bug:** [pallets/click#3487](https://github.com/pallets/click/issues/3487) (fixed by PR 3493). `click.echo(b"", nl=True)` to a binary stream raises `TypeError` because empty bytes are falsy and `out or ""` swaps them for a `str`. The fix is in `src/click/utils.py`.

**Judged by:** the original suite must still pass, and `test_regression.py` must pass. It checks that `b""`, `bytearray()`, and non-empty bytes/bytearray write correctly to a `BytesIO` with and without a newline, and that `None`, `""` and text still behave as before on a `StringIO`.

## Files

- `prompt.md`: the task text given to the model (bug description, reproducer, constraints).
- `reference.patch`: the upstream fix, used only by `eval.py validate` to prove the task is solvable. Never shown to the model.
- `test_regression.py`: withheld grading tests, copied into the workspace only after the model finishes.
