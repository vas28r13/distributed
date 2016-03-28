from __future__ import print_function, division, absolute_import

from collections import defaultdict
from itertools import chain

from toolz import pluck

from ..utils import ignoring

with ignoring(ImportError):
    from bokeh.models import ColumnDataSource, DataRange1d, Range1d
    from bokeh.palettes import Spectral9
    from bokeh.plotting import figure


def resource_profile_plot(width=600, height=300):
    names = ['time', 'cpu', 'memory-percent']
    source = ColumnDataSource({k: [] for k in names})

    x_range = DataRange1d(follow='end', follow_interval=30000, range_padding=0)
    y_range = Range1d(0, 100)
    p = figure(width=width, height=height, x_axis_type='datetime',
               responsive=True, tools='xpan,xwheel_zoom,box_zoom,resize,reset',
               x_range=x_range, y_range=y_range)
    p.line(x='time', y='memory-percent', line_width=2, line_alpha=0.8,
           color=Spectral9[7], legend='Avg Memory Usage', source=source)
    p.line(x='time', y='cpu', line_width=2, line_alpha=0.8,
           color=Spectral9[0], legend='Avg CPU Usage', source=source)
    p.legend[0].location = 'top_left'
    p.yaxis[0].axis_label = 'Percent'
    p.xaxis[0].axis_label = 'Time'
    p.min_border_right = 10

    return source, p


def resource_profile_update(source, worker_buffer, times_buffer):
    data = defaultdict(list)

    workers = sorted(list(set(chain(*list(w.keys() for w in worker_buffer)))))

    for name in ['cpu', 'memory-percent']:
        data[name] = [[msg[w][name] if w in msg and name in msg[w] else 'null'
                       for msg in worker_buffer]
                       for w in workers]

    data['workers'] = workers
    data['times'] = [[t * 1000 if w in worker_buffer[i] else 'null'
                      for i, t in enumerate(times_buffer)]
                      for w in workers]

    source.data.update(data)


def resource_append(lists, msg):
    L = list(msg.values())
    if not L:
        return
    for k in ['cpu', 'memory-percent']:
        lists[k].append(mean(pluck(k, L)))

    lists['time'].append(mean(pluck('time', L)) * 1000)


def mean(seq):
    seq = list(seq)
    return sum(seq) / len(seq)
