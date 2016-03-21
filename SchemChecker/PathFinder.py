from openpyxl import load_workbook
from SchemChecker.SchemComponent import *


class SourceReader(object):

    def __init__(self):
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
        pass

    def read_xlsx(self, file_name):
        print('importing schematic symbol & nets database...')
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
                                print('unknown part type: ' + ch[1])
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


class PathFinder(SourceReader, SpecialSymbols):

    def __init__(self):
        SourceReader.__init__(self)
        SpecialSymbols.__init__(self)
        self.seen = []
        self.path = []
        self.tab = ''
        self.tester_connections = []
        self.device_connections = []

    def find_path(self, ntail, level=0):
        # main function call for this class. finding path in this format:
        #     TAIL   -- EDGE -- HEAD
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
        self.record_path(ntail, edge, nheads)

        # PROCESS FOR THE NEXT ITERATION
        filtered_heads = self.filter_out_previous_nodes(nheads, self.seen)  # A, B, C --> A, B
        raw_next_tails = self.heads_to_tails(filtered_heads)  # A, B --> C, D, E
        next_tails = self.filter_out_terminal_nodes(raw_next_tails)
        self.seen.extend([str(x) for x in next_tails])

        # RECURSIVE SEARCH
        if next_tails:
            level += 1
            for next_tail in next_tails:
                self.find_path(next_tail, level)
            level -= 1
        else:
            pass

        return self.path

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
            return [SchematicNode(x) for x in self.NETS_DICT[edge.name] if SchematicNode(x) != tail]

    def heads_to_tails(self, heads):
        all_linked_ports = []
        for head in heads:
            (symbol, pin_num, pin_name) = head.tuple

            if str(symbol) in self.device_symbols:
                # TERMINAL: device symbol
                # linked_ports = [('[device]', '[pmic]', '[tangerine]')]
                # all_linked_ports.extend(linked_ports)
                # self.record_path(head, 'socket', linked_ports)
                pass

            elif str(symbol) in self.connector_symbols:
                # TERMINAL: connector symbol
                # linked_ports = [('[tester]', '[uflex]', '[8x_config]')]
                # all_linked_ports.extend(linked_ports)
                # self.record_path(head, 'connector', linked_ports)
                pass

            else:
                # internal connections within symbol
                states = self.SYMBOL_DICT[head.symbol].links.keys()
                for state in states:
                    linked_ports = self.SYMBOL_DICT[symbol].links[state][(pin_num, pin_name)]
                    linked_ports = [SchematicNode((symbol, u, v)) for (u, v) in linked_ports]
                    self.record_path(head, SchematicEdge(state), linked_ports)

                    all_linked_ports.extend(linked_ports)

        return all_linked_ports

    @staticmethod
    def filter_out_terminal_nodes(heads):
        return [x for x in heads if x.symbol not in ['[device]', '[tester]', '[WARNING]']]

    @staticmethod
    def filter_out_previous_nodes(heads, seen=None):
        if seen is None:
            seen = []
        return [x for x in heads if x.name not in seen]

    def record_path(self, ntail, edge, nheads):
        for nhead in nheads:
            self.path.append([ntail, nhead, edge])

    def clear_found_ports(self):
        self.seen = []
        self.path = []
