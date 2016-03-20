import re
from SchemChecker.SchemComponent import SpecialSymbols


class PathTester(SpecialSymbols):

    def __init__(self):
        SpecialSymbols.__init__(self)

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
            print(x)

        print('')
        print('masked reference path:')
        for x in self.path_reference:
            print(x)

    def is_multi_site_ok(self, path):

        self.path_under_test = self.__mask_symbol_and_nets_identifier(path)

        if self.path_reference == self.path_under_test:
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
                    if self.path_reference[i] == self.path_under_test[i]:
                        pass
                    else:
                        print(str(i) + ' ref: ' + str(self.path_reference[i]))
                        print(str(i) + ' res: ' + str(self.path_under_test[i]))
            return False

    def is_force_sense_connected(self, path):
        # TODO improve the force_sense detection logic
        pat_uvi_f = re.compile('J\d{1,2}_UVI80_\d{1,2}F(\w*)', re.I)
        pat_uvi_s = re.compile('J\d{1,2}_UVI80_\d{1,2}S(\w*)', re.I)

        f = False
        s = False

        for p in self.get_tester_nets(path):
            if pat_uvi_f.match(p) and not f:
                f = True
            if pat_uvi_s.match(p) and not s:
                s = True

        pass

    def is_connected_to_other_sites(self, path):
        pass

    @staticmethod
    def get_path_to_ground(path, ground_nets):
        # TODO consider get path to generic plane

        path_to_gnd = []
        nets = [x[2] for x in path]
        gnd_count = nets.count(ground_nets)

        # TODO improve logic to find multiple AGND connections.
        if gnd_count == 0:
            print('OK: no connections to ground')

        if gnd_count == 1:
            z = '[AGND]|00|plane'
            for i in range(len(path) - 1, 0, -1):
                if path[i][1] == z:
                    path_to_gnd.insert(0, path[i])
                    z = path[i][0]

        if gnd_count > 1:
            print('WARNING: more than 1 ground connections found')

        return path_to_gnd

    def get_path_to_supply(self, path):
        pass

    def get_tester_nets(self, path):
        return {x[2] for x in path if x[2].split('_')[0] in self.tester_symbols}

    def get_device_symbols(self, path):
        return {y for x in path for y in x[:2] if y.split('|')[0] in self.device_symbols}

    def __mask_symbol_and_nets_identifier(self, path):
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
                if y.split('|')[0] in self.connector_symbols:
                    z = pat_symbol_conn.sub('J##|##|IO##', y)
                else:
                    z = pat_symbol.sub(self.__replace_last_symbol_char, y)
                # print('symbol: ' + y + ' --> ' + z)
                inner_list.append(z)
            inner_list.append(x[2])
            outer_list.append(inner_list)

        final_list = []
        for t in outer_list:
            u = t[2]
            # tail = t[0].split('|')[0]
            # head = t[1].split('|')[0]
            # tailhead = '_'.join([tail, head])

            if pat_plane.search(u):
                v = u
            elif pat_hidden.search(u):
                v = pat_hidden.sub(r'hidden', u)
                # v = pat_hidden.sub(r'hidden_@' + tailhead, u)
            elif pat_site.search(u):
                v = pat_site.sub(r'S##\1', u)
                # v = pat_site.sub(r'S##\1_@' + tailhead, u)
            elif pat_udb.search(u):
                v = pat_udb.sub(r'UDB##', u)
                # v = pat_udb.sub(r'UDB##_@' + tailhead, u)
            elif pat_uvi.search(u):
                v = pat_uvi.sub(r'J##_UVI80_##\1', u)
                # v = pat_uvi.sub(r'J##_UVI80_##\1_@' + tailhead, u)
            elif pat_hsd.search(u):
                v = pat_hsd.sub(r'J##_HSD_###', u)
                # v = pat_hsd.sub(r'J##_HSD_###_@' + tailhead, u)
            elif pat_common.search(u):
                v = pat_common.sub(r'\1', u)
                # v = pat_common.sub(r'\1_@' + tailhead, u)
            else:
                v = u
                print('WARNING: unknown nets type')
            # print('nets: '+ u + ' --> ' + v)

            final_list.append([t[0], t[1], v])
        return final_list

    @staticmethod
    def __replace_last_symbol_char(match_obj):
        if re.search('[a-z]+[0-9]+\|', match_obj.group(0), re.I):
            return re.sub('([a-zA-Z]+)[0-9]+\|', '\\1##|', match_obj.group(0))
        else:
            return re.sub('([a-zA-Z]+[0-9]+)[a-zA-Z]+\|', '\\1#|', match_obj.group(0))
