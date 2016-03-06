
class SchematicComponent(object):

    def __init__(self):
        self.type = ''
        self.links = {}
        self.pins = {}


class SchematicSymbol(SchematicComponent):

    def __init__(self):
        SchematicComponent.__init__()
        self.id = ''
        self.state = []
        # self.type = ''
        # self.pins = {}
        # self.links = {}


