import click
import pytest


def usage(args, prefix, indent):
    formatter = click.HelpFormatter(width=80)
    formatter.current_indent = indent
    formatter.write_usage("demo", args=args, prefix=prefix)
    return formatter.getvalue()


@pytest.mark.parametrize("prefix", [None, "Run: "])
@pytest.mark.parametrize("indent", [0, 2, 8])
def test_no_args_is_prefix_line_without_trailing_space(prefix, indent):
    with_args = usage("[OPTIONS]", prefix, indent)
    assert with_args.endswith(" [OPTIONS]\n")
    assert usage("", prefix, indent) == with_args.removesuffix(" [OPTIONS]\n") + "\n"


def test_default_output():
    assert usage("", None, 0) == "Usage: demo\n"
    assert usage("[OPTIONS]", None, 0) == "Usage: demo [OPTIONS]\n"
