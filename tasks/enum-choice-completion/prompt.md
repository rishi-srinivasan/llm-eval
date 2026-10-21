Fix shell completion for Enum-valued Choice parameters.

Reproducer:
    from enum import Enum
    import click
    class Mode(Enum):
        fast = "speed"
        safe = "careful"
    choice = click.Choice(Mode)
    ctx = click.Context(click.Command("demo"))
    print([item.value for item in choice.shell_complete(ctx, None, "")])

Completion produces names such as Mode.fast, but the parser accepts fast.
Every suggested value must be accepted by the corresponding Choice.
Preserve prefix filtering, case-insensitive behavior and ordinary string
choices. Respect a Choice subclass's normalization behavior.

Work only on this bug. You may inspect source, run existing tests and add tests.
Keep compatibility with existing behavior outside this bug. Do not install
packages or access the internet. The environment is already prepared.
Run tests with: python -m pytest -q
The evaluator grades production changes against untouched original tests and
additional behavioral tests. Do not modify test configuration or dependencies.
Stop when the fix is complete and summarize what you changed and tested.
