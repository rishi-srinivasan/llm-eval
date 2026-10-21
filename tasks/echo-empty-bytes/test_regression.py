import io

import click
import pytest


@pytest.mark.parametrize("value", [b"", bytearray(), b"hello", bytearray(b"hello")])
@pytest.mark.parametrize("newline", [True, False])
def test_binary(value, newline):
    stream = io.BytesIO()
    expected = bytes(value) + (b"\n" if newline else b"")  # before echo: it may mutate a bytearray
    click.echo(value, file=stream, nl=newline)
    assert stream.getvalue() == expected


@pytest.mark.parametrize("value, expected", [(None, ""), ("", ""), ("hello", "hello")])
@pytest.mark.parametrize("newline", [True, False])
def test_text(value, expected, newline):
    stream = io.StringIO()
    click.echo(value, file=stream, nl=newline)
    assert stream.getvalue() == expected + ("\n" if newline else "")
