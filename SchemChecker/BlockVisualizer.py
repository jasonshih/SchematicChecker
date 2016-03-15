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

        g.graph_attr['ranksep'] = '0.1'
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

            if tail == head:
                g.add_edge(tail, head, label=i[2], tailport=tail_port, headport=head_port, style='dotted')
            else:
                g.add_edge(tail, head, label=i[2], tailport=tail_port, headport=head_port)

        g.add_subgraph(['J5', 'J6'], name='tester symbol', rank='same')
        g.write('test_file.dot')
        pass

#      digraph g {
# 2: node [shape = record,height=.1];
# 3: node0[label = "<f0> |<f1> G|<f2> "];
# 4: node1[label = "<f0> |<f1> E|<f2> "];
# 5: node2[label = "<f0> |<f1> B|<f2> "];
# 6: node3[label = "<f0> |<f1> F|<f2> "];
# 7: node4[label = "<f0> |<f1> R|<f2> "];
# 8: node5[label = "<f0> |<f1> H|<f2> "];
# 9: node6[label = "<f0> |<f1> Y|<f2> "];
# 10: node7[label = "<f0> |<f1> A|<f2> "];
# 11: node8[label = "<f0> |<f1> C|<f2> "];
# 12: "node0":f2 -> "node4":f1;
# 13: "node0":f0 -> "node1":f1; [tailport=f0, headport=f1];
# 14: "node1":f0 -> "node2":f1;
# 15: "node1":f2 -> "node3":f1;
# 16: "node2":f2 -> "node8":f1;
# 17: "node2":f0 -> "node7":f1;
# 18: "node4":f2 -> "node6":f1;
# 19: "node4":f0 -> "node5":f1;
# 20: }
# Fi