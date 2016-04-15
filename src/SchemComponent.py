import logging
import re
import json

from collections import defaultdict


class SpecialSymbols:

    def __init__(self):
        self.connector_symbols = ['J' + str(t) for t in range(1, 33)]
        self.device_symbols = ['X' + str(t) for t in range(16)]
        self.tester_symbols = ['J' + str(t) for t in range(0, 54, 2)]
        self.plane_symbols = ['[AGND]', '[+5V]', '[-5V]']
        self.terminal_symbols = ['[WARNING]', '[device]', '[tester]']

        # self.uvi80 = [BoardUVI80(str(x)) for x in [4, 6, 8, 10, 12, 18, 20, 22]]
        # self.upin1600 = [BoardUPIN1600(str(x)) for x in [0, 14, 16]]
        # self.dc30 = [BoardDC30(str(x)) for x in [2]]


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

    component_links = {}
    known_comp_types = []

    def __init__(self, comp_type=None):
        pin_pat = re.compile('\((\w+)[,\s]+(\w+)\)')
        self.logger = logging.getLogger(__name__)
        self.type = ''
        self.links = defaultdict(dict)
        self.pins = {}

        if not self.component_links:
            self.logger.info('importing component link database')
            self.import_standard_link()
            self.get_known_comp_types()

        if comp_type in self.known_comp_types:

            self.logger.debug('known comp_type: %s' % comp_type)
            x = self.component_links['records']
            for c in x:
                if comp_type in c['component']:
                    for state, links in c['links'].items():
                        for m, n in links.items():
                            pin_num = pin_pat.match(m).group(1)
                            pin_name = pin_pat.match(m).group(2)
                            linker = (pin_num, pin_name)

                            if n:
                                pin_num = pin_pat.match(n).group(1)
                                pin_name = pin_pat.match(n).group(2)
                                linked = (pin_num, pin_name)
                            else:
                                linked = None

                            self.links[state].update({linker: linked})

                    # TODO: ugly. should be able to automatically detect list of pins.
                    if c['name'] in ['plane', 'terminal']:
                        self.pins.update({
                            ('00', 'plane'): None
                        })
        else:
            self.logger.warn('unknown comp_type: %s' % comp_type)

    @classmethod
    def import_standard_link(cls, input_json='../config/component_links.json'):

        with open(input_json, encoding='utf-8') as json_file:
            cls.component_links = json.loads(json_file.read())

    @classmethod
    def get_known_comp_types(cls):

        cls.known_comp_types = [y for x in cls.component_links['records'] for y in x['component']]


class SchematicSymbol(SchematicComponent):

    def __init__(self, comp_type=None):
        self.logger = logging.getLogger(__name__)
        # self.logger.debug('comp type: %s', comp_type)
        SchematicComponent.__init__(self, comp_type)
        self.id = ''
        self.state = []
        self.dni = False
        self.active = False

    def __repr__(self):
        return '<symbol> ' + self.id


class SchematicPath(SpecialSymbols, SpecialNets):
    """consist of a collection of links"""

    def __init__(self, links: list, analyzer_obj):
        SpecialSymbols.__init__(self)
        SpecialNets.__init__(self)
        self.links = links
        self.origin = links[0].tail
        self.subset = defaultdict(list)
        self.az = analyzer_obj

        self.iter_devices = (node for link in links for node in link.nodes if node.symbol in self.device_symbols)
        self.iter_testers = (link.edge for link in links if link.edge.channel)

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
        self.name = nets
        self.channel = None

        board_classes = [BoardDC30, BoardUPIN1600, BoardUVI80]
        for b in board_classes:
            if b.is_this(nets):
                self.channel = b(nets)
                break

    def __str__(self):
        return self.name

    def __repr__(self):
        return '<edge>: ' + self.name


class TesterBoard:

    nets_pattern = re.compile('')

    def __init__(self, nets: str, ch_prefix: str):
        self.board_num = int(self.nets_pattern.match(nets).group(1))
        self.channel_num = int(self.nets_pattern.match(nets).group(2))
        self.ch_map = str(self.board_num) + ch_prefix + str(self.channel_num)

    @classmethod
    def is_this(cls, nets):
        return cls.nets_pattern.match(nets)


class BoardUVI80(TesterBoard):
    board_type = 'DC-07'
    ch_type = 'DCVI'
    nets_pattern = re.compile('J(\d+)_UVI80_(\d+)\w*')

    def __init__(self, nets):
        self.channel_prefix = '.sense'
        TesterBoard.__init__(self, nets, self.channel_prefix)


class BoardUPIN1600(TesterBoard):
    board_type = 'HSD'
    ch_type = 'I/O'
    nets_pattern = re.compile('J(\d+)_HSD_(\d+)')

    def __init__(self, nets):
        self.channel_prefix = '.ch'
        TesterBoard.__init__(self, nets, self.channel_prefix)
        self.pa_channels = []
        self.dssc_channels = []


class BoardDC30(TesterBoard):
    board_type = 'DC30'
    ch_type = 'DCVI'
    nets_pattern = re.compile('J(\d+)_DC30_(\d+)')

    def __init__(self, nets):
        self.channel_prefix = '.sense'
        TesterBoard.__init__(self, nets, self.channel_prefix)
