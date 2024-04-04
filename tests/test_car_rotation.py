import train_route.traveler as tr
from train_route.rotation import spheric_rotation as rot


def test_path():
    segment1 = tr.Segment(
        segment_id = 0,
        source = 0,
        target = 1,
        xs = [0, 10, 10],
        ys = [0, 0, 10]
    )

    segment2 = tr.Segment(
        segment_id = 1,
        source = 1,
        target = 1,
        xs = [10, 10],
        ys = [10, 10]
    )

    segment3 = tr.Segment(
        segment_id = 2,
        source = 1,
        target = 2,
        xs = [10, 20, 20],
        ys = [10, 10, 20]
    )
    path = tr.RelativePath(
        relative_path_id = 0.,
        segments = [segment1, segment2, segment3],
        ts = [4, 8, 10],
    )

    # straight line
    assert path.state(5, 4) == {'x': 5, 'y': 0, 'rotation': rot(3, 0, 7, 0)}
    assert path.state(15, 4) == {'x': 10, 'y': 5, 'rotation': rot(10, 3, 10, 7)}
    # turning
    assert path.state(10, 4) == {'x': 10, 'y': 0, 'rotation': rot(8, 0, 10, 2)}
