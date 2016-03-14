from graphviz import Graph


class BlockVisualizer(object):

    def __init__(self):
        self.path = []

    def draw(self):
        g = Graph("test graph", "test comment", filename='test_file.gv', format='ps', engine='dot')
        g.attr('graph', rankdir='TB', splines='ortho')
        g.attr('node', shape='box')

        for i in self.path:
            g.edge(i[0], i[1], i[2])

        g.view()

        pass