
class SchematicComponent(object):

    def __init__(self, standard_type=None):
        self.type = ''
        self.links = {}
        self.pins = {}

        if standard_type == 'gnd':
            self.pins.update({
                ('gnd', 'plane'): 'AGND'
            })
            self.links.update({
                    'na': {
                        ('gnd', 'plane'): []
                    }
                })

        elif standard_type == '+5V':
            self.pins.update({
                ('+5V', 'plane'): '+5V'
            })
            self.links.update({
                    'na': {
                        ('+5V', 'plane'): []
                    }
                })

        elif standard_type == '-5V':
            self.pins.update({
                ('-5V', 'plane'): '-5V'
            })
            self.links.update({
                    'na': {
                        ('-5V', 'plane'): []
                    }
                })

        elif standard_type == 'device':
            self.pins.update({
                ('_', '_'): 'socket'
            })
            self.links.update({
                    'na': {
                        ('_', '_'): []
                    }
                })

        elif standard_type == 'tester':
            self.pins.update({
                ('_', '_'): 'connector'
            })
            self.links.update({
                    'na': {
                        ('_', '_'): []
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

        elif standard_type == 'std_shorting_bar':
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