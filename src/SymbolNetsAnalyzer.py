import re
import logging
from src.SchemComponent import SpecialSymbols, SpecialNets


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

    def compile(self, obj_path):
        """Setting a path as the reference for is_multi_site_ok.
        :param obj_path: list of list of nodes and edge.
        """
        self.path_reference = self.__mask_symbol_and_nets_identifier(obj_path)

        self.logger.debug('original reference path:')
        [self.logger.debug('%s', x) for x in obj_path]

        self.logger.debug('masked reference path:')
        [self.logger.debug('%s', x) for x in self.path_reference]

    def is_multi_site_ok(self, path):
        """Comparing one path with a reference path.
        :param path: list of list of nodes and edge.
        """
        self.path_under_test = self.__mask_symbol_and_nets_identifier(path)

        reference = set(map(tuple, self.path_reference))
        response = set(map(tuple, self.path_under_test))

        if reference == response:
            self.logger.debug('multi site check: %s PASSED', path[0][0])
            return True
        else:
            if len(reference) != len(response):
                self.logger.warn('multi site check: %s FAILED, number of path mismatch', path[0][0])
            else:
                self.logger.warn('multi site check: %s FAILED, component mismatch', path[0][0])

            for i in range(len(response)):
                if self.path_under_test[i] not in self.path_reference:
                    self.logger.warn('no match found: %s', str(path[i]))
            return False

    def get_uvi_force_sense_merging_point(self, symbol_dict, nets_dict):
        # self.logger.setLevel(logging.DEBUG)
        pat_uvi_f = re.compile('(J\d{1,2}_UVI80_\d{1,2})S(\w*)', re.I)

        no_list = self.connector_symbols.copy()
        no_list.extend(self.device_symbols)

        uvi_forces = [x for x in nets_dict.keys() if pat_uvi_f.match(x)]

        ok_list = []
        for uvi_force in uvi_forces:
            symbols = [x[0] for x in nets_dict[uvi_force] if x[0] not in no_list]
            prefix = pat_uvi_f.match(uvi_force).group(1)
            posfix = pat_uvi_f.match(uvi_force).group(2)
            uvi_sense = prefix + 'F' + posfix

            merging_symbol = (uvi_force, uvi_sense, '[PART_NOT_FOUND]', 'DNI: N.A.')
            for symbol in symbols:
                nets_at_symbol = list(symbol_dict[symbol].pins.values())
                if uvi_force in nets_at_symbol and uvi_sense in nets_at_symbol:
                    merging_symbol = (uvi_force, uvi_sense, symbol, 'DNI: ' + str(symbol_dict[symbol].dni))
                    self.logger.debug(merging_symbol)
            ok_list.append(merging_symbol)

        bad_list = [x for x in ok_list if '[PART_NOT_FOUND]' in x or 'True' in x[3]]

        # self.logger.setLevel(logging.INFO)
        if bad_list:
            for x in bad_list:
                self.logger.warn('FORCE_SENSE not connected at %s -- %s, %s %s', x[0], x[1], x[2], x[3])

        return ok_list

    def get_path_to_nets(self, path, the_nets):
        # self.logger.setLevel(logging.DEBUG)
        all_nets_in_path = [x[2].name for x in path]
        occurrence = all_nets_in_path.count(the_nets)

        all_path_to_plane = []
        if occurrence == 0:
            self.logger.warn('No path from %s to %s', path[0][0].name, the_nets)
        else:
            matches_indexes = (i for i, x in enumerate(all_nets_in_path) if x == the_nets)
            for index in matches_indexes:
                self.logger.debug('-- searching connection to %s, starting [%s] --', the_nets, index)
                path_to_plane = []
                z = path[index][1].name
                # TODO try reveresed
                for i in range(index, -1, -1):
                    if path[i][1].name == z:
                        self.logger.debug('recording: [%s] %s', i, path[i])
                        path_to_plane.insert(0, path[i])
                        z = path[i][0].name
                    else:
                        self.logger.debug('ignoring: [%s] %s', i, path[i])

                self.logger.debug('saving with path length: %s', len(path_to_plane))
                all_path_to_plane.append(path_to_plane)

        # [u for t in path_to_plane for u in t[0:1]] tails
        # [u for t in path_to_plane for u in t[1:2]] heads
        # [u for t in path_to_plane for u in t[2:3]] edges
        # self.logger.setLevel(logging.INFO)
        return all_path_to_plane

    def get_tester_nets(self, path):
        return {x[2] for x in path if x[2].tester_pointer in self.tester_symbols}

    def get_device_symbols(self, path):
        return {y for x in path for y in x[:2] if y.symbol in self.device_symbols}

    @staticmethod
    def iter_all_pins_in_symbol(symbol, oo):
        return sorted((y for x, y in oo.SYMBOL_DICT[symbol].pins.keys()))

    def __mask_symbol_and_nets_identifier(self, path):
        # self.logger.setLevel(logging.DEBUG)
        pat_symbol = re.compile('^([A-Z])+\d+[A-Z]?\|', re.I)
        pat_symbol_conn = re.compile('^J\d+([\w|]+)IO\d+', re.I)
        pat_plane = re.compile('-5V|\+5V|\+5V_RLY|AGND|P5V|P15V|N15V|N5V', re.I)
        pat_hidden = re.compile('^\$(\w*)')
        pat_site = re.compile('^S\d{1,2}(_\w*)', re.I)
        pat_udb = re.compile('^UDB\d*')
        pat_uvi = re.compile('J\d{1,2}_UVI80_\d{1,2}(\w*)', re.I)
        pat_hsd = re.compile('^J\d{1,2}_HSD_\d{1,3}', re.I)
        pat_common = re.compile('(\w*)\d*$')

        outer_list = []
        for x in path:
            inner_list = []
            for y in x[0:2]:
                if y.symbol in self.connector_symbols:
                    z = pat_symbol_conn.sub('J##|##|IO##', y.name)
                else:
                    z = pat_symbol.sub(self.__replace_last_symbol_char, y.name)
                self.logger.debug('symbol: ' + y.name + ' --> ' + z)
                inner_list.append(z)
            inner_list.append(x[2])
            outer_list.append(inner_list)

        final_list = []
        for t in outer_list:
            u = t[2].name

            if pat_plane.search(u):
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

            final_list.append([t[0], t[1], v])
        # self.logger.setLevel(logging.INFO)
        return final_list

    @staticmethod
    def __replace_last_symbol_char(match_obj):
        if re.search('[a-z]+[0-9]+\|', match_obj.group(0), re.I):
            return re.sub('([a-zA-Z]+)[0-9]+\|', '\\1##|', match_obj.group(0))
        else:
            return re.sub('([a-zA-Z]+[0-9]+)[a-zA-Z]+\|', '\\1#|', match_obj.group(0))
