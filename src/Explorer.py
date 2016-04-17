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

        if len(node_tail) != 3:
            raise ValueError

        # PROCESS FOR THIS ITERATION
        self.seen_nodes.append(tail.name)
        edge = self.__tail_to_edge(tail)
        heads = self.__edge_to_heads(edge)
        self.logger.debug('exploring: found edge %s', edge.name)

        # RECORD LINK
        self.__record_link(tail, edge, heads)

        # PROCESS FOR THE NEXT ITERATION
        filtered_heads = self.__filter_out_previous_nodes(heads)  # A, B, C --> A, B
        raw_next_tails = self.__heads_to_tails(filtered_heads)  # A, B --> C, D, E
        next_tails = self.__filter_out_terminal_nodes(raw_next_tails)
        self.seen_nodes.extend([str(x) for x in next_tails])

        # RECURSIVE SEARCH
        if next_tails:
            self.logger.debug('explored: %s, found link to %s', tail.name, str(next_tails))
            level += 1
            for next_tail in next_tails:
                self.explore(next_tail, level)
            level -= 1
        else:
            self.logger.debug('explored: %s, found no more link', tail.name)
            pass

        # TODO consider using partial functools
        return SchematicPath(self.explored_links, PathAnalyzer())

    def __tail_to_edge(self, tail):
        (t, u, v) = tail.tuple
        return SchematicEdge(self.SYMBOL_DICT[t].pins[(u, v)])

    def __edge_to_heads(self, edge):
        all_edges = self.NETS_DICT[edge.name]
        if edge.name in ['unconnected']:
            return [SchematicNode(x) for x in all_edges if '[WARNING]' in x]
        elif edge.name in self.special_nets:
            return [SchematicNode(x) for x in all_edges if '[' + edge.name + ']' in x]
        else:
            return [SchematicNode(x) for x in all_edges if SchematicNode(x).name not in self.seen_nodes]

    def __heads_to_tails(self, heads):
        all_linked_ports = []
        for head in heads:
            (symbol, pin_num, pin_name) = head.tuple

            if not self.SYMBOL_DICT[symbol].dni:
                if str(symbol) in chain(self.device_symbols, self.connector_symbols):
                    # linked_nodes = [('[device]', '[pmic]', '[tangerine]')]
                    # all_linked_ports.extend(linked_nodes)
                    # self.__record_link(head, 'socket', linked_nodes)
                    pass

                else:
                    # internal connections within symbol
                    states = self.SYMBOL_DICT[head.symbol].links.keys()
                    for state in states:
                        linked_nodes = self.SYMBOL_DICT[symbol].links[state][(pin_num, pin_name)]
                        if linked_nodes:
                            # TODO: future improvement to have multiple linked nodes. VERY UGLY.
                            linked_node = SchematicNode((symbol, linked_nodes[0], linked_nodes[1]))
                            if linked_node.name not in self.seen_nodes:
                                linked_nodes = [linked_node]
                                self.__record_link(head, SchematicEdge(state), linked_nodes)
                                all_linked_ports.extend(linked_nodes)
            else:
                self.logger.debug('__heads_to_tails: DNI symbol %s', symbol)

        return all_linked_ports

    def __filter_out_terminal_nodes(self, heads):
        return [x for x in heads if x.symbol not in self.terminal_symbols]

    def __filter_out_previous_nodes(self, heads):
        return [x for x in heads if x.name not in self.seen_nodes]

    def __record_link(self, tail, edge, heads):
        for head in heads:
            link = SchematicLink((tail, head, edge, self.lvl))
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

        return nodes[0]
