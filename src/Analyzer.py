# import re
# import logging
from src.SchemComponent import *
from collections import defaultdict


class DebugLog:

    def __init__(self, func):
        self.func = func

    def __call__(self, *args, **kwargs):
        print('start dec')
        self.func(self, *args, **kwargs)
        print('end dec')


class PathAnalyzer(SpecialSymbols, SpecialNets):

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        SpecialSymbols.__init__(self)
        SpecialNets.__init__(self)

        self.path_reference = []
        self.path_under_test = []

    def compile(self, pathway):
        """Setting a path as the reference for is_multi_site_ok.
        :param pathway: list of list of nodes and edge.
        """

        if not pathway:
            raise ValueError

        self.path_reference = self.__mask_symbol_and_nets_identifier(pathway)

        self.logger.debug('original reference path:')
        [self.logger.debug('%s', x) for x in pathway.path]

        self.logger.debug('masked reference path:')
        [self.logger.debug('%s', x) for x in self.path_reference]

    def is_multi_site_ok(self, pathway):
        """Comparing one path with a reference path.
        :param pathway: list of list of nodes and edge.
        """

        if not pathway:
            raise ValueError

        self.path_under_test = self.__mask_symbol_and_nets_identifier(pathway)

        # TODO probably broken now
        # reference = set(map(tuple, self.path_reference))
        # response = set(map(tuple, self.path_under_test))

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

    def get_uvi_force_sense(self, oo):
        nets_dict = oo.NETS_DICT
        pat_uvi = re.compile('(J\d{1,2}_UVI80_\d{1,2})(\w*)', re.I)
        tester_resources = [n for n in nets_dict if n.split('_')[0] in self.tester_symbols]
        uvi_resources = sorted([n for n in tester_resources if pat_uvi.match(n)])

        checks = defaultdict(list)
        for uvi_resource in uvi_resources:
            mo = pat_uvi.match(uvi_resource)
            checks[mo.group(1)].append(mo.group(2))
        return checks

    def get_path_to_nets(self, pathway, the_nets):
        # self.logger.setLevel(logging.DEBUG)
        # tail, head, edge = 0, 1, 2
        all_nets_in_path = [link.edge.name for link in pathway.path]
        occurrence = all_nets_in_path.count(the_nets)

        all_path_to_plane = []
        if occurrence == 0:
            self.logger.debug('No path from %s to %s', pathway.origin.name, the_nets)
        else:
            matches_indexes = (i for i, n in enumerate(all_nets_in_path) if n == the_nets)
            for index in matches_indexes:
                self.logger.debug('-- searching connection to %s, starting [%s] --', the_nets, index)
                path_to_plane = []
                z = pathway.path[index].head.name
                # TODO try reveresed
                for i in range(index, -1, -1):
                    link = pathway.path[i]
                    if link.head.name == z:
                        self.logger.debug('recording: [%s] %s', i, link)
                        path_to_plane.insert(0, link)
                        z = link.tail.name
                    else:
                        self.logger.debug('ignoring: [%s] %s', i, link)

                self.logger.debug('saving with path length: %s', len(path_to_plane))
                all_path_to_plane.append(path_to_plane)

        # [u for t in path_to_plane for u in t[0:1]] tails
        # [u for t in path_to_plane for u in t[1:2]] heads
        # [u for t in path_to_plane for u in t[2:3]] edges
        # self.logger.setLevel(logging.INFO)
        return all_path_to_plane

    @staticmethod
    def iter_all_pins_in_symbol(symbol, oo):
        return sorted((y for x, y in oo.SYMBOL_DICT[symbol].pins.keys()))

    @staticmethod
    def iter_all_device_symbols(oo):
        return sorted((x for x in oo.SYMBOL_DICT.keys() if x in oo.device_symbols))

    @staticmethod
    def __replace_last_symbol_char(match_obj):
        if re.search('[a-z]+[0-9]+\|', match_obj.group(0), re.I):
            return re.sub('([a-zA-Z]+)[0-9]+\|', '\\1##|', match_obj.group(0))
        else:
            return re.sub('([a-zA-Z]+[0-9]+)[a-zA-Z]+\|', '\\1#|', match_obj.group(0))

    def __mask_symbol_and_nets_identifier(self, pathway):
        # self.logger.setLevel(logging.DEBUG)
        # TODO consider globalizing these.
        pat_symbol = re.compile('^([A-Z])+\d+[A-Z]?\|', re.I)
        pat_symbol_conn = re.compile('^J\d+([\w|]+)IO\d+', re.I)
        pat_hidden = re.compile('^\$(\w*)')
        pat_site = re.compile('^S\d{1,2}(_\w*)', re.I)
        pat_udb = re.compile('^UDB\d*')
        pat_uvi = re.compile('J\d{1,2}_UVI80_\d{1,2}(\w*)', re.I)
        pat_hsd = re.compile('^J\d{1,2}_HSD_\d{1,3}', re.I)
        pat_common = re.compile('(\w*)\d*$')

        outer_list = []
        for link in pathway.path:
            inner_list = []
            for y in link.nodes:
                if y.symbol in self.connector_symbols:
                    z = pat_symbol_conn.sub('J##|##|IO##', y.name)
                else:
                    z = pat_symbol.sub(self.__replace_last_symbol_char, y.name)
                self.logger.debug('symbol: ' + y.name + ' --> ' + z)
                inner_list.append(z)
            inner_list.append(link.edge)
            outer_list.append(inner_list)

        final_list = []
        for t in outer_list:
            u = t[2].name

            if u in self.plane:
                v = u
            elif pat_hidden.search(u):
                v = pat_hidden.sub(r'hidden', u)
            elif pat_site.search(u):
                v = pat_site.sub(r'S##\1', u)
            elif pat_udb.search(u):
                v = pat_udb.sub(r'UDB##', u)
            elif pat_uvi.search(u):
                v = pat_uvi.sub(r'J##_UVI80_##\1', u)
            elif pat_hsd.search(u):
                v = pat_hsd.sub(r'J##_HSD_###', u)
            elif pat_common.search(u):
                v = pat_common.sub(r'\1', u)
            else:
                v = u
                self.logger.warn('unknown nets type: %s', v)

            final_list.append((t[0], t[1], v))
        # self.logger.setLevel(logging.INFO)
        return final_list

    def get_tester_nets(self, pathway: SchematicPath):
        self.logger.warn('deprecating get_get_device_symbols, use pathway.subset instead')
        # TODO consider renaming it to iter_tester_nets_at_path
        return {link.edge for link in pathway.path if link.edge.tester_board in self.tester_symbols}

    def get_device_symbols(self, pathway: SchematicPath):
        # TODO consider renaming it to iter_device_symbols_at_path
        self.logger.warn('deprecating get_get_device_symbols, use pathway.subset instead')
        return {node for link in pathway.path for node in link.nodes if node.symbol in self.device_symbols}
