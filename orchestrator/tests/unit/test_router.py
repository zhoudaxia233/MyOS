from router import route_task


def test_route_decision():
    assert route_task("run decision audit") == "decision"
