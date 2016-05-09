from src.SchemComponent import *
from collections import defaultdict


class PathAnalyzer(SpecialSymbols, SpecialNets):

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        SpecialSymbols.__init__(self)
        SpecialNets.__init__(self)

        self.path_reference = []
        self.path_under_test = []

    def compile(self, pathway: SchematicPath):
        """Setting a path as the reference for is_multi_site_ok.
        :param pathway: list of list of nodes and edge.
        """

        if not pathway:
            raise ValueError

        self.path_reference = self.__mask_symbol_and_nets_identifier(pathway)

        self.logger.debug('original reference path:')
        [self.logger.debug('%s', x) for x in pathway.links]

        self.logger.debug('masked reference path:')
        [self.logger.debug('%s', x) for x in self.path_reference]

    def is_multi_site_ok(self, pathway: SchematicPath):
        """Comparing one path with a reference path.
        :param pathway: list of list of nodes and edge.
        """

        if not pathway:
            raise ValueError

        self.path_under_test = self.__mask_symbol_and_nets_identifier(pathway)

        reference = set(self.path_reference)
        response = set(self.path_under_test)

        if reference == response:
            self.logger.debug('multi site check: %s PASSED', pathway.origin.name)
            return True
        else:
            if len(reference) != len(response):
                self.logger.warn('multi site check: %s FAILED, number of path mismatch', pathway.origin.name)
            else:
                self.logger.warn('multi site check: %s FAILED, possible component mismatch', pathway.origin.name)

            for i, p in enumerate(response):
                if p not in reference:
                    self.logger.debug('no match found: [%s] %s', i, p)
            return False

    @staticmethod
    def __mask_symbol_and_nets_identifier(pathway: SchematicPath):
        outer_list = []
        for link in pathway.links:
            inner_tuple = tuple([y.masked_name for y in link.items])
            outer_list.append(inner_tuple)
        return outer_list

    @staticmethod
    def get_uvi_force_sense(oo):
        nets_dict = oo.NETS_DICT
        pat_uvi = re.compile('(J\d{1,2}_UVI80_\d{1,2})(\w*)', re.I)
        tester_resources = [n for n in nets_dict if SchematicEdge(n).channel]
        uvi_resources = sorted([n for n in tester_resources if pat_uvi.match(n)])

        checks = defaultdict(list)
        for uvi_resource in uvi_resources:
            mo = pat_uvi.match(uvi_resource)
            checks[mo.group(1)].append(mo.group(2))
        return checks


class ExplorerUtilities:

    def iter_all_pins_in_symbol(self, symbol):
        return sorted((y for x, y in self.SYMBOL_DICT[symbol].pins.keys()))

    def iter_all_device_symbols(self):
        return sorted((x for x in self.SYMBOL_DICT.keys() if x in self.device_symbols))

    def search_pins_or_nets(self, search_str, symbol='X0'):
        pins = sorted([SchematicNode((symbol, p[0], p[1])) for p in self.SYMBOL_DICT[symbol].pins if search_str in p[1]],
                      key=lambda x: x.name)
        nets = sorted([SchematicEdge(n) for n in self.NETS_DICT if search_str in n], key=lambda x: x.name)
        return {'pins': pins, 'nets': nets}

    def get_nodes_from_symbol_and_nets(self, symbol, nets):
        return sorted([SchematicNode(x) for x in self.NETS_DICT[nets] if x[0] in symbol], key=lambda x: x.pin_name)

    def get_nodes_from_symbol_and_pin(self, symbol, pin):
        lst = self.SYMBOL_DICT[symbol].pins.keys()
        nodes = [SchematicNode((symbol, x, y)) for x, y in lst if x == pin or y == pin]

        if len(nodes) > 1:
            self.logger.warn('get_nodes_with_pin: multiple nodes found on %s with pin = %s', symbol, pin)
        if len(nodes) == 0:
            self.logger.error('get_nodes_with_pin: zero nodes found on %s with pin = %s', symbol, pin)
            raise ValueError

        self.logger.debug('get_nodes_with_pin: %s' % str(nodes))
        return nodes[0]

    def get_nodes_from_nets(self, nets):
        return sorted([SchematicNode(x) for x in self.NETS_DICT[nets]], key=lambda x: x.symbol)

    def get_nets_which_contain(self, text):
        return sorted([x for x in self.NETS_DICT if text in x])

    def get_nets_count(self):
        return sorted([(x, len(y)) for x, y in self.NETS_DICT.items()], key=lambda x: x[1], reverse=True)
