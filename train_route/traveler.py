from typing import List
import math
from .rotation import spheric_rotation
import bisect
from datetime import datetime

def cumsum(xs:list):
    cs = [0.]
    for x in xs:
        cs.append(cs[-1] + x)
    return cs[1:]

def index_delta(ts, t):
    if ts[0] == t:
        return 0, 0.
    idx = bisect.bisect_left(ts, t)
    if idx == 0 or idx == len(ts):
        return None
    t0 = ts[idx - 1]
    t1 = ts[idx]
    delta = (t - t0) / (t1 - t0)
    return idx - 1, delta

def distances(xs, ys):
    distances = [0.]
    for i in range(1, len(xs)):
        x0, y0 = xs[i - 1], ys[i - 1]
        x1, y1 = xs[i], ys[i]
        distances.append(math.sqrt((x1 - x0)**2 + (y1 - y0)**2))
    return distances

class Segment:
    "Segment is used for inner paths with missing time points"
    def __init__(self, segment_id, source, target, xs, ys, ds = None) -> None:
        self.segment_id = segment_id
        self.source = source
        self.target = target
        self.xs = xs
        self.ys = ys

        # len(rs) = len(xs) - 1
        self.rs = [
            spheric_rotation(x0, y0, x1, y1) 
            for x0, y0, x1, y1 in zip(xs[:-1], ys[:-1], xs[1:], ys[1:])
        ]
        
        # ds = [0, d1, d2, d3, ...], len(ds) = len(xs)
        self.ds = ds if not ds is None else cumsum(distances(xs, ys))
        "distance from starting point"
        self.distance = self.ds[-1]
    
    def state(self, d):
        position = index_delta(self.ds, d)
        if position is None:
            return None
        if len(self.xs) < 2:
            return  {
                'x': self.xs[0], 
                'y': self.ys[0],
                'rotation': None
            }
        idx, delta = position
        x0, y0 = self.xs[idx], self.ys[idx]
        x1, y1 = self.xs[idx + 1], self.ys[idx + 1]
        r0 = self.rs[idx]
        return {
            'x': x0 + (x1 - x0) * delta,
            'y': y0 + (y1 - y0) * delta,
            'rotation': r0
        }
    
    def to_dict(self):
        return {
            'segment_id': self.segment_id,
            'source': self.source,
            'target': self.target,
            'xs': self.xs,
            'ys': self.ys,
            'ds': list(self.ds),
        }
    
    def to_ref(self):
        return self.segment_id

class RelativePath:
    "Path: t0 = 0 -> segment_1 -> t1 -> ... -> segment_n -> tn"
    def __init__(self, relative_path_id, segments:List[Segment], ts) -> None:
        self.relative_path_id = relative_path_id
        self.segments = segments

        self.distances = [0] + cumsum((s.distance for s in segments))
        self.ts = [0] + ts

        self.distance = self.distances[-1]
    
    def covered_distance(self, t):
        position = index_delta(self.ts, t)
        if position is None:
            return None
        idx, delta = position
        d0 = self.distances[idx]
        d1 = self.distances[idx + 1]
        return d0 + (d1 - d0) * delta

    def state(self, distance, car_length = None):
        position = index_delta(self.distances, distance)
        if position is None:
            return None
        idx, delta = position
        segment = self.segments[idx]
        segment_distance = segment.distance * delta
        center_position = segment.state(segment_distance)
        if car_length is None:
            return center_position
        d0 = max(0, distance - car_length / 2)
        d1 = min(self.distance, distance + car_length / 2)
        start_position = self.state(d0)
        end_position = self.state(d1)
        if start_position == end_position:
            # something strange
            return center_position
        x0, y0 = start_position['x'], start_position['y']
        x1, y1 = end_position['x'], end_position['y']
        center_position['rotation'] = spheric_rotation(x0, y0, x1, y1)
        center_position['x'] = (x0 + x1) / 2
        center_position['y'] = (y0 + y1) / 2
        return center_position
    
    def to_dict(self):
        return {
            'relative_path_id': self.relative_path_id,
            'segments': [s.to_ref() for s in self.segments],
            'ts': self.ts[1:]
        }
    def to_ref(self):
        return self.relative_path_id

class ScheduledPath:
    "Path with scheduled start (or starts), typically one per model"
    def __init__(self, path_id, path:RelativePath, scheduled_start):
        self.path_id = path_id
        self.path = path
        self.start = scheduled_start
    
    def state(self, t):
        "State of traveler at t"
        state = self.chain_state(t, distance_lags=[0])
        if state:
            return state[0]
        else:
            return None
        
    def chain_state(self, t, distance_lags = [0], car_length = None):
        if isinstance(self.start, datetime):
            relative_t = (t - self.start).total_seconds()
        else:
            relative_t = t - self.start
        distance = self.path.covered_distance(relative_t)
        if distance is None:
            return None
        
        return [self.path.state(distance - l, car_length) for l in distance_lags if distance - l >= 0]

    def to_dict(self):
        return {
            'path_id': self.path_id,
            'path': self.path.to_ref(),
            'start': self.start if isinstance(self.start, int) else str(self.start),
        }
