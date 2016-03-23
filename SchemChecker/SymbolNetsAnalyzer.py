import re
import logging
from SchemChecker.SchemComponent import SpecialSymbols, SpecialNets


class PathTester(SpecialSymbols, SpecialNets):

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        SpecialSymbols.__init__(self)
        SpecialNets.__init__(self)

        self.path_reference = []
        self.path_under_test = []

        self.path_reference = {
            'X0': [['X0|90|GPIO6', 'R43A|1|POS', 'S0_GPIO6'],
                   ['R43A|1|POS', 'R43A|2|NEG', 'na'],
                   ['R43A|2|NEG', 'J6|R12|IO68', 'J16_HSD_156']]
        }

        self.path_under_test = {
            'X1': [['X1|90|GPIO6', 'R43B|1|POS', 'S1_GPIO6'],
                   ['R43B|1|POS', 'R43B|2|NEG', 'na'],
                   ['R43B|2|NEG', 'J8|R12|IO68', 'J16_HSD_188']],
            'X2': [['X2|90|GPIO6', 'R43C|1|POS', 'S2_GPIO6'],
                   ['R43C|1|POS', 'R43C|2|NEG', 'na'],
                   ['R43C|2|NEG', 'J26|R12|IO68', 'J16_HSD_212']]
        }

    def compile(self, path):

        self.path_reference = self.__mask_symbol_and_nets_identifier(path)

        print('original reference path:')
        for x in path:
            print(', '.join([x[0].name, x[1].name, x[2].name]))

        print('')
        print('masked reference path:')
        for x in self.path_reference:
            print(x)

    def is_multi_site_ok(self, path):

        self.path_under_test = self.__mask_symbol_and_nets_identifier(path)

        reference = set(map(tuple, self.path_reference))
        response = set(map(tuple, self.path_under_test))

        if reference == response:
            print('OK: multi site compare')
            return True
        else:
            if self.path_reference.__len__() != self.path_under_test.__len__():
                print('WARNING: different number of path')
                for i in range(self.path_under_test.__len__()):
                    if self.path_under_test[i] in self.path_reference:
                        pass
                    else:
                        print('no match found: ' + str(self.path_under_test[i]))

            else:
                print('WARNING: same number of path but not equal')
                for i in range(self.path_under_test.__len__()):
                    if self.path_under_test[i] not in self.path_reference:
                        print(str(i) + ' no match found: ' + str(self.path_under_test[i]))

            return False

    def get_uvi_force_sense_merging_point(self, SYMBOL_DICT, NETS_DICT):
        # self.logger.setLevel(logging.DEBUG)
        pat_uvi_f = re.compile('(J\d{1,2}_UVI80_\d{1,2})S(\w*)', re.I)

        no_list = self.connector_symbols.copy()
        no_list.extend(self.device_symbols)

        uvi_forces = [x for x in NETS_DICT.keys() if pat_uvi_f.match(x)]

        ok_list = []
        for uvi_force in uvi_forces:
            symbols = [x[0] for x in NETS_DICT[uvi_force] if x[0] not in no_list]
            prefix = pat_uvi_f.match(uvi_force).group(1)
            posfix = pat_uvi_f.match(uvi_force).group(2)
            uvi_sense = prefix + 'F' + posfix

            merging_symbol = (uvi_force, uvi_sense, '[PART_NOT_FOUND]', 'DNI: N.A.')
            for symbol in symbols:
                nets_at_symbol = list(SYMBOL_DICT[symbol].pins.values())
                if uvi_force in nets_at_symbol and uvi_sense in nets_at_symbol:
                    merging_symbol = (uvi_force, uvi_sense, symbol, 'DNI: ' + str(SYMBOL_DICT[symbol].dni))
                    self.logger.debug(merging_symbol)
            ok_list.append(merging_symbol)

        bad_list = [x for x in ok_list if '[PART_NOT_FOUND]' in x or 'True' in x[3]]

        # self.logger.setLevel(logging.INFO)
        if bad_list:
            for x in bad_list:
                self.logger.warn('FORCE_SENSE not connected at %s -- %s, %s %s', x[0], x[1], x[2], x[3])

        return ok_list

    def is_connected_to_other_sites(self, path):
        pass

    def get_path_to_plane(self, path, nets_to_plane):

        path_to_gnd = []
        nets = [x[2].name for x in path]
        occurrence = nets.count(nets_to_plane)

        all_path_to_plane = []
        if occurrence == 0:
            print('OK: no connections to ground')

        else:
            matches_indexes = (i for i, x in enumerate(nets) if x == nets_to_plane)
            for index in matches_indexes:
                z = self.plane[nets_to_plane]
                for i in range(index, 0, -1):
                    if path[i][1].name == z:
                        path_to_gnd.insert(0, path[i])
                        z = path[i][0].name
                all_path_to_plane.append(path_to_gnd)

        symbols = [str(z) for x in all_path_to_plane for y in x for z in y[:2]]
        seen = set()
        cleaned_symbols = [x for x in symbols if not (x in seen or seen.add(x))]

        return cleaned_symbols

    def get_tester_nets(self, path):
        return {x[2] for x in path if x[2].tester_pointer in self.tester_symbols}

    def get_device_symbols(self, path):
        return {y for x in path for y in x[:2] if y.symbol in self.device_symbols}

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
                # TODO differentiate connector symbols
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
            # tail = t[0].split('|')[0]
            # head = t[1].split('|')[0]
            # tailhead = '_'.join([tail, head])

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
            # print('nets: '+ u + ' --> ' + v)

            final_list.append([t[0], t[1], v])
        # self.logger.setLevel(logging.INFO)
        return final_list

    @staticmethod
    def __replace_last_symbol_char(match_obj):
        if re.search('[a-z]+[0-9]+\|', match_obj.group(0), re.I):
            return re.sub('([a-zA-Z]+)[0-9]+\|', '\\1##|', match_obj.group(0))
        else:
            return re.sub('([a-zA-Z]+[0-9]+)[a-zA-Z]+\|', '\\1#|', match_obj.group(0))

    #
    # def debug_log(f):
    #     def decorator():
    #         logging.basicConfig(level=logging.DEBUG)
    #         f()
    #         logging.basicConfig(level=logging.INFO)
