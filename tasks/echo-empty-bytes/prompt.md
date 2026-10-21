Fix Click's handling of empty binary output.

Reproducer:
    import io, click
    stream = io.BytesIO()
    click.echo(b"", file=stream, nl=True)

This raises TypeError instead of writing b"\n". Empty bytes and bytearrays
must work with and without a newline. Preserve nonempty binary output,
text output, and the existing behavior of None. Do not change the public API.

Work only on this bug. You may inspect source, run existing tests and add tests.
Keep compatibility with existing behavior outside this bug. Do not install
packages or access the internet. The environment is already prepared.
Run tests with: python -m pytest -q
The evaluator grades production changes against untouched original tests and
additional behavioral tests. Do not modify test configuration or dependencies.
Stop when the fix is complete and summarize what you changed and tested.
