import json
from datetime import datetime
import train_route.traveler as trv

def load_segments(file):
    with open(file) as io:
        segment_generator = json.load(io)['segments']
        return {
            s['segment_id']: trv.Segment(
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
            s['relative_path_id']: trv.RelativePath(
                s['relative_path_id'],
                [segments[i] for i in s['segments']],
                s['ts'],
            ) for s in path_generator
        }

def load_scheduled_paths(file, *, relative_paths):
    with open(file) as io:
        path_generator = json.load(io)['scheduled_paths']
        return {
            s['path_id']: trv.ScheduledPath(
                s['path_id'],
                relative_paths[s['path']],
                datetime.strptime(s['start'], '%Y-%m-%d %H:%M:%S%z'),
            ) for s in path_generator
        }

segments = load_segments('tests/data/segments.json')
relative_paths = load_relative_paths('tests/data/relative_paths.json', segments=segments)
scheduled_paths = load_scheduled_paths(
    'tests/data/scheduled_paths.json',
    relative_paths=relative_paths
)

start_time = datetime.strptime('2024-03-28 00:00:00+00:00', '%Y-%m-%d %H:%M:%S%z')
states = [tr.state(start_time) for i, tr in scheduled_paths.items()]
