from openpyxl import load_workbook
from .SchemComponent import *
from .Analyzer import ExplorerUtilities
import logging
from itertools import chain


class SourceReader(SpecialNets, SpecialSymbols, LOG):

    def __init__(self):
        SpecialNets.__init__(self)
        SpecialSymbols.__init__(self)
        self.logger = logging.getLogger(__name__)

        self.SYMBOL_DICT = {}
        for s in chain(self.plane_symbols, self.terminal_symbols):
            self.SYMBOL_DICT[s] = SchematicSymbol('[CUSTOM]', s)

        self.NETS_DICT = defaultdict(list)
        self.NETS_DICT.update(self.special_nets)

    def read_xlsx(self, file_name):
        self.logger.info('importing schematic symbol and nets database...')
        wb = load_workbook(file_name)
        ws = wb.active

        for row in ws.rows:
            for cell in row:
                this_line = str(cell.value)

                if 'manufacturer Part number' in this_line or 'pin number' in this_line:
                    continue

                if "COMP:" in this_line:
                    c_line = this_line.replace('\'', '').split(' ')

                    assert len(c_line) == 3, 'unexpected number of data at line tagged with "COMP:"'

                    if c_line[2] in self.SYMBOL_DICT:
                        oo = self.SYMBOL_DICT[c_line[2]]
                    else:
                        oo = SchematicSymbol(c_line[1], c_line[2])
                        self.SYMBOL_DICT[oo.id] = oo

                if "Property:" in this_line:
                    if 'Part List Exclude=DNI' in this_line:
                        self.SYMBOL_DICT[oo.id].set_dni()

                    if oo.unknown_links:
                        self.logger.warn('unknown comp_type prop: {}, {}'.format(oo.id, this_line))

                if "Explicit Pin:" in this_line:
                    c_line = this_line.strip().replace('\'', '').split(' ')

                    assert len(c_line) == 5, 'unexpected number of data at line tagged with "Explicit Pin:"'
                    [_, _, pin_num, pin_name, nets] = c_line
                    self.SYMBOL_DICT[oo.id].pins[(pin_num, pin_name)] = nets
                    self.NETS_DICT[nets].append((oo.id, pin_num, pin_name))

                    if oo.unknown_links \
                            and oo.id not in self.device_symbols \
                            and oo.id not in self.connector_symbols:
                        self.logger.warn('unknown comp_type pins: ' + this_line)

        self.logger.info('importing schematic symbol and nets database done!')


class Explorer(SourceReader, SpecialSymbols, ExplorerUtilities):

    def __init__(self, connected_to=None):
        self.logger = logging.getLogger(__name__)
        SourceReader.__init__(self)
        SpecialSymbols.__init__(self)
        self._seen_nodes = []
        self._explored_links = []
        self._lvl = 0
        self.extension = connected_to

    def explore(self, tail, level=0):
        # main function call for this class. finding path in this format:
        #     TAIL   -- EDGE -- HEAD
        self.logger.debug('-' * 60)
        self.logger.debug('exploring: %s, at level %s', tail.name, level)

        self._lvl = level
        node_tail = tail.tuple
        if self._lvl == 0:
            self.__clear_nodes_and_links()
            tail.is_origin = True

        if len(node_tail) != 3:
            raise ValueError

        # PROCESS FOR THIS ITERATION
        self._seen_nodes.append(tail.name)
        edge = self.__tail_to_edge(tail)
        heads = self.__edge_to_heads(edge)
        self.logger.debug('exploring: found edge %s', edge.name)
        self.logger.debug('exploring: found heads %s', str(heads))

        # RECORD LINK
        self.__tag_active_nodes(tail, heads)
        self.__record_link(tail, edge, heads, self._lvl)

        # PROCESS FOR THE NEXT ITERATION
        # self.lvl += 1
        filtered_heads = self.__filter_out_previous_nodes(heads)  # A, B, C --> A, B
        raw_next_tails = self.__heads_to_tails(filtered_heads)  # A, B --> C, D, E
        next_tails = self.__filter_out_terminal_nodes(raw_next_tails)
        self._seen_nodes.extend([str(x) for x in next_tails])

        # RECURSIVE SEARCH
        if next_tails:
            self.logger.debug('explored: %s, found link to %s', tail.name, str(next_tails))
            self._lvl += 2
            for next_tail in next_tails:
                # self.__reshuffle_links(next_tail.name)
                self.explore(next_tail, self._lvl)
            self._lvl -= 2
        else:
            self.logger.debug('explored: %s, found no more link', tail.name)
            pass

        if self._lvl == 0:
            return SchematicPath(self._explored_links)

    def __reshuffle_links(self, tail_name):
        for i, lnk in enumerate(self._explored_links):
            if lnk.head.name == tail_name:
                self.logger.debug('reshuffle: found %s' % str(lnk))
                self.logger.debug('reshuffle: from %s to %s' % (str(i), str(len(self._explored_links))))
                leading_link = self._explored_links.pop(i)
                self._explored_links.append(leading_link)
                break

    def __tail_to_edge(self, tail):
        (t, u, v) = tail.tuple
        return SchematicEdge(self.SYMBOL_DICT[t].pins[(u, v)])

    def __edge_to_heads(self, edge):
        node_tuples = self.NETS_DICT[edge.name]
        if edge.name in ['unconnected']:
            return [SchematicNode(x) for x in node_tuples if '[WARNING]' in x]
        elif edge.name in self.special_nets:
            return [SchematicNode(x) for x in node_tuples if x[0].startswith('[')]
        else:
            return [SchematicNode(x) for x in node_tuples if SchematicNode(x).name not in self._seen_nodes]

    def __heads_to_tails(self, heads):
        all_linked_ports = []
        for head in heads:
            (t, u, v) = head.tuple

            if self.SYMBOL_DICT[t].is_dni():
                head.set_dni()
                for lnk in reversed(self._explored_links):
                    if lnk.head.name == head.name:
                        lnk.head.is_terminal = True

            elif self.SYMBOL_DICT[head.symbol].links:
                # internal connections within symbol
                states = self.SYMBOL_DICT[head.symbol].links.keys()
                for state in states:
                    linked_res = self.SYMBOL_DICT[t].links[state][(u, v)]
                    if isinstance(linked_res, list):
                        pass
                    elif isinstance(linked_res, tuple):
                        linked_node = SchematicNode((t, linked_res[0], linked_res[1]))
                        if linked_node.name not in self._seen_nodes:
                            edge = SchematicEdge(state)
                            self.__record_link(head, edge, [linked_node], self._lvl + 1, internal_link=True)
                            all_linked_ports.extend([linked_node])
                    else:
                        output_msg = 'linked_res nf {} ({}), {}/{}, type: {}'
                        self.logger.info(output_msg.format(t, state, u, v, self.SYMBOL_DICT[t].type))

            elif head.symbol in self.connector_symbols and self.extension:

                ext_tail = SchematicNode((head.symbol.replace('J', 'P'), head.pin_number, head.pin_name))
                edge = SchematicEdge('connector')
                self.__record_link(head, edge, [ext_tail], self._lvl + 1, internal_link=True)

                ext = self.extension.explore(ext_tail, 0)
                for link in ext.links:
                    link.level += self._lvl + 2

                self._explored_links.extend(ext.links)

            else:
                for lnk in reversed(self._explored_links):
                    if lnk.head.name == head.name:
                        lnk.head.is_terminal = True
                # self.__record_link(head, SchematicEdge('[TERMINAL]'),
                #                    [SchematicNode(self.NETS_DICT['[TERMINAL]'][0])],
                #                    self.lvl + 1, internal_link=True)

        return all_linked_ports

    def __tag_active_nodes(self, tail, heads):
        tail.is_active = True if self.SYMBOL_DICT[tail.symbol].is_active else False
        for head in heads:
            head.is_active = True if self.SYMBOL_DICT[head.symbol].is_active else False

    def __filter_out_terminal_nodes(self, heads):
        return [head for head in heads if head.symbol not in list(chain(self.terminal_symbols, self.plane_symbols))]

    def __filter_out_previous_nodes(self, heads):
        return [x for x in heads if x.name not in self._seen_nodes]

    def __record_link(self, tail, edge, heads, lvl, internal_link=False, connector_link=False):
        for head in heads:
            link = SchematicLink((tail, head, edge, lvl))
            link.is_internal = internal_link
            link.is_connector = connector_link
            self._explored_links.append(link)

    def __clear_nodes_and_links(self):
        self._seen_nodes = []
        self._explored_links = []
