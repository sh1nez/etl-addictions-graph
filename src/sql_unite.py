from collections import defaultdict
from sqlglot import parse_one
from sqlglot.expressions import Update, Insert, Table
import networkx as nx
from os.path import join

from os import listdir

import matplotlib.pyplot as plt



def process_data_move(parsed, depends):
    if 'this' not in parsed.args:
        raise Exception('Unsupported structure')

    to_table = get_table_name(parsed)
    from_table = get_first_from(parsed)
    if from_table is None:
        from_table = 'input'
    else:
        from_table = get_table_name(from_table)

    depends[to_table].add(from_table)

def get_first_from(parsed):
    if 'from' in parsed.args:
        return parsed.args['from']

    if 'expression' in parsed.args:
        return get_first_from(parsed.expression)

    return None

def get_table_name(parsed):
    while 'this' in parsed.args:
        if isinstance(parsed, Table):
            return parsed.this.this
        parsed = parsed.this

    raise Exception('No table found')

def process_stmt(parsed, depends):
    match parsed:
        case Insert() | Update():
            process_data_move(parsed, depends)
        case _:
            pass

depends = defaultdict(set)
for filename in listdir('dml'):
    with open(join('dml', filename), encoding="utf-8") as file:
        stmt = file.read()

    for i in parse_one(stmt).walk():
        process_stmt(i, depends)

graph = nx.DiGraph()

for k, v in depends.items():
    for i in v:
        graph.add_edge(i, k)

plt.gcf().canvas.manager.set_window_title(f'view')
nx.draw(graph, with_labels=True, font_weight='bold')
plt.show()
