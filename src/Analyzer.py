# import re
# import logging
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

    def create_subset_path(self, pathway: SchematicPath, the_nets):
        # self.logger.setLevel(logging.INFO)
        all_nets_in_path = [link.edge.name for link in pathway.links]
        occurrence = all_nets_in_path.count(the_nets)

        all_path_to_plane = []
        if occurrence == 0:
            self.logger.debug('create_subset_path: No path from %s to %s', pathway.origin.name, the_nets)
        else:
            matches_indexes = (i for i, n in enumerate(all_nets_in_path) if n == the_nets)
            for index in matches_indexes:
                self.logger.debug('create_subset_path: from %s to %s, starting index [%s]',
                                  pathway.origin.name, the_nets, index)
                path_to_plane = []
                z = pathway.links[index].head.name
                # TODO try reversed
                for i in range(index, -1, -1):
                    link = pathway.links[i]
                    if link.head.name == z:
                        # self.logger.debug('create_subset_path: recording: [%s] %s', i, link)
                        path_to_plane.insert(0, link)
                        z = link.tail.name
                    else:
                        # self.logger.debug('create_subset_path: ignoring: [%s] %s', i, link)
                        pass

                self.logger.debug('create_subset_path: saving with path length: %s', len(path_to_plane))
                all_path_to_plane.append(SchematicPath(path_to_plane, PathAnalyzer()))

        # self.logger.setLevel(logging.DEBUG)
        return all_path_to_plane

    @staticmethod
    def iter_all_pins_in_symbol(symbol, oo):
        return sorted((y for x, y in oo.SYMBOL_DICT[symbol].pins.keys()))

    @staticmethod
    def iter_all_device_symbols(oo):
        return sorted((x for x in oo.SYMBOL_DICT.keys() if x in oo.device_symbols))

    @staticmethod
    def __mask_symbol_and_nets_identifier(pathway: SchematicPath):
        outer_list = []
        for link in pathway.links:
            inner_tuple = tuple([y.masked_name for y in link.items])
            outer_list.append(inner_tuple)
        return outer_list

    @staticmethod
    def iterset_tester_nets(pathway: SchematicPath):
        return {link.edge for link in pathway.links if link.edge.channel}

    @staticmethod
    def iterset_device_symbols(pathway: SchematicPath):
        return {node for link in pathway.links for node in link.nodes if node.is_device}

    def ascii_tree(self, pathway: SchematicPath):
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
                        d[branch].update({key: val})
                    else:
                        d[branch] = {key: val}
                    found = True

            if is_root:
                if not found:
                    d.update({key: val})
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
                        if i == lvl-1:
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
        for link in pathway.links:
            nested_dict = set_key_at_branch(nested_dict, branch=link.tail.short_name, key=link.head.short_name)

        return asciify({pathway.origin.short_name: nested_dict})

