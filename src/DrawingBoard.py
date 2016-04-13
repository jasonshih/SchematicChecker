import pygraphviz as p
from src.SchemComponent import *
import logging


class BlockVisualizer(SpecialSymbols, SpecialNets):

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        SpecialSymbols.__init__(self)
        SpecialNets.__init__(self)

    def draw(self, pathway: SchematicPath):
        self.logger.info('drawing ...')
        g = p.AGraph(strict=False)

        flatten_path = [y for lo in pathway.links for y in lo.link]
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

        for link in pathway.links:

            tail, tail_port = link.tail.symbol, link.tail.pin_name
            head, head_port = link.head.symbol, link.head.pin_name
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
                # g.add_edge(tail, head, label=link.edge, tailport=tail_port, headport=head_port, style='dotted')
            else:
                g.add_edge(tail, head, label=link.edge, tailport=tail_port, headport=head_port,
                           color=edge_color, style=edge_style)

        devices = {x for x in all_nodes if x in self.device_symbols}
        bottom_rank = {x for x in all_nodes if x in self.connector_symbols}
        # print(devices)
        # print(bottom_rank)
        # g.add_subgraph(top_rank, name='planes', rank='min')
        g.add_subgraph(devices, name='device symbol', rank='same')
        g.add_subgraph(bottom_rank, name='tester symbol', rank='max')
        g.write('../output_files/test_file.dot')
        g.layout(prog='dot')
        g.draw('../output_files/test_file.ps', format='ps')
        pass
