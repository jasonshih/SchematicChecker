import logging
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
        self.logger = logging.getLogger(__name__)
        self.type = ''
        self.links = {}
        self.pins = {}

        if not self.standard_links:
            self.import_standard_link()

        if standard_type in self.standard_links.keys():
            self.links = self.standard_links[standard_type]

        if standard_type in ['plane', 'terminal']:
            self.pins.update({
                ('00', 'plane'): ''
            })

    def import_standard_link(self, input_txt='component_links.txt'):

        self.logger.info('importing component link database...')
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
                        self.logger.debug('reading... %s, %s', part_type, s_th)
                        if part_type not in ss.keys():
                            ss.update({part_type: s_th})
                        else:
                            if state in ss[part_type].keys():
                                ss[part_type][state].update(th)
                            else:
                                ss[part_type].update(s_th)
        self.logger.info('importing component link database done!')


class SchematicSymbol(SchematicComponent):

    def __init__(self, standard_type=None):
        SchematicComponent.__init__(self, standard_type)
        self.id = ''
        self.state = []
        self.dni = False
        self.site = 0


class SchematicNode:

    def __init__(self, symbol_and_pins):
        (self.symbol, self.pin_number, self.pin_name) = symbol_and_pins
        self.tuple = symbol_and_pins
        self.name = '|'.join(symbol_and_pins)
        self.dni = False
        self.site = 0

    def __str__(self):
        return self.name

    def __repr__(self):
        return '<node>:' + self.name


class SchematicEdge:

    def __init__(self, nets):
        uvi_pat = re.compile('J(\d+)_UVI80_(\d+)S\w*')
        hsd_pat = re.compile('J(\d+)_HSD_(\d+)')

        self.name = nets
        self.site = 0
        self.tester_pointer = nets.split('_')[0]

        mo_uvi = uvi_pat.match(nets)
        mo_hsd = hsd_pat.match(nets)
        if mo_uvi:
            self.tester_channel = str(mo_uvi.group(1)) + '.sense' + str(mo_uvi.group(2))
        elif mo_hsd:
            self.tester_channel = str(mo_hsd.group(1)) + '.ch' + str(mo_hsd.group(2))
        else:
            self.tester_channel = ''



    def __str__(self):
        return self.name

    def __repr__(self):
        return '<edge>: ' + self.name
