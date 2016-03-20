import pygraphviz as p
from SchemChecker.SchemComponent import *

class BlockVisualizer(object):

    def __init__(self):
        self.path = []
        self.SYMBOL_DICT = {}

        # TODO: handle these better!
        self.connector_symbols = ['J' + str(t) for t in range(1, 33)]
        self.connector_symbols.extend(['[AGND]', '[WARNING]'])
        self.device_symbols = ['X' + str(t) for t in range(16)]
        self.tester_symbols = ['J' + str(t) for t in range(0, 54, 2)]
        self.tester_symbols.append('AGND')

    def draw(self):
        g = p.AGraph(strict=False)

        flatten_path = [y for x in self.path for y in x]
        flatten_nodes = [x for x in flatten_path if type(x) is SchematicNode]
        all_nodes = {x.symbol for x in flatten_nodes}

        g.graph_attr['size'] = '7.5,10'
        # g.graph_attr['splines'] = 'polyline'
        g.graph_attr['rankdir'] = 'LR'
        g.graph_attr['ranksep'] = '0.5'
        g.node_attr['shape'] = 'Mrecord'
        g.node_attr['fontsize'] = '8'
        g.edge_attr['fontsize'] = '8'

        for each_node in all_nodes:
            pins = {'<' + t.pin_name + '>' + t.pin_name for t in flatten_nodes if t.symbol == each_node}
            node_label = '<dft>' + each_node + '|' + '|'.join(pins) + ''

            g.add_node(each_node, label=node_label)

        for i in self.path:

            tail, tail_port = i[0].symbol, i[0].pin_name
            head, head_port = i[1].symbol, i[1].pin_name
            if tail == head:
                tail_port += ':w'
                head_port += ':w'
            else:
                tail_port += ':e'
                head_port += ':w'

            if '[WARNING]' in [head, tail]:
                edge_color = 'red'
                edge_style = 'dotted'
            else:
                edge_color = 'blue'
                edge_style = 'solid'

            if tail == head:
                continue
                # g.add_edge(tail, head, label=i[2], tailport=tail_port, headport=head_port, style='dotted')
            else:
                g.add_edge(tail, head, label=i[2], tailport=tail_port, headport=head_port,
                           color=edge_color, style=edge_style)

        devices = {x for x in all_nodes if x in self.device_symbols}
        bottom_rank = {x for x in all_nodes if x in self.connector_symbols}
        print(devices)
        print(bottom_rank)
        # g.add_subgraph(top_rank, name='planes', rank='min')
        g.add_subgraph(devices, name='device symbol', rank='same')
        g.add_subgraph(bottom_rank, name='tester symbol', rank='max')
        g.write('../output_files/test_file.dot')
        g.layout(prog='dot')
        g.draw('../output_files/test_file.ps', format='ps')
        pass
