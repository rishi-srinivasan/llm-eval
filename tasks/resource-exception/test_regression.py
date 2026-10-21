import click
import pytest


class Resource:
    def __init__(self, events, name, suppress=False):
        self.events, self.name, self.suppress = events, name, suppress

    def __enter__(self):
        return self

    def __exit__(self, kind, error, traceback):
        self.events.append((self.name, kind, error, traceback))
        return self.suppress


def test_exception_is_forwarded():
    events = []
    error = ValueError("failed")
    with pytest.raises(ValueError, match="failed"):
        with click.Context(click.Command("demo")) as ctx:
            ctx.with_resource(Resource(events, "resource"))
            raise error
    name, kind, received, traceback = events[0]
    assert (name, kind, received) == ("resource", ValueError, error)
    assert traceback is not None


def test_suppression_and_reverse_order():
    events = []
    with click.Context(click.Command("demo")) as ctx:
        ctx.with_resource(Resource(events, "outer"))
        ctx.with_resource(Resource(events, "inner", suppress=True))
        raise ValueError("handled")
    assert [event[0] for event in events] == ["inner", "outer"]
    assert events[0][1] is ValueError
    assert events[1][1:] == (None, None, None)


def test_normal_close_and_reuse():
    events = []
    ctx = click.Context(click.Command("demo"))
    with ctx:
        ctx.with_resource(Resource(events, "first"))
        with ctx:
            assert events == []
        assert events == []
    ctx.close()
    with ctx:
        ctx.with_resource(Resource(events, "second"))
    ctx.with_resource(Resource(events, "explicit"))
    ctx.close()
    assert events == [(name, None, None, None) for name in ["first", "second", "explicit"]]
