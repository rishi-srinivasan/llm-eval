Forward exception information to resources managed by Click contexts.

Reproducer:
    import click
    class Resource:
        def __enter__(self):
            return self
        def __exit__(self, kind, error, traceback):
            print(kind, error, traceback)
    ctx = click.Context(click.Command("demo"))
    with ctx:
        ctx.with_resource(Resource())
        raise ValueError("failed")

The resource receives three None values, incorrectly signaling success.
Forward the actual exception type, instance and traceback. Respect a resource
that suppresses the exception. Preserve normal exits, reverse cleanup order,
explicit close(), nested contexts and reuse of a closed context. A suppressed
exception must not be forwarded to resources unwound after its suppression.

Work only on this bug. You may inspect source, run existing tests and add tests.
Keep compatibility with existing behavior outside this bug. Do not install
packages or access the internet. The environment is already prepared.
Run tests with: python -m pytest -q
The evaluator grades production changes against untouched original tests and
additional behavioral tests. Do not modify test configuration or dependencies.
Stop when the fix is complete and summarize what you changed and tested.
