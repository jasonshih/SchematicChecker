from openpyxl import load_workbook
from src.SchemComponent import *
from src.Analyzer import PathAnalyzer
import logging


class SourceReader(object):

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.SYMBOL_DICT = {
            '[AGND]': SchematicSymbol('plane'),
            '[+5V]': SchematicSymbol('plane'),
            '[-5V]': SchematicSymbol('plane'),
            '[device]': SchematicSymbol('terminal'),
            '[tester]': SchematicSymbol('terminal'),
            '[WARNING]': SchematicSymbol('terminal')
        }

        self.NETS_DICT = {
            'AGND': [('[AGND]', '00', 'plane')],
            'unconnected': [('[WARNING]', '00', 'terminal')],
        }

    def read_xlsx(self, file_name):
        self.logger.info('importing schematic symbol and nets database...')
        # print('importing schematic symbol & nets database...')
        wb = load_workbook(file_name)
        ws = wb.get_active_sheet()
        cc = ''

        unknown_parts = []

        for row in ws.rows:
            for cell in row:
                if "COMP:" in str(cell.value):
                    ch = str(cell.value).replace('\'', '').split(' ')

                    if len(ch) == 3:

                        if ch[1].startswith('10'):
                            oo = SchematicSymbol('std_2pins_passive')

                        elif ch[1].startswith('300-23460'):
                            oo = SchematicSymbol('std_8pins_relay')

                        elif ch[1].startswith('EMBEDDED_SHORTING_BAR'):
                            oo = SchematicSymbol('jumper')

                        else:
                            oo = SchematicSymbol()
                            if ch[1] not in unknown_parts:
                                self.logger.warn('reading... unknown type: %s', ch[1])
                                # print('unknown part type: ' + ch[1])
                                unknown_parts.append(ch[1])

                        [_, oo.type, oo.id] = ch
                        self.SYMBOL_DICT.update({oo.id: oo})

                        cc = oo.id

                if "Property:" in str(cell.value):
                    if 'Part List Exclude=DNI' in str(cell.value):
                        self.SYMBOL_DICT[cc].dni = True

                if "Explicit Pin:" in str(cell.value):
                    ep = str(cell.value).strip().replace('\'', '').split(' ')
                    if len(ep) == 5:
                        [_, _, pin_num, pin_name, nets] = ep
                        self.SYMBOL_DICT[cc].pins.update({(pin_num, pin_name): nets})

                        if nets in self.NETS_DICT.keys():
                            self.NETS_DICT[nets].append((cc, pin_num, pin_name))
                        else:
                            self.NETS_DICT.update({nets: [(cc, pin_num, pin_name)]})
        self.logger.info('importing schematic symbol and nets database done!')


class Explorer(SourceReader, SpecialSymbols):

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        SourceReader.__init__(self)
        SpecialSymbols.__init__(self)
        self.seen = []
        self.path_obj = []

    def explore(self, ntail, level=0):
        # main function call for this class. finding path in this format:
        #     TAIL   -- EDGE -- HEAD
        self.logger.debug('finding path for %s, at level %s', ntail.symbol, level)

        node_tail = ntail.tuple
        if level == 0:
            self.clear_found_ports()

        if len(node_tail) != 3:
            raise ValueError

        # PROCESS FOR THIS ITERATION
        edge = self.tail_to_edge(ntail, level)
        nheads = self.edge_to_heads(edge, ntail)
        self.seen.append(ntail.name)

        # RECORD PATH
        self.record_path_obj(ntail, edge, nheads)

        # PROCESS FOR THE NEXT ITERATION
        filtered_heads = self.filter_out_previous_nodes(nheads, self.seen)  # A, B, C --> A, B
        raw_next_tails = self.heads_to_tails(filtered_heads)  # A, B --> C, D, E
        next_tails = self.filter_out_terminal_nodes(raw_next_tails)
        self.seen.extend([str(x) for x in next_tails])

        # RECURSIVE SEARCH
        if next_tails:
            level += 1
            for next_tail in next_tails:
                self.explore(next_tail, level)
            level -= 1
        else:
            pass

        # TODO consider using partial functools
        return SchematicPath(self.path_obj, PathAnalyzer())

    def tail_to_edge(self, tail, level):
        (t, u, v) = tail.tuple
        if str(t) in self.connector_symbols and level > 0:
            n = 'connector'
        elif str(t) in self.device_symbols and level > 0:
            n = 'socket'
        else:
            n = self.SYMBOL_DICT[t].pins[(u, v)]
        return SchematicEdge(n)

    def edge_to_heads(self, edge, tail):
        if edge.name in ['unconnected']:  # , 'AGND', '+5V', '-5V', 'tester', 'device']:
            return [SchematicNode(x) for x in self.NETS_DICT[edge.name] if '[WARNING]' in x]
        elif edge.name in ['AGND', '+5V', '-5V']:
            return [SchematicNode(x) for x in self.NETS_DICT[edge.name] if '[' + edge.name + ']' in x]
        else:
            return [SchematicNode(x) for x in self.NETS_DICT[edge.name] if SchematicNode(x).name != tail.name]

    def heads_to_tails(self, heads):
        all_linked_ports = []
        for head in heads:
            (symbol, pin_num, pin_name) = head.tuple

            if not self.SYMBOL_DICT[symbol].dni:
                if str(symbol) in [self.device_symbols, self.connector_symbols]:
                    # TERMINAL: device symbol
                    # linked_ports = [('[device]', '[pmic]', '[tangerine]')]
                    # all_linked_ports.extend(linked_ports)
                    # self.record_path_obj(head, 'socket', linked_ports)
                    pass

                else:
                    # internal connections within symbol
                    states = self.SYMBOL_DICT[head.symbol].links.keys()
                    for state in states:
                        linked_ports = self.SYMBOL_DICT[symbol].links[state][(pin_num, pin_name)]
                        linked_ports = [SchematicNode((symbol, u, v)) for (u, v) in linked_ports]
                        self.record_path_obj(head, SchematicEdge(state), linked_ports)

                        all_linked_ports.extend(linked_ports)
            else:
                self.logger.debug('DNI: symbol %s', symbol)

        return all_linked_ports

    @staticmethod
    def filter_out_terminal_nodes(heads):
        return [x for x in heads if x.symbol not in ['[device]', '[tester]', '[WARNING]']]

    @staticmethod
    def filter_out_previous_nodes(heads, seen=None):
        if seen is None:
            seen = []
        return [x for x in heads if x.name not in seen]

    def record_path_obj(self, ntail, edge, nheads):
        for nhead in nheads:
            link = SchematicLink((ntail, nhead, edge))
            self.path_obj.append(link)

    def clear_found_ports(self):
        # self.logger.debug('clearing self.seen and self.path ...')
        self.seen = []
        self.path_obj = []

    def get_nodes_with_pin(self, symbol, pin):

        lst = self.SYMBOL_DICT[symbol].pins.keys()
        nodes = [SchematicNode((symbol, x, y)) for x, y in lst if x == pin or y == pin]

        if len(nodes) > 1:
            self.logger.warn('multiple nodes found on %s with pin = %s', symbol, pin)
        if len(nodes) == 0:
            self.logger.error('zero nodes found on %s with pin = %s', symbol, pin)
            raise ValueError

        return nodes
