from openpyxl import load_workbook
from src.SchemComponent import *
from src.Analyzer import PathAnalyzer
import logging
from itertools import chain


class SourceReader(SpecialNets, SpecialSymbols):

    def __init__(self):
        SpecialNets.__init__(self)
        SpecialSymbols.__init__(self)
        self.logger = logging.getLogger(__name__)

        self.SYMBOL_DICT = {}
        for s in chain(self.plane_symbols, self.terminal_symbols):
            self.SYMBOL_DICT.update({s: SchematicSymbol(s)})

        self.NETS_DICT = defaultdict(list)
        self.NETS_DICT.update(self.special_nets)

    def read_xlsx(self, file_name):
        self.logger.info('importing schematic symbol and nets database...')
        wb = load_workbook(file_name)
        ws = wb.get_active_sheet()

        for row in ws.rows:
            for cell in row:
                this_line = str(cell.value)
                if "COMP:" in this_line:
                    cleaned_line = this_line.replace('\'', '').split(' ')
                    if len(cleaned_line) == 3:
                        oo = SchematicSymbol(cleaned_line[1])
                        [_, oo.type, oo.id] = cleaned_line
                        self.SYMBOL_DICT.update({oo.id: oo})

                if "Property:" in this_line:
                    if 'Part List Exclude=DNI' in this_line:
                        self.SYMBOL_DICT[oo.id].dni = True

                    if oo.unknown_links:
                        self.logger.warn('unknown comp_type prop: ' + this_line)

                if "Explicit Pin:" in this_line:
                    cleaned_line = this_line.strip().replace('\'', '').split(' ')
                    if len(cleaned_line) == 5:
                        [_, _, pin_num, pin_name, nets] = cleaned_line
                        self.SYMBOL_DICT[oo.id].pins.update({(pin_num, pin_name): nets})
                        self.NETS_DICT[nets].append((oo.id, pin_num, pin_name))

                        if oo.unknown_links \
                                and oo.id not in self.device_symbols \
                                and oo.id not in self.connector_symbols:
                            self.logger.warn('unknown comp_type pins: ' + this_line)

        self.logger.info('importing schematic symbol and nets database done!')


class Explorer(SourceReader, SpecialSymbols):

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        SourceReader.__init__(self)
        SpecialSymbols.__init__(self)
        self.seen_nodes = []
        self.explored_links = []
        self.lvl = 0

    def explore(self, tail, level=0):
        # main function call for this class. finding path in this format:
        #     TAIL   -- EDGE -- HEAD
        self.logger.debug('-' * 60)
        self.logger.debug('exploring: %s, at level %s', tail.name, level)

        self.lvl = level
        node_tail = tail.tuple
        if self.lvl == 0:
            self.__clear_nodes_and_links()
            tail.is_origin = True

        if len(node_tail) != 3:
            raise ValueError

        # PROCESS FOR THIS ITERATION
        self.seen_nodes.append(tail.name)
        edge = self.__tail_to_edge(tail)
        heads = self.__edge_to_heads(edge)
        self.logger.debug('exploring: found edge %s', edge.name)
        self.logger.debug('exploring: found heads %s', str(heads))

        # RECORD LINK
        self.__record_link(tail, edge, heads, self.lvl)

        # PROCESS FOR THE NEXT ITERATION
        # self.lvl += 1
        filtered_heads = self.__filter_out_previous_nodes(heads)  # A, B, C --> A, B
        raw_next_tails = self.__heads_to_tails(filtered_heads)  # A, B --> C, D, E
        next_tails = self.__filter_out_terminal_nodes(raw_next_tails)
        self.seen_nodes.extend([str(x) for x in next_tails])

        # RECURSIVE SEARCH
        if next_tails:
            self.logger.debug('explored: %s, found link to %s', tail.name, str(next_tails))
            self.lvl += 2
            for next_tail in next_tails:
                # self.__reshuffle_links(next_tail.name)
                self.explore(next_tail, self.lvl)
            self.lvl -= 2
        else:
            self.logger.debug('explored: %s, found no more link', tail.name)
            pass

        # TODO consider using partial functools
        if self.lvl == 0:
            return SchematicPath(self.explored_links, PathAnalyzer())

    def __reshuffle_links(self, tail_name):
        for i, lnk in enumerate(self.explored_links):
            if lnk.head.name == tail_name:
                self.logger.debug('reshuffle: found %s' % str(lnk))
                self.logger.debug('reshuffle: from %s to %s' % (str(i), str(len(self.explored_links))))
                leading_link = self.explored_links.pop(i)
                self.explored_links.append(leading_link)
                break

    def __tail_to_edge(self, tail):
        (t, u, v) = tail.tuple
        return SchematicEdge(self.SYMBOL_DICT[t].pins[(u, v)])

    def __edge_to_heads(self, edge):
        all_edges = self.NETS_DICT[edge.name]
        if edge.name in ['unconnected']:
            return [SchematicNode(x) for x in all_edges if '[WARNING]' in x]
        elif edge.name in self.special_nets:
            return [SchematicNode(x) for x in all_edges if x[0].startswith('[')]
        else:
            return [SchematicNode(x) for x in all_edges if SchematicNode(x).name not in self.seen_nodes]

    def __heads_to_tails(self, heads):
        all_linked_ports = []
        for head in heads:
            (symbol, pin_num, pin_name) = head.tuple

            if not self.SYMBOL_DICT[symbol].dni:
                if self.SYMBOL_DICT[head.symbol].links:
                    # internal connections within symbol
                    states = self.SYMBOL_DICT[head.symbol].links.keys()
                    for state in states:
                        linked_nodes = self.SYMBOL_DICT[symbol].links[state][(pin_num, pin_name)]
                        if linked_nodes:
                            # TODO: future improvement to have multiple linked nodes. VERY UGLY.
                            linked_node = SchematicNode((symbol, linked_nodes[0], linked_nodes[1]))
                            if linked_node.name not in self.seen_nodes:
                                linked_nodes = [linked_node]
                                # self.__reshuffle_links(head.name)
                                self.__record_link(head, SchematicEdge(state), linked_nodes,
                                                   self.lvl + 1, internal_link=True)
                                all_linked_ports.extend(linked_nodes)
                else:
                    for lnk in reversed(self.explored_links):
                        if lnk.head.name == head.name:
                            lnk.head.is_terminal = True
                            break
            else:
                # TODO: also should set is_terminal = True
                self.logger.debug('__heads_to_tails: DNI symbol %s', symbol)

        return all_linked_ports

    def __filter_out_terminal_nodes(self, heads):
        return [head for head in heads if head.symbol not in self.terminal_symbols]

    def __filter_out_previous_nodes(self, heads):
        return [x for x in heads if x.name not in self.seen_nodes]

    def __record_link(self, tail, edge, heads, lvl, internal_link=False):
        for head in heads:
            link = SchematicLink((tail, head, edge, lvl))
            link.tail.is_active = True if self.SYMBOL_DICT[tail.symbol].is_active else False
            link.head.is_active = True if self.SYMBOL_DICT[head.symbol].is_active else False
            link.is_internal = internal_link
            self.explored_links.append(link)

    def __clear_nodes_and_links(self):
        self.seen_nodes = []
        self.explored_links = []

    def get_nodes_with_pin(self, symbol, pin):
        lst = self.SYMBOL_DICT[symbol].pins.keys()
        nodes = [SchematicNode((symbol, x, y)) for x, y in lst if x == pin or y == pin]

        if len(nodes) > 1:
            self.logger.warn('get_nodes_with_pin: multiple nodes found on %s with pin = %s', symbol, pin)
        if len(nodes) == 0:
            self.logger.error('get_nodes_with_pin: zero nodes found on %s with pin = %s', symbol, pin)
            raise ValueError

        self.logger.debug('get_nodes_with_pin: %s' % str(nodes))
        return nodes[0]

    def get_nodes_with_nets(self, nets):
        lst = self.NETS_DICT[nets]
        return [SchematicNode(x) for x in lst]

    def get_nets_which_contain(self, text):
        return sorted([x for x in self.NETS_DICT if text in x])
