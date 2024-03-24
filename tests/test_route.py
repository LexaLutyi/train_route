import train_route.route as tr

def test_route():
    xs = [1, 2, 3]
    ys = [1, 2, 3]
    ts = [1, 2, 3]
    route = tr.Route(ts, xs, ys)
    assert isinstance(route, tr.Route)
    assert route.is_outside(0)
    assert not route.is_outside(1)
    assert route.find_next_point(2.5, 0) == 2
    assert route.find_next_point(0.5, 0) == 0
    assert route.find_next_point(3.5, 0) == 3

def test_position():
    xs = [1, 1, 2, 3, 3]
    ys = [0, 0, 1, 1, 1]
    ts = [0, 1, 2, 3, 4]
    route = tr.Route(ts, xs, ys)
    train = tr.Train(route)
    # consequence t
    assert train.state(0.) == (1, 0, 45)
    assert train.state(0.5) == (1, 0, 45)
    assert train.state(1.) == (1, 0, 45)
    assert train.state(1.5) == (1.5, 0.5, 45)
    assert train.state(2.) == (2, 1, 45)
    assert train.state(2.5) == (2.5, 1.0, 0)
    assert train.state(3.) == (3, 1, 0)
    assert train.state(3.5) == (3, 1, 0)
    assert train.state(4) == (3, 1, 0)
    # random t
    assert train.state(2.) == (2, 1, 45)
    assert train.state(3.5) == (3, 1, 0)
    # outside t
    assert train.state(-1) is None
    assert train.state(100) is None
