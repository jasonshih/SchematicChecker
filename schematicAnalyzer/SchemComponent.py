import logging
import re
import json

from collections import defaultdict
from functools import wraps


class LOG:

    def debug_lvl(lvl=logging.DEBUG):
        """example: @LOG.debug_lvl('DEBUG')"""
        def enable(f):
            @wraps(f)
            def wrapper(slf, *args, **kwargs):
                p, n = slf.logger.getEffectiveLevel(), lvl
                slf.logger.setLevel(n)
                y = f(slf, *args, **kwargs)
                slf.logger.setLevel(p)
                return y
            return wrapper
        return enable


class SpecialSymbols:

    def __init__(self):
        self.connector_symbols = ['J' + str(t) for t in range(1, 33)]
        self.device_symbols = ['X' + str(t) for t in range(16)]  # 16 for 16 sites
        self.tester_symbols = ['J' + str(t) for t in [4, 6, 8, 10, 12, 18, 20, 22, 0, 14, 16, 2]]
        self.plane_symbols = ['[AGND]', '[+5V]', '[-5V]', '[P5V]', '[N5V]', '[P15V]', '[N15V]', '[+5V_RLY]']
        self.terminal_symbols = ['[WARNING]', '[OTHER_SITES]']  # '[device]', '[tester]'

class SpecialNets:

    def __init__(self):
        self.special_nets = {
            'AGND': [('[AGND]', '00', 'plane')],
            '+5V': [('[+5V]', '00', 'plane')],
            '-5V': [('[-5V]', '00', 'plane')],
            '+5V_RLY': [('[+5V_RLY]', '00', 'plane')],
            'P5V': [('[P5V]', '00', 'plane')],
            'N5V': [('[N5V]', '00', 'plane')],
            'P15V': [('[P15V]', '00', 'plane')],
            'N15V': [('[N15V]', '00', 'plane')],
            '[TERMINAL]': [('[WARNING]', '00', 'terminal')],
            'unconnected': [('[WARNING]', '00', 'terminal')],
            'J2_DC30_10F': [('[OTHER_SITES]', '00', 'terminal')],
            'J2_DC30_10S': [('[OTHER_SITES]', '00', 'terminal')],
            'J2_DC30_15F': [('[OTHER_SITES]', '00', 'terminal')],
            'J2_DC30_15S': [('[OTHER_SITES]', '00', 'terminal')]
        }


class SchematicComponent:

    component_links = {}
    known_comp_types = []
    unknown_comp_types = set()

    def __init__(self, comp_type='', comp_link='../config/component_links.json'):
        pin_pat = re.compile('\((\w+)[,\s]+(\w+)\)')
        self.logger = logging.getLogger(__name__)
        self.type = comp_type
        self.links = defaultdict(dict)
        self.pins = {}
        self.unknown_links = False
        self.is_active = False

        if not self.component_links:
            self.logger.info('importing component link database')
            self.import_standard_link('/Users/cahyo/Dropbox/programming/python/SchematicChecker/config/component_links.json')
            self.get_known_comp_types()

        if comp_type in self.known_comp_types:
            # self.logger.debug('known comp_type: %s' % comp_type)
            x = self.component_links['records']
            for c in x:
                if comp_type in c['component']:
                    if c['active']:
                        self.is_active = True

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

                            self.links[state][linker] = linked

                    # TODO: ugly. should be able to automatically detect list of pins.
                    if c['name'] in ['plane', 'terminal']:
                        self.pins[('00', 'plane')] = None

        else:
            if comp_type not in self.unknown_comp_types:
                if not comp_type.startswith('['):
                    self.logger.warn('unknown comp_type: %s' % comp_type)
                self.unknown_comp_types.add(comp_type)
                self.unknown_links = True

    @classmethod
    # def import_standard_link(cls, input_json='../config/component_links.json'):
    def import_standard_link(cls, input_json):
        with open(input_json, encoding='utf-8') as json_file:
            cls.component_links = json.loads(json_file.read())

    @classmethod
    def get_known_comp_types(cls):
        cls.known_comp_types = [y for x in cls.component_links['records'] for y in x['component']]


class SchematicSymbol(SchematicComponent):

    def __init__(self, comp_type, symbol):
        self.logger = logging.getLogger(__name__)
        # self.logger.debug('comp type: %s', comp_type)
        SchematicComponent.__init__(self, comp_type)
        self.id = symbol
        self.__dni = False
        self.schematic = ''

    def set_dni(self):
        self.__dni = True

    def is_dni(self):
        return self.__dni

    def __repr__(self):
        return '<symbol> ' + self.id


class SchematicPath(SpecialSymbols, SpecialNets):
    """consist of a collection of links"""

    def __init__(self, links: list):
        self.logger = logging.getLogger(__name__)
        SpecialSymbols.__init__(self)
        SpecialNets.__init__(self)
        self.links = self.__sort_links(links)
        # self.links = links
        self.origin = self.links[0].tail
        # self.subset = defaultdict(list)

        self.iter_devices_at_links = (node for link in self.links for node in link.nodes
                                      if node.is_device)
        self.iter_testers_at_links = (link.edge for link in self.links if link.edge.channel)

        self.iter_active_components = (link for link in self.links if link.tail.is_active and link.is_internal)

    @staticmethod
    def __sort_links(links):
        head_record = []
        sorted_links = []
        x = links.pop(0)
        sorted_links.append(x)
        head_record.append(x.head.name)
        while links:
            not_found = True
            for i, lnk in enumerate(links):
                if lnk.tail.name == x.head.name:
                    x = links.pop(i)
                    sorted_links.append(x)
                    head_record.append(x.head.name)
                    not_found = False
                    break
            for i, lnk in reversed(list(enumerate(links))):
                if lnk.tail.name in head_record:
                    y = links.pop(i)
                    links.insert(0, y)
                    break
            if not_found:
                x = links.pop(0)
                sorted_links.append(x)
                head_record.append(x.head.name)
        return sorted_links

    def create_subset_path(self, the_nets):
        # self.logger.setLevel(logging.INFO)
        all_nets_in_path = [link.edge.name for link in self.links]
        occurrence = all_nets_in_path.count(the_nets)

        all_path_to_plane = []
        if occurrence == 0:
            self.logger.debug('create_subset_path: No path from %s to %s', self.origin.name, the_nets)
        else:
            matches_indexes = (i for i, n in enumerate(all_nets_in_path) if n == the_nets)
            for index in matches_indexes:
                self.logger.debug('create_subset_path: from %s to %s, starting index [%s]',
                                  self.origin.name, the_nets, index)
                path_to_plane = []
                z = self.links[index].head.name
                # TODO try reversed
                for i in range(index, -1, -1):
                    link = self.links[i]
                    if link.head.name == z:
                        # self.logger.debug('create_subset_path: recording: [%s] %s', i, link)
                        path_to_plane.insert(0, link)
                        z = link.tail.name
                    else:
                        # self.logger.debug('create_subset_path: ignoring: [%s] %s', i, link)
                        pass

                self.logger.debug('create_subset_path: saving with path length: %s', len(path_to_plane))
                all_path_to_plane.append(SchematicPath(path_to_plane))

        # self.logger.setLevel(logging.DEBUG)
        return all_path_to_plane

    def ascii_tree(self):
        # TODO: separate this to another class

        def get_val_at_nested_key(d: dict, key, is_root=True, found_vals=list):
            if is_root:
                found_vals = []

            for k, v in d.items():
                if isinstance(v, dict):
                    found_vals = get_val_at_nested_key(v, key, is_root=False, found_vals=found_vals)
                else:
                    pass

                if k == key:
                    found_vals.append(v)
                    print('{0}: {1}'.format(k, v))

            if is_root:
                return found_vals

        def set_key_at_branch(d: dict, branch, key, val=None, is_root=True, found=False):
            for k, v in d.items():
                if isinstance(v, dict):
                    found = set_key_at_branch(v, branch, key, is_root=False, found=found)
                else:
                    pass

                if k == branch:
                    if d[branch]:
                        d[branch][key] = val
                    else:
                        d[branch] = {key: val}
                    found = True

            if is_root:
                if not found:
                    d[key] = val
                return d
            else:
                return found

        def asciify(d: dict, is_root=True, al=list, lvl=0):
            if is_root:
                al = []
                lvl = 0

            if d:
                for k, v in d.items():
                    il = []
                    for i in range(lvl):
                        if i == lvl - 1:
                            il.append('`-- ')
                        else:
                            il.append('    ')
                    il.append(k)
                    al.append(il)

                    if d[k]:
                        lvl += 1
                        al = asciify(d[k], is_root=False, al=al, lvl=lvl)
                        lvl -= 1

            if is_root:
                empt_fill = '    '
                vert_fill = '|   '
                end__fill = '`-- '
                plus_fill = '+-- '

                replacement = set()
                for each_line in reversed(al):

                    to_remove = []
                    for index in replacement:
                        if each_line[index] == empt_fill:
                            each_line[index] = vert_fill
                        elif each_line[index] == end__fill:
                            each_line[index] = plus_fill
                        else:
                            to_remove.append(index)

                    while to_remove:
                        replacement.discard(to_remove.pop())

                    for i, e in enumerate(each_line):
                        if e == end__fill:
                            replacement.add(i)

                sl = [''.join(x) for x in al]

                return sl
            else:
                return al

        nested_dict = {}
        for link in sorted(self.links, key=lambda x: x.level):
            nested_dict = set_key_at_branch(nested_dict, branch=link.tail.short_name, key=link.head.short_name)

        return asciify({self.origin.short_name: nested_dict})


class SchematicLink(SpecialSymbols, SpecialNets):
    """consist of (node, node, edge)"""

    def __init__(self, link_level: tuple):
        SpecialSymbols.__init__(self)
        SpecialNets.__init__(self)

        if len(link_level) != 4:
            raise ValueError

        self.items = link_level[0:3]
        self.tail, self.head, self.edge, self.level = link_level
        self.nodes = [self.tail, self.head]
        self.is_internal = False
        self.is_connector = False

    def __repr__(self):
        return '<link>: ' + ' -- '.join([self.tail.name, self.edge.name, self.head.name])

    def __str__(self):
        star = ' *' if self.head.is_terminal else ''
        return ' --> '.join([self.tail.name, self.edge.name, self.head.name]) + star


class SchematicNode(SpecialSymbols):

    pat_symbol = re.compile('^([A-Z])+\d+[A-Z]?\|', re.I)
    pat_symbol_conn = re.compile('^J\d+([\w|]+)IO\d+', re.I)

    def __init__(self, symbol_and_pins):
        SpecialSymbols.__init__(self)
        (self.symbol, self.pin_number, self.pin_name) = symbol_and_pins
        self.tuple = symbol_and_pins
        self.name = '|'.join(symbol_and_pins)
        self.dni = False
        self.short_name = self.symbol + ' @' + self.pin_name
        self.masked_name = self.name
        self.is_device = True if self.symbol in self.device_symbols else False
        self.is_active = False
        self.is_origin = False
        self.is_terminal = False

        # TODO wrap this to another function
        if self.symbol in self.connector_symbols:
            self.masked_name = self.pat_symbol_conn.sub('J##|##|IO##', self.name)
        else:
            self.masked_name = self.pat_symbol.sub(self.__replace_last_symbol_char, self.name)

    def set_dni(self):
        self.dni = True
        self.short_name = self.symbol + ' @' + self.pin_name + ' (DNI)'

    @staticmethod
    def __replace_last_symbol_char(match_obj):
        if re.search('[a-z]+[0-9]+\|', match_obj.group(0), re.I):
            return re.sub('([a-zA-Z]+)[0-9]+\|', '\\1##|', match_obj.group(0))
        else:
            return re.sub('([a-zA-Z]+[0-9]+)[a-zA-Z]+\|', '\\1#|', match_obj.group(0))

    def __str__(self):
        return self.name

    def __repr__(self):
        return '<node>:' + self.name


class SchematicEdge(SpecialNets):

    _pat_hidden = re.compile('^\$(\w*)')
    _pat_site = re.compile('^S\d{1,2}(_\w*)', re.I)
    _pat_common = re.compile('(\w*?)\d*$')

    def __init__(self, nets):
        self.logger = logging.getLogger(__name__)
        SpecialNets.__init__(self)
        self.name = nets
        self.masked_name = nets
        self.channel = None
        self.is_plane = True if nets in self.special_nets else False

        board_classes = [BoardDC30, BoardUPIN1600, BoardUVI80, BoardUtility]
        for b in board_classes:
            if b.is_this(nets):
                self.channel = b(nets)
                break

        if nets in self.special_nets:
            self.masked_name = nets

        elif self._pat_hidden.search(nets):
            self.masked_name = self._pat_hidden.sub(r'hidden', nets)

        elif self._pat_site.search(nets):
            self.masked_name = self._pat_site.sub(r'S##\1', nets)

        elif BoardUtility.get_pat().match(nets):
            self.masked_name = BoardUtility.get_pat().sub(r'UDB##', nets)

        elif BoardUVI80.get_pat().match(nets):
            self.masked_name = BoardUVI80.get_pat().sub(r'J##_UVI80_##\3', nets)

        elif BoardDC30.get_pat().match(nets):
            self.masked_name = BoardDC30.get_pat().sub(r'J##_DC30_##\3', nets)

        elif BoardUPIN1600.get_pat().match(nets):
            self.masked_name = BoardUPIN1600.get_pat().sub(r'J##_HSD_###', nets)

        elif self._pat_common.search(nets):
            self.masked_name = self._pat_common.sub(r'\1', nets)

        else:
            self.masked_name = nets
            self.logger.warn('unknown nets type: %s', nets)

    def __str__(self):
        return self.name

    def __repr__(self):
        return '<edge>: ' + self.name


class TesterBoard:

    nets_pattern = re.compile('')

    def __init__(self, nets: str, ch_prefix: str):
        self.board_num = 0
        self.channel_num = 0
        self.parse_board_and_channel_num(nets)

        self.ch_map = str(self.board_num) + ch_prefix + str(self.channel_num)

    def parse_board_and_channel_num(self, nets):
        self.board_num = int(self.nets_pattern.match(nets).group(1))
        self.channel_num = int(self.nets_pattern.match(nets).group(2))


    @classmethod
    def is_this(cls, nets):
        return cls.nets_pattern.match(nets)

    @classmethod
    def get_pat(cls):
        return cls.nets_pattern


class BoardUVI80(TesterBoard):

    board_type = 'DC07'
    ch_type = 'DCVI'
    nets_pattern = re.compile('^J(\d{1,2})_UVI80_(\d{1,2})(\w*)')

    def __init__(self, nets):
        self.channel_prefix = '.sense'
        TesterBoard.__init__(self, nets, self.channel_prefix)


class BoardUPIN1600(TesterBoard):

    board_type = 'HSD'
    ch_type = 'I/O'
    nets_pattern = re.compile('^J(\d{1,2})_HSD_(\d{1,3})')

    def __init__(self, nets):
        self.channel_prefix = '.ch'
        TesterBoard.__init__(self, nets, self.channel_prefix)
        self.pa_channels = []
        self.dssc_channels = []


class BoardDC30(TesterBoard):

    board_type = 'DC30'
    ch_type = 'DCVI'
    nets_pattern = re.compile('^J(\d{1,2})_DC30_(\d{1,2})(\w*)')

    def __init__(self, nets):
        self.channel_prefix = '.sense'
        TesterBoard.__init__(self, nets, self.channel_prefix)


class BoardUtility(TesterBoard):

    board_type = 'Utility'
    ch_type = 'Utility'
    nets_pattern = re.compile('^UDB(\d{1,3})')

    def __init__(self, nets):
        self.channel_prefix = '.util'
        TesterBoard.__init__(self, nets, self.channel_prefix)

    def parse_board_and_channel_num(self, nets):
        self.board_num = 7
        self.channel_num = int(self.nets_pattern.match(nets).group(1))
