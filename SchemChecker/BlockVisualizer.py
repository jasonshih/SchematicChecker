from graphviz import Digraph


class BlockVisualizer(object):

    def __init__(self):
        self.path = []
        self.SYMBOL_DICT={}

    def draw(self):
        g = Digraph("test graph", "test comment", filename='test_file.gv', format='ps', engine='dot')
        g.attr('graph', rankdir='TB', splines='polylines')
        g.attr('node', shape='box', fontsize='8')

        all_nodes = {y.split('|')[0] for x in self.path for y in x if '|' in y}
        for each_node in all_nodes:
            pins = ['<' + x[1] + '>' for x in self.SYMBOL_DICT[each_node].pins.keys()]
            node_label = each_node + '<dft>|' + '|'.join(pins)
            g.node(name= each_node, label=node_label)

        for i in self.path:
            g.edge(i[0].split('|')[0], i[1], i[2], tailport='COM')

        g.view()

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