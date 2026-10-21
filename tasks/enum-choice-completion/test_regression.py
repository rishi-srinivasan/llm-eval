from enum import Enum

import click
import pytest


class Mode(Enum):
    FAST = "speed"
    SAFE = "careful"


@pytest.mark.parametrize("case_sensitive", [True, False])
@pytest.mark.parametrize("enum", [True, False])
def test_completion_round_trip(case_sensitive, enum):
    choices = Mode if enum else ["FAST", "SAFE"]
    choice = click.Choice(choices, case_sensitive=case_sensitive)
    ctx = click.Context(click.Command("demo"))
    items = choice.shell_complete(ctx, None, "")
    # case of suggestions is unspecified when case-insensitive
    assert [item.value.casefold() for item in items] == ["fast", "safe"]
    if case_sensitive:
        assert [item.value for item in items] == ["FAST", "SAFE"]
    assert [choice.convert(item.value, None, ctx) for item in items] == list(choices)
    prefix = "F" if case_sensitive else "f"
    assert [item.value.casefold() for item in choice.shell_complete(ctx, None, prefix)] == ["fast"]
    assert choice.shell_complete(ctx, None, "missing") == []


def test_custom_normalization():
    class DashedChoice(click.Choice):
        def normalize_choice(self, choice, ctx):
            return super().normalize_choice(choice, ctx).replace("_", "-")

    choice = DashedChoice(["fast_mode", "safe_mode"])
    ctx = click.Context(click.Command("demo"))
    items = choice.shell_complete(ctx, None, "fast-")
    assert [item.value for item in items] == ["fast-mode"]
    assert choice.convert(items[0].value, None, ctx) == "fast_mode"
