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
                    # TODO get DNI property
                    pass

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

    def find_path(self, node_tail, level=0):
        # main function call for this class. finding path in this format:
        #     TAIL   -- EDGE -- HEAD

        if level == 0:
            self.clear_found_ports()

        if len(node_tail) != 3:
            raise ValueError

        # PROCESS FOR THIS ITERATION
        edge = self.tail_to_edge(node_tail, level)
        node_head = self.edge_to_head(edge, node_tail)
        self.seen.append(node_tail)

        # RECORD PATH
        self.record_path(node_tail, edge, node_head)

        # PROCESS FOR THE NEXT ITERATION
        filtered_node_head = self.filter_out_previous_nodes(node_head, self.seen)  # A, B, C --> A, B
        next_node_tail = self.head_to_tail(filtered_node_head)  # A, B --> C, D, E
        filtered_next_tail = self.filter_out_terminal_nodes(next_node_tail)
        self.seen.extend(filtered_next_tail)

        # RECURSIVE SEARCH
        if filtered_next_tail:
            level += 1
            for each_node in filtered_next_tail:
                self.find_path(each_node, level)
            level -= 1
        else:
            pass

        return self.path

    def record_path(self, node, nets, ports):
        for each_port in ports:
            this_path = ['|'.join(node), '|'.join(each_port), nets]
            self.path.append(this_path)
            # print(this_path)
            pass

    @staticmethod
    def filter_out_previous_nodes(ports, seen=None):
        if seen is None:
            seen = []
        return [x for x in ports if x not in seen]

    @staticmethod
    def filter_out_terminal_nodes(ports):
        return [x for x in ports if x[0] not in ['[device]', '[tester]', '[WARNING]']]

    def tail_to_edge(self, tail, level):
        (t, u, v) = tail
        if str(t) in self.connector_symbols and level > 0:
            n = 'connector'
        elif str(t) in self.device_symbols and level > 0:
            n = 'socket'
        else:
            n = self.SYMBOL_DICT[t].pins[(u, v)]
        return n

    def edge_to_head(self, edge, tail):
        if edge in ['unconnected']:  # , 'AGND', '+5V', '-5V', 'tester', 'device']:
            return [x for x in self.NETS_DICT[edge] if '[WARNING]' in x]
        elif edge in ['AGND', '+5V', '-5V']:
            return [x for x in self.NETS_DICT[edge] if '[' + edge + ']' in x]
        else:
            return [x for x in self.NETS_DICT[edge] if x != tail]

    def head_to_tail(self, head):
        all_linked_ports = []
        for each_node in head:
            (symbol, port_num, port_name) = each_node

            if str(symbol) in self.device_symbols:
                # TERMINAL: device symbol
                # linked_ports = [('[device]', '[pmic]', '[tangerine]')]
                # all_linked_ports.extend(linked_ports)
                # self.record_path(each_node, 'socket', linked_ports)
                pass

            elif str(symbol) in self.connector_symbols:
                # TERMINAL: connector symbol
                # linked_ports = [('[tester]', '[uflex]', '[8x_config]')]
                # all_linked_ports.extend(linked_ports)
                # self.record_path(each_node, 'connector', linked_ports)
                pass

            else:
                # internal connections within symbol
                states = self.SYMBOL_DICT[symbol].links.keys()
                for state in states:
                    linked_ports = self.SYMBOL_DICT[symbol].links[state][(port_num, port_name)]
                    linked_ports = [(symbol, u, v) for (u, v) in linked_ports]
                    all_linked_ports.extend(linked_ports)

                    self.record_path(each_node, state, linked_ports)

        return all_linked_ports

    def clear_found_ports(self):
        self.seen = []
        self.path = []
