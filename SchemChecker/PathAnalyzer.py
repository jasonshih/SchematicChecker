import re

    # regular expression, to detect X0, R43B, but not S0_GPIO6:  '^\w\d*\w?\|'
    # regular expression, to detect 12 in X12: '[0-9]*$'
    # regular expression, to detect B in R43B: '[a-zA-Z]*$'

'''
{'X0': [['X0|90|GPIO6', 'R43A|1|POS', 'S0_GPIO6'],
  ['R43A|1|POS', 'R43A|2|NEG', 'na'],
  ['R43A|2|NEG', 'J6|R12|IO68', 'J16_HSD_156']],
 'X1': [['X1|90|GPIO6', 'R43B|1|POS', 'S1_GPIO6'],
  ['R43B|1|POS', 'R43B|2|NEG', 'na'],
  ['R43B|2|NEG', 'J8|R12|IO68', 'J16_HSD_188']],
 'X2': [['X2|90|GPIO6', 'R43C|1|POS', 'S2_GPIO6'],
  ['R43C|1|POS', 'R43C|2|NEG', 'na'],
  ['R43C|2|NEG', 'J26|R12|IO68', 'J16_HSD_212']]}
'''

class PathCruncher(object):

    def __init__(self):
        self.path_reference = {}
        self.path_under_test = {}
        self.path_re = []

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
        pass

    def is_multi_site_ok(self):
        symbol_match = re.compile('^[a-z]+\d+[a-z]?\|', re.I)

        outer_list = []
        for x in self.path_reference['X0']:
            inner_list = []
            for y in x:
                z = re.sub('^[A-Z]+\d+[A-Z]?\|', self.replace_last_symbol_char, y)
                inner_list.append(z)
            outer_list.append(inner_list)
        outer_list = []

        for x in self.path_reference['X0']:
            inner_list = []
            for y in x:
                pass
            # OPAMP_POS_103	COMMON      remove last numbers
            # $100N1742	HIDDEN          start with $, random
            # J0_HSD_107	HSD
            # -5V	PLANE
            # +5V	PLANE
            # +5V_RLY	PLANE
            # AGND	PLANE
            # N15V	PLANE
            # N5V	PLANE
            # UDB108	UDB
            # J10_UVI80_59F_A	UVI
            # J10_UVI80_59S_B	UVI
            # J10_UVI80_5F	UVI
            # J10_UVI80_5S	UVI
        pass

    def replace_last_symbol_char(self, match_obj):
        return re.sub('[A-Z0-9]?\|', '#|', match_obj.group(0))


