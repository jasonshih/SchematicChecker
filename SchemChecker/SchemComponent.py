
class SpecialSymbols(object):

    def __init__(self):
        self.connector_symbols = ['J' + str(t) for t in range(1, 33)]
        self.device_symbols = ['X' + str(t) for t in range(16)]
        self.tester_symbols = ['J' + str(t) for t in range(0, 54, 2)]
        self.tester_symbols.append('AGND')
        self.plane_symbols = ['GND', '+5V', '-5V']


class SchematicComponent(object):

    def __init__(self, standard_type=None):
        self.type = ''
        self.DNI = False
        self.links = {}
        self.pins = {}

        # TODO: simplify the hell out of this.
        if standard_type == 'plane':
            self.pins.update({
                ('00', 'plane'): ''
            })
            self.links.update({
                    'na': {
                        ('00', 'plane'): []
                    }
                })

        elif standard_type == 'terminal':
            self.pins.update({
                ('00', 'plane'): ''
            })
            self.links.update({
                    'na': {
                        ('00', 'terminal'): []
                    }
                })

        elif standard_type == 'std_8pins_relay':
            self.links.update(
                {
                    'off': {('1', 'N1'): [('8', 'N2')],
                            ('2', 'S1'): [('3', 'COM1')],
                            ('3', 'COM1'): [('2', 'S1')],
                            ('4', 'S2'): [],
                            ('5', 'S4'): [],
                            ('6', 'COM2'): [('7', 'S3')],
                            ('7', 'S3'): [('6', 'COM2')],
                            ('8', 'N2'): [('1', 'N1')]}
                })
            self.links.update(
                {
                    'on': {('1', 'N1'): [('8', 'N2')],
                           ('2', 'S1'): [],
                           ('3', 'COM1'): [('4', 'S2')],
                           ('4', 'S2'): [('3', 'COM1')],
                           ('5', 'S4'): [('6', 'COM2')],
                           ('6', 'COM2'): [('5', 'S4')],
                           ('7', 'S3'): [],
                           ('8', 'N2'): [('1', 'N1')]}
                })

        elif standard_type == 'std_2pins_passive':
            self.links.update(
                {
                    'na': {('1', 'POS'): [('2', 'NEG')],
                           ('2', 'NEG'): [('1', 'POS')]}
                })

        elif standard_type == 'jumper':
            self.links.update(
                {
                    'na': {('1', 'IO1'): [('2', 'IO2')],
                           ('2', 'IO2'): [('1', 'IO1')]}
                })


class SchematicSymbol(SchematicComponent):

    def __init__(self, standard_type=None):
        SchematicComponent.__init__(self, standard_type)
        self.id = ''
        self.state = []
