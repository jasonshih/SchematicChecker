
class SchematicSymbol(object):

    def __init__(self):
        self.id = ''
        self.type = ''
        self.pins = {}
        self.state = []
        self.links = {}


class SchematicComponent(object):

    def __init__(self):
        self.type = ''
        self.links = {}
