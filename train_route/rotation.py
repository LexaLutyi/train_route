from math import radians, sin ,cos, atan2, degrees

def spheric_rotation(x0, y0, x1, y1):
    "assumes x, y is latitude, longitude"
    if x0 == x1 and y0 == y1:
        return None
    lat1, lon1, lat2, lon2 = [radians(phi) for phi in [x0, y0, x1, y1]]
    dLon = lon2 - lon1
    x = sin(dLon) * cos(lat2)
    y = cos(lat1) * sin(lat2) - sin(lat1) * cos(lat2) * cos(dLon)
    initial_bearing = atan2(x, y)
    initial_bearing_degrees = degrees(initial_bearing)
    return initial_bearing_degrees