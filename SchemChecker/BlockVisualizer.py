import pygraphviz as p


class BlockVisualizer(object):

    def __init__(self):
        self.path = []
        self.SYMBOL_DICT = {}

    def draw(self):
        g = p.AGraph(strict=False)

        flatten_path = [y.split('|') for x in self.path for y in x]
        flatten_nodes = [x for x in flatten_path if len(x) == 3]
        all_nodes = {x[0] for x in flatten_nodes}

        g.graph_attr['size'] = '8,11'
        g.graph_attr['splines'] = 'polyline'
        g.graph_attr['rankdir'] = 'TB'
        g.graph_attr['ranksep'] = '0.5'
        g.node_attr['shape'] = 'Mrecord'
        g.node_attr['fontsize'] = '8'
        g.edge_attr['fontsize'] = '8'

        for each_node in all_nodes:
            pins = {'<' + v + '>' + v for t, u, v in flatten_nodes if t == each_node}
            node_label = '<dft>' + each_node + '|' + '|'.join(pins) + ''

            g.add_node(each_node, label=node_label)

        for i in self.path:

            tail, _, tail_port = i[0].split('|')
            head, _, head_port = i[1].split('|')
            if tail == head:
                tail_port += ':n'
                head_port += ':n'
            else:
                tail_port += ':s'
                head_port += ':n'

            if tail == head:
                continue
                # g.add_edge(tail, head, label=i[2], tailport=tail_port, headport=head_port, style='dotted')
            else:
                g.add_edge(tail, head, label=i[2], tailport=tail_port, headport=head_port)

        g.add_subgraph(['J5', 'J6', 'J27', '[AGND]'], name='tester symbol', rank='same')
        g.write('test_file.dot')
        g.layout(prog='dot')
        g.draw('test_file.ps', format='ps')
        pass

