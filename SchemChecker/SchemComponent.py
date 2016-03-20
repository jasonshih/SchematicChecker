import re


class SpecialSymbols(object):

    def __init__(self):
        self.connector_symbols = ['J' + str(t) for t in range(1, 33)]
        self.device_symbols = ['X' + str(t) for t in range(16)]
        self.tester_symbols = ['J' + str(t) for t in range(0, 54, 2)]
        self.plane_symbols = ['[AGND]', '[+5V]', '[-5V]']
        self.terminal_symbols = ['[WARNING]', '[device]', '[tester]']


class SpecialNets(object):

    def __init__(self):
        self.plane = {
            'AGND': '[AGND]|00|plane',
            '+5V': '[+5V]|00|plane',
            '-5V': '[-5V]|00|plane',
            '+5V_RLY': '[+5V_RLY]|00|plane',
            'P5V': '[P5V]|00|plane',
            'N5V': '[N5V]|00|plane',
            'P15V': '[P15V]|00|plane',
            'N15V': '[N15V]|00|plane',
            'unconnected': '[WARNING]|00|terminal'
        }


class SchematicComponent(object):

    def __init__(self, standard_type=None):
        self.type = ''
        self.links = {}
        self.pins = {}

        self.standard_links = {}
        self.import_standard_link()

        # TODO: simplify the hell out of this.
        if standard_type == 'plane':
            self.pins.update({
                ('00', 'plane'): ''
            })
            self.links = self.standard_links['plane']
            # self.links.update({
            #         'na': {
            #             ('00', 'plane'): []
            #         }
            #     })

        elif standard_type == 'terminal':
            self.pins.update({
                ('00', 'plane'): ''
            })
            self.links = self.standard_links['terminal']
            # self.links.update({
            #         'na': {
            #             ('00', 'terminal'): []
            #         }
            #     })

        elif standard_type == 'std_8pins_relay':
            self.links = self.standard_links['std_8pins_relay']
            # self.links.update(
            #     {
            #         'off': {('1', 'N1'): [('8', 'N2')],
            #                 ('2', 'S1'): [('3', 'COM1')],
            #                 ('3', 'COM1'): [('2', 'S1')],
            #                 ('4', 'S2'): [],
            #                 ('5', 'S4'): [],
            #                 ('6', 'COM2'): [('7', 'S3')],
            #                 ('7', 'S3'): [('6', 'COM2')],
            #                 ('8', 'N2'): [('1', 'N1')]}
            #     })
            # self.links.update(
            #     {
            #         'on': {('1', 'N1'): [('8', 'N2')],
            #                ('2', 'S1'): [],
            #                ('3', 'COM1'): [('4', 'S2')],
            #                ('4', 'S2'): [('3', 'COM1')],
            #                ('5', 'S4'): [('6', 'COM2')],
            #                ('6', 'COM2'): [('5', 'S4')],
            #                ('7', 'S3'): [],
            #                ('8', 'N2'): [('1', 'N1')]}
            #     })

        elif standard_type == 'std_2pins_passive':
            self.links = self.standard_links['std_2pins_passive']
            # self.links.update(
            #     {
            #         'na': {('1', 'POS'): [('2', 'NEG')],
            #                ('2', 'NEG'): [('1', 'POS')]}
            #     })

        elif standard_type == 'jumper':
            self.links = self.standard_links['jumper']
            # self.links.update(
            #     {
            #         'na': {('1', 'IO1'): [('2', 'IO2')],
            #                ('2', 'IO2'): [('1', 'IO1')]}
            #     })

    def import_standard_link(self, input_txt='component_links.txt'):
        pat_pins = re.compile('\((\w+),\s*(\w+)\)')
        pat_type = re.compile('\<(\w+)\>')
        part_type, state, tail, heads = '', '', '', []
        with open(input_txt, mode='rt', encoding='utf-8') as fin:
            for ln in fin:
                if ln.startswith(';'):
                    pass
                elif ln.startswith('<'):
                    part_type = pat_type.match(ln).group(1).strip()
                elif (':' in ln):
                    (s, link) = ln.split(':')
                    state = s.strip()
                    (t, h) = link.split('--')

                    [tail] = pat_pins.findall(t)
                    heads = pat_pins.findall(h)

                if part_type and state and tail:
                    self.standard_links.update({part_type:{state:{tail:heads}}})
                    pass

                    # pat_type = re.compile('([<]\w+[>])')
                    # pat_link = re.compile('(\w+):()--()')

                    # self.standard_links.update()


class SchematicSymbol(SchematicComponent):

    def __init__(self, standard_type=None):
        SchematicComponent.__init__(self, standard_type)
        self.id = ''
        self.state = []
        self.DNI = False


class SchematicNode(object):

    def __init__(self, symbol_and_pins):
        (self.symbol, self.pin_number, self.pin_name) = symbol_and_pins
        self.tuple = symbol_and_pins
        self.name = '|'.join(symbol_and_pins)
        self.DNI = False

    def __str__(self):
        return self.name


class SchematicEdge(object):

    def __init__(self, nets):
        self.name = nets
        self.tester_pointer = self.name.split('_')[0]

    def __str__(self):
        return self.name
