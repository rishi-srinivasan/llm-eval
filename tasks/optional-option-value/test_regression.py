import click
import pytest
from click.testing import CliRunner


@pytest.mark.parametrize("type_, default, flag, explicit", [(str, "fallback", "bare", "alice"), (int, 0, 1, "7")])
@pytest.mark.parametrize("form", ["absent", "bare", "explicit", "equals"])
def test_optional_values(type_, default, flag, explicit, form):
    @click.command()
    @click.option("--value", is_flag=False, flag_value=flag, default=default, type=type_)
    def command(value):
        click.echo(value)

    args = {"absent": [], "bare": ["--value"], "explicit": ["--value", explicit], "equals": [f"--value={explicit}"]}
    expected = {"absent": default, "bare": flag, "explicit": explicit, "equals": explicit}
    result = CliRunner().invoke(command, args[form])
    assert result.exit_code == 0, result.output
    assert result.output == f"{expected[form]}\n"


def test_invalid_integer_and_required_value():
    @click.command()
    @click.option("--value", is_flag=False, flag_value=1, default=0, type=int)
    @click.option("--required-value", type=str)
    def command(**kwargs):
        pass

    runner = CliRunner()
    invalid = runner.invoke(command, ["--value", "nope"])
    assert invalid.exit_code == 2
    assert "Invalid value" in invalid.output
    missing = runner.invoke(command, ["--required-value"])
    assert missing.exit_code == 2
    assert "requires an argument" in missing.output
