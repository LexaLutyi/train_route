from math import cos, sin, radians, atan2, pi, degrees
from typing import Literal

class Route:
    def __init__(self, ts, xs, ys) -> None:
        self.xs = xs
        self.ys = ys
        self.ts = ts

    def state(self, next_point:int):
        return self.xs[next_point], self.ys[next_point], self.ts[next_point]
    
    def location(self, point:int):
        return self.xs[point], self.ys[point]
    
    def find_next_point(self, t, point:int = 0):
        while point < len(self.ts) and self.ts[point] < t:
            point += 1
        return point
    
    def is_outside(self, t):
        # return self.next_point == 0 or self.next_point >= len(self.ts)
        return t < self.ts[0] or t > self.ts[-1]
    
    def segment(self, point:int):
        cur_state = self.location(point)
        prev_point = point
        while prev_point >= 0:
            prev_state = self.location(prev_point)
            if prev_state != cur_state:
                break
            prev_point -= 1
        
        next_point = point
        while next_point < len(self.ts):
            next_state = self.location(next_point)
            if next_state != prev_state:
                break
            next_point += 1
        if prev_state == next_state:
            return None
        return prev_state, next_state
    def plane_rotation(self, point):
        prev_state, next_state = self.segment(point)
        x0, y0 = prev_state
        x1, y1 = next_state
        dx, dy = x1 - x0, y1 - y0
        return degrees(atan2(dy, dx))
    
    def spheric_rotation(self, point:int):
        "assumes x, y is latitude, longitude"
        prev_state, next_state = self.segment(point)
        lat1, lon1 = [radians(phi) for phi in prev_state]
        lat2, lon2 = [radians(phi) for phi in next_state]
        dLon = lon2 - lon1
        x = sin(dLon) * cos(lat2)
        y = cos(lat1) * sin(lat2) - sin(lat1) * cos(lat2) * cos(dLon)
        initial_bearing = atan2(x, y)
        initial_bearing_degrees = degrees(initial_bearing)
        return initial_bearing_degrees

class Train():
    def __init__(self, route:Route) -> None:
        self.route = route
        self.reset()
    
    def reset(self) -> None:
        # store next point in route, for optimization
        self.next_point = 0
        self.t = self.route.ts[0]
    
    def is_on_route(self):
        return not self.is_outside_route()
    
    def is_outside_route(self):
        return self.route.is_outside(self.t)

    def state(self, t, *, rotation:Literal['plane', 'spheric'] = 'plane') -> None:
        "train[t] = f(train[t - 1], t)"

        if t < self.t:
            self.reset()
        self.t = t

        if not self.is_on_route():
            return

        # train between old_point and next_point
        self.next_point = self.route.find_next_point(t, self.next_point)
        old_point = self.next_point - 1
        next_x, next_y, next_t = self.route.state(self.next_point)
        old_x, old_y, old_t = self.route.state(old_point)
        # part of segment made by train, delta in [0, 1]
        delta = 0. if old_t == next_t else (t - old_t) / (next_t - old_t)
        
        x = delta * (next_x - old_x) + old_x
        y = delta * (next_y - old_y) + old_y
        if rotation == 'plane':
            phi = self.route.plane_rotation(self.next_point)
        else:
            phi = self.route.spheric_rotation(self.next_point)
        return x, y, phi

def to_geo_feature(lng, lat, rotation):
    return {
        'type': 'Feature',
        'properties': {
            'rotation': rotation,
        },
        'geometry': {
            'type': 'Point',
            'coordinates': [lng, lat],
        }
    }

def wrap_features(features):
    return {
        'type': 'FeatureCollection',
        'features': features
    }