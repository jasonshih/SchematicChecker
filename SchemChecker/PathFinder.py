from openpyxl import load_workbook
from SchemChecker.SchemComponent import *
from graphviz import Graph


class PathFinder(object):

    def __init__(self):
        self.SYMBOL_DICT = {
            '[AGND]': SchematicSymbol('gnd'),
            '[+5V]': SchematicSymbol('+5V'),
            '[-5V]': SchematicSymbol('-5V'),
            '[device]': SchematicSymbol('device'),
            '[tester]': SchematicSymbol('tester')
        }
        self.NETS_DICT = {
            'AGND': [('[AGND]', 'gnd', 'plane')],
            '+5V': [('[+5V]', '+5V', 'plane')],
            '-5V': [('[-5V]', '-5V', 'plane')],
            'socket': [('[device]', '[pmic]', '[tangerine]')],
            'connector': [('[tester]', '[uflex]', '[8x_config]')],
        }
        self.COMP_DICT = {}
        self.seen = []
        self.path = []
        self.tab = ''
        self.tester_symbols = ['J' + str(t) for t in range(0, 54, 2)]
        self.tester_symbols.append('AGND')
        self.connector_symbols = ['J' + str(t) for t in range(1, 33)]
        self.device_symbols = ['X' + str(t) for t in range(16)]
        self.plane_symbols = ['GND', '+5V', '-5V']
        self.tester_connections = []
        self.device_connections = []

    def get_tester_connections(self):
        return set([x for _, x, _, _ in self.path if x.split('_')[0] in self.tester_symbols])

    def get_device_connections(self):
        return set([x for _, x, _, _ in self.path if x.split('|')[0] in self.device_symbols])

    def populate_dictionaries(self, file_name):
        wb = load_workbook(file_name)
        ws = wb.get_active_sheet()

        # self.SYMBOL_DICT = {}
        # self.NETS_DICT = {}
        # self.COMP_DICT = self.populate_component()
        cc = ''

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
                            oo = SchematicComponent('std_shorting_bar')

                        else:
                            oo = SchematicComponent()
                            print('unknown part type: ' + ch[1])

                        [_, oo.type, oo.id] = ch
                        self.SYMBOL_DICT.update({oo.id: oo})

                        cc = oo.id
                        # print(ch)

                if "Property:" in str(cell.value):
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

    @staticmethod
    def populate_component():

        comp_dict = {
            '300-23460-0237': SchematicComponent('std_8pins_relay'),
            '100-46302-2491': SchematicComponent('std_2pins_passive'),
            '100-46312-0000': SchematicComponent('std_2pins_passive'),
            '100-46302-9093': SchematicComponent('std_2pins_passive'),
            '100-55258-0105': SchematicComponent('std_2pins_passive'),
            '105-35077-3222': SchematicComponent('std_2pins_passive'),
            '100-46302-1002': SchematicComponent('std_2pins_passive'),
            '105-35273-2475': SchematicComponent('std_2pins_passive'),
            '100-46312-0103': SchematicComponent('std_2pins_passive'),
            '100-76445-31R6': SchematicComponent('std_2pins_passive'),
            '100-46313-0160': SchematicComponent('std_2pins_passive'),
            '105-35273-2225': SchematicComponent('std_2pins_passive'),
            '100-46302-1212': SchematicComponent('std_2pins_passive'),
            '100-46311-0000': SchematicComponent('std_2pins_passive'),
            'EMBEDDED_SHORTING_BAR': SchematicComponent('std_shorting_bar')
        }

        return comp_dict

    def find_path(self, symbol, pin_num, pin_name, state='init', level=0):

        if state == 'init':
            self.clear_found_ports()

        # PROCESS FOR THIS ITERATION
        node = (symbol, pin_num, pin_name)
        nets = self.node_to_nets(node, state)
        ports = self.nets_to_ports(nets, node)
        self.seen.append(node)

        # RECORD PATH
        self.record_path(node, nets, ports)
        # for each_port in ports:
        #     this_path = '|'.join(node) + ' -- ' + nets + ' -- ' + '|'.join(each_port) + ';'
        #     self.path.append(this_path)
        #     print(this_path)

        # PROCESS FOR THE NEXT ITERATION
        filtered_ports = self.remove_previous_ports(ports, self.seen)  # A, B, C --> A, B
        unfiltered_next_nodes = self.ports_to_nodes(filtered_ports)  # A, B --> C, D
        next_nodes = self.remove_tester_and_device_nodes(unfiltered_next_nodes)
        self.seen.extend(next_nodes)

        if next_nodes:
            level += 1
            for (t, u, v) in next_nodes:
                self.find_path(t, u, v, '', level)
            level -= 1
        else:
            pass

        return True

    def record_path(self, node, nets, ports):
        # TODO: confirm this with graphviz
        for each_port in ports:
            # this_path = '|'.join(node) + ' -- ' + nets + ' -- ' + '|'.join(each_port) + ';'
            # this_path = '\"' + '|'.join(node) + '\" -- \"' + '|'.join(each_port) + '\" [label = \"' + nets + '\"];'
            this_path = ['|'.join(node), '|'.join(each_port), nets]
            self.path.append(this_path)
            # print(this_path)

    @staticmethod
    def remove_previous_ports(ports, seen=None):
        if seen is None:
            seen = []
        return [x for x in ports if x not in seen]

    @staticmethod
    def remove_tester_and_device_nodes(ports):
        return [x for x in ports if x[0] not in ['[device]', '[tester]']]

    def node_to_nets(self, symbol_and_pin, state):
        (t, u, v) = symbol_and_pin
        if str(t) in self.connector_symbols and state != 'init':
            n = 'connector'
        elif str(t) in self.device_symbols and state != 'init':
            n = 'socket'
        else:
            n = self.SYMBOL_DICT[t].pins[(u, v)]
        return n

    def nets_to_ports(self, nets, symbol_and_pin):
        if nets in ['unconnected']:  # , 'AGND', '+5V', '-5V', 'tester', 'device']:
            return []
        elif nets in ['AGND', '+5V', '-5V']:
            return [x for x in self.NETS_DICT[nets] if '[' + nets + ']' in x]
        else:
            # print(symbol_and_pin)
            return [x for x in self.NETS_DICT[nets] if x != symbol_and_pin]

    def ports_to_nodes(self, ports):

        all_linked_ports = []
        for each_node in ports:
            (symbol, port_num, port_name) = each_node

            if str(symbol) in self.device_symbols:
                # device symbol
                linked_ports = [('[device]', '[pmic]', '[tangerine]')]
                all_linked_ports.extend(linked_ports)

                self.record_path(each_node, 'socket', linked_ports)

            elif str(symbol) in self.connector_symbols:
                # tester symbol
                linked_ports = [('[tester]', '[uflex]', '[8x_config]')]
                all_linked_ports.extend(linked_ports)

                self.record_path(each_node, 'connector', linked_ports)

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
