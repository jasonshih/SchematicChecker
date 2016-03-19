import re


class PathCruncher(object):

    def __init__(self):
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

    def mask_symbol_and_nets_identifier(self, path):
        pat_symbol = re.compile('^([A-Z])+\d+[A-Z]?\|', re.I)
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
                z = pat_symbol.sub(self.replace_last_symbol_char, y)
                # print('symbol: ' + y + ' --> ' + z)
                inner_list.append(z)
            inner_list.append(x[2])
            outer_list.append(inner_list)

        final_list = []
        for t in outer_list:
            u = t[2]
            v = None
            tail = t[0].split('|')[0]
            head = t[1].split('|')[0]
            tailhead = '_'.join([tail, head])

            if pat_plane.search(u):
                v = u
            elif pat_hidden.search(u):
                v = pat_hidden.sub(r'hidden_@' + tailhead, u)
            elif pat_site.search(u):
                v = pat_site.sub(r'S##\1_@' + tailhead, u)
            elif pat_udb.search(u):
                v = pat_udb.sub(r'UDB##_@' + tailhead, u)
            elif pat_uvi.search(u):
                v = pat_uvi.sub(r'J##_UVI80_##\1_@' + tailhead, u)
            elif pat_hsd.search(u):
                v = pat_hsd.sub(r'J##_HSD_###_@' + tailhead, u)
            elif pat_common.search(u):
                v = pat_common.sub(r'\1_@' + tailhead, u)
            else:
                v = u
                print('WARNING: unknown nets type')
            # print('nets: '+ u + ' --> ' + v)

            final_list.append([t[0], t[1], v])
        return final_list

    def create_reference(self, path):

        self.path_reference = self.mask_symbol_and_nets_identifier(path)
        for x in self.path_reference:
            print(x)

    def set_path_under_test(self, path):

        self.path_under_test = self.mask_symbol_and_nets_identifier(path)

    def is_multi_site_ok(self):

        if self.path_reference == self.path_under_test:
            print('OK: all good')
            return True
        else:
            if self.path_reference.__len__() != self.path_under_test.__len__():
                print('WARNING: different number of path')
            else:
                print('WARNING: same number of path but not equal')
                for i in range(self.path_reference.__len__()):
                    if self.path_reference[i] == self.path_under_test[i]:
                        print('actually it\'s ok')
                    else:
                        print(str(i) +': ' + str(self.path_reference[i]))
                        print(str(i) +': ' + str(self.path_under_test[i]))
            return False

    def replace_last_symbol_char(self, match_obj):

        if re.search('[a-z]+[0-9]+\|', match_obj.group(0), re.I):
            return re.sub('([a-zA-Z]+)[0-9]+\|', '\\1##|', match_obj.group(0))
        else:
            return re.sub('([a-zA-Z]+[0-9]+)[a-zA-Z]+\|', '\\1#|', match_obj.group(0))
