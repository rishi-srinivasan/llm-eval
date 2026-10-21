Fix usage formatting for programs without arguments.

Reproducer:
    import click
    formatter = click.HelpFormatter()
    formatter.write_usage("program")
    print(repr(formatter.getvalue()))

The result is a blank line. It should be "Usage: program\n".
Preserve the configured prefix, indentation and normal argument formatting.
Do not add trailing separator whitespace when arguments are absent.

Work only on this bug. You may inspect source, run existing tests and add tests.
Keep compatibility with existing behavior outside this bug. Do not install
packages or access the internet. The environment is already prepared.
Run tests with: python -m pytest -q
The evaluator grades production changes against untouched original tests and
additional behavioral tests. Do not modify test configuration or dependencies.
Stop when the fix is complete and summarize what you changed and tested.
