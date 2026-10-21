Restore parameter-source information during parameter processing.

Reproducer:
    import click
    from click.testing import CliRunner
    class Source(click.ParamType):
        name = "source"
        def convert(self, value, param, ctx):
            return ctx.get_parameter_source(param.name)
    @click.command()
    @click.option("--value", type=Source(), default="fallback")
    def command(value):
        click.echo(repr(value))
    print(CliRunner().invoke(command, ["--value", "explicit"]).output)

The source is None during conversion. It must identify the actual value
source, including command-line arguments, environment variables and defaults.
Eager callbacks must also see their parameter's source. Preserve precedence
when multiple flag options share a destination: a losing option must not
replace the winning option's final source. Preserve existing public APIs.

Work only on this bug. You may inspect source, run existing tests and add tests.
Keep compatibility with existing behavior outside this bug. Do not install
packages or access the internet. The environment is already prepared.
Run tests with: python -m pytest -q
The evaluator grades production changes against untouched original tests and
additional behavioral tests. Do not modify test configuration or dependencies.
Stop when the fix is complete and summarize what you changed and tested.
