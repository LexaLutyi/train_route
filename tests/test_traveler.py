import train_route.traveler as tr
from train_route.rotation import spheric_rotation as rot

def test_segment():
    segment = tr.Segment(
        segment_id = 0,
        source = 0,
        target = 0,
        xs = [0, 1, 1],
        ys = [0, 0, 1]
    )

    assert segment.distance == 2
    assert segment.state(-0.01) is None
    assert segment.state(0) == {'x': 0, 'y': 0, 'rotation': 0}
    assert segment.state(0.5) == {'x': 0.5, 'y': 0, 'rotation': 0}
    assert segment.state(1) == {'x': 1, 'y': 0, 'rotation': 0}
    assert segment.state(1.5) == {'x': 1, 'y': 0.5, 'rotation': rot(1, 0, 1, 1)}
    assert segment.state(2) == {'x': 1, 'y': 1, 'rotation': rot(1, 0, 1, 1)}
    assert segment.state(segment.distance + 0.01) is None

    segment = tr.Segment(
        segment_id = 0,
        source = 0,
        target = 0,
        xs = [0, 0],
        ys = [0, 0]
    )
    assert segment.distance == 0
    assert segment.state(-0.01) is None
    assert segment.state(0) == {'x': 0, 'y': 0, 'rotation': None}
    assert segment.state(0.01) is None

def test_path():
    segment1 = tr.Segment(
        segment_id = 0,
        source = 0,
        target = 1,
        xs = [0, 1, 1],
        ys = [0, 0, 1]
    )

    segment2 = tr.Segment(
        segment_id = 1,
        source = 1,
        target = 1,
        xs = [1, 1],
        ys = [1, 1]
    )

    segment3 = tr.Segment(
        segment_id = 2,
        source = 1,
        target = 2,
        xs = [1, 2, 2],
        ys = [1, 1, 2]
    )
    path = tr.RelativePath(
        relative_path_id = 0.,
        segments = [segment1, segment2, segment3],
        ts = [4, 8, 10],
    )

    assert path.distance == 4
    assert path.distances == [0, 2, 2, 4]
    assert path.covered_distance(-0.01) is None
    assert path.covered_distance(0) == 0
    assert path.covered_distance(1) == 0.5
    assert path.covered_distance(4) == 2
    assert path.covered_distance(7) == 2
    assert path.covered_distance(8) == 2
    assert path.covered_distance(9) == 3
    assert path.covered_distance(10) == 4
    assert path.covered_distance(path.ts[-1] + 0.01) is None

    assert path.state(-0.01) is None
    assert path.state(0) == {'x': 0, 'y': 0, 'rotation': 0}
    assert path.state(0.5) == {'x': 0.5, 'y': 0, 'rotation': 0}
    assert path.state(1) == {'x': 1, 'y': 0, 'rotation': 0}
    assert path.state(1.5) == {'x': 1, 'y': 0.5, 'rotation': rot(1, 0, 1, 1)}
    assert path.state(2) == {'x': 1, 'y': 1, 'rotation': rot(1, 0, 1, 1)}
    assert path.state(2.5) == {'x': 1.5, 'y': 1, 'rotation': 0}
    assert path.state(3) == {'x': 2, 'y': 1, 'rotation': 0}
    assert path.state(3.5) == {'x': 2, 'y': 1.5, 'rotation': rot(2, 1, 2, 2)}
    assert path.state(4) == {'x': 2, 'y': 2, 'rotation': rot(2, 1, 2, 2)}
    assert path.state(path.distance + 0.01) is None

    train = tr.ScheduledPath(
        path_id = 0,
        path = path,
        scheduled_start = 11
    )

    assert train.state(12.3) == path.state(path.covered_distance(12.3 - train.start))

    train = tr.ScheduledPath(
        path_id = 1,
        path = path,
        scheduled_start = 0
    )
    chain_state = train.chain_state(5, distance_lags=[0, 0.5, 1.5])
    assert chain_state[0] == {'x': 1, 'y': 1, 'rotation': rot(1, 0, 1, 1)}
    assert chain_state[1] == {'x': 1, 'y': 0.5, 'rotation': rot(1, 0, 1, 1)}
    assert chain_state[2] == {'x': 0.5, 'y': 0, 'rotation': 0}
