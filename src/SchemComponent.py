import logging
import re

from collections import defaultdict


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
        # s_th = defaultdict(dict)
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
                    # s_th[state] = {tail: heads}

                    if part_type and state and tail:
                        self.logger.debug('reading... %s, %s', part_type, s_th)
                        # TODO consider ChainMap or defaultdict(lambda: defaultdic(dict))
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

    def __repr__(self):
        return '<symbol> ' + self.id


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
        dc30_pat = re.compile('J(\d+)_DC30_(\d+)')

        self.name = nets
        self.site = 0
        self.tester_board = nets.split('_')[0]

        mo_uvi = uvi_pat.match(nets)
        mo_hsd = hsd_pat.match(nets)
        mo_dc30 = dc30_pat.match(nets)
        if mo_uvi:
            self.pin_channel = '.sense'.join([str(mo_uvi.group(1)), str(mo_uvi.group(2))])
            self.pin_type = 'DCVI'
        elif mo_hsd:
            self.pin_channel = '.ch'.join([str(mo_hsd.group(1)), str(mo_hsd.group(2))])
            self.pin_type = 'I/O'
        elif mo_dc30:
            self.pin_channel = '.sense'.join([str(mo_dc30.group(1)), str(mo_dc30.group(2))])
            self.pin_type = 'DCVI'
        else:
            self.pin_channel = ''
            self.pin_type = ''

    def __str__(self):
        return self.name

    def __repr__(self):
        return '<edge>: ' + self.name


class SchematicPath(SpecialSymbols, SpecialNets):
    """consist of a collection of links"""

    def __init__(self, path, analyzer_obj):
        SpecialSymbols.__init__(self)
        SpecialNets.__init__(self)
        self.path = path
        self.origin = path[0].tail
        self.subset = defaultdict(list)
        self.az = analyzer_obj

        self.iter_devices = (node for link in path for node in link.nodes if node.symbol in self.device_symbols)
        self.iter_testers = (link.edge for link in path if link.edge.tester_board in self.tester_symbols)

        self.populate_subset()

    def populate_subset(self):
        # az = PathAnalyzer()
        for channel in self.iter_testers:
            self.subset[channel.name].extend(self.az.get_path_to_nets(self, channel.name))

        for plane in self.plane:
            to_plane = self.az.get_path_to_nets(self, plane)
            if to_plane:
                self.subset[plane].extend(to_plane)


class SchematicLink(SpecialSymbols, SpecialNets):
    """consist of (node, node, edge)"""

    def __init__(self, link: tuple):
        SpecialSymbols.__init__(self)
        SpecialNets.__init__(self)

        if len(link) != 3:
            raise ValueError

        self.link = link
        self.tail, self.head, self.edge = link
        self.nodes = [self.tail, self.head]

    def __repr__(self):
        return '<link>: ' + ' -- '.join([self.tail.name, self.edge.name, self.head.name])
