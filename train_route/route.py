import math

class Route:
    def __init__(self, ts, xs, ys) -> None:
        self.xs = xs
        self.ys = ys
        self.ts = ts

    def state(self, next_point:int):
        return self.xs[next_point], self.ys[next_point], self.ts[next_point]
    
    def find_next_point(self, t, point:int = 0):
        while point < len(self.ts) and self.ts[point] < t:
            point += 1
        return point
    
    def is_outside(self, t):
        # return self.next_point == 0 or self.next_point >= len(self.ts)
        return t < self.ts[0] or t > self.ts[-1]
    
    def rotation(self, point:int):
        cur_state = self.state(point)
        prev_point = point
        while prev_point >= 0:
            prev_state = self.state(prev_point)
            if prev_state != cur_state:
                break
            prev_point -= 1
        
        next_point = point
        while next_point < len(self.ts):
            next_state = self.state(next_point)
            if next_state != prev_state:
                break
            next_point += 1
        if prev_state == next_state:
            return None
        
        x0, y0, _ = prev_state
        x1, y1, _ = next_state
        dx, dy = x1 - x0, y1 - y0
        return 180 * math.atan2(dy, dx) / math.pi
        
    
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

    def state(self, t) -> None:
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
        return x, y, self.route.rotation(self.next_point)

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