import train_route.traveler as tr
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from datetime import datetime
from tqdm import tqdm

def random_path(start, n):
    deltas = np.random.random(n)
    deltas.put(0, 0)
    return np.cumsum(deltas) + start

segment1 = tr.Segment(
    segment_id = 0,
    source = 0,
    target = 1,
    xs = random_path(0, 10),
    ys = random_path(0, 10)
)

segment2 = tr.Segment(
    segment_id = 1,
    source = 1,
    target = 1,
    xs = [segment1.xs[-1], segment1.xs[-1]],
    ys = [segment1.ys[-1], segment1.ys[-1]]
)

segment3 = tr.Segment(
    segment_id = 2,
    source = 1,
    target = 2,
    xs = random_path(segment2.xs[-1], 10),
    ys = random_path(segment2.ys[-1], 10),
)
path = tr.RelativePath(
    relative_path_id = 0.,
    segments = [segment1, segment2, segment3],
    ts = [9, 13, 19],
)

train = tr.ScheduledPath(
    path_id = 1,
    path = path,
    scheduled_start = 0
)

def state(train, t, lags = [0.4 * i for i in range(5)]):
    data = train.chain_state(t, lags)
    if data is None:
        return [], [], []
    
    x = [d['x'] for d in data]
    y = [d['y'] for d in data]
    r = [d['rotation'] for d in data]
    return x, y, r

def plot(
        train, 
        n = 100, 
        xlims = None, 
        ylims = None, 
        *, 
        t0 = None,
        t1 = None,
        file = 'examples/chain.gif', 
        lags = [0.4 * i for i in range(5)]
        ):
    t0 = t0 if t0 else train.path.ts[0] + train.start
    t1 = t1 if t1 else train.path.ts[-1] + train.start
    dt = (t1 - t0) / n
    
    fig, ax = plt.subplots()

    xss = [x for s in train.path.segments for x in s.xs ]
    yss = [y for s in train.path.segments for y in s.ys ]
    xlim = xlims if xlims else [min(xss), (max(xss))]
    ylim = ylims if ylims else [min(yss), (max(yss))]
    ax.set(xlim = xlim, ylim = ylim)
    print(train.path.ts)

    def update(frame):
        print(frame, '/', n)
        t = t0 + frame * dt
        xs, ys, rs = state(train, t, lags=lags)
        # print(t, xs)

        # data = np.stack([x, y]).T
        # scat.set_offsets(data)
        ax.clear()
        ax.plot(xss, yss, color = 'gray')
        ax.plot(xs, ys)
        if xs:
            delta = 500 / 111000
            xlim[0], xlim[1] = [xs[0] - delta, xs[0] + delta]
            ylim[0], ylim[1] = [ys[0] - delta, ys[0] + delta]
        ax.set(xlim = xlim, ylim = ylim, title = f't = {round(t, 2)}')
        ax.set_aspect('equal', adjustable='box')
        for x, y, r in zip(xs, ys, rs):
            scat = ax.scatter([x], [y], marker=(3, 0, r - 90))
        return

    ani = animation.FuncAnimation(fig=fig, func=update, frames=n, interval=30, repeat=False)
    ani.save(file)

# ani = plot(train, 50, xlims=[-1, 11], ylims = [-1, 11])

# real route
import json

def load_segments(file):
    with open(file) as io:
        segment_generator = json.load(io)['segments']
        return {
            s['segment_id']: tr.Segment(
                s['segment_id'],
                s['source'],
                s['target'],
                s['xs'],
                s['ys'],
                s['ds']
            ) for s in segment_generator
        }

def load_relative_paths(file, *, segments):
    with open(file) as io:
        path_generator = json.load(io)['relative_paths']
        return {
            s['relative_path_id']: tr.RelativePath(
                s['relative_path_id'],
                [segments[i] for i in s['segments']],
                s['ts'],
            ) for s in path_generator
        }

def load_scheduled_paths(file, *, relative_paths):
    with open(file) as io:
        path_generator = json.load(io)['scheduled_paths']
        return {
            s['path_id']: tr.ScheduledPath(
                s['path_id'],
                relative_paths[s['path']],
                datetime.strptime(s['start'], '%Y-%m-%d %H:%M:%S%z').timestamp(),
            ) for s in path_generator
        }

segments = load_segments('tests/data/segments.json')
relative_paths = load_relative_paths('tests/data/relative_paths.json', segments=segments)
scheduled_paths = load_scheduled_paths(
    'tests/data/scheduled_paths.json',
    relative_paths=relative_paths
)
train = scheduled_paths[0]

plot(
    train, 
    1000, 
    file='examples/route.gif', 
    lags=[30 / 111000 * i for i in range(5)],
    t0 = train.start,
    t1 = train.start + train.path.ts[-1] / 10
)
