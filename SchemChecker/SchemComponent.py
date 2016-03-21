import re


class SpecialSymbols:

    def __init__(self):
        self.connector_symbols = ['J' + str(t) for t in range(1, 33)]
        self.device_symbols = ['X' + str(t) for t in range(16)]
        self.tester_symbols = ['J' + str(t) for t in range(0, 54, 2)]
        self.plane_symbols = ['[AGND]', '[+5V]', '[-5V]']
        self.terminal_symbols = ['[WARNING]', '[device]', '[tester]']


class SpecialNets:

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


class SchematicComponent:

    standard_links = {}

    def __init__(self, standard_type=None):
        self.type = ''
        self.links = {}
        self.pins = {}

        if not self.standard_links:
            print('importing component link database...')
            self.import_standard_link()

        if standard_type in self.standard_links.keys():
            self.links = self.standard_links[standard_type]

        if standard_type in ['plane', 'terminal']:
            self.pins.update({
                ('00', 'plane'): ''
            })

    def import_standard_link(self, input_txt='component_links.txt'):
        ss = self.standard_links
        pat_pins = re.compile('\((\w+),\s*(\w+)\)')
        pat_type = re.compile('<(\w+)>')
        # part_type, state, tail, heads = '', '', '', []
        with open(input_txt, mode='rt', encoding='utf-8') as fin:
            for ln in fin:
                if ln.startswith(';'):
                    pass
                elif ln.startswith('<'):
                    part_type = pat_type.match(ln).group(1).strip()
                    # state, tail, heads = '', '', []
                elif ':' in ln:
                    (s, link) = ln.split(':')
                    (t, h) = link.split('--')

                    state = s.strip()
                    [tail] = pat_pins.findall(t)
                    heads = pat_pins.findall(h)

                    th = {tail: heads}
                    s_th = {state: th}

                    if part_type and state and tail:
                        # print(': '.join([part_type, state, str(tail), str(heads)]))
                        if part_type not in ss.keys():
                            ss.update({part_type: s_th})
                        else:
                            if state in ss[part_type].keys():
                                ss[part_type][state].update(th)
                            else:
                                ss[part_type].update(s_th)


class SchematicSymbol(SchematicComponent):

    def __init__(self, standard_type=None):
        SchematicComponent.__init__(self, standard_type)
        self.id = ''
        self.state = []
        self.DNI = False


class SchematicNode:

    def __init__(self, symbol_and_pins):
        (self.symbol, self.pin_number, self.pin_name) = symbol_and_pins
        self.tuple = symbol_and_pins
        self.name = '|'.join(symbol_and_pins)
        self.DNI = False

    def __str__(self):
        return self.name


class SchematicEdge:

    def __init__(self, nets):
        self.name = nets
        self.tester_pointer = self.name.split('_')[0]

    def __str__(self):
        return self.name
