Restore options that accept zero or one explicit values.

Reproducer:
    import click
    from click.testing import CliRunner
    @click.command()
    @click.option("--name", is_flag=False, flag_value="Flag", default="Default")
    def command(name):
        click.echo(name)
    print(CliRunner().invoke(command, ["--name"]).output)

The bare option incorrectly requires an argument. An omitted option should
produce Default, --name alone should produce Flag, and --name Alice should
produce Alice. Preserve explicit integer conversion, invalid-value errors,
and normal required-value options. Do not change the public API.

Work only on this bug. You may inspect source, run existing tests and add tests.
Keep compatibility with existing behavior outside this bug. Do not install
packages or access the internet. The environment is already prepared.
Run tests with: python -m pytest -q
The evaluator grades production changes against untouched original tests and
additional behavioral tests. Do not modify test configuration or dependencies.
Stop when the fix is complete and summarize what you changed and tested.
