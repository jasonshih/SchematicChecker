import SchemChecker.SchemComponent as sc
from openpyxl import load_workbook


class PathFinder(object):

    def __init__(self):
        self.SYMBOL_DICT = {}
        self.NETS_DICT = {}
        self.COMP_DICT = {}
        self.seen = []
        self.tab = ''

    def populate_dictionaries(self, file_name):
        wb = load_workbook(file_name)
        ws = wb.get_active_sheet()

        self.SYMBOL_DICT = {}
        self.NETS_DICT = {}
        # self.COMP_DICT = self.populate_component()
        cc = ''

        for row in ws.rows:
            for cell in row:
                if "COMP:" in str(cell.value):
                    ch = str(cell.value).replace('\'', '').split(' ')

                    if len(ch) == 3:

                        if ch[1].startswith('10'):
                            oo = sc.SchematicSymbol('std_2pins_passive')

                        elif ch[1].startswith('300-23460'):
                            oo = sc.SchematicSymbol('std_8pins_relay')

                        elif ch[1].startswith('EMBEDDED_SHORTING_BAR'):
                            oo = sc.SchematicComponent('std_shorting_bar')

                        else:
                            oo = sc.SchematicComponent()
                            print('unknown part type: ' + ch[1])

                        [_, oo.type, oo.id] = ch

                        # if oo.type in self.COMP_DICT.keys():
                        #     oo.links = self.COMP_DICT[oo.type].links
                        # else:
                        #     oo.links = {}

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

    def populate_component(self):

        comp_dict = {
            '300-23460-0237': sc.SchematicComponent('std_8pins_relay'),
            '100-46302-2491': sc.SchematicComponent('std_2pins_passive'),
            '100-46312-0000': sc.SchematicComponent('std_2pins_passive'),
            '100-46302-9093': sc.SchematicComponent('std_2pins_passive'),
            '100-55258-0105': sc.SchematicComponent('std_2pins_passive'),
            '105-35077-3222': sc.SchematicComponent('std_2pins_passive'),
            '100-46302-1002': sc.SchematicComponent('std_2pins_passive'),
            '105-35273-2475': sc.SchematicComponent('std_2pins_passive'),
            '100-46312-0103': sc.SchematicComponent('std_2pins_passive'),
            '100-76445-31R6': sc.SchematicComponent('std_2pins_passive'),
            '100-46313-0160': sc.SchematicComponent('std_2pins_passive'),
            '105-35273-2225': sc.SchematicComponent('std_2pins_passive'),
            '100-46302-1212': sc.SchematicComponent('std_2pins_passive'),
            '100-46311-0000': sc.SchematicComponent('std_2pins_passive'),
            'EMBEDDED_SHORTING_BAR': sc.SchematicComponent('std_shorting_bar')
        }

        return comp_dict

    def find_path(self, symbol, pin_num, pin_name, state='init'):

        # PROCESS FOR THIS ITERATION
        self.seen.append((symbol, pin_num, pin_name))
        nets = self.SYMBOL_DICT[symbol].pins[(pin_num, pin_name)]

        if nets in ['unconnected', 'AGND', '+5V']:
            ports_at_nets = []
        else:
            ports_at_nets = [x for x in self.NETS_DICT[nets] if x != (symbol, pin_num, pin_name)]

        # PRINT OUT FOR DEBUG
        starting_symbol_string = ' ' + '|'.join([symbol, state, pin_num, pin_name])
        final_symbol_string = ' & '.join(['|'.join([x, y, z]) for x, y, z in ports_at_nets])
        sep = ' --> '
        print(self.tab + starting_symbol_string + sep + nets + sep + final_symbol_string)

        # PROCESS FOR THE NEXT ITERATION
        filtered_ports = self.remove_previous_ports(ports_at_nets, self.seen)
        processed_ports = self.process_ports(filtered_ports)
        self.seen.extend([(x, y, z) for (x, _, y, z) in processed_ports])

        if processed_ports:
            self.tab += '--'
            for (x, s, y, z) in processed_ports:
                self.find_path(x, y, z, s)
            self.tab = self.tab[:-2]
        else:
            pass

        # return path

    @staticmethod
    def remove_previous_ports(ports, seen=None):
        if seen is None:
            seen = []

        # print (str([x for x in ports if x in seen]))
        return [x for x in ports if x not in seen]

    def process_ports(self, ports):

        all_linked_ports = []
        for each_port in ports:
            (symbol, port_num, port_name) = each_port

            states = self.SYMBOL_DICT[symbol].links.keys()

            for state in states:
                # print(str(state) + ' ' + str(each_port))
                linked_ports = self.SYMBOL_DICT[symbol].links[state][(port_num, port_name)]
                linked_ports = [(symbol, state, x, y) for (x, y) in linked_ports]
                all_linked_ports.extend(linked_ports)

        return all_linked_ports

    def clear_found_ports(self):
        self.seen = []

if __name__ == "__main__":

    xlsx_file = '/Users/cahyo/Dropbox/programming/python/SchematicChecker/input_files/P1495_sample.xlsx'
    pf = PathFinder()
    pf.populate_dictionaries(xlsx_file)

    # print('=' * 80)
    # pf.clear_found_ports()
    # pf.find_path('X0', '90', 'GPIO6')

    print('=' * 80)
    pf.clear_found_ports()
    pf.find_path('X0', '143', 'GPIO7')

    # print('=' * 80)
    # pf.clear_found_ports()
    # pf.find_path('X0', '110', 'MPP3')
    #
    # print('=' * 80)
    # pf.clear_found_ports()
    # pf.find_path('X2', '110', 'MPP3')
    #
    # print('=' * 80)
    # pf.clear_found_ports()
    # pf.find_path('J6', 'T8', 'IO85')

    print('=' * 80)
    pf.clear_found_ports()
    pf.find_path('J6', 'A15', 'IO8')
    pass