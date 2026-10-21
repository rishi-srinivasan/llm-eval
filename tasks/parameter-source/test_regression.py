import click
import pytest
from click.core import ParameterSource
from click.testing import CliRunner


@pytest.mark.parametrize("origin", ["default", "environment", "commandline", "default_map"])
@pytest.mark.parametrize("eager", [False, True])
def test_source_during_processing(origin, eager):
    observations = []

    class Source(click.ParamType):
        name = "source"

        def convert(self, value, param, ctx):
            observations.append(ctx.get_parameter_source(param.name))
            return value

    def callback(ctx, param, value):
        observations.append(ctx.get_parameter_source(param.name))
        return value

    @click.command()
    @click.option("--value", default="fallback", envvar="EVAL_VALUE", type=Source(), callback=callback, is_eager=eager)
    def command(value):
        observations.append(click.get_current_context().get_parameter_source("value"))

    args = ["--value", "cli"] if origin == "commandline" else []
    env = {"EVAL_VALUE": "env" if origin == "environment" else None}
    defaults = {"value": "mapped"} if origin == "default_map" else {}
    result = CliRunner().invoke(command, args, env=env, default_map=defaults)
    assert result.exit_code == 0, result.exception
    expected = ParameterSource[origin.upper()]
    assert observations == [expected, expected, expected]


@pytest.mark.parametrize("reverse", [False, True])
def test_shared_destination_retains_winning_source(reverse):
    options = [click.Option(["--fast", "mode"], flag_value="fast"), click.Option(["--safe", "mode"], flag_value="safe", default=True)]
    if reverse:
        options.reverse()
    seen = []

    def callback(mode):
        seen.append((mode, click.get_current_context().get_parameter_source("mode")))

    command = click.Command("demo", params=options, callback=callback)
    result = CliRunner().invoke(command, ["--fast"])
    assert result.exit_code == 0, result.exception
    assert seen == [("fast", ParameterSource.COMMANDLINE)]
