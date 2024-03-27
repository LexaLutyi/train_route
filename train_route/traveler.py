from typing import List
import math
from rotation import spheric_rotation

def cumsum(xs:list):
    cs = xs.copy()
    for i in range(1, len(cs)):
        cs[i] += cs[i - 1]
    return cs

class OptimizedTraveler():
    def __init__(self, ts):
        self.ts = ts
        self.reset()

    def reset(self):
        self.index = 0
        self.t = self.ts[0]
    
    def index_delta(self, t):
        "return index and delta"
        if t < self.t:
            self.reset()
        self.t = t
        while self.index < len(self.ts) and self.ts[self.index] < t:
            self.index += 1
        if self.index == 0 or self.index == len(self.ts):
            # outside of ts
            return None
        t0 = self.ts[self.index - 1]
        t1 = self.ts[self.index]
        delta = (t - t0) / (t1 - t0)
        return self.index, delta

class Segment:
    "Segment is used for inner paths with missing time points"
    def __init__(self, segment_id, source, target, xs, ys, ds = None) -> None:
        self.segment_id = segment_id
        self.source = source
        self.target = target
        self.xs = xs
        self.ys = ys
        self.ds = ds if not ds is None else cumsum(distances(xs, ys))
        "distance from starting point"
        self.distance = self.ds[-1]

    def state(self, index, delta, default_rotation = 0.):
        if len(self.xs) > 1:
            x0, y0 = self.xs[index - 1], self.ys[index - 1]
            x1, y1 = self.xs[index], self.ys[index]
            return {
                'x': x0 + (x1 - x0) * delta,
                'y': y0 + (y1 - y0) * delta,
                'rotation': spheric_rotation(x0, y0, x1, y1)
            }
        else:
            return {
                'x': self.xs[0], 
                'y': self.ys[0],
                'rotation': default_rotation
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
        self.distance = sum([s.distance for s in segments])
        self.ts = [0] + ts
    
    def state(self, index):
        segment = self.segments[index - 1]
        return segment
    
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
        self.reset_path_traveler()
        self.reset_segment_traveler()
    
    def segment(self) -> Segment:
        return self.path.state(self.segment_index)
    
    def reset_path_traveler(self):
        self.rotation = 0.
        self.path_traveler = OptimizedTraveler(self.path.ts)
        self.segment_index:int = 0

    def reset_segment_traveler(self):
        self.segment_traveler = OptimizedTraveler(self.segment().ds)

    def state(self, t):
        "State of traveler at t"
        if isinstance(self.start, int):
            relative_t = t - self.start
        else:
            relative_t = (t - self.start).total_seconds()
        path_position = self.path_traveler.index_delta(relative_t)
        if path_position:
            index, delta = path_position
        else:
            return None
        if self.segment_index != index:
            self.segment_index = index
            self.reset_segment_traveler()
        if self.segment().distance == 0:
            index, delta = 0, 0
        else:
            delta_distance = delta * self.segment().distance
            segment_position = self.segment_traveler.index_delta(delta_distance)
            if segment_position is None:
                print(self.start, t, delta, delta_distance, self.segment().distance, sep='\n')
                raise
            index, delta = segment_position
        state = self.segment().state(index, delta, default_rotation=self.rotation)
        self.rotation = state['rotation']
        return state
    
    def to_dict(self):
        return {
            'path_id': self.path_id,
            'path': self.path.to_ref(),
            'start': self.start if isinstance(self.start, int) else str(self.start),
        }

def distances(xs, ys):
    distances = [0.]
    for i in range(1, len(xs)):
        x0, y0 = xs[i - 1], ys[i - 1]
        x1, y1 = xs[i], ys[i]
        distances.append(math.sqrt((x1 - x0)**2 + (y1 - y0)**2))
    return distances
